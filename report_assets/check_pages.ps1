$word = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $doc = $word.Documents.Open("P:\SEM3_CAPSTONE\EXPLAINABLE_INDUSTRIAL_AI_RCA_PROJECT_REPORT.docx")
    $pages = $doc.ComputeStatistics(2) # 2 = wdStatisticPages
    $words = $doc.ComputeStatistics(0) # 0 = wdStatisticWords
    $doc.Close(0)
    $word.Quit()
    Write-Host "WORD_PAGES: $pages"
    Write-Host "WORD_COUNT: $words"
}
catch {
    Write-Host "Word not available or COM error: $_"
}
finally {
    if ($word -ne $null) {
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
    }
}
