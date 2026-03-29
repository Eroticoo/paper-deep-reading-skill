import Foundation
import PDFKit
import AppKit
import Vision

struct MatchRecord {
    let pageIndex: Int
    let rect: CGRect
    let text: String
    let source: String
}

enum ToolError: Error, CustomStringConvertible {
    case usage(String)
    case openPDF(String)
    case openPage(Int)
    case encodeImage(String)
    case missingCGImage
    case noMatch(String)

    var description: String {
        switch self {
        case .usage(let message):
            return message
        case .openPDF(let path):
            return "failed_to_open_pdf=\(path)"
        case .openPage(let pageIndex):
            return "failed_to_open_page=\(pageIndex)"
        case .encodeImage(let path):
            return "failed_to_encode_image=\(path)"
        case .missingCGImage:
            return "failed_to_create_cgimage"
        case .noMatch(let query):
            return "no_match=\(query)"
        }
    }
}

let arguments = CommandLine.arguments

func loadDocument(_ path: String) throws -> PDFDocument {
    let expandedPath = NSString(string: path).expandingTildeInPath
    guard let document = PDFDocument(url: URL(fileURLWithPath: expandedPath)) else {
        throw ToolError.openPDF(expandedPath)
    }
    return document
}

func loadPage(document: PDFDocument, pageIndex: Int) throws -> PDFPage {
    guard let page = document.page(at: pageIndex) else {
        throw ToolError.openPage(pageIndex)
    }
    return page
}

func renderPageImage(page: PDFPage, cropRect: CGRect?, scale: CGFloat) throws -> NSImage {
    let pageBounds = page.bounds(for: .mediaBox)
    let targetRect = (cropRect ?? pageBounds).intersection(pageBounds)
    let size = NSSize(width: targetRect.width * scale, height: targetRect.height * scale)
    let image = NSImage(size: size)

    image.lockFocus()
    NSColor.white.setFill()
    NSBezierPath(rect: NSRect(origin: .zero, size: size)).fill()

    guard let context = NSGraphicsContext.current?.cgContext else {
        throw ToolError.missingCGImage
    }

    context.saveGState()
    context.scaleBy(x: scale, y: scale)
    context.translateBy(x: -targetRect.origin.x, y: -targetRect.origin.y)
    page.draw(with: .mediaBox, to: context)
    context.restoreGState()
    image.unlockFocus()

    return image
}

func writePNG(_ image: NSImage, to outputPath: String) throws {
    let outputURL = URL(fileURLWithPath: NSString(string: outputPath).expandingTildeInPath)
    let parent = outputURL.deletingLastPathComponent()
    try FileManager.default.createDirectory(at: parent, withIntermediateDirectories: true)

    guard let tiff = image.tiffRepresentation,
          let bitmap = NSBitmapImageRep(data: tiff),
          let png = bitmap.representation(using: .png, properties: [:]) else {
        throw ToolError.encodeImage(outputPath)
    }

    try png.write(to: outputURL)
}

func cgImage(from image: NSImage) throws -> CGImage {
    var rect = CGRect(origin: .zero, size: image.size)
    guard let cgImage = image.cgImage(forProposedRect: &rect, context: nil, hints: nil) else {
        throw ToolError.missingCGImage
    }
    return cgImage
}

func printMatch(_ index: Int, _ match: MatchRecord) {
    let text = match.text.replacingOccurrences(of: "\n", with: " ").replacingOccurrences(of: "\t", with: " ")
    print(
        "match=\(index) source=\(match.source) page=\(match.pageIndex) x=\(String(format: "%.1f", match.rect.origin.x)) y=\(String(format: "%.1f", match.rect.origin.y)) w=\(String(format: "%.1f", match.rect.size.width)) h=\(String(format: "%.1f", match.rect.size.height)) text=\(text)"
    )
}

func twoColumnCropBounds(pageBounds: CGRect, anchor: CGRect) -> (CGFloat, CGFloat) {
    if pageBounds.width < 500 {
        return (pageBounds.minX + 24, pageBounds.maxX - 24)
    }

    let midpoint = pageBounds.midX
    let gutter: CGFloat = 16
    if anchor.midX < midpoint {
        return (pageBounds.minX + 24, midpoint - gutter)
    }
    return (midpoint + gutter, pageBounds.maxX - 24)
}

func isSameColumn(pageBounds: CGRect, reference: CGRect, candidate: CGRect) -> Bool {
    if pageBounds.width < 500 {
        return true
    }

    let midpoint = pageBounds.midX
    let referenceIsLeft = reference.midX < midpoint
    let candidateIsLeft = candidate.midX < midpoint
    return referenceIsLeft == candidateIsLeft
}

func matchRects(document: PDFDocument, pageIndex: Int, query: String) -> [CGRect] {
    let selections = document.findString(query, withOptions: .caseInsensitive)
    return selections.compactMap { selection in
        guard let page = selection.pages.first,
              document.index(for: page) == pageIndex else { return nil }
        return selection.bounds(for: page)
    }
}

func nearestStopBelowRect(
    document: PDFDocument,
    pageIndex: Int,
    pageBounds: CGRect,
    anchor: CGRect,
    queries: [String],
    maxDistance: CGFloat
) -> CGRect? {
    var candidates: [CGRect] = []
    for query in queries {
        for rect in matchRects(document: document, pageIndex: pageIndex, query: query) {
            guard isSameColumn(pageBounds: pageBounds, reference: anchor, candidate: rect) else { continue }
            guard rect.maxY < anchor.minY else { continue }
            guard anchor.minY - rect.maxY <= maxDistance else { continue }
            candidates.append(rect)
        }
    }
    return candidates.max(by: { $0.maxY < $1.maxY })
}

func nearestStopAboveRect(
    document: PDFDocument,
    pageIndex: Int,
    pageBounds: CGRect,
    anchor: CGRect,
    queries: [String],
    maxDistance: CGFloat
) -> CGRect? {
    var candidates: [CGRect] = []
    for query in queries {
        for rect in matchRects(document: document, pageIndex: pageIndex, query: query) {
            guard isSameColumn(pageBounds: pageBounds, reference: anchor, candidate: rect) else { continue }
            guard rect.minY > anchor.maxY else { continue }
            guard rect.minY - anchor.maxY <= maxDistance else { continue }
            candidates.append(rect)
        }
    }
    return candidates.min(by: { $0.minY < $1.minY })
}

func cropRect(
    for preset: String,
    pageBounds: CGRect,
    anchor: CGRect,
    document: PDFDocument? = nil,
    pageIndex: Int? = nil
) -> CGRect {
    let theoremStopQueries = ["Proof", "Remark", "Theorem", "Lemma", "Proposition", "Corollary", "Assumption"]
    let captionQueries = ["Fig.", "Figure", "Table", "Tab.", "TABLE"]
    let sectionStopQueries = ["CONCLUSION", "REFERENCES", "Conclusion", "References"]

    switch preset {
    case "exact":
        return anchor.intersection(pageBounds)

    case "theorem":
        let (columnLeft, columnRight) = twoColumnCropBounds(pageBounds: pageBounds, anchor: anchor)
        let left = max(pageBounds.minX + 14, columnLeft - 8)
        let right = min(pageBounds.maxX - 10, columnRight + 26)
        var bottom = max(pageBounds.minY + 10, anchor.minY - 340)
        if let document, let pageIndex,
           let stopRect = nearestStopBelowRect(
               document: document,
               pageIndex: pageIndex,
               pageBounds: pageBounds,
               anchor: anchor,
               queries: theoremStopQueries,
               maxDistance: 420
           ) {
            bottom = max(bottom, stopRect.maxY + 1)
        }
        let top = min(pageBounds.maxY - 10, anchor.maxY + 2)
        return CGRect(x: left, y: bottom, width: right - left, height: top - bottom)

    case "figure-column":
        let (left, right) = twoColumnCropBounds(pageBounds: pageBounds, anchor: anchor)
        let bottom = max(pageBounds.minY + 10, anchor.minY - 10)
        var top = min(pageBounds.maxY - 10, anchor.maxY + 220)
        if let document, let pageIndex,
           let previousCaption = nearestStopAboveRect(
               document: document,
               pageIndex: pageIndex,
               pageBounds: pageBounds,
               anchor: anchor,
               queries: captionQueries,
               maxDistance: 360
           ) {
            top = min(top, previousCaption.minY - 12)
        }
        return CGRect(x: left, y: bottom, width: right - left, height: top - bottom)

    case "figure":
        let left = pageBounds.minX + 18
        let right = pageBounds.maxX - 18
        let bottom = max(pageBounds.minY + 10, anchor.minY - 10)
        let top = min(pageBounds.maxY - 10, anchor.maxY + 220)
        return CGRect(x: left, y: bottom, width: right - left, height: top - bottom)

    case "table":
        let (left, right) = twoColumnCropBounds(pageBounds: pageBounds, anchor: anchor)
        var bottom = max(pageBounds.minY + 10, anchor.minY - 102)
        var top = min(pageBounds.maxY - 10, anchor.maxY + 28)
        if let document, let pageIndex,
           let previousCaption = nearestStopAboveRect(
               document: document,
               pageIndex: pageIndex,
               pageBounds: pageBounds,
               anchor: anchor,
               queries: captionQueries,
               maxDistance: 260
           ) {
            top = min(top, previousCaption.minY - 12)
        }
        if let document, let pageIndex,
           let nextSection = nearestStopBelowRect(
               document: document,
               pageIndex: pageIndex,
               pageBounds: pageBounds,
               anchor: anchor,
               queries: sectionStopQueries,
               maxDistance: 220
           ) {
            bottom = max(bottom, nextSection.maxY + 10)
        }
        return CGRect(x: left, y: bottom, width: right - left, height: top - bottom)

    default:
        let marginX: CGFloat = 90
        let marginY: CGFloat = 90
        let rect = CGRect(
            x: anchor.minX - marginX,
            y: anchor.minY - marginY,
            width: anchor.width + 2 * marginX,
            height: anchor.height + 2 * marginY
        )
        return rect.intersection(pageBounds)
    }
}

func pdfTextMatches(document: PDFDocument, query: String, maxCount: Int) -> [MatchRecord] {
    let selections = document.findString(query, withOptions: .caseInsensitive)
    var records: [MatchRecord] = []

    for selection in selections {
        guard let page = selection.pages.first else { continue }
        let pageIndex = document.index(for: page)
        let rect = selection.bounds(for: page)
        let text = selection.string ?? query
        records.append(MatchRecord(pageIndex: pageIndex, rect: rect, text: text, source: "pdf"))
        if records.count >= maxCount {
            break
        }
    }

    return records
}

func ocrObservations(for page: PDFPage, scale: CGFloat = 2.0) throws -> [(CGRect, String)] {
    let pageBounds = page.bounds(for: .mediaBox)
    let image = try renderPageImage(page: page, cropRect: nil, scale: scale)
    let fullImage = try cgImage(from: image)

    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = false

    let handler = VNImageRequestHandler(cgImage: fullImage, options: [:])
    try handler.perform([request])

    let observations = request.results ?? []
    return observations.compactMap { observation in
        guard let candidate = observation.topCandidates(1).first else { return nil }
        let box = observation.boundingBox
        let rect = CGRect(
            x: box.origin.x * pageBounds.width,
            y: box.origin.y * pageBounds.height,
            width: box.size.width * pageBounds.width,
            height: box.size.height * pageBounds.height
        )
        return (rect, candidate.string)
    }
}

func ocrMatches(document: PDFDocument, query: String, maxCount: Int) throws -> [MatchRecord] {
    let queryLower = query.lowercased()
    var records: [MatchRecord] = []

    for pageIndex in 0..<document.pageCount {
        let page = try loadPage(document: document, pageIndex: pageIndex)
        let observations = try ocrObservations(for: page)
        for observation in observations {
            if observation.1.lowercased().contains(queryLower) {
                records.append(
                    MatchRecord(pageIndex: pageIndex, rect: observation.0, text: observation.1, source: "ocr")
                )
                if records.count >= maxCount {
                    return records
                }
            }
        }
    }

    return records
}

func collectMatches(document: PDFDocument, query: String, mode: String, maxCount: Int) throws -> [MatchRecord] {
    switch mode {
    case "pdf":
        return pdfTextMatches(document: document, query: query, maxCount: maxCount)
    case "ocr":
        return try ocrMatches(document: document, query: query, maxCount: maxCount)
    default:
        let direct = pdfTextMatches(document: document, query: query, maxCount: maxCount)
        if !direct.isEmpty {
            return direct
        }
        return try ocrMatches(document: document, query: query, maxCount: maxCount)
    }
}

func pageText(document: PDFDocument, pageIndex: Int, useOCRFallback: Bool) throws -> String {
    let page = try loadPage(document: document, pageIndex: pageIndex)
    if let text = page.string, !text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
        return text
    }
    if !useOCRFallback {
        return ""
    }

    let observations = try ocrObservations(for: page)
    let sorted = observations.sorted {
        if abs($0.0.midY - $1.0.midY) > 6 {
            return $0.0.midY > $1.0.midY
        }
        return $0.0.minX < $1.0.minX
    }
    return sorted.map { $0.1 }.joined(separator: "\n")
}

func optionValue(arguments: [String], name: String, defaultValue: String) -> String {
    if let index = arguments.firstIndex(of: name), index + 1 < arguments.count {
        return arguments[index + 1]
    }
    return defaultValue
}

func run() throws {
    guard arguments.count >= 3 else {
        throw ToolError.usage(
            """
            usage:
              pdf_snapshot.swift probe <pdf>
              pdf_snapshot.swift extract-text <pdf> <output>
              pdf_snapshot.swift find <pdf> <query> [--mode auto|pdf|ocr] [--max N]
              pdf_snapshot.swift render-page <pdf> <page-index> <output> [--scale S]
              pdf_snapshot.swift snapshot-query <pdf> <query> <match-index> <output> [--preset exact|generic|theorem|figure|figure-column|table] [--mode auto|pdf|ocr] [--scale S]
              pdf_snapshot.swift snapshot-rect <pdf> <page-index> <x> <y> <w> <h> <output> [--preset exact|generic|theorem|figure|figure-column|table] [--scale S]
            """
        )
    }

    let command = arguments[1]

    switch command {
    case "probe":
        let document = try loadDocument(arguments[2])
        print("pdf=\(NSString(string: arguments[2]).expandingTildeInPath)")
        print("page_count=\(document.pageCount)")
        if let title = document.documentAttributes?[PDFDocumentAttribute.titleAttribute] as? String,
           !title.isEmpty {
            print("title=\(title)")
        }

    case "extract-text":
        guard arguments.count >= 4 else {
            throw ToolError.usage("extract-text requires <pdf> <output>")
        }
        let document = try loadDocument(arguments[2])
        let output = NSString(string: arguments[3]).expandingTildeInPath
        let outputURL = URL(fileURLWithPath: output)
        try FileManager.default.createDirectory(
            at: outputURL.deletingLastPathComponent(),
            withIntermediateDirectories: true
        )

        var sections: [String] = []
        for pageIndex in 0..<document.pageCount {
            let text = try pageText(document: document, pageIndex: pageIndex, useOCRFallback: true)
            sections.append("===== Page \(pageIndex + 1) =====\n\(text)")
        }
        try sections.joined(separator: "\n\n").write(to: outputURL, atomically: true, encoding: .utf8)
        print("wrote=\(output)")

    case "find":
        guard arguments.count >= 4 else {
            throw ToolError.usage("find requires <pdf> <query>")
        }
        let document = try loadDocument(arguments[2])
        let query = arguments[3]
        let mode = optionValue(arguments: arguments, name: "--mode", defaultValue: "auto")
        let maxCount = Int(optionValue(arguments: arguments, name: "--max", defaultValue: "10")) ?? 10
        let matches = try collectMatches(document: document, query: query, mode: mode, maxCount: maxCount)
        if matches.isEmpty {
            throw ToolError.noMatch(query)
        }
        for (index, match) in matches.enumerated() {
            printMatch(index, match)
        }

    case "render-page":
        guard arguments.count >= 5 else {
            throw ToolError.usage("render-page requires <pdf> <page-index> <output>")
        }
        let document = try loadDocument(arguments[2])
        let pageIndex = Int(arguments[3]) ?? 0
        let output = arguments[4]
        let scale = Double(optionValue(arguments: arguments, name: "--scale", defaultValue: "2.0")) ?? 2.0
        let page = try loadPage(document: document, pageIndex: pageIndex)
        let image = try renderPageImage(page: page, cropRect: nil, scale: CGFloat(scale))
        try writePNG(image, to: output)
        print("wrote=\(NSString(string: output).expandingTildeInPath)")

    case "snapshot-query":
        guard arguments.count >= 6 else {
            throw ToolError.usage("snapshot-query requires <pdf> <query> <match-index> <output>")
        }
        let document = try loadDocument(arguments[2])
        let query = arguments[3]
        let matchIndex = Int(arguments[4]) ?? 0
        let output = arguments[5]
        let preset = optionValue(arguments: arguments, name: "--preset", defaultValue: "generic")
        let mode = optionValue(arguments: arguments, name: "--mode", defaultValue: "auto")
        let scale = Double(optionValue(arguments: arguments, name: "--scale", defaultValue: "4.0")) ?? 4.0
        let matches = try collectMatches(document: document, query: query, mode: mode, maxCount: matchIndex + 1)
        guard matches.indices.contains(matchIndex) else {
            throw ToolError.noMatch(query)
        }

        let match = matches[matchIndex]
        let page = try loadPage(document: document, pageIndex: match.pageIndex)
        let pageBounds = page.bounds(for: .mediaBox)
        let targetRect = cropRect(
            for: preset,
            pageBounds: pageBounds,
            anchor: match.rect,
            document: document,
            pageIndex: match.pageIndex
        )
        let image = try renderPageImage(page: page, cropRect: targetRect, scale: CGFloat(scale))
        try writePNG(image, to: output)
        print("wrote=\(NSString(string: output).expandingTildeInPath)")
        printMatch(matchIndex, match)

    case "snapshot-rect":
        guard arguments.count >= 9 else {
            throw ToolError.usage("snapshot-rect requires <pdf> <page-index> <x> <y> <w> <h> <output>")
        }
        let document = try loadDocument(arguments[2])
        let pageIndex = Int(arguments[3]) ?? 0
        let x = CGFloat(Double(arguments[4]) ?? 0)
        let y = CGFloat(Double(arguments[5]) ?? 0)
        let w = CGFloat(Double(arguments[6]) ?? 0)
        let h = CGFloat(Double(arguments[7]) ?? 0)
        let output = arguments[8]
        let preset = optionValue(arguments: arguments, name: "--preset", defaultValue: "generic")
        let scale = Double(optionValue(arguments: arguments, name: "--scale", defaultValue: "4.0")) ?? 4.0
        let page = try loadPage(document: document, pageIndex: pageIndex)
        let pageBounds = page.bounds(for: .mediaBox)
        let anchor = CGRect(x: x, y: y, width: w, height: h)
        let targetRect = cropRect(
            for: preset,
            pageBounds: pageBounds,
            anchor: anchor,
            document: document,
            pageIndex: pageIndex
        )
        let image = try renderPageImage(page: page, cropRect: targetRect, scale: CGFloat(scale))
        try writePNG(image, to: output)
        print("wrote=\(NSString(string: output).expandingTildeInPath)")

    default:
        throw ToolError.usage("unknown_command=\(command)")
    }
}

do {
    try run()
} catch {
    if let toolError = error as? ToolError {
        fputs("\(toolError.description)\n", stderr)
    } else {
        fputs("\(error)\n", stderr)
    }
    exit(1)
}
