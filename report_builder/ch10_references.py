import docx
from docx.shared import Pt, RGBColor
from report_builder.helpers import (
    add_chapter_header, add_section_heading, add_paragraph
)

def build_chapter_10(doc):
    add_chapter_header(doc, 10, "References & Bibliography")

    add_paragraph(doc, (
        "The following comprehensive references encompass academic literature, foundational chemical engineering benchmarks, "
        "causal inference theory, knowledge graphs, deep learning frameworks, and official industrial process standards "
        "consulted and cited throughout the engineering of this capstone research project:"
    ))

    references = [
        "Downs, J. J., and Vogel, E. F. (1993). 'A plant-wide industrial process control problem.' Computers & Chemical Engineering, 17(3), pp. 245-255.",
        "Bathelt, A., Ricker, N. L., and Jelali, M. (2015). 'Revision of the Tennessee Eastman Process model.' IFAC-PapersOnLine, 48(8), pp. 309-314.",
        "Granger, C. W. J. (1969). 'Investigating causal relations by econometric models and cross-spectral methods.' Econometrica, 37(3), pp. 424-438.",
        "Pearl, J. (2009). 'Causality: Models, Reasoning, and Inference.' 2nd Edition, Cambridge University Press, New York.",
        "Holland, P. W. (1986). 'Statistics and causal inference.' Journal of the American Statistical Association, 81(396), pp. 945-960.",
        "International Society of Automation. (2016). 'ANSI/ISA-18.2-2016: Management of Alarm Systems for the Process Industries.' ISA, Research Triangle Park, NC.",
        "International Electrotechnical Commission. (2018). 'IEC 62682: Management of alarm systems for the process industries.' Edition 1.1, IEC, Geneva.",
        "Chiang, L. H., Russell, E. L., and Braatz, R. D. (2001). 'Fault Detection and Diagnosis in Industrial Systems.' Springer-Verlag, London.",
        "Venkatasubramanian, V., Rengaswamy, R., Yin, K., and Kavuri, S. N. (2003). 'A review of process fault detection and diagnosis: Part I: Quantitative model-based methods.' Computers & Chemical Engineering, 27(3), pp. 293-311.",
        "Venkatasubramanian, V., Rengaswamy, R., and Kavuri, S. N. (2003). 'A review of process fault detection and diagnosis: Part II: Qualitative models and search strategies.' Computers & Chemical Engineering, 27(3), pp. 313-326.",
        "Venkatasubramanian, V., Rengaswamy, R., Kavuri, S. N., and Yin, K. (2003). 'A review of process fault detection and diagnosis: Part III: Process history based methods.' Computers & Chemical Engineering, 27(3), pp. 327-346.",
        "Hochreiter, S., and Schmidhuber, J. (1997). 'Long Short-Term Memory.' Neural Computation, 9(8), pp. 1735-1780.",
        "Malhotra, P., Vig, L., Shroff, G., and Agarwal, P. (2015). 'Long Short Term Memory Networks for Anomaly Detection in Time Series.' Proceedings of ESANN, Bruges, Belgium.",
        "Paszke, A., Gross, S., Massa, F., et al. (2019). 'PyTorch: An Imperative Style, High-Performance Deep Learning Library.' Advances in Neural Information Processing Systems (NeurIPS 32), pp. 8024-8035.",
        "Neo4j Graph Database. (2024). 'The Neo4j Operations and Cypher Query Manual v5.' Neo4j, Inc., San Mateo, CA. Available at: https://neo4j.com/docs/",
        "Dijkstra, E. W. (1959). 'A note on two problems in connexion with graphs.' Numerische Mathematik, 1(1), pp. 269-271.",
        "Freedman, M., and Timescale Team. (2020). 'TimescaleDB: SQL Made Scalable for Time-Series.' Proceedings of the VLDB Endowment.",
        "Seabold, S., and Perktold, J. (2010). 'Statsmodels: Econometric and statistical modeling with Python.' Proceedings of the 9th Python in Science Conference.",
        "FastAPI Documentation. (2024). 'FastAPI: High performance, easy to learn, fast to code, ready for production.' Available at: https://fastapi.tiangolo.com/",
        "Jiang, A. Q., Sablayrolles, A., Mensch, A., et al. (2023). 'Mistral 7B.' arXiv preprint arXiv:2310.06825.",
        "LangChain Inc. (2024). 'LangGraph: Building Language Agents as Graphs.' Available at: https://langchain-ai.github.io/langgraph/",
        "React Documentation. (2024). 'React: The library for web and native user interfaces.' Meta Platforms Inc. Available at: https://react.dev/",
        "Franz, M., Lopes, C. T., Huck, G., et al. (2016). 'Cytoscape.js: a graph theory library for visualisation and analysis.' Bioinformatics, 32(2), pp. 309-311.",
        "Eastman Chemical Company. (1993). 'Tennessee Eastman Process Benchmark Data Archives.' Department of Chemical Engineering, University of Washington.",
        "Yin, S., Ding, S. X., Xie, X., and Luo, H. (2014). 'A review on basic data-driven approaches for industrial process monitoring.' IEEE Transactions on Industrial Electronics, 61(11), pp. 6418-6428.",
        "Luo, H., Ding, S. X., Kong, X., and Yin, S. (2020). 'An overview on data-driven root cause analysis for industrial processes.' IEEE Transactions on Cybernetics, 50(12), pp. 4880-4893.",
        "Aamodt, A., and Plaza, E. (1994). 'Case-based reasoning: Foundational issues, methodological variations, and system approaches.' AI Communications, 7(1), pp. 39-59.",
        "Ji, Z., Lee, N., Frieske, R., et al. (2023). 'Survey of hallucination in natural language generation.' ACM Computing Surveys, 55(12), pp. 1-38.",
        "Shrikumar, A., Greenside, P., and Kundaje, A. (2017). 'Learning Important Features Through Propagating Activation Differences.' Proceedings of the 34th International Conference on Machine Learning (ICML), pp. 3145-3153.",
        "Lundberg, S. M., and Lee, S. I. (2017). 'A Unified Approach to Interpreting Model Predictions.' Advances in Neural Information Processing Systems (NeurIPS 30), pp. 4765-4774.",
        "Bauer, M., and Craig, I. K. (2008). 'Economic assessment of advanced process control—A survey and framework.' IEEE Transactions on Automation Science and Engineering, 5(1), pp. 2-18.",
        "Thornhill, N. F., and Horch, A. (2007). 'Advances and new directions in plant-wide disturbance detection and diagnosis.' Control Engineering Practice, 15(10), pp. 1196-1206.",
        "Ricker, N. L. (1996). 'Decentralized control of the Tennessee Eastman Challenge Process.' Journal of Process Control, 6(4), pp. 205-221.",
        "McAvoy, T. J., and Ye, N. (1994). 'Base control for the Tennessee Eastman problem.' Computers & Chemical Engineering, 18(5), pp. 383-413.",
        "Wadher, V. U., and Singh, M. K. (2026). 'Explainable Industrial AI Root-Cause Agent using Temporal and Knowledge Graphs for Continuous Chemical Processes.' Capstone Project Technical Documentation, Department of Artificial Intelligence, KES' Shroff College of Arts and Commerce, Mumbai, India."
    ]

    for i, ref in enumerate(references):
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.space_before = Pt(2)
        p_ref.paragraph_format.space_after = Pt(4)
        p_ref.paragraph_format.line_spacing = 1.15
        r_num = p_ref.add_run(f"[{i+1}] ")
        r_num.font.name = "Times New Roman"
        r_num.font.size = Pt(10)
        r_num.font.bold = True
        r_num.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        
        r_txt = p_ref.add_run(ref)
        r_txt.font.name = "Times New Roman"
        r_txt.font.size = Pt(10)
        r_txt.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
