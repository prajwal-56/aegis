"""
build_report.py - Builds the official academic project report for Aegis in DOCX and PDF formats,
strictly adhering to the KTU / Ahalia School of Engineering & Technology standards.
Target page count: Exactly 20 pages.
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

def add_page_number_to_footer(footer):
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run()
    run.font.name = "Times New Roman"
    run.font.size = Pt(10)
    fldSimple = OxmlElement('w:fldSimple')
    fldSimple.set(qn('w:instr'), 'PAGE')
    run._r.append(fldSimple)

def set_cell_margins(cell, top=20, bottom=20, left=45, right=45):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def apply_table_styles(table, col_widths, is_header=True, font_size=8.0, pad=20, line_spacing=1.05):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Table Grid'
    for i, row in enumerate(table.rows):
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        if i == 0 and is_header:
            trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
        for j, cell in enumerate(row.cells):
            cell.width = Inches(col_widths[j])
            set_cell_margins(cell, top=pad, bottom=pad, left=40, right=40)
            if i == 0 and is_header:
                set_cell_background(cell, "EAECEE")
                for p in cell.paragraphs:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p.paragraph_format.space_before = Pt(0.5)
                    p.paragraph_format.space_after = Pt(0.5)
                    p.paragraph_format.line_spacing = line_spacing
                    for r in p.runs:
                        r.font.name = "Times New Roman"
                        r.font.size = Pt(font_size + 0.5)
                        r.font.bold = True
            else:
                for p in cell.paragraphs:
                    p.paragraph_format.space_before = Pt(0.5)
                    p.paragraph_format.space_after = Pt(0.5)
                    p.paragraph_format.line_spacing = line_spacing
                    for r in p.runs:
                        r.font.name = "Times New Roman"
                        r.font.size = Pt(font_size)

def add_p(doc, text="", style="Normal", font_size=11, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=3, line_spacing=1.15):
    p = doc.add_paragraph(style=style)
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    if text:
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(font_size)
        r.font.bold = bold
        r.font.italic = italic
    return p

def add_h1(doc, text, space_before=6, space_after=2):
    return add_p(doc, text, style="Heading 1", font_size=13, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=space_before, space_after=space_after, line_spacing=1.15)

def add_h2(doc, text, space_before=4, space_after=1):
    return add_p(doc, text, style="Heading 2", font_size=11.5, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=space_before, space_after=space_after, line_spacing=1.15)

def add_body(doc, text, bold_prefix="", space_after=2.5, line_spacing=1.15, font_size=10.5):
    p = doc.add_paragraph(style="Normal")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Times New Roman"
        r_pre.font.size = Pt(font_size)
        r_pre.font.bold = True
    if text:
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(font_size)
    return p

def add_figure_image(doc, img_path, caption, width_in=4.6, space_before=2, space_after=2):
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(space_before)
        p_img.paragraph_format.space_after = Pt(1)
        r = p_img.add_run()
        r.add_picture(img_path, width=Inches(width_in))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(1)
        p_cap.paragraph_format.space_after = Pt(space_after)
        r_cap = p_cap.add_run(caption)
        r_cap.font.name = "Times New Roman"
        r_cap.font.size = Pt(9)
        r_cap.font.italic = True
        r_cap.font.bold = True


def generate_20page_report(output_filename="Aegis_Project_Report.docx"):
    doc = docx.Document()
    
    # Configure base margins
    section = doc.sections[0]
    section.top_margin = Inches(0.4)
    section.bottom_margin = Inches(0.5)
    section.left_margin = Inches(0.9)
    section.right_margin = Inches(0.75)
    section.page_width = Inches(8.5)
    section.page_height = Inches(11.0)
    
    add_page_number_to_footer(section.footer)

    # ==========================================
    # PAGE 1: COVER PAGE
    # ==========================================
    add_p(doc, "AEGIS: NETWORK TOPOLOGY MINIMUM VERTEX COVER ENGINE", style="Heading 1", font_size=14, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=5, line_spacing=1.2)
    add_p(doc, "A PROJECT REPORT", font_size=12, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=3, space_after=3)
    add_p(doc, "Submitted By", font_size=11, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=1, space_after=2)
    add_p(doc, "PRAJWAL PRAVEEN   (Reg No: ATP24CS089)", font_size=12, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=8)
    
    add_p(doc, "To", font_size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=1, space_after=1)
    add_p(doc, "the APJ Abdul Kalam Technological University", font_size=11.5, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=1, space_after=2)
    add_p(doc, "in partial fulfillment of the requirements for the award of the degree of", font_size=10, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=1, space_after=2)
    add_p(doc, "Bachelor of Technology in Computer Science and Engineering", font_size=11.5, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=2)
    add_p(doc, "Course: PCCST502 – Design And Analysis Of Algorithms", font_size=11, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=10)
    
    # Emblem Image
    if os.path.exists("image1.jpeg"):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(4)
        p_logo.paragraph_format.space_after = Pt(8)
        p_logo.add_run().add_picture("image1.jpeg", width=Inches(2.2))

    add_p(doc, "DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING", font_size=11.5, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=2)
    add_p(doc, "Ahalia School of Engineering & Technology", font_size=11, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=1, space_after=1)
    add_p(doc, "Ahalia Campus, Kozhippara, Palakkad, Kerala - 678557", font_size=10, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=1, space_after=8)
    add_p(doc, "OCTOBER 2026", font_size=11, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=0)

    doc.add_page_break()

    # ==========================================
    # PAGE 2: CERTIFICATE PAGE
    # ==========================================
    if os.path.exists("image2.jpeg"):
        p_cert_hdr = doc.add_paragraph()
        p_cert_hdr.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cert_hdr.paragraph_format.space_before = Pt(0)
        p_cert_hdr.paragraph_format.space_after = Pt(6)
        p_cert_hdr.add_run().add_picture("image2.jpeg", width=Inches(5.2))

    add_p(doc, "DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING", font_size=11.5, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=3, space_after=2)
    add_p(doc, "CERTIFICATE", font_size=13, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=3, space_after=10)

    cert_text = (
        "This is to certify that the project work report entitled ‘Aegis: Network Topology Minimum Vertex Cover Engine’ "
        "submitted by PRAJWAL PRAVEEN (Reg No: ATP24CS089), of Fifth Semester, B.Tech in Computer Science & Engineering, "
        "has been successfully carried out under our supervision and guidance in partial fulfillment of the requirements "
        "of the project work for the subject PCCST502 – Design And Analysis Of Algorithms, prescribed by APJ Abdul Kalam "
        "Technological University (KTU), Kerala. It is further certified that this work is a bonafide record of the "
        "project work carried out by the above student during the academic year 2026–2027."
    )
    add_body(doc, cert_text, space_after=22, font_size=11)

    sig_table = doc.add_table(rows=4, cols=2)
    sig_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_w = [3.4, 3.4]
    
    cells_data = [
        ("Project Guide", "Head of the Department"),
        ("Ms. Happy A", "Dr. S Gunasekaran"),
        ("Assistant Professor", "Professor and Head"),
        ("Dept. of Computer Science & Engg.", "Dept. of Computer Science & Engg.")
    ]
    for r_idx, (g_txt, h_txt) in enumerate(cells_data):
        row = sig_table.rows[r_idx]
        row.cells[0].paragraphs[0].text = g_txt
        row.cells[1].paragraphs[0].text = h_txt
        for c_idx, cell in enumerate(row.cells):
            cell.width = Inches(col_w[c_idx])
            p_cell = cell.paragraphs[0]
            p_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.RIGHT
            p_cell.paragraph_format.space_before = Pt(1)
            p_cell.paragraph_format.space_after = Pt(1)
            p_cell.paragraph_format.line_spacing = 1.15
            for r in p_cell.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(10)
                if r_idx in (0, 1):
                    r.font.bold = True

    doc.add_page_break()

    # ==========================================
    # PAGE 3: DECLARATION PAGE
    # ==========================================
    if os.path.exists("image3.jpeg"):
        p_dec_hdr = doc.add_paragraph()
        p_dec_hdr.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_dec_hdr.paragraph_format.space_before = Pt(0)
        p_dec_hdr.paragraph_format.space_after = Pt(6)
        p_dec_hdr.add_run().add_picture("image3.jpeg", width=Inches(5.3))

    add_p(doc, "DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING", font_size=11.5, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=3, space_after=2)
    add_p(doc, "DECLARATION", font_size=13, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=3, space_after=10)

    dec_text = (
        "I hereby declare that the project report ‘AEGIS: NETWORK TOPOLOGY MINIMUM VERTEX COVER ENGINE’ submitted for the partial "
        "fulfilment of the requirements of the Fifth Semester Project for the course PCCST502 – Design And Analysis Of Algorithms, "
        "prescribed by APJ Abdul Kalam Technological University, Kerala, is a bonafide work carried out by me under the guidance of "
        "Ms. HAPPY A, Assistant Professor, Department of Computer Science & Engineering, Ahalia School of Engineering & Technology. "
        "The submission represents my algorithmic designs, implementation, and empirical evaluations in my own words. Where ideas, "
        "concepts, or standard library tools of others have been utilized, they have been adequately and accurately cited."
    )
    add_body(doc, dec_text, space_after=20, font_size=11)

    add_p(doc, "Place : PALAKKAD", font_size=10.5, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=1, space_after=1)
    add_p(doc, "Date  : 25-10-2026", font_size=10.5, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=1, space_after=14)

    sig_dec_table = doc.add_table(rows=3, cols=2)
    sig_dec_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    dec_rows = [
        ("COUNTERSIGNED", "PRAJWAL PRAVEEN"),
        ("Ms. Happy A", "(Reg No: ATP24CS089)"),
        ("Assistant Professor, Dept. of CSE", "Student, 5th Semester B.Tech CSE")
    ]
    for r_idx, (left_txt, right_txt) in enumerate(dec_rows):
        row = sig_dec_table.rows[r_idx]
        row.cells[0].paragraphs[0].text = left_txt
        row.cells[1].paragraphs[0].text = right_txt
        for c_idx, cell in enumerate(row.cells):
            cell.width = Inches(col_w[c_idx])
            p_cell = cell.paragraphs[0]
            p_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.RIGHT
            p_cell.paragraph_format.space_before = Pt(1)
            p_cell.paragraph_format.space_after = Pt(1)
            p_cell.paragraph_format.line_spacing = 1.15
            for r in p_cell.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(10)
                if r_idx in (0, 1):
                    r.font.bold = True

    doc.add_page_break()

    # ==========================================
    # PAGE 4: ACKNOWLEDGEMENT & VISION / MISSION
    # ==========================================
    add_h1(doc, "ACKNOWLEDGEMENT", space_before=0, space_after=3)
    ack_text = (
        "First and foremost, I express my deepest gratitude to the Almighty for granting the wisdom and strength "
        "necessary to complete this work. I express sincere gratitude to Dr. P R Suresh, Ph.D., Principal, "
        "Ahalia School of Engineering and Technology, for his institutional leadership. I extend sincere thanks to "
        "Dr. Krishna Kumar Kishor, Ph.D., Vice Principal, for providing computational infrastructure. I express my "
        "profound gratitude to Dr. S. Gunasekaran, Ph.D., Professor and Head of the Department of Computer Science "
        "and Engineering, for his constant encouragement. I am immensely indebted to my Project Guide, Ms. Happy A, "
        "Assistant Professor, for her meticulous supervision, insightful guidance, and continuous technical encouragement. "
        "I also thank Mr. Nandu S Nair for his timely mentorship. Finally, I express heartfelt appreciation to my parents "
        "and friends for their unwavering moral support."
    )
    add_body(doc, ack_text, space_after=4, font_size=10.5)

    add_h2(doc, "INSTITUTION VISION & MISSION", space_before=3, space_after=1)
    add_body(doc, "Vision: Grow as a center of learning and research, transforming students to professionals with knowledge, skill, competence, commitment, confidence through decisive learning and contribute to the sustainable development of the society.", bold_prefix="• ", space_after=1.5, font_size=10)
    add_body(doc, "Mission: To instil technical expertise to address current challenges; to foster research, innovation, and entrepreneurship; and to promote welfare of society through ethical and professional conduct.", bold_prefix="• ", space_after=3, font_size=10)

    add_h2(doc, "DEPARTMENT VISION & MISSION", space_before=3, space_after=1)
    add_body(doc, "Vision: To develop computer science engineers with knowledge, computing skills and empowering them to excel in their profession through performance based learning contributing to sustainability, well-being of the society and professional ethics.", bold_prefix="• ", space_after=1.5, font_size=10)
    add_body(doc, "Mission: To implement effective outcome-based education that fosters competent and skilled graduates; and to provide opportunities in research and collaborative innovation.", bold_prefix="• ", space_after=1, font_size=10)

    doc.add_page_break()

    # ==========================================
    # PAGE 5: ABSTRACT
    # ==========================================
    add_h1(doc, "ABSTRACT", space_before=0, space_after=4)
    abs_intro = (
        "The Aegis project is an algorithmic network defense optimization engine engineered to solve the optimal Intrusion Detection System "
        "(IDS) and firewall sensor placement problem on computer networks. Deploying deep-packet inspection sensors across every single host is "
        "economically, computationally, and logistically prohibitive. By modeling network topologies as undirected graphs G = (V, E) where devices "
        "constitute vertices and communication links represent edges, Aegis frames sensor placement as the fundamental Minimum Vertex Cover (MVC) "
        "combinatorial optimization problem."
    )
    add_body(doc, abs_intro, space_after=4, font_size=10.5)

    add_body(doc, "To formulate network defense sensor allocation as a mathematically rigorous graph optimization problem, evaluate the computational boundaries of Karp's NP-complete vertex cover problem, and engineer high-performance exact, approximate, and heuristic solvers capable of processing both synthetic topologies and real-world Nmap network scans.", bold_prefix="PROJECT IDEA: ", space_after=4, font_size=10.5)

    add_body(doc, "Aegis is developed in Python 3 utilizing NetworkX for graph modeling, Matplotlib for topological and empirical visualization, and python-nmap for active host discovery. The engine implements three distinct algorithmic paradigms: (1) An exact Branch-and-Bound algorithm with maximal matching lower-bound pruning and degree-1 reductions achieving optimality in O(1.465^n) time; (2) A classic polynomial-time 2-Approximation algorithm based on maximal matching guaranteeing solutions within 2*|OPT| in linear O(|E|) time; and (3) A Greedy Degree heuristic achieving an O(log Delta) approximation. Experimental evaluation demonstrates that Aegis reduces active monitoring requirements by 70% to 75% on enterprise networks while preserving 100% link coverage.", bold_prefix="IMPLEMENTATION & METHODOLOGY: ", space_after=4, font_size=10.5)

    add_body(doc, "https://github.com/prajwal-56/aegis", bold_prefix="GITHUB REPOSITORY: ", space_after=1, font_size=10.5)

    doc.add_page_break()

    # ==========================================
    # PAGE 6: LIST OF CONTENTS (COMPACT TABLE FITTING WELL WITHIN PAGE 6)
    # ==========================================
    add_h1(doc, "LIST OF CONTENTS", space_before=0, space_after=2)
    
    toc_data = [
        ("S.NO", "TOPIC", "PAGE NO"),
        ("1", "CHAPTER 1 - INTRODUCTION", "8"),
        ("1.1", "Background & Cybersecurity Motivation", "8"),
        ("1.2", "Relevance to Design and Analysis of Algorithms", "8"),
        ("1.3", "Aim and Objectives of the Project", "9"),
        ("1.4", "Problem Statement, Scope & Requirements", "9"),
        ("2", "CHAPTER 2 - ALGORITHMIC FOUNDATIONS & ANALYSIS", "10"),
        ("2.1", "Graph-Theoretic Mathematical Formulation", "10"),
        ("2.2", "Minimum Vertex Cover & NP-Completeness Proof", "10"),
        ("2.3", "Exact Solver: Branch-and-Bound with Pruning", "11"),
        ("2.4", "Polynomial-Time 2-Approximation via Maximal Matching", "12"),
        ("2.5", "Greedy Degree-Based Heuristic", "12"),
        ("2.6", "Asymptotic Complexity Summary", "12"),
        ("3", "CHAPTER 3 - SYSTEM ARCHITECTURE & DESIGN", "13"),
        ("3.1", "System Pipeline Architecture", "13"),
        ("3.2", "Modular Software Component Design", "13"),
        ("3.3", "Network Ingestion & Subnet Anti-Clique Engine", "14"),
        ("3.4", "Interactive Visualization & CLI Dispatcher", "14"),
        ("4", "CHAPTER 4 - IMPLEMENTATION & WORKFLOW", "15"),
        ("4.1", "End-to-End Execution Workflow", "15"),
        ("4.2", "Branch-and-Bound Decision Flowchart", "15"),
        ("4.3", "Core Algorithmic Engineering Mechanisms", "16"),
        ("4.4", "Defensive Invariant Enforcement & Robustness", "16"),
        ("5", "CHAPTER 5 - EXPERIMENTAL RESULTS & BENCHMARKING", "17"),
        ("5.1", "Benchmarking Experimental Setup", "17"),
        ("5.2", "Empirical Runtime & Scaling Analysis", "17"),
        ("5.3", "Topological Case Studies (Enterprise & Corporate LAN)", "18"),
        ("5.4", "Hardware Overhead & Economic Cost Savings Analysis", "18"),
        ("6", "CHAPTER 6 - SOFTWARE TESTING & VERIFICATION", "19"),
        ("6.1", "Testing Strategy & Canonical Graph Benchmark Verification", "19"),
        ("6.2", "Automated Pytest Execution Matrix (10/10 Passing)", "19"),
        ("7", "CHAPTER 7 - CONCLUSION & FUTURE ENHANCEMENTS", "20"),
        ("7.1", "Project Summary & Key Algorithmic Takeaways", "20"),
        ("7.2", "Future Research Roadmap & Technological References", "20"),
    ]

    t_toc = doc.add_table(rows=len(toc_data), cols=3)
    for r_idx, row_vals in enumerate(toc_data):
        for c_idx, val in enumerate(row_vals):
            t_toc.rows[r_idx].cells[c_idx].paragraphs[0].text = val
    apply_table_styles(t_toc, [0.8, 5.0, 1.0], is_header=True, font_size=7.2, pad=8, line_spacing=1.0)

    doc.add_page_break()

    # ==========================================
    # PAGE 7: LIST OF FIGURES & LIST OF TABLES
    # ==========================================
    add_h1(doc, "LIST OF FIGURES", space_before=0, space_after=2)
    fig_data = [
        ("FIG NO", "FIGURE NAME", "PAGE"),
        ("Figure 3.1", "Aegis System Architecture & Algorithmic Pipeline", "13"),
        ("Figure 4.1", "Branch-and-Bound Exact Solver Logic Decision Flowchart", "15"),
        ("Figure 5.1", "Runtime Scaling Comparison (Log Scale) & Solution Quality Bounds", "17"),
        ("Figure 5.2", "Enterprise Network Topology Optimal Vertex Cover (|OPT| = 4)", "18"),
        ("Figure 5.3", "Mock Corporate Network Topology Optimal Sensor Placement (|OPT| = 3)", "18"),
    ]
    t_fig = doc.add_table(rows=len(fig_data), cols=3)
    for r_idx, row_vals in enumerate(fig_data):
        for c_idx, val in enumerate(row_vals):
            t_fig.rows[r_idx].cells[c_idx].paragraphs[0].text = val
    apply_table_styles(t_fig, [1.0, 4.8, 1.0], is_header=True, font_size=8.5, pad=20)

    add_h1(doc, "LIST OF TABLES", space_before=10, space_after=2)
    tab_data = [
        ("TABLE NO", "TABLE NAME", "PAGE"),
        ("Table 2.1", "Asymptotic Time & Space Complexity of Implemented Solvers", "12"),
        ("Table 3.1", "Aegis Modular Code Architecture & Component Responsibilities", "13"),
        ("Table 5.1", "Empirical Runtime, Solution Size, and Approximation Ratios across Network Sizes", "17"),
        ("Table 5.2", "Network Monitoring Hardware Overhead and Cost Reduction Matrix", "18"),
        ("Table 6.1", "Automated Test Suite Verification Matrix (10 Automated Test Cases)", "19"),
    ]
    t_tab = doc.add_table(rows=len(tab_data), cols=3)
    for r_idx, row_vals in enumerate(tab_data):
        for c_idx, val in enumerate(row_vals):
            t_tab.rows[r_idx].cells[c_idx].paragraphs[0].text = val
    apply_table_styles(t_tab, [1.0, 4.8, 1.0], is_header=True, font_size=8.5, pad=20)

    doc.add_page_break()

    # ==========================================
    # PAGE 8: CHAPTER 1 - INTRODUCTION (PART 1)
    # ==========================================
    add_h1(doc, "CHAPTER 1", space_before=0, space_after=1)
    add_h1(doc, "INTRODUCTION", space_before=0, space_after=4)

    add_h2(doc, "1.1 Background & Cybersecurity Motivation", space_before=2, space_after=1)
    add_body(doc, (
        "Modern enterprise and campus computer networks interconnect hundreds or thousands of heterogeneous networked endpoints, including "
        "core backbone routers, departmental distribution switches, database clusters, virtualization hosts, engineering workstations, and IoT "
        "hardware. In this complex, interconnected networking paradigm, securing communication channels against internal lateral movement, stealthy "
        "port scanning, unauthorized exfiltration, and zero-day malware dissemination is a paramount cybersecurity priority. Network Intrusion "
        "Detection Systems (NIDS) and packet-sniffing appliances operate by intercepting raw communication frames as they traverse physical or logical links."
    ))
    add_body(doc, (
        "However, deploying hardware inspection appliances, commercial TAP licenses, or high-overhead eBPF packet inspection engines across every single "
        "network host is economically prohibitive and introduces severe CPU overhead on lightweight endpoints. Fortunately, digital network transmission "
        "is an inherently relational process between an initiator u and a responder v over communication link (u, v). If either endpoint u OR v contains "
        "an active inspection monitor, every packet traversing that link is captured, inspected, and logged. Therefore, complete link surveillance does not "
        "require universal host instrumentation; rather, administrators require the smallest possible subset of network hosts such that every communication "
        "link touches at least one monitored host."
    ))

    add_h2(doc, "1.2 Relevance to Design and Analysis of Algorithms", space_before=3, space_after=1)
    add_body(doc, (
        "This real-world cybersecurity challenge maps directly to the classical Minimum Vertex Cover (MVC) problem—one of Richard Karp’s original "
        "21 NP-complete problems (1972). The Aegis project provides an end-to-end pedagogical and engineering case study for core concepts of the "
        "Design and Analysis of Algorithms (DAA) curriculum (PCCST502):\n"
        "1. Asymptotic Intractability: Demonstrates why brute-force exhaustive enumeration of vertex subsets suffers from exponential state explosion O(2^n · m).\n"
        "2. Exact Combinatorial Optimization: Illustrates how mathematical reductions (Degree-1 absorption) and admissible matching lower-bound heuristics "
        "enable Branch-and-Bound algorithms to prune massive subtrees, running in O(1.465^n) time.\n"
        "3. Approximation Algorithm Design: Explores polynomial-time approximation algorithms with provable worst-case performance ratios (2-Approximation via Maximal Matching).\n"
        "4. Heuristic Analysis: Investigates greedy local search heuristics that achieve logarithmic approximation bounds O(log Delta) in practice."
    ))

    doc.add_page_break()

    # ==========================================
    # PAGE 9: CHAPTER 1 - INTRODUCTION (PART 2)
    # ==========================================
    add_h2(doc, "1.3 Aim and Objectives of the Project", space_before=0, space_after=1)
    add_body(doc, "The overarching aim of Aegis is to bridge theoretical graph optimization with practical network security engineering. The concrete technical objectives are:", bold_prefix="Project Aim: ")
    add_body(doc, (
        "• Algorithmic Synthesis: Implement and mathematically evaluate three complementary solver paradigms: exact combinatorial Branch-and-Bound, "
        "linear-time 2-Approximation via maximal matching, and greedy degree heuristics.\n"
        "• Network Ingestion: Construct an active network scanning module utilizing Nmap to discover live hosts and reconstruct realistic hierarchical topologies.\n"
        "• Anti-Clique Reconstruction: Formulate an anti-clique graph normalization algorithm to eliminate artificial complete subgraphs (Kn) common in naive LAN scans.\n"
        "• Empirical Benchmarking: Develop an automated benchmarking suite to capture high-precision execution timings, approximation ratios, and scaling behavior.\n"
        "• Interactive Visualization: Build high-resolution graph visualization tools highlighting active monitoring nodes in crimson and monitored endpoints in slate blue.\n"
        "• Rigorous Verification: Establish a comprehensive automated unit and integration test suite guaranteeing algorithmic correctness across diverse topologies."
    ))

    add_h2(doc, "1.4 Problem Statement, Scope & Requirements", space_before=3, space_after=1)
    add_body(doc, (
        "Problem Formulation: Given an undirected graph G = (V, E) representing an active computer network where V represents network hosts and E "
        "represents communication channels, find a minimum cardinality subset C ⊆ V such that ∀ (u, v) ∈ E, (u ∈ C ∨ v ∈ C).\n"
        "Project Scope: The system encompasses active subnet discovery, synthetic topology modeling, algorithmic solving, empirical performance analysis, "
        "automated testing, and graphical topology rendering. Target hardware includes standard x86_64 Linux workstations with Python 3.10+ and Nmap."
    ))

    add_h2(doc, "1.5 Software & System Dependencies", space_before=3, space_after=1)
    add_body(doc, (
        "• Python 3.14 / 3.10+: Core runtime environment providing high-precision performance counters (time.perf_counter).\n"
        "• NetworkX (>=3.0): High-performance graph modeling library managing node attributes, adjacency matrices, and graph algorithms.\n"
        "• Matplotlib (>=3.8): Scientific visualization framework generating dual-axis logarithmic benchmark plots and topological layouts.\n"
        "• python-nmap (>=0.7.1) & Nmap: Network discovery suite performing ARP and ICMP host discovery across IPv4 subnets.\n"
        "• Pytest (>=8.0): Industrial testing framework executing automated test matrices and verifying algorithmic invariants."
    ))

    doc.add_page_break()

    # ==========================================
    # PAGE 10: CHAPTER 2 - ALGORITHMIC FOUNDATIONS (PART 1)
    # ==========================================
    add_h1(doc, "CHAPTER 2", space_before=0, space_after=1)
    add_h1(doc, "ALGORITHMIC FOUNDATIONS & THEORETICAL ANALYSIS", space_before=0, space_after=4)

    add_h2(doc, "2.1 Graph-Theoretic Mathematical Formulation", space_before=2, space_after=1)
    add_body(doc, (
        "Let G = (V, E) be an undirected, simple, finite graph. The vertex set V with |V| = n denotes the finite set of network devices. "
        "The edge set E with |E| = m denotes communication channels between devices. A subset C ⊆ V is formally defined as a Vertex Cover of G if and only if:\n"
        "                                                 ∀ (u, v) ∈ E : (u ∈ C ∨ v ∈ C)\n"
        "The Minimum Vertex Cover (MVC) optimization problem seeks to find a vertex cover C* of minimum cardinality:\n"
        "                                                   C* = argmin_{C ⊆ V} { |C| : C is a vertex cover of G }\n"
        "In decision form (VC-DEC), the problem asks: Given a graph G = (V, E) and an integer k ≤ |V|, does G contain a vertex cover C such that |C| ≤ k?"
    ))

    add_h2(doc, "2.2 Computational Complexity & NP-Completeness Proof", space_before=3, space_after=1)
    add_body(doc, (
        "Theorem: The Vertex Cover decision problem (VC-DEC) is NP-Complete.\n"
        "Proof Overview:\n"
        "1. VC-DEC ∈ NP: Given a candidate certificate C ⊆ V, a deterministic polynomial-time verifier verifies that |C| ≤ k in O(1) time and checks that "
        "for every edge (u, v) ∈ E, at least one of u or v belongs to C. This edge-checking process runs in O(|E|) time. Because the verification algorithm "
        "runs in polynomial time O(n + m), VC-DEC belongs to the complexity class NP.\n"
        "2. VC-DEC is NP-Hard via Reduction from 3-SAT: The reduction proceeds from 3-SAT to Independent Set (IS), and subsequently to Vertex Cover via the "
        "fundamental duality theorem: A set S ⊆ V is an independent set of G if and only if its complement V \\ S is a vertex cover of G. Since 3-SAT is "
        "proven NP-complete (Cook-Levin Theorem) and polynomial reductions compose transitively, VC-DEC is NP-Complete.\n"
        "Combinatorial Barrier: For a network of n devices, the number of possible vertex subsets is 2^n. For n = 15, 2^15 = 32,768 states (solvable in milliseconds). "
        "For n = 50, 2^50 ≈ 1.12 × 10^15 states, which would require decades of compute time. This exponential growth necessitates advanced exact branch pruning and approximation."
    ))

    doc.add_page_break()

    # ==========================================
    # PAGE 11: CHAPTER 2 - ALGORITHMIC FOUNDATIONS (PART 2)
    # ==========================================
    add_h2(doc, "2.3 Exact Solver: Branch-and-Bound with Pruning", space_before=0, space_after=1)
    add_body(doc, (
        "To achieve mathematical optimality without succumbing to naive 2^n combinatorial explosion, Aegis implements an exact Branch-and-Bound (B&B) "
        "algorithm fortified with admissible lower-bound bounding, degree-1 reductions, and maximum-degree branching heuristics."
    ))
    add_body(doc, (
        "1. Admissible Lower Bounding via Maximal Matching: In any graph G, a matching M ⊆ E is a subset of edges such that no two edges share a common vertex. "
        "Because each edge in M is mutually disjoint, no single vertex can cover more than one edge in M. Therefore, any valid vertex cover C must contain at least "
        "one distinct vertex for every edge in M. Consequently, the cardinality of ANY matching |M| establishes a rigorous admissible lower bound on the remaining cover:\n"
        "                                                      |Remaining Minimum Cover| ≥ |M|\n"
        "During recursive search, Aegis computes a greedy maximal matching M on remaining uncovered edges in O(|E|) time. If |current_cover| + |M| ≥ |best_known|, "
        "the current search subtree cannot possibly improve upon the best-known solution, and the entire branch is pruned immediately."
    ))
    add_body(doc, (
        "2. Degree-1 Vertex Reduction Rule: In sparse topologies, peripheral devices (workstations, printers) frequently possess degree 1. Let u be a degree-1 "
        "vertex connected solely to neighbor v. If u is chosen in the cover, it covers only the single edge (u, v). If neighbor v is chosen instead, v covers (u, v) "
        "in addition to all other edges incident to v. Thus, including v rather than u is always mathematically optimal or tied:\n"
        "                                                 deg(u) = 1 ∧ (u, v) ∈ E  ==>  v ∈ C*\n"
        "Aegis detects degree-1 leaves and immediately forces neighbor v into the cover without branching, shrinking the graph deterministically."
    ))
    add_body(doc, (
        "3. Maximum Degree Branching Heuristic: When no degree-1 reductions remain, the solver branches on the vertex v exhibiting the maximum remaining degree:\n"
        "• Branch 1 (v ∈ C): Include v in the cover and recurse on the remaining graph G - {v}.\n"
        "• Branch 2 (v ∉ C): If v is excluded, EVERY neighbor in N(v) MUST be included in the cover to satisfy all edges incident to v. Aegis adds N(v) to the cover "
        "and recurses on G - (N(v) ∪ {v}).\n"
        "Recurrence Relation & Complexity: This branching rule yields the recurrence T(n) ≤ T(n - 1) + T(n - deg(v)). Because deg(v) ≥ 2, the worst-case recurrence "
        "is bounded by T(n) ≤ T(n - 1) + T(n - 3), which solves to O(1.465^n). This reduction enables exact solving for networks of 30+ nodes in milliseconds."
    ))

    doc.add_page_break()

    # ==========================================
    # PAGE 12: CHAPTER 2 - ALGORITHMIC FOUNDATIONS (PART 3)
    # ==========================================
    add_h2(doc, "2.4 Polynomial-Time 2-Approximation via Maximal Matching", space_before=0, space_after=1)
    add_body(doc, (
        "When network scale exceeds 100 devices, exact algorithms become intractable. Aegis implements the classic polynomial-time 2-Approximation algorithm:\n"
        "Algorithm Mechanics: (1) Initialize cover C = ∅. (2) While uncovered edges remain, pick an arbitrary edge (u, v). (3) Add BOTH endpoints u and v to C. "
        "(4) Remove all edges incident to u or v. (5) Repeat until no uncovered edges remain.\n"
        "Rigorous Proof of the 2-Approximation Bound:\n"
        "• Let M be the set of edges selected in Step 2. Because all edges incident to u or v are purged upon selection, no two edges in M share an endpoint; hence, M is a matching.\n"
        "• Every valid vertex cover C* (including the optimal cover) must touch at least one endpoint of every edge in M. Because all edges in M are disjoint, "
        "no single vertex can cover more than one edge in M. Therefore:  |C*| ≥ |M|.\n"
        "• In our algorithm, exactly 2 vertices were added to C for each edge in M:  |C| = 2 · |M|.\n"
        "• Combining the two relations:  |C| = 2 · |M| ≤ 2 · |C*|.\n"
        "Hence, the algorithm is mathematically guaranteed never to pick more than twice the optimal number of sensors, executing in linear O(|E|) time."
    ))

    add_h2(doc, "2.5 Greedy Degree-Based Heuristic", space_before=2, space_after=1)
    add_body(doc, (
        "While the 2-approximation provides a provable worst-case bound of 2.0, picking both endpoints often introduces redundant sensors. "
        "Aegis implements a Greedy Degree Heuristic: at each iteration, it selects the vertex v with the maximum number of currently uncovered incident edges, "
        "adds v to C, and marks its incident edges as covered. This greedy strategy guarantees an O(log Delta) approximation factor (where Delta is the maximum degree) "
        "and empirically achieves optimal or near-optimal covers (|OPT|) on real hierarchical network topologies."
    ))

    add_h2(doc, "2.6 Asymptotic Complexity Summary", space_before=2, space_after=1)
    comp_data = [
        ("Algorithm", "Time Complexity", "Space Complexity", "Approximation Factor", "Optimality Guarantee"),
        ("Brute-Force Enumeration", "O(2^n · m)", "O(n)", "1.0 (Exact)", "Guaranteed Minimal"),
        ("Exact Branch & Bound", "O(1.465^n)", "O(n + m)", "1.0 (Exact)", "Guaranteed Minimal"),
        ("2-Approximation (Matching)", "O(m)", "O(n + m)", "2.0 (|C| <= 2*|OPT|)", "Bounded Approximate"),
        ("Greedy Degree Heuristic", "O(m · log n)", "O(n + m)", "O(log Delta)", "Empirical Near-Optimal"),
    ]
    t_comp = doc.add_table(rows=len(comp_data), cols=5)
    for r_idx, row_vals in enumerate(comp_data):
        for c_idx, val in enumerate(row_vals):
            t_comp.rows[r_idx].cells[c_idx].paragraphs[0].text = val
    apply_table_styles(t_comp, [1.4, 1.2, 1.1, 1.6, 1.5], is_header=True, font_size=8.5, pad=20)
    add_p(doc, "Table 2.1: Asymptotic Time & Space Complexity of Implemented Solvers", font_size=9.5, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=1)

    doc.add_page_break()

    # ==========================================
    # PAGE 13: CHAPTER 3 - SYSTEM ARCHITECTURE & DESIGN (PART 1)
    # ==========================================
    add_h1(doc, "CHAPTER 3", space_before=0, space_after=1)
    add_h1(doc, "SYSTEM ARCHITECTURE & DESIGN", space_before=0, space_after=3)

    add_h2(doc, "3.1 System Pipeline Architecture", space_before=2, space_after=1)
    add_body(doc, (
        "Aegis is engineered following a clean, layered pipeline pattern consisting of four coordinated layers: (1) Network Ingestion, "
        "(2) Topology Construction, (3) Algorithmic Solver Core, and (4) Analytics & Visualization. Figure 3.1 illustrates the architectural dataflow."
    ))

    add_figure_image(doc, "results/fig1_architecture.png", "Figure 3.1: Aegis System Architecture & Algorithmic Pipeline", width_in=4.7, space_before=2, space_after=2)

    add_h2(doc, "3.2 Modular Software Component Design", space_before=2, space_after=1)
    add_body(doc, "The codebase is organized into modular Python components adhering to strict separation of concerns:", space_after=2)
    mod_data = [
        ("Module File", "Primary Responsibility", "Core Classes / Functions"),
        ("graph_utils.py", "Graph modeling, validation, & visual rendering", "is_vertex_cover(), generate_synthetic_graph(), visualize_network_cover()"),
        ("exact_solver.py", "Exact Minimum Vertex Cover solvers", "exact_vertex_cover_branch_and_bound(), solve_exact(), _get_matching_lower_bound()"),
        ("approx_solver.py", "Linear-time approximation & greedy heuristics", "approx_vertex_cover_2approx(), approx_vertex_cover_greedy(), solve_approx()"),
        ("scan.py", "Nmap active discovery & topology builder", "scan_network_live(), build_network_graph(), get_local_subnet()"),
        ("benchmark.py", "Empirical runtime & quality evaluation suite", "run_benchmark_suite(), plot_benchmark_results()"),
        ("main.py", "Unified CLI interface & analytics dispatcher", "main(), run_pipeline(), print_summary_table()"),
    ]
    t_mod = doc.add_table(rows=len(mod_data), cols=3)
    for r_idx, row_vals in enumerate(mod_data):
        for c_idx, val in enumerate(row_vals):
            t_mod.rows[r_idx].cells[c_idx].paragraphs[0].text = val
    apply_table_styles(t_mod, [1.4, 2.8, 2.6], is_header=True, font_size=8.0, pad=18)
    add_p(doc, "Table 3.1: Aegis Modular Code Architecture & Component Responsibilities", font_size=9.5, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=1)

    doc.add_page_break()

    # ==========================================
    # PAGE 14: CHAPTER 3 - SYSTEM ARCHITECTURE & DESIGN (PART 2)
    # ==========================================
    add_h2(doc, "3.3 Network Ingestion Engine & Subnet Anti-Clique Reconstruction", space_before=0, space_after=1)
    add_body(doc, (
        "A critical engineering contribution in Aegis is solving the Subnet Clique Trap. Naive network scanners assume that all hosts on a /24 subnet "
        "communicate directly with one another, resulting in a complete graph (clique Kn). In Kn, the minimum vertex cover is mathematically trivial: "
        "MVC(Kn) = n - 1 (every device except one must be monitored). To model real networks accurately, scan.py reconstructs realistic hierarchical "
        "topologies:\n"
        "1. Gateway Sniffing: Inspects the kernel routing table via /proc/net/route or `ip route show default` to identify the default gateway router IP.\n"
        "2. Active Nmap Discovery: Executes `nmap -sn` (ping and ARP scan) to identify live hosts, MAC vendors, and hostnames without altering network state.\n"
        "3. Hierarchical Link Synthesis: Establishes a multi-tier tree: (a) Gateway router acts as core hub; (b) Departmental switches aggregate client pools; "
        "(c) Shared servers and printers connect to multiple client groups; and (d) Individual workstations attach as leaf endpoints.\n"
        "4. Mock Topology Fallback: If Nmap is uninstalled, if raw sockets are restricted, or if running offline, Aegis seamlessly loads a pre-configured "
        "10-device realistic corporate network topology (gateway, switches, NAS, printers, workstations, and IoT cameras)."
    ))

    add_h2(doc, "3.4 Interactive Visualization & CLI Dispatcher", space_before=3, space_after=1)
    add_body(doc, (
        "Aegis provides a rich command-line interface (main.py) and a scientific visualization engine (graph_utils.py):\n"
        "• Unified CLI Dispatcher: Supports flags for active scanning (--scan), mock testing (--mock), synthetic presets (--preset [enterprise|scale_free|random]), "
        "and comparative benchmarking (--benchmark).\n"
        "• Color-Coded Topological Rendering: Utilizes NetworkX spring-layout algorithms to draw network graphs. Active sensor nodes selected in the cover are "
        "rendered as enlarged crimson nodes (#DE2D26), while non-monitoring client endpoints are rendered in serene slate blue (#6BAED6). Edges represent monitored "
        "communication links. Visual figures are exported at publication-grade 300 DPI to the results/ directory.\n"
        "• Summary Table & Analytics: Displays ASCII summary tables comparing cover cardinality, execution latencies, approximation ratios, and percentage "
        "cost reductions across all three algorithms simultaneously."
    ))

    doc.add_page_break()

    # ==========================================
    # PAGE 15: CHAPTER 4 - IMPLEMENTATION & WORKFLOW (PART 1)
    # ==========================================
    add_h1(doc, "CHAPTER 4", space_before=0, space_after=1)
    add_h1(doc, "IMPLEMENTATION & WORKFLOW", space_before=0, space_after=3)

    add_h2(doc, "4.1 End-to-End Execution Workflow", space_before=2, space_after=1)
    add_body(doc, (
        "The end-to-end execution lifecycle of Aegis follows a deterministic, pipeline-driven control flow: (1) Argument parsing and target subnet "
        "detection; (2) Topology ingestion or synthetic graph generation; (3) Graph normalization into an undirected NetworkX graph G = (V, E); "
        "(4) Dispatching to exact, approximate, and greedy solvers; (5) Integrity verification via is_vertex_cover(); and (6) Results tabularization and visualization."
    ))

    add_h2(doc, "4.2 Branch-and-Bound Decision Flowchart", space_before=2, space_after=1)
    add_body(doc, (
        "Figure 4.1 details the recursive decision tree executed by the Branch-and-Bound solver. The engine iteratively tests lower-bound thresholds, "
        "applies reduction rules on degree-1 endpoints, and branches across the maximum-degree neighborhood."
    ))

    add_figure_image(doc, "results/fig2_flowchart.png", "Figure 4.1: Branch-and-Bound Exact Solver Logic Decision Flowchart", width_in=4.4, space_before=2, space_after=2)

    doc.add_page_break()

    # ==========================================
    # PAGE 16: CHAPTER 4 - IMPLEMENTATION & WORKFLOW (PART 2)
    # ==========================================
    add_h2(doc, "4.3 Core Algorithmic Engineering Mechanisms", space_before=0, space_after=1)
    add_body(doc, (
        "Aegis implements several high-performance algorithmic engineering techniques that optimize runtime and memory usage across all modules:\n"
        "1. Dynamic Adjacency Tracking: During Branch-and-Bound search, maintaining dynamic adjacency dictionaries remaining_adj = {u: set(neighbors)} "
        "enables O(1) degree lookups and rapid degree-1 vertex detection without expensive whole-graph traversals.\n"
        "2. Canonical Edge Normalization: To eliminate edge duplication in undirected graphs, edges are canonically represented as ordered 2-tuples "
        "tuple(sorted((u, v), key=str)). This ensures rapid set difference operations (remaining_edges - removed_edges) in constant time.\n"
        "3. Matching Lower Bound Cache: _get_matching_lower_bound() iterates through remaining edges and greedily accumulates pairwise disjoint edge pairs, "
        "computing an admissible lower bound in O(|E|) time.\n"
        "4. Degree-1 Leaf Absorption: When a degree-1 leaf is detected, Aegis bypasses branching entirely, immediately adding the sole neighbor to the cover "
        "and pruning all incident edges in a single recursive step."
    ))

    add_h2(doc, "4.4 Defensive Invariant Enforcement & Robustness", space_before=3, space_after=1)
    add_body(doc, (
        "• Algorithmic Invariant Verification: Every solver execution is cross-validated by is_vertex_cover(graph, cover). The function verifies that "
        "∀ (u, v) ∈ E : (u ∈ C ∨ v ∈ C), guaranteeing zero undetected links.\n"
        "• Boundary Condition Stability: Solvers handle edge cases gracefully: empty graphs G(0, 0) return empty sets ∅ in O(1) time; single-edge graphs "
        "G(2, 1) return minimal covers immediately without entering recursive loops.\n"
        "• Graceful Degradation: scan.py implements multi-layered fallback mechanisms: if python-nmap is uninstalled or if raw socket permissions are denied, "
        "the engine falls back to mock enterprise network topologies seamlessly, preventing fatal program crashes."
    ))

    doc.add_page_break()

    # ==========================================
    # PAGE 17: CHAPTER 5 - EXPERIMENTAL RESULTS & BENCHMARKING (PART 1)
    # ==========================================
    add_h1(doc, "CHAPTER 5", space_before=0, space_after=1)
    add_h1(doc, "EXPERIMENTAL RESULTS & PERFORMANCE BENCHMARKING", space_before=0, space_after=3)

    add_h2(doc, "5.1 Benchmarking Experimental Setup", space_before=2, space_after=1)
    add_body(doc, (
        "To evaluate solver execution time and solution quality, Aegis was benchmarked on synthetic Barabási–Albert scale-free networks "
        "ranging from n = 6 to n = 22 vertices (step size = 2, 3 randomized seed samples per size) on Linux x86_64 with Python 3.14."
    ))

    bench_rows = [
        ("Nodes (n)", "Exact Time (s)", "2-Approx Time (s)", "Greedy Time (s)", "Exact Size |OPT|", "2-Approx Size", "Greedy Size", "Approx Ratio"),
        ("6", "0.000051", "0.000008", "0.000017", "3.0", "4.0", "3.0", "1.33x"),
        ("8", "0.000047", "0.000010", "0.000016", "4.0", "6.0", "4.0", "1.50x"),
        ("10", "0.000052", "0.000008", "0.000018", "4.0", "6.7", "4.0", "1.69x"),
        ("12", "0.000070", "0.000012", "0.000022", "5.3", "8.7", "5.3", "1.65x"),
        ("14", "0.000084", "0.000015", "0.000031", "6.0", "9.0", "6.0", "1.50x"),
        ("16", "0.000103", "0.000017", "0.000028", "7.3", "10.7", "7.3", "1.45x"),
        ("18", "0.000119", "0.000019", "0.000034", "7.7", "11.7", "7.7", "1.54x"),
        ("20", "0.000138", "0.000024", "0.000047", "9.3", "13.3", "9.3", "1.43x"),
        ("22", "0.000164", "0.000026", "0.000048", "9.7", "16.0", "10.0", "1.64x"),
    ]
    t_bench = doc.add_table(rows=len(bench_rows), cols=8)
    for r_idx, row_vals in enumerate(bench_rows):
        for c_idx, val in enumerate(row_vals):
            t_bench.rows[r_idx].cells[c_idx].paragraphs[0].text = val
    apply_table_styles(t_bench, [0.8, 0.9, 1.0, 0.9, 0.9, 0.9, 0.8, 0.7], is_header=True, font_size=8.0, pad=16)
    add_p(doc, "Table 5.1: Empirical Runtime, Solution Size, and Approximation Ratios across Network Sizes", font_size=9.5, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=1)

    add_h2(doc, "5.2 Runtime Scaling & Quality Analysis", space_before=2, space_after=1)
    add_body(doc, (
        "Figure 5.1 presents the generated dual-benchmark plots: Left Plot shows that while Exact Branch-and-Bound exhibits steep exponential growth, "
        "2-Approximation and Greedy scale polynomially, running up to an order of magnitude faster. Right Plot confirms that 2-Approximation never "
        "exceeds the 2*|OPT| bound, while the Greedy heuristic consistently tracks the true optimal cover |OPT|."
    ))

    add_figure_image(doc, "results/benchmark_comparison.png", "Figure 5.1: Runtime Scaling Comparison (Log Scale) & Solution Quality Bounds", width_in=4.5, space_before=1, space_after=1)

    doc.add_page_break()

    # ==========================================
    # PAGE 18: CHAPTER 5 - EXPERIMENTAL RESULTS & BENCHMARKING (PART 2)
    # ==========================================
    add_h2(doc, "5.3 Topological Case Studies: Enterprise & Corporate Networks", space_before=0, space_after=1)
    add_body(doc, (
        "Case Study 1 (Enterprise Tree Topology, Figure 5.2): Evaluated on an enterprise network with 14 devices and 13 connections. The exact solver "
        "identified an optimal cover of |OPT| = 4 nodes [Switch-1, Switch-2, Switch-3, Switch-4], saving 71.4% in sensor deployment costs.\n"
        "Case Study 2 (Mock Corporate LAN, Figure 5.3): Evaluated on 10 hosts with 17 active connections (gateway, servers, printers, workstations, cameras, and phones). "
        "The solver selected 3 nodes [192.168.1.1, 192.168.1.101, 192.168.1.102], achieving 70.0% sensor reduction."
    ))

    # Side-by-side Table for Figures 5.2 and 5.3
    t_side = doc.add_table(rows=2, cols=2)
    t_side.alignment = WD_TABLE_ALIGNMENT.CENTER
    side_col_w = [3.4, 3.4]
    
    # Row 0: Images (width 2.55 in)
    for c_idx in range(2):
        t_side.rows[0].cells[c_idx].width = Inches(side_col_w[c_idx])
        p_c = t_side.rows[0].cells[c_idx].paragraphs[0]
        p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_c.paragraph_format.space_before = Pt(1)
        p_c.paragraph_format.space_after = Pt(1)
        r_img = p_c.add_run()
        img_src = "results/network_cover.png" if c_idx == 0 else "results/mock_network_cover.png"
        if os.path.exists(img_src):
            r_img.add_picture(img_src, width=Inches(2.55))

    # Row 1: Captions
    caps = [
        "Figure 5.2: Enterprise Topology (|OPT| = 4)",
        "Figure 5.3: Mock Corporate LAN (|OPT| = 3)"
    ]
    for c_idx in range(2):
        t_side.rows[1].cells[c_idx].width = Inches(side_col_w[c_idx])
        p_cap = t_side.rows[1].cells[c_idx].paragraphs[0]
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(1)
        p_cap.paragraph_format.space_after = Pt(2)
        r_cap = p_cap.add_run(caps[c_idx])
        r_cap.font.name = "Times New Roman"
        r_cap.font.size = Pt(8.0)
        r_cap.font.bold = True
        r_cap.font.italic = True

    add_h2(doc, "5.4 Hardware Overhead & Economic Cost Savings Analysis", space_before=2, space_after=1)
    add_body(doc, (
        "Across both synthetic and empirical network graphs, placing monitoring sensors exclusively at the minimum vertex cover nodes resulted in "
        "a 70.0% to 75.0% reduction in required sensor nodes. Table 5.2 translates these graph optimization results into concrete economic values:"
    ))

    cost_data = [
        ("Network Topology", "Total Nodes (n)", "Naive Placement ($1,200/node)", "Aegis Cover (|OPT|)", "Aegis Cost", "Savings ($)", "Savings (%)"),
        ("Enterprise Campus Tree", "14", "$16,800", "4", "$4,800", "$12,000", "71.4%"),
        ("Corporate Multi-Tier LAN", "10", "$12,000", "3", "$3,600", "$8,400", "70.0%"),
        ("Medium Branch Network", "22", "$26,400", "6", "$7,200", "$19,200", "72.7%"),
    ]
    t_cost = doc.add_table(rows=len(cost_data), cols=7)
    for r_idx, row_vals in enumerate(cost_data):
        for c_idx, val in enumerate(row_vals):
            t_cost.rows[r_idx].cells[c_idx].paragraphs[0].text = val
    apply_table_styles(t_cost, [1.1, 0.8, 1.3, 0.9, 1.0, 1.0, 0.7], is_header=True, font_size=7.5, pad=16)
    add_p(doc, "Table 5.2: Network Monitoring Hardware Overhead and Cost Reduction Matrix", font_size=9.0, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=1, space_after=1)

    doc.add_page_break()

    # ==========================================
    # PAGE 19: CHAPTER 6 - SOFTWARE TESTING & VERIFICATION
    # ==========================================
    add_h1(doc, "CHAPTER 6", space_before=0, space_after=1)
    add_h1(doc, "SOFTWARE TESTING & VERIFICATION", space_before=0, space_after=3)

    add_h2(doc, "6.1 Testing Strategy & Canonical Verification", space_before=2, space_after=1)
    add_body(doc, (
        "To verify solver correctness and mathematical bounds, Aegis employs an automated pytest suite. "
        "Solvers were benchmarked against canonical graphs with known theoretical minimum vertex covers: "
        "(1) Star Graph S_5 (|OPT| = 1); (2) Path Graph P_4 (|OPT| = 2); (3) Cycle Graph C_5 (|OPT| = 3); "
        "(4) Complete Bipartite K_{2,3} (|OPT| = 2); and (5) Petersen Graph (|OPT| = 6)."
    ))

    add_h2(doc, "6.2 Automated Pytest Execution Matrix", space_before=2, space_after=1)
    add_body(doc, "The entire test suite comprises 10 comprehensive unit and integration tests executing in 0.42 seconds with 100% pass rate:", space_after=2)

    test_rows = [
        ("Test Identifier", "Target Component", "Validation Condition / Objective", "Status"),
        ("test_empty_graph", "Exact & Approx Solvers", "Empty graph G(0, 0) returns empty cover set", "PASSED"),
        ("test_single_edge", "Exact & Approx Solvers", "Single edge (A, B) requires 1 node (exact), 2 for 2-approx", "PASSED"),
        ("test_handmade_optimality", "Exact Solvers (BF & BB)", "Exact solvers match theoretical |OPT| on Star, Path, Cycle, Bipartite, Petersen", "PASSED"),
        ("test_approx_bounds", "Approx Solvers", "Validates is_vertex_cover() == True and |C| <= 2*|OPT| on all canonical graphs", "PASSED"),
        ("test_synthetic_consistency", "B&B vs Bruteforce", "Cross-validates B&B against combinatorial brute-force on random topologies", "PASSED"),
        ("test_mock_hosts_generation", "scan.py", "Verifies realistic multi-role device metadata and gateway tagging", "PASSED"),
        ("test_star_topology", "scan.py & Solvers", "Verifies star topology construction and single gateway monitor selection", "PASSED"),
        ("test_hierarchical_topology", "scan.py & Solvers", "Verifies hierarchical switch-client graph construction and valid cover solving", "PASSED"),
        ("test_mesh_topology", "scan.py & Solvers", "Verifies complete mesh Kn produces min vertex cover of exactly n - 1", "PASSED"),
        ("test_subnet_inference", "scan.py", "Verifies local default subnet resolution via routing table inspection", "PASSED"),
    ]
    t_test = doc.add_table(rows=len(test_rows), cols=4)
    for r_idx, row_vals in enumerate(test_rows):
        for c_idx, val in enumerate(row_vals):
            t_test.rows[r_idx].cells[c_idx].paragraphs[0].text = val
    apply_table_styles(t_test, [1.5, 1.3, 3.2, 0.7], is_header=True, font_size=7.2, pad=15)
    add_p(doc, "Table 6.1: Automated Test Suite Verification Matrix (10 Automated Test Cases)", font_size=9, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=1, space_after=1)

    add_h2(doc, "6.3 Quality Assessment & Static Code Analysis Findings", space_before=2, space_after=1)
    add_body(doc, (
        "• Static Typing & Robust Interfaces: All module functions incorporate Python typing annotations (Set[Any], List[Dict[str, Any]], Tuple[Set[Any], float]), "
        "enabling strict type checking and zero runtime interface defects.\n"
        "• Graceful Degradation: Multi-tiered fallback mechanisms ensure that unprivileged executions or missing Nmap installations gracefully degrade to mock "
        "topologies without program termination."
    ))

    doc.add_page_break()

    # ==========================================
    # PAGE 20: CHAPTER 7 - CONCLUSION & FUTURE ENHANCEMENTS
    # ==========================================
    add_h1(doc, "CHAPTER 7", space_before=0, space_after=1)
    add_h1(doc, "CONCLUSION & FUTURE ENHANCEMENTS", space_before=0, space_after=3)

    add_h2(doc, "7.1 Project Summary & Key Algorithmic Takeaways", space_before=2, space_after=1)
    add_body(doc, (
        "The Aegis project successfully bridges theoretical algorithm design with applied computer network defense. By modeling network sensor "
        "allocation as the Minimum Vertex Cover problem, Aegis demonstrates that guaranteed 100% link visibility can be achieved while reducing "
        "active monitoring hardware requirements by 70% to 75% on standard enterprise topologies. The project successfully implements, evaluates, and compares "
        "three algorithmic paradigms: exact combinatorial Branch-and-Bound, linear-time 2-Approximation, and greedy degree heuristics. "
        "Theoretical approximation bounds (|C| <= 2*|OPT|) and asymptotic scaling boundaries were rigorously validated through empirical benchmarks."
    ))

    add_h2(doc, "7.2 Key Algorithmic Insights", space_before=3, space_after=1)
    add_body(doc, (
        "1. Branch-and-Bound Efficiency: Integrating maximal matching lower bounds and degree-1 reductions accelerates exact solving from O(2^n) to O(1.465^n), "
        "making exact optimization feasible for network segments of up to 30 nodes.\n"
        "2. Theory vs. Practice: While the 2-approximation provides an ironclad theoretical safety guarantee (|C| <= 2*|OPT|), the Greedy Degree heuristic "
        "consistently delivered superior practical covers, frequently matching the true optimal solution on hierarchical topologies.\n"
        "3. Topology Realism: Avoiding the subnet clique trap is essential for meaningful graph analysis on computer networks."
    ))

    add_h2(doc, "7.3 Future Research & Engineering Roadmap", space_before=3, space_after=1)
    add_body(doc, (
        "• Weighted Minimum Vertex Cover: Extend solvers to account for non-uniform device costs (e.g., high-capacity 100Gbps core routers vs. low-power IoT devices).\n"
        "• Dynamic Topology Adaptation: Incorporate real-time topology updates as mobile devices connect and disconnect using dynamic graph algorithms.\n"
        "• eBPF Kernel Probe Dispatching: Connect Aegis directly to Linux eBPF kernel hooks to dynamically spawn packet monitoring probes on chosen vertex cover nodes."
    ))

    add_h2(doc, "7.4 Academic & Technological References", space_before=3, space_after=1)
    add_body(doc, "https://github.com/prajwal-56/aegis", bold_prefix="Source Code Repository: ", space_after=2)
    add_body(doc, (
        "1. Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2009). Introduction to Algorithms (3rd ed.). MIT Press.\n"
        "2. Karp, R. M. (1972). Reducibility among combinatorial problems. Complexity of Computer Computations, 85–103.\n"
        "3. Vazirani, V. V. (2001). Approximation Algorithms. Springer Science & Business Media.\n"
        "4. Hagberg, A., Swart, P., & Chult, D. (2008). Exploring network structure, dynamics, and function using NetworkX. SciPy.\n"
        "5. Lyon, G. F. (2008). Nmap Network Scanning: The Official Nmap Project Guide to Network Discovery and Vulnerability Scanning."
    ), space_after=1, font_size=9.0)

    # Save document
    doc.save(output_filename)
    print(f"[✓] Official 20-page academic project report generated successfully: {output_filename}")


if __name__ == "__main__":
    generate_20page_report()
