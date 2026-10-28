$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open("P:\SEM3_CAPSTONE\EXPLAINABLE_INDUSTRIAL_AI_RCA_PROJECT_REPORT.docx")

foreach ($p in $doc.Paragraphs) {
    $txt = $p.Range.Text.Trim()
    if ($txt -match "^Chapter (\d+)") {
        $chNum = $matches[1]
        $page = $p.Range.Information(3) # wdActiveEndPageNumber
        if ($page -ge 12) {
            Write-Host "Chapter $chNum starts on Page: $page"
        }
    }
}
$doc.Close(0)
$word.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
