$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open("P:\SEM3_CAPSTONE\EXPLAINABLE_INDUSTRIAL_AI_RCA_PROJECT_REPORT.docx")

$selection = $word.Selection
for ($i = 1; $i -le 10; $i++) {
    $word.Selection.HomeKey(6) # wdStory
    $find = $word.Selection.Find
    $find.Text = "Chapter " + $i
    $found = $find.Execute()
    if ($found) {
        $page = $word.Selection.Information(3) # wdActiveEndPageNumber
        Write-Host "Chapter $i Page: $page"
    }
}
$doc.Close(0)
$word.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
