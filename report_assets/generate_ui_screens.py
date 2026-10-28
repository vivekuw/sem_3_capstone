import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

os.makedirs('report_assets', exist_ok=True)

def create_ui_mockup(title, subtitle, filename, content_fn):
    fig, ax = plt.subplots(figsize=(10, 5.8), dpi=200)
    ax.set_facecolor('#0f172a') # dark slate theme
    ax.axis('off')
    
    # Outer window border
    window = mpatches.FancyBboxPatch((0.02, 0.02), 0.96, 0.96, boxstyle="round,pad=0.01", facecolor='#1e293b', edgecolor='#334155', linewidth=2, transform=ax.transAxes)
    ax.add_patch(window)
    
    # Title Bar
    titlebar = mpatches.Rectangle((0.02, 0.91), 0.96, 0.07, facecolor='#0f172a', edgecolor='#334155', linewidth=1, transform=ax.transAxes)
    ax.add_patch(titlebar)
    
    # Window circles
    for i, c in enumerate(['#ef4444', '#f59e0b', '#10b981']):
        ax.add_patch(plt.Circle((0.045 + i*0.02, 0.945), 0.01, color=c, transform=ax.transAxes))
        
    ax.text(0.12, 0.945, f"Industrial Root-Cause AI - {title}", color='#f8fafc', fontsize=10, weight='bold', va='center', transform=ax.transAxes)
    ax.text(0.70, 0.945, "Status: ONLINE | Port: 8005 | Model: Mistral-7B", color='#94a3b8', fontsize=8, va='center', transform=ax.transAxes)
    
    # Subtitle / Header bar
    ax.text(0.05, 0.86, title.upper(), color='#38bdf8', fontsize=11, weight='bold', transform=ax.transAxes)
    ax.text(0.05, 0.82, subtitle, color='#94a3b8', fontsize=8.5, transform=ax.transAxes)
    
    # Custom inner content
    content_fn(ax)
    
    plt.tight_layout()
    fig.savefig(f'report_assets/{filename}', bbox_inches='tight', dpi=200)
    plt.close(fig)

# 1. Overview Dashboard
def draw_overview(ax):
    # Summary cards
    cards = [
        ("CSTR Reactor", "TEMP: 104.2 °C (CRITICAL)", "#dc2626", 0.05, 0.62, 0.28, 0.16),
        ("Recycle Comp", "FLOW: 45.1 kscmh (WARN)", "#ea580c", 0.36, 0.62, 0.28, 0.16),
        ("Separator Fl.", "PRESS: 2801 kPa (NOMINAL)", "#16a34a", 0.67, 0.62, 0.28, 0.16),
    ]
    for name, stat, col, x, y, w, h in cards:
        rect = mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01", facecolor='#1e293b', edgecolor=col, linewidth=1.5, transform=ax.transAxes)
        ax.add_patch(rect)
        ax.text(x + 0.02, y + 0.11, name, color='#f8fafc', fontsize=9.5, weight='bold', transform=ax.transAxes)
        ax.text(x + 0.02, y + 0.05, stat, color=col, fontsize=8.5, weight='bold', transform=ax.transAxes)
        
    # Table of 43 sensors overview
    table_bg = mpatches.FancyBboxPatch((0.05, 0.08), 0.90, 0.48, boxstyle="round,pad=0.01", facecolor='#0f172a', edgecolor='#334155', linewidth=1, transform=ax.transAxes)
    ax.add_patch(table_bg)
    ax.text(0.07, 0.51, "REAL-TIME SENSOR TELEMETRY MATRIX (41 PROCESS VARIABLES + 2 ACTUATOR FEEDS)", color='#e2e8f0', fontsize=9, weight='bold', transform=ax.transAxes)
    
    sensors_demo = [
        ("XMEAS_1", "A Feed Stream 1", "0.2505 kscmh", "NOMINAL", "#10b981"),
        ("XMEAS_2", "D Feed Stream 2", "3664.0 kg/h", "NOMINAL", "#10b981"),
        ("XMEAS_9", "Reactor Temperature", "104.20 °C", "ANOMALY (+3.8σ)", "#ef4444"),
        ("XMEAS_21", "Reactor Cooling Water Outlet Temp", "88.45 °C", "ANOMALY (+4.1σ)", "#ef4444"),
        ("XMV_10", "Reactor Cooling Water Flow Valve", "100.00 %", "SATURATED", "#f59e0b"),
        ("XMEAS_13", "Separator Pressure", "2801.4 kPa", "HIGH (+2.1σ)", "#f59e0b"),
        ("XMEAS_17", "Stripper Underflow Stream 11", "22.88 m3/h", "NOMINAL", "#10b981"),
    ]
    y_row = 0.44
    for tag, desc, val, st, sc in sensors_demo:
        ax.text(0.08, y_row, tag, color='#38bdf8', fontsize=8, weight='bold', transform=ax.transAxes)
        ax.text(0.22, y_row, desc, color='#cbd5e1', fontsize=8, transform=ax.transAxes)
        ax.text(0.55, y_row, val, color='#f8fafc', fontsize=8, weight='bold', transform=ax.transAxes)
        ax.text(0.78, y_row, st, color=sc, fontsize=8, weight='bold', transform=ax.transAxes)
        y_row -= 0.055

create_ui_mockup("Plant Overview & Telemetry Matrix", "Real-time 43-sensor monitoring with continuous anomaly scanning", "ui_overview_dashboard.png", draw_overview)

# 2. Root Cause Panel with Downside Drawer
def draw_rca_panel(ax):
    # Left: Root cause ranked list
    left_bg = mpatches.FancyBboxPatch((0.05, 0.08), 0.43, 0.70, boxstyle="round,pad=0.01", facecolor='#0f172a', edgecolor='#dc2626', linewidth=1.5, transform=ax.transAxes)
    ax.add_patch(left_bg)
    ax.text(0.07, 0.73, "RANKED CAUSAL ANOMALIES", color='#ef4444', fontsize=9.5, weight='bold', transform=ax.transAxes)
    
    rc_items = [
        ("1. XMEAS_21 (Cooling Water Outlet)", "Score: 0.942 | Lead: +42s", True),
        ("2. XMEAS_9 (Reactor Temperature)", "Score: 0.915 | Lead: +18s", False),
        ("3. XMV_10 (Cooling Valve Demand)", "Score: 0.887 | Saturation", False),
        ("4. XMEAS_13 (Separator Pressure)", "Score: 0.654 | Lead: -12s", False),
        ("5. XMEAS_11 (Separator Temp)", "Score: 0.540 | Downstream", False),
    ]
    y_it = 0.65
    for name, sub, sel in rc_items:
        bg_col = '#1e293b' if not sel else '#3b0764'
        border_col = '#475569' if not sel else '#a855f7'
        r = mpatches.FancyBboxPatch((0.07, y_it - 0.04), 0.39, 0.08, boxstyle="round,pad=0.01", facecolor=bg_col, edgecolor=border_col, linewidth=1.2, transform=ax.transAxes)
        ax.add_patch(r)
        ax.text(0.085, y_it + 0.01, name, color='#f8fafc', fontsize=8.5, weight='bold', transform=ax.transAxes)
        ax.text(0.085, y_it - 0.025, sub, color='#a855f7' if sel else '#94a3b8', fontsize=7.5, transform=ax.transAxes)
        y_it -= 0.10
        
    # Right: Interactive Downside Component Solution Drawer
    right_bg = mpatches.FancyBboxPatch((0.51, 0.08), 0.44, 0.70, boxstyle="round,pad=0.01", facecolor='#0f172a', edgecolor='#a855f7', linewidth=1.5, transform=ax.transAxes)
    ax.add_patch(right_bg)
    ax.text(0.53, 0.73, "COMPONENT RECOVERY DRAWER: XMEAS_21", color='#c084fc', fontsize=9.5, weight='bold', transform=ax.transAxes)
    ax.text(0.53, 0.68, "Diagnosis: Reactor Cooling Water Loss / Fouled Heat Exchanger", color='#f8fafc', fontsize=8, weight='bold', transform=ax.transAxes)
    
    steps = [
        "Component: CSTR Reactor Cooling Jacket (HEX-201)",
        "Failure Mechanism: Loss of cooling water pressure or valve jam",
        "Action 1: Switch to Secondary Aux Cooling Loop Pump (P-202B)",
        "Action 2: Throttle XMV_10 bypass valve to ensure 100% cold flow",
        "Action 3: Cut reactant A & C feed rate by 20% to curb exotherm",
        "Interlock Action: Enable auto-trip override if T > 108.0 °C",
        "[ CLICK TO EXECUTE AUTOMATED COMPONENT RECOVERY ]"
    ]
    y_st = 0.61
    for st in steps:
        if "CLICK" in st:
            btn = mpatches.FancyBboxPatch((0.53, y_st - 0.02), 0.40, 0.065, boxstyle="round,pad=0.01", facecolor='#7e22ce', edgecolor='#d8b4fe', linewidth=1.2, transform=ax.transAxes)
            ax.add_patch(btn)
            ax.text(0.73, y_st + 0.012, st, color='#ffffff', fontsize=7.8, weight='bold', ha='center', va='center', transform=ax.transAxes)
        else:
            ax.text(0.53, y_st, f"• {st}", color='#e2e8f0' if 'Action' not in st else '#38bdf8', fontsize=7.8, transform=ax.transAxes)
        y_st -= 0.062

create_ui_mockup("Root Cause Analysis & Downside Recovery", "Temporal precedence, Granger causality, and component-level recovery drawer", "ui_root_cause_analysis.png", draw_rca_panel)

# 3. Knowledge Graph Subgraph Selector
def draw_kg_view(ax):
    # Selector bar on top
    sel_box = mpatches.FancyBboxPatch((0.05, 0.69), 0.90, 0.09, boxstyle="round,pad=0.01", facecolor='#1e293b', edgecolor='#38bdf8', linewidth=1.2, transform=ax.transAxes)
    ax.add_patch(sel_box)
    ax.text(0.07, 0.735, "Machine Focus Dropdown: [ UNIT_REACTOR (CSTR Reactor Subgraph)  v ]", color='#38bdf8', fontsize=9, weight='bold', transform=ax.transAxes)
    ax.text(0.65, 0.735, "Nodes: 12 | Edges: 18 | Physics: Exothermic CSTR", color='#94a3b8', fontsize=8, transform=ax.transAxes)
    
    # Graph area
    g_bg = mpatches.FancyBboxPatch((0.05, 0.08), 0.90, 0.58, boxstyle="round,pad=0.01", facecolor='#0f172a', edgecolor='#334155', linewidth=1, transform=ax.transAxes)
    ax.add_patch(g_bg)
    
    # Nodes in subgraph
    nodes = [
        ("UNIT_REACTOR\n(CSTR Vessel)", 0.48, 0.38, 0.18, 0.12, '#7f1d1d', '#ef4444'),
        ("XMEAS_9\n(Reactor Temp)", 0.20, 0.46, 0.16, 0.10, '#991b1b', '#f87171'),
        ("XMEAS_21\n(CW Out Temp)", 0.20, 0.24, 0.16, 0.10, '#991b1b', '#f87171'),
        ("XMV_10\n(Cooling Valve)", 0.48, 0.14, 0.16, 0.10, '#b45309', '#f59e0b'),
        ("Stream 6 (Out)\n(To Condenser)", 0.75, 0.38, 0.16, 0.10, '#1e3a8a', '#3b82f6'),
    ]
    for lbl, x, y, w, h, bg, bd in nodes:
        rect = mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02", facecolor=bg, edgecolor=bd, linewidth=1.5, transform=ax.transAxes)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, lbl, color='#ffffff', fontsize=7.8, weight='bold', ha='center', va='center', transform=ax.transAxes)
        
    # Edges
    ax.annotate("MEASURES", xy=(0.36, 0.48), xytext=(0.48, 0.42), arrowprops=dict(facecolor='#94a3b8', width=1, headwidth=5), color='#cbd5e1', fontsize=7, transform=ax.transAxes)
    ax.annotate("MEASURES", xy=(0.36, 0.28), xytext=(0.48, 0.40), arrowprops=dict(facecolor='#94a3b8', width=1, headwidth=5), color='#cbd5e1', fontsize=7, transform=ax.transAxes)
    ax.annotate("CONTROLS", xy=(0.56, 0.38), xytext=(0.56, 0.24), arrowprops=dict(facecolor='#f59e0b', width=1, headwidth=5), color='#fcd34d', fontsize=7, transform=ax.transAxes)
    ax.annotate("FEEDS", xy=(0.75, 0.43), xytext=(0.66, 0.43), arrowprops=dict(facecolor='#38bdf8', width=1, headwidth=5), color='#38bdf8', fontsize=7, transform=ax.transAxes)

create_ui_mockup("Cytoscape Knowledge Graph Subgraph View", "Per-machine graph selector filtering reactor, condenser, and compressor subgraphs", "ui_knowledge_graph_view.png", draw_kg_view)

print("UI mockups generated successfully.")
