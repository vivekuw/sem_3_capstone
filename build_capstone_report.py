import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

from report_builder.helpers import (
    set_page_borders, setup_footer
)
from report_builder.preliminaries import build_preliminaries
from report_builder.ch1_intro import build_chapter_1
from report_builder.ch2_analysis import build_chapter_2
from report_builder.ch3_dataset import build_chapter_3
from report_builder.ch4_tech import build_chapter_4
from report_builder.ch5_methods import build_chapter_5
from report_builder.ch6_design import build_chapter_6
from report_builder.ch7_implementation import build_chapter_7
from report_builder.ch8_results import build_chapter_8
from report_builder.ch9_conclusion import build_chapter_9
from report_builder.ch10_references import build_chapter_10

OUTPUT_FILE = "EXPLAINABLE_INDUSTRIAL_AI_RCA_PROJECT_REPORT.docx"

def main():
    print("Initializing Document...")
    doc = docx.Document()

    # Section 1: Preliminaries (Cover, Certificate, Proforma, Declaration, Ack, Abstract, TOC, Synopsis)
    sec_pre = doc.sections[0]
    sec_pre.top_margin = Inches(1.0)
    sec_pre.bottom_margin = Inches(1.0)
    sec_pre.left_margin = Inches(1.25)
    sec_pre.right_margin = Inches(1.0)
    set_page_borders(sec_pre)
    
    print("Building Preliminaries (Pages i to xi)...")
    build_preliminaries(doc)

    # Section 2: Main Body Chapters (1 to 10)
    print("Creating Main Body Section with Arabic Page Numbers...")
    sec_body = doc.add_section(docx.enum.section.WD_SECTION.NEW_PAGE)
    sec_body.top_margin = Inches(1.0)
    sec_body.bottom_margin = Inches(1.0)
    sec_body.left_margin = Inches(1.25)
    sec_body.right_margin = Inches(1.0)
    set_page_borders(sec_body)

    # Unlink footer from preliminary section
    sec_body.footer.is_linked_to_previous = False
    setup_footer(sec_body, is_preliminary=False)

    # Set page number to start at 1
    sectPr = sec_body._sectPr
    pgNumType = parse_xml(f'<w:pgNumType {nsdecls("w")} w:start="1"/>')
    sectPr.append(pgNumType)

    print("Building Chapter 1: Introduction...")
    build_chapter_1(doc)

    print("Building Chapter 2: System Analysis...")
    build_chapter_2(doc)

    print("Building Chapter 3: Dataset & Process Description...")
    build_chapter_3(doc)

    print("Building Chapter 4: Technologies Used & UI Screenshots...")
    build_chapter_4(doc)

    print("Building Chapter 5: Methods & Mathematical Algorithms...")
    build_chapter_5(doc)

    print("Building Chapter 6: System Design...")
    build_chapter_6(doc)

    print("Building Chapter 7: Implementation Details...")
    build_chapter_7(doc)

    print("Building Chapter 8: Results and Discussion...")
    build_chapter_8(doc)

    print("Building Chapter 9: Conclusion & Future Scope...")
    build_chapter_9(doc)

    print("Building Chapter 10: References & Bibliography...")
    build_chapter_10(doc)

    print(f"Saving final report document to {OUTPUT_FILE}...")
    doc.save(OUTPUT_FILE)
    print(f"Report generation complete: {OUTPUT_FILE} saved successfully ({os.path.getsize(OUTPUT_FILE):,} bytes).")

if __name__ == "__main__":
    main()
