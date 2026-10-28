import docx
from docx.shared import Pt, RGBColor
from report_builder.helpers import (
    add_chapter_header, add_section_heading, add_subsection_heading,
    add_paragraph, add_bullet, add_figure, add_code_block, add_table_data
)

def build_chapter_5(doc):
    add_chapter_header(doc, 5, "Methods & Algorithms")

    add_section_heading(doc, "5.1 Introduction to Grounded Industrial Reasoning")
    add_paragraph(doc, (
        "Root-cause analysis in continuous chemical processes cannot rely solely on black-box heuristics or unstructured "
        "natural language generation. To ensure absolute safety, diagnostic decisions must be grounded in physical laws, "
        "rigorous statistical time-series tests, and verifiable mathematical equations. This chapter presents the complete "
        "algorithmic and mathematical foundations of the Explainable Industrial AI Root-Cause Agent, detailing the deep "
        "reconstruction anomaly formulation, temporal onset detection, ontological graph proximity, Granger causality VAR "
        "hypotheses, composite multi-modal causal fusion, and closed-loop mitigation logic."
    ))

    add_section_heading(doc, "5.2 Deep Reconstruction Anomaly Scoring (LSTM Loss & Dynamic 3-Sigma)")
    add_paragraph(doc, (
        "To detect operational departures without requiring labeled fault datasets, we implement an unsupervised Long "
        "Short-Term Memory (LSTM) Autoencoder. Let X = [x_1, x_2, ..., x_T] represent a multivariate time-series window of "
        "length T across M continuous sensor channels, where x_t in R^M. The autoencoder consists of an encoder LSTM network f_enc "
        "that maps the input sequence into a low-dimensional latent bottleneck z_T, and a decoder LSTM network f_dec that "
        "reconstructs the original sequence X_hat:"
    ))
    
    math_p1 = doc.add_paragraph()
    math_p1.paragraph_format.space_before = Pt(4)
    math_p1.paragraph_format.space_after = Pt(4)
    r_m1 = math_p1.add_run("    z_T = f_enc(X; θ_enc),        X_hat = f_dec(z_T; θ_dec)")
    r_m1.font.name = "Consolas"
    r_m1.font.size = Pt(10.5)
    r_m1.font.bold = True
    r_m1.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    add_paragraph(doc, "The model is trained by minimizing the Mean Squared Error (MSE) loss function L_recon across nominal steady-state data:")
    
    math_p2 = doc.add_paragraph()
    math_p2.paragraph_format.space_before = Pt(4)
    math_p2.paragraph_format.space_after = Pt(4)
    r_m2 = math_p2.add_run("    L_recon(X, X_hat) = (1 / (T * M)) * sum_{t=1}^T sum_{j=1}^M (x_{t,j} - x_hat_{t,j})^2")
    r_m2.font.name = "Consolas"
    r_m2.font.size = Pt(10.5)
    r_m2.font.bold = True
    r_m2.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    add_paragraph(doc, (
        "For each individual sensor j, the point anomaly score a_j(t) at time tick t is defined as the normalized residual "
        "squared error: a_j(t) = (x_{t,j} - x_hat_{t,j})^2. A sensor is flagged as anomalous if its error exceeds a dynamic "
        "3-sigma statistical threshold: a_j(t) > mu_j + 3.0 * sigma_j, where mu_j and sigma_j denote the rolling mean and "
        "standard deviation of nominal residuals."
    ))

    add_figure(doc, "report_assets/fig8_lstm_loss.png", "Figure 5.1: Real-Time LSTM Autoencoder Reconstruction Loss Excursion Crossing Dynamic 3-Sigma Threshold", width_inches=6.0)

    add_section_heading(doc, "5.3 Temporal Precedence & Anomaly Onset Lead Computation")
    add_paragraph(doc, (
        "In physical process networks, an initiating cause must chronologically precede its downstream effects. While "
        "recirculation causes many sensors to violate thresholds almost simultaneously, high-frequency (1 Hz) sampling reveals "
        "subtle millisecond-to-second onset disparities. For each anomalous sensor s_i in the active anomaly set S_anom, we record "
        "its precise onset timestamp t_onset(s_i), defined as the earliest time tick where the dynamic 3-sigma condition is violated."
    ))
    add_paragraph(doc, (
        "Let t_earliest = min_{s_k in S_anom} { t_onset(s_k) } and t_latest = max_{s_k in S_anom} { t_onset(s_k) }. "
        "The normalized Temporal Lead Score S_temporal(s_i) in [0.0, 1.0] is computed as:"
    ))

    math_p3 = doc.add_paragraph()
    math_p3.paragraph_format.space_before = Pt(4)
    math_p3.paragraph_format.space_after = Pt(4)
    r_m3 = math_p3.add_run("    S_temporal(s_i) = 1.0 - [ (t_onset(s_i) - t_earliest) / (t_latest - t_earliest + epsilon) ]")
    r_m3.font.name = "Consolas"
    r_m3.font.size = Pt(10.5)
    r_m3.font.bold = True
    r_m3.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    add_paragraph(doc, "The sensor that deviates first receives S_temporal = 1.0, while late downstream responders receive scores approaching 0.0.")

    add_section_heading(doc, "5.4 Graph-Theoretic Physical Proximity Algorithm")
    add_paragraph(doc, (
        "Temporal priority alone can be fooled by varying sensor response latencies (e.g., thermocouple thermal inertia vs. "
        "instantaneous piezo-resistive pressure transducers). To prevent false attributions, the causal engine checks physical "
        "plausibility against the Neo4j Piping and Instrumentation Diagram (P&ID) graph G = (V, E)."
    ))
    add_paragraph(doc, (
        "Let d(s_i, s_j) represent the shortest directed flow distance (hop count) along fluid piping streams from sensor s_i to "
        "sensor s_j. If s_i is a true root cause, it should have short directed paths to other co-deviating sensors. The Topological "
        "Proximity Score S_graph(s_i) is formulated as the normalized inverse mean directed distance to all other anomalous sensors:"
    ))

    math_p4 = doc.add_paragraph()
    math_p4.paragraph_format.space_before = Pt(4)
    math_p4.paragraph_format.space_after = Pt(4)
    r_m4 = math_p4.add_run("    S_graph(s_i) = (1 / (|S_anom| - 1)) * sum_{s_j != s_i} [ 1.0 / (1.0 + lambda * d(s_i, s_j)) ]")
    r_m4.font.name = "Consolas"
    r_m4.font.size = Pt(10.5)
    r_m4.font.bold = True
    r_m4.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    add_paragraph(doc, "Here, lambda = 0.5 is an attenuation factor. If no directed path exists (d = infinity), the term evaluates to 0.0.")

    add_subsection_heading(doc, "Dijkstra Directed Stream Flow Traversal")
    add_paragraph(doc, "The graph traversal algorithm is implemented using an optimized priority queue Dijkstra formulation:")
    add_code_block(doc, (
        "Algorithm 1: Directed Flow Distance on Neo4j P&ID Topology\n"
        "Input: Source sensor s_src, Target sensor s_dst, Plant Graph G=(V,E)\n"
        "Output: Shortest directed piping hop count d_min\n"
        "1: u_src <- GetParentUnit(s_src), u_dst <- GetParentUnit(s_dst)\n"
        "2: if u_src == u_dst then return 0.0 (Colocated on same vessel)\n"
        "3: Q <- PriorityQueue(), dist <- {v: Infinity for v in V}, dist[u_src] <- 0\n"
        "4: Q.push(u_src, priority=0)\n"
        "5: while Q is not empty do:\n"
        "6:     curr, d <- Q.pop()\n"
        "7:     if curr == u_dst then return d\n"
        "8:     for neighbor, edge in OutgoingEdges(curr, type='FEEDS') do:\n"
        "9:         alt <- d + edge.length_weight\n"
        "10:        if alt < dist[neighbor] then:\n"
        "11:            dist[neighbor] <- alt; Q.push(neighbor, priority=alt)\n"
        "12: return Infinity (No downstream fluid path exists)"
    ))

    add_section_heading(doc, "5.5 Granger Causality VAR F-Test Formulation & Wald Statistics")
    add_paragraph(doc, (
        "To verify whether a statistical causal dependency exists between candidate sensor s_i and target sensor s_j, we formulate "
        "a bivariate Vector Autoregression (VAR) of lag order p (p = 2 to 5 lags). The unrestricted regression model is given by:"
    ))

    math_p5 = doc.add_paragraph()
    math_p5.paragraph_format.space_before = Pt(4)
    math_p5.paragraph_format.space_after = Pt(4)
    r_m5 = math_p5.add_run("    s_j(t) = c_1 + sum_{k=1}^p alpha_k * s_j(t-k) + sum_{k=1}^p beta_k * s_i(t-k) + epsilon_t")
    r_m5.font.name = "Consolas"
    r_m5.font.size = Pt(10.5)
    r_m5.font.bold = True
    r_m5.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    add_paragraph(doc, (
        "We test the null hypothesis H_0: beta_1 = beta_2 = ... = beta_p = 0 (implying s_i does NOT Granger-cause s_j). "
        "The Wald F-statistic tests the reduction in residual sum of squares between the restricted model (omitting s_i lags) "
        "and the unrestricted model:"
    ))

    math_p6 = doc.add_paragraph()
    math_p6.paragraph_format.space_before = Pt(4)
    math_p6.paragraph_format.space_after = Pt(4)
    r_m6 = math_p6.add_run("    F_stat = [ (RSS_restricted - RSS_unrestricted) / p ] / [ RSS_unrestricted / (N - 2p - 1) ]")
    r_m6.font.name = "Consolas"
    r_m6.font.size = Pt(10.5)
    r_m6.font.bold = True
    r_m6.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    add_paragraph(doc, (
        "The Granger Causal Score S_granger(s_i) is the average normalized F-statistic across all coupled downstream sensors: "
        "S_granger(s_i) = (1 / K) * sum_{k=1}^K min(1.0, F_{stat}(s_i -> s_k) / F_{crit}). Table 5.1 outlines the F-distribution critical values."
    ))

    f_crit_headers = ["Model Lag Order (p)", "Sample Size (N)", "Numerator df", "Denominator df", "F_crit (α = 0.05)", "F_crit (α = 0.01)", "Statistical Decision"]
    f_crit_data = [
        ["Lag p = 2", "120 ticks", "2", "115", "3.076", "4.795", "Reject H0 if F > 4.795 (99% Confidence)"],
        ["Lag p = 3", "120 ticks", "3", "113", "2.685", "3.953", "Reject H0 if F > 3.953 (99% Confidence)"],
        ["Lag p = 4", "120 ticks", "4", "111", "2.453", "3.490", "Reject H0 if F > 3.490 (99% Confidence)"],
        ["Lag p = 5", "120 ticks", "5", "109", "2.298", "3.195", "Reject H0 if F > 3.195 (99% Confidence)"]
    ]
    add_table_data(doc, f_crit_headers, f_crit_data, [1.0, 0.9, 0.8, 0.9, 1.1, 1.1, 1.7])

    add_section_heading(doc, "5.6 The Unified Multi-Modal Causal Fusion Scoring Formula")
    add_paragraph(doc, (
        "The three independent diagnostic signals—Temporal Precedence (chronological priority), Graph Proximity (physical connectivity), "
        "and Granger Causality (statistical forecasting)—are synthesized into a unified composite root-cause score C(s_i):"
    ))

    math_p7 = doc.add_paragraph()
    math_p7.paragraph_format.space_before = Pt(6)
    math_p7.paragraph_format.space_after = Pt(6)
    r_m7 = math_p7.add_run("    C(s_i) = w_1 * S_temporal(s_i) + w_2 * S_graph(s_i) + w_3 * S_granger(s_i)")
    r_m7.font.name = "Consolas"
    r_m7.font.size = Pt(11)
    r_m7.font.bold = True
    r_m7.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    add_paragraph(doc, "where the weights are constrained such that w_1 + w_2 + w_3 = 1.0. Through sensitivity analysis, optimal values were determined as:")
    add_bullet(doc, "w_1 = 0.40 (Temporal Lead Weight — strong priority to earliest onset under high-frequency 1 Hz sampling)", bold_prefix="Temporal Weight")
    add_bullet(doc, "w_2 = 0.35 (Graph Topology Weight — guarantees mass/energy conservation along P&ID stream paths)", bold_prefix="Topology Weight")
    add_bullet(doc, "w_3 = 0.25 (Granger Statistical Weight — empirical confirmation of dynamic correlation)", bold_prefix="Granger Weight")

    add_figure(doc, "report_assets/fig5_causal_signals.png", "Figure 5.2: Multi-Modal Causal Fusion Scoring Weights and Diagnostic Signal Confidence Under Noise", width_inches=6.0)

    add_subsection_heading(doc, "Complete Tri-Modal Root-Cause Isolation Algorithm")
    add_paragraph(doc, "The end-to-end multi-modal scoring pipeline is encapsulated in Algorithm 2:")
    add_code_block(doc, (
        "Algorithm 2: Tri-Modal Industrial Causal Root-Cause Isolation\n"
        "Input: Active Anomalies S_anom, TimescaleDB Telemetry Buffer D, Neo4j Graph G\n"
        "Output: Ranked list of Root Causes with Confidence Scores\n"
        "1: S_candidates <- PruneByTopologicalReachability(S_anom, G, max_depth=3)\n"
        "2: S_top8 <- SortByTemporalOnset(S_candidates)[0:8]\n"
        "3: for each sensor s_i in S_top8 do:\n"
        "4:     S_temp[s_i] <- ComputeTemporalLead(s_i, S_top8)\n"
        "5:     S_topo[s_i] <- ComputeInverseFlowProximity(s_i, S_top8, G)\n"
        "6:     S_gran[s_i] <- ComputePairwiseGrangerVAR(s_i, S_top8, D, lag=3)\n"
        "7:     Score[s_i] <- 0.40 * S_temp[s_i] + 0.35 * S_topo[s_i] + 0.25 * S_gran[s_i]\n"
        "8: end for\n"
        "9: RankedResults <- SortDescending(Score)\n"
        "10: return RankedResults"
    ))

    add_section_heading(doc, "5.7 Case-Based Reasoning (CBR) Historical Knowledge Retrieval")
    add_paragraph(doc, (
        "Once the top root-cause sensor s* = argmax_{s_i} { C(s_i) } is identified, the system queries a structured repository "
        "of historical plant work orders and incident reports. The query vector q is constructed by encoding the active fault features: "
        "q = [s*, unit_id, delta_T, delta_P, delta_F]. The similarity to historical case c_k is computed via cosine similarity: "
        "Sim(q, c_k) = (q . c_k) / (||q|| * ||c_k||). The top matching historical recovery procedure is extracted and injected "
        "into the LLM context prompt."
    ))

    add_section_heading(doc, "5.8 Faithfulness Metric & Hallucination Elimination Verification")
    add_paragraph(doc, (
        "To guarantee operator safety, generated diagnostic narratives are subjected to an automated Faithfulness Verification "
        "Algorithm before presentation. The verbalized text T_text is parsed into extracted named entities E_gen (sensor tags, units, "
        "mitigation valves, numerical values). The Factual Faithfulness Score F_score is computed as:"
    ))

    math_p8 = doc.add_paragraph()
    math_p8.paragraph_format.space_before = Pt(4)
    math_p8.paragraph_format.space_after = Pt(4)
    r_m8 = math_p8.add_run("    F_score = |E_gen intersect E_ground_truth| / |E_gen|")
    r_m8.font.name = "Consolas"
    r_m8.font.size = Pt(10.5)
    r_m8.font.bold = True
    r_m8.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    add_paragraph(doc, "If F_score < 0.90 or any ungrounded entity tag is detected, the LLM output is rejected and replaced by a deterministic rule-based fallback summary.")

    add_section_heading(doc, "5.9 Automated Closed-Loop Mitigation & Actuator Recovery")
    add_paragraph(doc, (
        "When an operator clicks 'Execute Automated Mitigation', the agent initiates closed-loop control adjustments. "
        "The target valve position u_new is calculated using a safety-bounded proportional adjustment: "
        "u_new = clip(u_nominal + K_p * (y_target - y_actual), u_min, u_max). For instance, under reactor cooling water failure "
        "(IDV 4), the agent commands XMV_10 (Cooling Valve) to 100.0% open while simultaneously trimming feed valves XMV_1 and XMV_4 "
        "by 15% to immediately halt exothermic heat generation."
    ))

    doc.add_page_break()
