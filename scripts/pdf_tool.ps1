param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ArgsList
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$toolPath = Join-Path $scriptDir 'pdf_tool.py'

if (Get-Command python -ErrorAction SilentlyContinue) {
    & python $toolPath @ArgsList
    exit $LASTEXITCODE
}

if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 $toolPath @ArgsList
    exit $LASTEXITCODE
}

Write-Error 'missing_runtime=python'
exit 1
