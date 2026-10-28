import docx
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from docx.shared import Inches, Pt, RGBColor
import os

doc = docx.Document()
section = doc.sections[0]
sectPr = section._sectPr
border_xml = (
    f'<w:pgBorders {nsdecls("w")} w:offsetFrom="page">'
    '<w:top w:val="single" w:sz="12" w:space="24" w:color="000000"/>'
    '<w:left w:val="single" w:sz="12" w:space="24" w:color="000000"/>'
    '<w:bottom w:val="single" w:sz="12" w:space="24" w:color="000000"/>'
    '<w:right w:val="single" w:sz="12" w:space="24" w:color="000000"/>'
    '</w:pgBorders>'
)
sectPr.append(parse_xml(border_xml))
doc.add_paragraph("Testing border XML")
doc.save("test_border.docx")
if os.path.exists("test_border.docx"):
    print("Test passed successfully, file created!")
    os.remove("test_border.docx")
