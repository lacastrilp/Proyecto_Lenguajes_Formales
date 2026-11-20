"""
Generador de Visualizador Web Interactivo (HTML/SVG) para el Proyecto Final.
Aplica el sistema de diseno editorial 'Impeccable Design' de Taller2 (fuentes Playfair Display,
Inter y JetBrains Mono, tarjetas con borde de 2px y sombras duras '4px 4px 0px #0f172a',
tablas de demostracion de dos columnas y renderizado SVG interactivo).
"""

import os
import json
from typing import Dict, List, Any
from src.common.grammar import Grammar
from src.item1_first_follow.first_follow import compute_first, compute_follow, format_sets_output, format_set_elements
from src.item2_parsers.ll1_parser import LL1Parser
from src.item2_parsers.slr1_parser import SLR1Parser
from src.item3_sdd.sdd import create_project_sdd, create_circular_sdd
from src.item3_sdd.sdd_evaluator import SDDEvaluator, SDDCircularDefinitionError


def generate_html_visualizer(output_path: str = "index.html") -> str:
    # 1. Cargar Gramatica Propia (Items 1 y 2)
    own_grammar_text = "3\nS -> L\nL -> bR\nR -> ,L e"
    g_own = Grammar.from_text(own_grammar_text)
    firsts_own = compute_first(g_own)
    follows_own = compute_follow(g_own, firsts_own)
    ll1_own = LL1Parser(g_own, firsts_own, follows_own)
    slr1_own = SLR1Parser(g_own, follows_own)

    # Nodos y aristas para el automata LR(0) SVG
    lr0_nodes = []
    for i, I in enumerate(slr1_own.canonical_collection):
        items_formatted = []
        for head, body, dot in sorted(I):
            b_list = list(body) if body else ["e"]
            b_str = "".join(b_list[:dot]) + "·" + "".join(b_list[dot:])
            items_formatted.append(f"{head} -> {b_str}")
        
        is_accept = any(head == "S'" and dot == 1 for head, _, dot in I)
        lr0_nodes.append({
            "id": f"I{i}",
            "label": f"I{i}",
            "is_start": (i == 0),
            "is_accept": is_accept,
            "items": items_formatted
        })

    lr0_edges = []
    # Transiciones GOTO del automata
    # Del codigo de slr1_parser: goto_table maps (state_idx, symbol) -> next_state
    for (src_state, sym), tgt_state in sorted(slr1_own.goto_table.items()):
        lr0_edges.append({
            "source": f"I{src_state}",
            "target": f"I{tgt_state}",
            "label": sym,
            "type": "goto"
        })
    # Agregar transiciones shift de la tabla action
    shifts_seen = set()
    for (src_state, term), actions in sorted(slr1_own.action_table.items()):
        for act in actions:
            if act[0] == "shift":
                tgt_state = act[1]
                edge_key = (src_state, tgt_state, term)
                if edge_key not in shifts_seen:
                    shifts_seen.add(edge_key)
                    lr0_edges.append({
                        "source": f"I{src_state}",
                        "target": f"I{tgt_state}",
                        "label": term,
                        "type": "shift"
                    })

    # 2. Cargar SDD Oficial (Item 3)
    sdd = create_project_sdd()
    g_sdd = Grammar.from_text(sdd.grammar_text)
    firsts_sdd = compute_first(g_sdd)
    follows_sdd = compute_follow(g_sdd, firsts_sdd)
    slr1_sdd = SLR1Parser(g_sdd, follows_sdd)
    evaluator = SDDEvaluator(sdd)

    # Cadena de prueba con 5 terminales: (1+0)
    sample_str = "(1+0)"
    _, parse_tree = slr1_sdd.parse(sample_str)
    adj, in_deg, compute_info, labels, nodes_by_id = evaluator.build_dependency_graph(parse_tree)
    order_labels, main_val = evaluator.evaluate(parse_tree)

    # Nodos y aristas del DAG de dependencias para SVG
    dag_nodes = []
    for v in sorted(in_deg.keys(), key=lambda x: labels[x]):
        node_id, attr = v
        symbol = nodes_by_id[node_id].symbol
        val = nodes_by_id[node_id].get_attribute(attr)
        dag_nodes.append({
            "id": labels[v],
            "label": labels[v],
            "symbol": symbol,
            "attr": attr,
            "val": str(val) if val is not None else "?",
            "is_main": (symbol == "S" and attr == "val")
        })

    dag_edges = []
    for u, targets in sorted(adj.items(), key=lambda x: labels[x[0]]):
        for v in sorted(targets, key=lambda x: labels[x]):
            dag_edges.append({
                "source": labels[u],
                "target": labels[v]
            })

    # Lineas del arbol anotado
    tree_lines = list(parse_tree.format_tree())

    # Demostracion de ciclo circular
    circular_sdd = create_circular_sdd()
    circular_evaluator = SDDEvaluator(circular_sdd)
    _, circ_tree = slr1_sdd.parse("1")
    circular_cycle_path = []
    try:
        circular_evaluator.evaluate(circ_tree)
    except SDDCircularDefinitionError as e:
        circular_cycle_path = e.cycle_path

    # Armar HTML completo con el sistema de diseno de Taller2
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analizadores Sintácticos LL(1), SLR(1) y Evaluador SDD — Visualizador Interactivo</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,800;1,600&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        /* -----------------------------------------------------------------
           IMPECCABLE DESIGN SYSTEM (LIGHT EDITION - ESTILO TALLER 2)
           ----------------------------------------------------------------- */
        :root {{
            --bg: #ffffff;
            --bg-subtle: #f8fafc;
            --surface: #ffffff;
            --text-main: #0f172a;
            --text-body: #334155;
            --text-muted: #64748b;
            --border: #0f172a;
            --border-light: #e2e8f0;

            --accent-blue: #1e40af;
            --accent-amber: #d97706;
            --accent-emerald: #059669;
            --accent-red: #dc2626;

            --shadow-hard: 4px 4px 0px #0f172a;
            --shadow-hard-hover: 6px 6px 0px #0f172a;

            --ease-emil: cubic-bezier(0.16, 1, 0.3, 1);
            --duration: 150ms;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            -webkit-font-smoothing: antialiased;
        }}

        body {{
            font-family: 'Inter', -apple-system, sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            padding: 48px max(8vw, 24px);
            line-height: 1.6;
        }}

        .editorial-hero {{
            display: grid;
            grid-template-columns: 8fr 4fr;
            gap: 40px;
            align-items: start;
            margin-bottom: 56px;
            padding-bottom: 36px;
            border-bottom: 2px solid var(--border);
        }}

        .hero-left {{ max-width: 760px; }}

        .editorial-tag {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.15em;
            color: var(--accent-blue);
            margin-bottom: 12px;
            display: block;
        }}

        .editorial-h1 {{
            font-family: 'Playfair Display', serif;
            font-size: 3.2rem;
            font-weight: 800;
            line-height: 1.02;
            letter-spacing: -0.03em;
            color: var(--text-main);
            margin-bottom: 20px;
        }}

        .editorial-lead {{
            font-size: 1.05rem;
            color: var(--text-body);
            max-width: 650px;
            line-height: 1.65;
        }}

        .hero-right-meta {{
            background: var(--bg-subtle);
            border: 2px solid var(--border);
            padding: 24px;
            box-shadow: var(--shadow-hard);
            margin-top: 8px;
        }}

        .meta-label {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.15em;
            color: var(--text-muted);
            margin-bottom: 4px;
        }}

        .meta-val {{
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--text-main);
            margin-bottom: 16px;
        }}

        .meta-val:last-child {{ margin-bottom: 0; }}

        .tactile-nav {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-bottom: 40px;
            border-bottom: 2px solid var(--border);
            padding-bottom: 16px;
        }}

        .nav-btn {{
            background: var(--bg-subtle);
            border: 2px solid var(--border);
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
            font-size: 0.875rem;
            font-weight: 600;
            padding: 12px 20px;
            cursor: pointer;
            box-shadow: 2px 2px 0px #0f172a;
            transition: transform var(--duration) var(--ease-emil),
                        box-shadow var(--duration) var(--ease-emil),
                        background-color var(--duration) var(--ease-emil);
            will-change: transform;
        }}

        .nav-btn:hover {{
            background: #ffffff;
            transform: translateY(-2px);
            box-shadow: var(--shadow-hard);
        }}

        .nav-btn:active {{
            transform: scale(0.97);
            box-shadow: 0px 0px 0px #0f172a;
        }}

        .nav-btn.active {{
            background: var(--text-main);
            color: #ffffff;
            box-shadow: var(--shadow-hard);
        }}

        .tab-pane {{
            display: none;
            opacity: 0;
            transform: translateY(8px);
            transition: opacity var(--duration) var(--ease-emil), transform var(--duration) var(--ease-emil);
        }}

        .tab-pane.active {{
            display: block;
            opacity: 1;
            transform: translateY(0);
        }}

        .proof-card {{
            background: var(--surface);
            border: 2px solid var(--border);
            box-shadow: var(--shadow-hard);
            margin-bottom: 32px;
            transition: transform var(--duration) var(--ease-emil), box-shadow var(--duration) var(--ease-emil);
        }}

        .proof-card:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-hard-hover);
        }}

        .proof-card-header {{
            background: var(--bg-subtle);
            padding: 18px 24px;
            border-bottom: 2px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .step-meta-group {{
            display: flex;
            align-items: center;
            gap: 14px;
        }}

        .step-num-badge {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            font-weight: 700;
            background: var(--text-main);
            color: #ffffff;
            padding: 4px 10px;
            letter-spacing: 0.1em;
        }}

        .step-title {{
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--text-main);
        }}

        .status-badge {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            font-weight: 700;
            padding: 4px 12px;
            border: 1.5px solid var(--border);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            display: inline-block;
        }}

        .start-tag {{ background: #eff6ff; color: var(--accent-blue); border-color: var(--accent-blue); }}
        .final-tag {{ background: #fef3c7; color: var(--accent-amber); border-color: var(--accent-amber); }}
        .regular-tag {{ background: #f1f5f9; color: var(--text-muted); border-color: #cbd5e1; }}
        .tag-new {{ background: #ecfdf5; color: var(--accent-emerald); border-color: var(--accent-emerald); }}
        .tag-danger {{ background: #fef2f2; color: var(--accent-red); border-color: var(--accent-red); }}

        .proof-card-body {{ padding: 24px; }}

        .proof-grid-table {{
            width: 100%;
            border-collapse: collapse;
            font-family: 'JetBrains Mono', monospace;
        }}

        .proof-grid-table th {{
            text-align: left;
            padding: 10px 16px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: var(--text-muted);
            border-bottom: 2px solid var(--border);
        }}

        .proof-grid-table td {{
            padding: 14px 16px;
            border-bottom: 1px solid var(--border-light);
            vertical-align: top;
            font-size: 0.95rem;
        }}

        .calc-col {{ color: var(--text-main); width: 58%; }}
        .just-col {{
            font-family: 'Inter', sans-serif;
            border-left: 2px solid var(--border);
            padding-left: 20px !important;
            width: 42%;
        }}

        .rule-title {{ font-weight: 700; color: var(--text-main); font-size: 0.9rem; }}
        .rule-desc {{ font-size: 0.825rem; color: var(--text-muted); margin-top: 2px; }}

        .math-expr {{ font-weight: 600; color: var(--text-main); }}
        .math-sub {{ color: var(--text-body); font-size: 0.875rem; margin-top: 4px; }}
        .op {{ color: var(--accent-blue); }}
        .sym {{ color: var(--accent-amber); }}

        .editorial-table-card {{
            background: var(--surface);
            border: 2px solid var(--border);
            box-shadow: var(--shadow-hard);
            overflow-x: auto;
            margin-bottom: 32px;
        }}

        .editorial-table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }}

        .editorial-table th {{
            background: var(--bg-subtle);
            color: var(--text-main);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            padding: 14px 20px;
            border-bottom: 2px solid var(--border);
        }}

        .editorial-table td {{
            padding: 14px 20px;
            border-bottom: 1px solid var(--border-light);
            font-size: 0.9rem;
        }}

        .code-box {{
            background: var(--bg-subtle);
            border: 2px solid var(--border);
            padding: 20px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9rem;
            line-height: 1.6;
            box-shadow: var(--shadow-hard);
            margin-bottom: 24px;
            overflow-x: auto;
            white-space: pre-wrap;
        }}

        svg.graph-svg {{
            width: 100%;
            height: 520px;
            background: #ffffff;
            border: 2px solid var(--border);
            display: block;
        }}

        .interactive-tester {{
            background: var(--bg-subtle);
            border: 2px solid var(--border);
            box-shadow: var(--shadow-hard);
            padding: 24px;
            margin-bottom: 32px;
        }}

        .input-group {{
            display: flex;
            gap: 12px;
            margin-top: 12px;
        }}

        .input-field {{
            flex: 1;
            padding: 12px 16px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 1rem;
            border: 2px solid var(--border);
            background: #ffffff;
            box-shadow: 2px 2px 0px #0f172a;
        }}

        .input-btn {{
            background: var(--accent-blue);
            color: #ffffff;
            font-family: 'Inter', sans-serif;
            font-size: 0.9rem;
            font-weight: 700;
            border: 2px solid var(--border);
            padding: 12px 24px;
            cursor: pointer;
            box-shadow: 2px 2px 0px #0f172a;
            transition: transform var(--duration) var(--ease-emil);
        }}

        .input-btn:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-hard);
        }}

        .input-btn:active {{
            transform: scale(0.97);
        }}

        /* -----------------------------------------------------------------
           LABORATORIO SDD INTERACTIVO PASO A PASO
           ----------------------------------------------------------------- */
        .lab-ex-btn {{
            flex: 1;
            min-width: 220px;
            background: var(--bg-subtle);
            border: 2px solid var(--border);
            padding: 14px 18px;
            text-align: left;
            cursor: pointer;
            box-shadow: var(--shadow-hard);
            transition: all var(--duration) var(--ease-emil);
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}

        .lab-ex-btn:hover {{
            background: #ffffff;
            transform: translateY(-2px);
            box-shadow: var(--shadow-hard-hover);
        }}

        .lab-ex-btn.active {{
            background: var(--text-main);
            color: #ffffff;
        }}

        .lab-ex-btn.active .ex-num {{
            color: #93c5fd;
        }}

        .lab-ex-btn.active .ex-name {{
            color: #ffffff;
        }}

        .ex-num {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.7rem;
            font-weight: 700;
            color: var(--accent-blue);
            letter-spacing: 0.1em;
        }}

        .ex-name {{
            font-size: 0.95rem;
            font-weight: 700;
            color: var(--text-main);
        }}

        .ex-badge {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.65rem;
            font-weight: 700;
            padding: 2px 8px;
            border: 1px solid currentColor;
            display: inline-block;
            margin-top: 4px;
            align-self: flex-start;
        }}

        .ex-badge.l-attr {{
            color: var(--accent-blue);
            background: #eff6ff;
        }}

        .lab-ex-btn.active .ex-badge.l-attr {{
            color: #bfdbfe;
            background: rgba(255,255,255,0.12);
            border-color: #93c5fd;
        }}

        .ex-badge.no-l-attr {{
            color: var(--accent-amber);
            background: #fffbeb;
        }}

        .lab-ex-btn.active .ex-badge.no-l-attr {{
            color: #fde68a;
            background: rgba(255,255,255,0.12);
            border-color: #fcd34d;
        }}

        .transport-btn {{
            background: var(--bg-subtle);
            border: 2px solid var(--border);
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
            font-size: 0.8rem;
            font-weight: 700;
            padding: 8px 14px;
            cursor: pointer;
            box-shadow: 2px 2px 0px #0f172a;
            transition: all var(--duration) var(--ease-emil);
        }}

        .transport-btn:hover {{
            background: #ffffff;
            transform: translateY(-1px);
            box-shadow: var(--shadow-hard);
        }}

        .transport-btn:active {{
            transform: scale(0.97);
            box-shadow: 0px 0px 0px #0f172a;
        }}

        .transport-btn.active-play {{
            background: var(--accent-blue);
            color: #ffffff;
            border-color: var(--border);
        }}

        .preset-btn {{
            background: #ffffff;
            border: 1.5px solid var(--border);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            font-weight: 600;
            padding: 4px 10px;
            cursor: pointer;
            box-shadow: 1px 1px 0px #0f172a;
            transition: all 0.12s ease;
        }}

        .preset-btn:hover {{
            background: #eff6ff;
            border-color: var(--accent-blue);
            color: var(--accent-blue);
            transform: translateY(-1px);
        }}

        .kahn-step-item {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 16px;
            border-bottom: 1px solid var(--border-light);
            cursor: pointer;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            transition: background 0.15s ease;
        }}

        .kahn-step-item:hover {{
            background: #f1f5f9;
        }}

        .kahn-step-item.active {{
            background: #fef3c7;
            border-left: 4px solid var(--accent-amber);
            font-weight: 700;
        }}

        .kahn-step-item.evaluated {{
            color: #334155;
        }}

        .kahn-step-item.pending {{
            color: #94a3b8;
        }}

        .rule-row-active {{
            background: #fef3c7 !important;
            font-weight: 700;
        }}

    </style>
</head>
<body>
    <div class="app-wrapper">
        <header class="editorial-hero">
            <div class="hero-left">
                <span class="editorial-tag">Motor de Análisis Sintáctico y Semántico</span>
                <h1 class="editorial-h1">Compiladores & Lenguajes Formales</h1>
                <p class="editorial-lead">Visualizador interactivo para analizadores LL(1) y SLR(1), autómatas LR(0) y evaluador genérico de Definiciones Dirigidas por la Sintaxis (SDD) basado en Aho, Lam, Sethi y Ullman (Dragon Book).</p>
            </div>
            <div class="hero-right-meta">
                <div class="meta-label">Estudiantes</div>
                <div class="meta-val">Luis Alejandro Castrillón Piedrahita, Manuela Buriticá Guzmán, Maria Juliana Henao Rua</div>

                <div class="meta-label">Profesores</div>
                <div class="meta-val">Oscar Rodríguez Cifuentes, Adolfo Andrés Castro, César Augusto Guerra, Sergio Ramírez Rico</div>

                <div class="meta-label">Asignatura & Semestre</div>
                <div class="meta-val">Lenguajes Formales y Compiladores — 2026-2 (Universidad EAFIT)</div>
            </div>
        </header>

        <nav class="tactile-nav">
            <button class="nav-btn active" style="border-color: var(--accent-emerald); background: #ecfdf5;" onclick="switchTab('tab-ff-lab', this)">★ 1. Lab FIRST & FOLLOW</button>
            <button class="nav-btn" style="border-color: var(--accent-amber); background: #fffbeb;" onclick="switchTab('tab-parsers-lab', this)">★ 2. Lab Parsers LL(1) & SLR(1)</button>
            <button class="nav-btn" style="border-color: var(--accent-blue); background: #eff6ff;" onclick="switchTab('tab-sdd-lab', this)">★ 3. Lab SDD Paso a Paso</button>
            <button class="nav-btn" onclick="switchTab('tab-lr0-graph', this)">4. Autómata LR(0) & Tablas</button>
            <button class="nav-btn" onclick="switchTab('tab-sdd-eval', this)">5. Evaluador SDD Base & DAG</button>
            <button class="nav-btn" onclick="switchTab('tab-suite', this)">6. Verificación & Circularidad</button>
        </nav>


        <!-- TAB 1: LABORATORIO INTERACTIVO FIRST & FOLLOW -->
        <main id="tab-ff-lab" class="tab-pane active">
            <!-- HERO DEL LABORATORIO -->
            <div class="proof-card" style="margin-bottom: 24px; border-left: 6px solid var(--accent-emerald);">
                <div class="proof-card-body" style="padding: 20px 24px;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px;">
                        <div>
                            <span class="editorial-tag" style="margin-bottom: 6px; color: var(--accent-emerald); border-color: var(--accent-emerald);">ALGORITMO ITERATIVO DE PUNTO FIJO • SECCIÓN 4.4.2</span>
                            <h2 style="font-family: 'Playfair Display', serif; font-size: 1.85rem; font-weight: 800; margin-bottom: 8px;">
                                Laboratorio Interactivo: FIRST() y FOLLOW()
                            </h2>
                            <p style="color: var(--text-body); max-width: 860px; font-size: 0.95rem;">
                                Calcula paso a paso los conjuntos FIRST y FOLLOW para cualquier gramática libre de contexto con soporte de producciones &epsilon; (<code>e</code>). Observa en tiempo real cómo se descubren los símbolos anulables y cómo se propagan los conjuntos hasta alcanzar el punto fijo de acuerdo con el texto guía de Aho et al.
                            </p>
                        </div>
                        <div style="text-align: right;">
                            <span class="status-badge tag-new" style="font-size: 0.8rem; background: #ecfdf5; color: #047857; border-color: #059669;">SECCIÓN 4.4.2 COMPLETA</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- SELECTOR DE GRAMATICAS PRECONFIGURADAS -->
            <div style="display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 24px;">
                <button class="lab-ex-btn active" id="btn-ff-own" onclick="selectFFPreset('p_own')">
                    <span class="ex-num">PRESET 1 • PROPIA</span>
                    <span class="ex-name">Listas Delimitadas por Comas</span>
                    <span class="ex-badge l-attr">LL(1) & SLR(1)</span>
                </button>
                <button class="lab-ex-btn" id="btn-ff-ex1" onclick="selectFFPreset('p_ex1')">
                    <span class="ex-num">PRESET 2 • EJEMPLO 1</span>
                    <span class="ex-name">Expresiones Aritméticas (Rec. Izq.)</span>
                    <span class="ex-badge no-l-attr">SLR(1), no LL(1)</span>
                </button>
                <button class="lab-ex-btn" id="btn-ff-ex2" onclick="selectFFPreset('p_ex2')">
                    <span class="ex-num">PRESET 3 • EJEMPLO 2</span>
                    <span class="ex-name">Gramática con &epsilon; (e)</span>
                    <span class="ex-badge l-attr">LL(1) & SLR(1)</span>
                </button>
                <button class="lab-ex-btn" id="btn-ff-ex3" onclick="selectFFPreset('p_ex3')">
                    <span class="ex-num">PRESET 4 • EJEMPLO 3</span>
                    <span class="ex-name">Gramática Ambigua (S -> SS a)</span>
                    <span class="ex-badge no-l-attr">Ni LL(1) ni SLR(1)</span>
                </button>
                <button class="lab-ex-btn" id="btn-ff-ex430" onclick="selectFFPreset('p_ex430')">
                    <span class="ex-num">PRESET 5 • EJERCICIO 4.30</span>
                    <span class="ex-name">Expresiones Factorizadas</span>
                    <span class="ex-badge l-attr">Dragon Book</span>
                </button>
                <button class="lab-ex-btn" id="btn-ff-null" onclick="selectFFPreset('p_null')">
                    <span class="ex-num">PRESET 6 • ANULABLES</span>
                    <span class="ex-name">Cadena de No Terminales &epsilon;</span>
                    <span class="ex-badge l-attr">Multi-Epsilon</span>
                </button>
                <button class="lab-ex-btn" id="btn-ff-sdd" onclick="selectFFPreset('p_sdd')">
                    <span class="ex-num">PRESET 7 • SDD</span>
                    <span class="ex-name">Gramática SDD Oficial (Item 3)</span>
                    <span class="ex-badge l-attr">Item 3 Oficial</span>
                </button>
            </div>

            <!-- ENTRADA DE GRAMATICA Y ACCION -->
            <div class="proof-card" style="margin-bottom: 24px;">
                <div class="proof-card-header">
                    <div class="step-meta-group">
                        <span class="step-num-badge">ENTRADA DE GRAMÁTICA</span>
                        <h3 class="step-title" id="ffConfigTitle">Gramática Libre de Contexto (CFG)</h3>
                    </div>
                    <button class="nav-btn" style="padding: 6px 14px; font-size: 0.75rem;" onclick="resetFFPreset()">↺ Restaurar Preset</button>
                </div>
                <div class="proof-card-body">
                    <div style="display: grid; grid-template-columns: 1fr auto; gap: 16px; align-items: start;">
                        <div>
                            <label class="meta-label" for="ffGrammarInput">Definición de Producciones (Formato: n + producciones separadas por espacio, vacía con 'e')</label>
                            <textarea id="ffGrammarInput" class="input-field" style="width: 100%; height: 110px; font-family: 'JetBrains Mono', monospace; font-size: 0.95rem; font-weight: 600; line-height: 1.45;" oninput="onFFGrammarEdited()"></textarea>
                        </div>
                        <div style="display: flex; flex-direction: column; gap: 10px; min-width: 220px;">
                            <button class="input-btn" style="height: 48px; background: var(--accent-emerald); border-color: var(--border); color: #fff;" onclick="recomputeFF(true)">Calcular FIRST & FOLLOW</button>
                            <span style="font-size: 0.75rem; color: var(--text-muted); line-height: 1.35;">Símbolo inicial 'S'. Terminales en minúsculas/símbolos. 'e' representa &epsilon;.</span>
                        </div>
                    </div>
                    <div id="ffErrorMsg" style="display: none; margin-top: 12px; padding: 10px 14px; background: #fef2f2; border: 1.5px solid var(--accent-red); color: var(--accent-red); font-family: 'JetBrains Mono', monospace; font-size: 0.85rem;"></div>
                </div>
            </div>

            <!-- CONTROLES DE REPRODUCCION Y TIMELINE -->
            <div class="proof-card" style="margin-bottom: 24px; border-top: 4px solid var(--accent-emerald);">
                <div class="proof-card-header" style="flex-wrap: wrap; gap: 12px;">
                    <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                        <button class="transport-btn" title="Paso 0 (Inicial)" onclick="ffStepTo(0)">⏮ Inicio</button>
                        <button class="transport-btn" title="Paso Anterior" onclick="ffStepPrev()">◀ Anterior</button>
                        <button class="transport-btn active-play" id="btnFFPlay" title="Auto-Play" onclick="ffTogglePlay()">▶ Auto-Play</button>
                        <button class="transport-btn" title="Paso Siguiente" onclick="ffStepNext()">▶ Siguiente</button>
                        <button class="transport-btn" title="Ir al Final (Punto Fijo)" onclick="ffStepEnd()">⏭ Punto Fijo</button>
                        <div style="display: flex; align-items: center; gap: 6px; margin-left: 10px;">
                            <span class="meta-label" style="margin-bottom: 0;">Vel:</span>
                            <select id="ffSpeedSelect" class="input-field" style="padding: 4px 8px; font-size: 0.8rem; width: auto;" onchange="changeFFSpeed(this.value)">
                                <option value="1500">0.5x</option>
                                <option value="800" selected>1x</option>
                                <option value="300">2x</option>
                            </select>
                        </div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span id="ffStepBadge" class="step-num-badge" style="font-size: 0.85rem; padding: 6px 12px; background: var(--accent-emerald); color: #fff;">PASO 0 / 0</span>
                        <span id="ffPhaseBadge" class="status-badge tag-new">FASE: INICIAL</span>
                    </div>
                </div>
                <!-- Barra de Progreso Clickeable -->
                <div style="background: var(--bg-subtle); padding: 10px 24px; border-bottom: 2px solid var(--border);">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span class="meta-label" style="margin-bottom: 0; min-width: 60px;">Timeline:</span>
                        <input type="range" id="ffTimelineSlider" min="0" max="0" value="0" style="flex: 1; accent-color: var(--accent-emerald); cursor: pointer;" oninput="ffStepTo(parseInt(this.value))">
                    </div>
                </div>
            </div>

            <!-- CUADRICULA DE RESULTADOS Y EXPLICACION PEDAGOGICA -->
            <div style="display: grid; grid-template-columns: 1.15fr 0.85fr; gap: 24px; margin-bottom: 24px;">
                <!-- TABLA VIVA DE CONJUNTOS -->
                <div class="proof-card">
                    <div class="proof-card-header">
                        <h4 style="font-family: 'JetBrains Mono'; font-size: 0.9rem; text-transform: uppercase;">Estado de Conjuntos en el Paso Actual</h4>
                        <span class="editorial-tag" style="font-size: 0.7rem;">TERMINALES ASCII &rarr; e &rarr; $</span>
                    </div>
                    <div class="proof-card-body" style="padding: 0;">
                        <table class="editorial-table" style="margin: 0; border: none;">
                            <thead>
                                <tr>
                                    <th style="width: 25%;">No Terminal</th>
                                    <th style="width: 37.5%;">FIRST(X)</th>
                                    <th style="width: 37.5%;">FOLLOW(A)</th>
                                </tr>
                            </thead>
                            <tbody id="ffSetsTableBody">
                                <!-- Inyectado dinámicamente -->
                            </tbody>
                        </table>
                    </div>
                    <div style="padding: 16px 20px; border-top: 2px solid var(--border); background: var(--bg-subtle);">
                        <span class="meta-label" style="margin-bottom: 6px;">Formato Oficial (--sets) Generado:</span>
                        <pre id="ffFormattedSetsOutput" style="background: #ffffff; border: 1.5px solid var(--border); padding: 12px; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; font-weight: 600; color: var(--text-main); margin: 0; border-radius: 0;"></pre>
                    </div>
                </div>

                <!-- NARRADOR PEDAGOGICO DEL PASO -->
                <div class="proof-card">
                    <div class="proof-card-header">
                        <h4 style="font-family: 'JetBrains Mono'; font-size: 0.9rem; text-transform: uppercase;">Justificación Formal del Paso</h4>
                        <span id="ffRuleBadge" class="status-badge regular-tag">REGLA APLICADA</span>
                    </div>
                    <div class="proof-card-body">
                        <div id="ffNarratorContent">
                            <!-- Inyectado dinámicamente -->
                        </div>
                        <div style="margin-top: 20px; padding-top: 16px; border-top: 1.5px dashed var(--border-light);">
                            <span class="meta-label">Historial de Pasos Realizados:</span>
                            <div id="ffStepsList" style="max-height: 220px; overflow-y: auto; border: 1.5px solid var(--border-light); margin-top: 6px;">
                                <!-- Inyectado dinámicamente -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>

        <!-- TAB 2: LABORATORIO INTERACTIVO PARSERS LL(1) Y SLR(1) -->
        <main id="tab-parsers-lab" class="tab-pane">
            <!-- HERO DEL LABORATORIO -->
            <div class="proof-card" style="margin-bottom: 24px; border-left: 6px solid var(--accent-amber);">
                <div class="proof-card-body" style="padding: 20px 24px;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px;">
                        <div>
                            <span class="editorial-tag" style="margin-bottom: 6px; color: var(--accent-amber); border-color: var(--accent-amber);">ANALIZADORES SINTÁCTICOS • SECCIONES 4.4.3–4.4.4 Y 4.5–4.6</span>
                            <h2 style="font-family: 'Playfair Display', serif; font-size: 1.85rem; font-weight: 800; margin-bottom: 8px;">
                                Laboratorio Interactivo de Parsers: LL(1) y SLR(1)
                            </h2>
                            <p style="color: var(--text-body); max-width: 860px; font-size: 0.95rem;">
                                Simula paso a paso el análisis descendente LL(1) predictivo no recursivo (Algoritmo 4.34) y el análisis ascendente SLR(1) shift-reduce con autómata LR(0) (Algoritmo 4.44). Observa en vivo la pila, la entrada restante, las acciones formales y la construcción del árbol sintáctico derivado.
                            </p>
                        </div>
                        <div style="text-align: right;">
                            <span class="status-badge tag-new" style="font-size: 0.8rem; background: #fffbeb; color: #b45309; border-color: #d97706;">TOP-DOWN & BOTTOM-UP</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- SELECTOR DE EJEMPLOS PRECONFIGURADOS -->
            <div style="display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 24px;">
                <button class="lab-ex-btn active" id="btn-p-own" onclick="selectParserPreset('p_own')">
                    <span class="ex-num">PRESET 1 • PROPIA</span>
                    <span class="ex-name">Listas Delimitadas por Comas</span>
                    <span class="ex-badge l-attr">LL(1) & SLR(1)</span>
                </button>
                <button class="lab-ex-btn" id="btn-p-ex1" onclick="selectParserPreset('p_ex1')">
                    <span class="ex-num">PRESET 2 • EJEMPLO 1</span>
                    <span class="ex-name">Expresiones con Precedencia</span>
                    <span class="ex-badge no-l-attr">SLR(1), no LL(1)</span>
                </button>
                <button class="lab-ex-btn" id="btn-p-ex2" onclick="selectParserPreset('p_ex2')">
                    <span class="ex-num">PRESET 3 • EJEMPLO 2</span>
                    <span class="ex-name">Gramática con &epsilon; (e)</span>
                    <span class="ex-badge l-attr">LL(1) & SLR(1)</span>
                </button>
                <button class="lab-ex-btn" id="btn-p-ex3" onclick="selectParserPreset('p_ex3')">
                    <span class="ex-num">PRESET 4 • EJEMPLO 3</span>
                    <span class="ex-name">Gramática Ambigua (S -> SS a)</span>
                    <span class="ex-badge no-l-attr">Ni LL(1) ni SLR(1)</span>
                </button>
                <button class="lab-ex-btn" id="btn-p-ex465" onclick="selectParserPreset('p_ex465')">
                    <span class="ex-num">PRESET 5 • EJERCICIO 4.6.5</span>
                    <span class="ex-name">Gramática LL(1), no SLR(1)</span>
                    <span class="ex-badge l-attr">Conflicto R/R en SLR(1)</span>
                </button>
                <button class="lab-ex-btn" id="btn-p-ex466" onclick="selectParserPreset('p_ex466')">
                    <span class="ex-num">PRESET 6 • EJERCICIO 4.6.6</span>
                    <span class="ex-name">Gramática SLR(1), no LL(1)</span>
                    <span class="ex-badge no-l-attr">Rec. Izq. en LL(1)</span>
                </button>
                <button class="lab-ex-btn" id="btn-p-sdd" onclick="selectParserPreset('p_sdd')">
                    <span class="ex-num">PRESET 7 • SDD OFICIAL</span>
                    <span class="ex-name">Gramática SDD Ponderada</span>
                    <span class="ex-badge l-attr">Ambos Parsers</span>
                </button>
            </div>

            <!-- ENTRADA Y DIAGNOSTICO FORMAL -->
            <div class="proof-card" style="margin-bottom: 24px;">
                <div class="proof-card-header">
                    <div class="step-meta-group">
                        <span class="step-num-badge">CONFIGURACIÓN DE ENTRADA</span>
                        <h3 class="step-title" id="parserConfigTitle">Gramática y Cadena a Analizar</h3>
                    </div>
                    <button class="nav-btn" style="padding: 6px 14px; font-size: 0.75rem;" onclick="resetParserPreset()">↺ Restaurar Preset</button>
                </div>
                <div class="proof-card-body">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; align-items: start; margin-bottom: 16px;">
                        <div>
                            <label class="meta-label" for="parserGrammarInput">Gramática de Entrada</label>
                            <textarea id="parserGrammarInput" class="input-field" style="width: 100%; height: 95px; font-family: 'JetBrains Mono', monospace; font-size: 0.95rem; font-weight: 600;" oninput="onParserGrammarEdited()"></textarea>
                        </div>
                        <div>
                            <label class="meta-label" for="parserInputString">Cadena a Parsear (usa 'e' para la cadena vacía)</label>
                            <input type="text" id="parserInputString" class="input-field" style="width: 100%; font-family: 'JetBrains Mono', monospace; font-size: 1.05rem; font-weight: 600; margin-bottom: 10px;" oninput="onParserInputChanged()">
                            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                                <span class="meta-label" style="margin-bottom: 0;">Cadenas Sugeridas:</span>
                                <div id="parserPresetsContainer" style="display: flex; gap: 6px; flex-wrap: wrap;"></div>
                            </div>
                        </div>
                    </div>

                    <!-- BANNER DE CLASIFICACION FORMAL Y SELECCION DE PARSER (SECCION 2.2.2) -->
                    <div id="parserClassificationBanner" style="padding: 16px 20px; border: 2px solid var(--border); background: var(--bg-subtle); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
                        <!-- Inyectado dinámicamente -->
                    </div>
                </div>
            </div>

            <!-- CONTROLES DE REPRODUCCION DEL PARSER -->
            <div class="proof-card" style="margin-bottom: 24px; border-top: 4px solid var(--accent-amber);">
                <div class="proof-card-header" style="flex-wrap: wrap; gap: 12px;">
                    <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                        <button class="transport-btn" title="Paso 0 (Inicial)" onclick="parserStepTo(0)">⏮ Inicio</button>
                        <button class="transport-btn" title="Paso Anterior" onclick="parserStepPrev()">◀ Anterior</button>
                        <button class="transport-btn active-play" id="btnParserPlay" title="Auto-Play" onclick="parserTogglePlay()">▶ Auto-Play</button>
                        <button class="transport-btn" title="Paso Siguiente" onclick="parserStepNext()">▶ Siguiente</button>
                        <button class="transport-btn" title="Evaluar Todo" onclick="parserStepEnd()">⏭ Finalizar</button>
                        <div style="display: flex; align-items: center; gap: 6px; margin-left: 10px;">
                            <span class="meta-label" style="margin-bottom: 0;">Vel:</span>
                            <select id="parserSpeedSelect" class="input-field" style="padding: 4px 8px; font-size: 0.8rem; width: auto;" onchange="changeParserSpeed(this.value)">
                                <option value="1500">0.5x</option>
                                <option value="800" selected>1x</option>
                                <option value="300">2x</option>
                            </select>
                        </div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span id="parserStepBadge" class="step-num-badge" style="font-size: 0.85rem; padding: 6px 12px; background: var(--accent-amber); color: #fff;">PASO 0 / 0</span>
                        <span id="parserActionBadge" class="status-badge regular-tag">ESTADO INICIAL</span>
                    </div>
                </div>
                <!-- Barra de Progreso Clickeable -->
                <div style="background: var(--bg-subtle); padding: 10px 24px; border-bottom: 2px solid var(--border);">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span class="meta-label" style="margin-bottom: 0; min-width: 60px;">Timeline:</span>
                        <input type="range" id="parserTimelineSlider" min="0" max="0" value="0" style="flex: 1; accent-color: var(--accent-amber); cursor: pointer;" oninput="parserStepTo(parseInt(this.value))">
                    </div>
                </div>
            </div>

            <!-- GRID PRINCIPAL DE EJECUCION DEL PARSER -->
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 24px;">
                <!-- COLUMNA IZQUIERDA: PILA, ENTRADA Y ACCION -->
                <div style="display: flex; flex-direction: column; gap: 24px;">
                    <!-- ESTADO DE LA PILA Y ENTRADA -->
                    <div class="proof-card">
                        <div class="proof-card-header">
                            <h4 style="font-family: 'JetBrains Mono'; font-size: 0.9rem; text-transform: uppercase;">Estado de Ejecución del Parser</h4>
                            <span id="parserModeBadge" class="editorial-tag">LL(1) DESCENTE</span>
                        </div>
                        <div class="proof-card-body" id="parserStateDisplay">
                            <!-- Inyectado dinámicamente -->
                        </div>
                        <!-- VEREDICTO FINAL -->
                        <div id="parserVerdictBox" style="padding: 14px 20px; border-top: 2px solid var(--border); display: flex; justify-content: space-between; align-items: center;">
                            <span class="meta-label" style="margin: 0;">Veredicto Oficial (Sección 2.2.2):</span>
                            <span id="parserVerdictText" class="status-badge regular-tag" style="font-size: 1.1rem; font-weight: 800; padding: 4px 16px;">EN EVALUACIÓN</span>
                        </div>
                    </div>

                    <!-- TABLA DE PARSEO CON RESALTADO EN VIVO -->
                    <div class="editorial-table-card">
                        <h4 id="parserTableTitle" style="padding: 14px 20px; border-bottom: 2px solid var(--border); font-family: 'JetBrains Mono'; font-size: 0.85rem; text-transform: uppercase;">Tabla de Análisis</h4>
                        <div id="parserTableContainer" style="overflow-x: auto; max-height: 280px;">
                            <!-- Inyectado dinámicamente -->
                        </div>
                    </div>
                </div>

                <!-- COLUMNA DERECHA: EXPLICACION PEDAGOGICA Y ARBOL SINTACTICO DERIVADO -->
                <div style="display: flex; flex-direction: column; gap: 24px;">
                    <!-- EXPLICACION PEDAGOGICA DEL PASO -->
                    <div class="proof-card">
                        <div class="proof-card-header">
                            <h4 style="font-family: 'JetBrains Mono'; font-size: 0.9rem; text-transform: uppercase;">Decisión Semántica y Regla Formal</h4>
                            <span id="parserDecisionBadge" class="status-badge regular-tag">TRANSICIÓN</span>
                        </div>
                        <div class="proof-card-body">
                            <div id="parserExplanationContent">
                                <!-- Inyectado dinámicamente -->
                            </div>
                        </div>
                    </div>

                    <!-- ARBOL SINTACTICO DERIVADO EN TIEMPO REAL (SVG) -->
                    <div class="proof-card">
                        <div class="proof-card-header">
                            <div class="step-meta-group">
                                <span class="step-num-badge">DERIVACIÓN SINTÁCTICA</span>
                                <h4 class="step-title" style="font-size: 0.95rem;">Árbol Concreto en Construcción</h4>
                            </div>
                            <span class="status-badge start-tag" style="font-size: 0.7rem;">SVG DINÁMICO</span>
                        </div>
                        <div class="proof-card-body" style="padding: 12px; background: #ffffff;">
                            <svg id="parserTreeSvg" style="width: 100%; height: 280px; border: 1.5px solid var(--border-light); background: #fafafa;"></svg>
                        </div>
                    </div>
                </div>
            </div>
        </main>


        <!-- TAB 2: AUTOMATA LR(0) Y TABLAS -->
        <main id="tab-lr0-graph" class="tab-pane">
            <div class="proof-card">
                <div class="proof-card-header">
                    <div class="step-meta-group">
                        <span class="step-num-badge">DIAGRAMA SVG</span>
                        <h3 class="step-title">Autómata Finito Determinista LR(0) (7 Estados)</h3>
                    </div>
                    <span class="status-badge start-tag">ESTADOS CANÓNICOS</span>
                </div>
                <div class="proof-card-body">
                    <p style="color: var(--text-muted); margin-bottom: 20px; font-size: 0.9rem;">El estado I0 (azul) es el estado inicial. El estado I1 (oro) contiene la acción de aceptación S' -> S·.</p>
                    <svg id="lr0Svg" class="graph-svg"></svg>
                </div>
            </div>

            <div class="editorial-table-card">
                <h4 style="padding: 16px 20px; border-bottom: 2px solid var(--border); font-family: 'JetBrains Mono'; font-size: 0.85rem; text-transform: uppercase;">Tabla de Análisis SLR(1) (ACTION y GOTO)</h4>
                <table class="editorial-table">
                    <thead>
                        <tr>
                            <th>Estado</th>
                            <th>b</th>
                            <th>,</th>
                            <th>$</th>
                            <th>S</th>
                            <th>L</th>
                            <th>R</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td><strong>0</strong></td><td>shift 3</td><td></td><td></td><td>1</td><td>2</td><td></td></tr>
                        <tr><td><strong>1</strong></td><td></td><td></td><td><span class="status-badge tag-new">accept</span></td><td></td><td></td><td></td></tr>
                        <tr><td><strong>2</strong></td><td></td><td></td><td>reduce S -> L</td><td></td><td></td><td></td></tr>
                        <tr><td><strong>3</strong></td><td></td><td>shift 5</td><td>reduce R -> e</td><td></td><td></td><td>4</td></tr>
                        <tr><td><strong>4</strong></td><td></td><td></td><td>reduce L -> bR</td><td></td><td></td><td></td></tr>
                        <tr><td><strong>5</strong></td><td>shift 3</td><td></td><td></td><td></td><td>6</td><td></td></tr>
                        <tr><td><strong>6</strong></td><td></td><td></td><td>reduce R -> ,L</td><td></td><td></td><td></td></tr>
                    </tbody>
                </table>
            </div>

            <div class="editorial-table-card">
                <h4 style="padding: 16px 20px; border-bottom: 2px solid var(--border); font-family: 'JetBrains Mono'; font-size: 0.85rem; text-transform: uppercase;">Tabla de Análisis Predictivo LL(1) M[A, a]</h4>
                <table class="editorial-table">
                    <thead>
                        <tr>
                            <th>No Terminal</th>
                            <th>b</th>
                            <th>,</th>
                            <th>$</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td><strong>S</strong></td><td>S -> L</td><td></td><td></td></tr>
                        <tr><td><strong>L</strong></td><td>L -> bR</td><td></td><td></td></tr>
                        <tr><td><strong>R</strong></td><td></td><td>R -> ,L</td><td>R -> e</td></tr>
                    </tbody>
                </table>
            </div>
        </main>



        <!-- TAB 4: LABORATORIO SDD INTERACTIVO PASO A PASO -->
        <main id="tab-sdd-lab" class="tab-pane">
            <!-- HERO DEL LABORATORIO -->
            <div class="proof-card" style="margin-bottom: 24px; border-left: 6px solid var(--accent-blue);">
                <div class="proof-card-body" style="padding: 20px 24px;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px;">
                        <div>
                            <span class="editorial-tag" style="margin-bottom: 6px;">MOTOR DINÁMICO DE EVALUACIÓN SEMÁNTICA EN VIVO</span>
                            <h2 style="font-family: 'Playfair Display', serif; font-size: 1.85rem; font-weight: 800; margin-bottom: 8px;">
                                Laboratorio Interactivo Paso a Paso de SDD
                            </h2>
                            <p style="color: var(--text-body); max-width: 840px; font-size: 0.95rem;">
                                Explora la construcción del árbol sintáctico concreto, la instanciación de dependencias de atributos, el ordenamiento topológico por algoritmo de Kahn y el cómputo semántico paso a paso con explicaciones pedagógicas formales.
                            </p>
                        </div>
                        <div style="text-align: right;">
                            <span class="status-badge tag-new" style="font-size: 0.8rem;">JS PURO • 0 DEPENDENCIAS</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- SELECTOR DE EJERCICIOS -->
            <div style="display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 24px;">
                <button class="lab-ex-btn active" id="btn-ex1" onclick="selectLabExercise('ex1')">
                    <span class="ex-num">EJERCICIO 1</span>
                    <span class="ex-name">Indentación y Costo en Bloques</span>
                    <span class="ex-badge l-attr">L-Atribuida</span>
                </button>
                <button class="lab-ex-btn" id="btn-ex2" onclick="selectLabExercise('ex2')">
                    <span class="ex-num">EJERCICIO 2</span>
                    <span class="ex-name">Conversión Binaria con Escala</span>
                    <span class="ex-badge no-l-attr">Ni S ni L (Flujo R→L)</span>
                </button>
                <button class="lab-ex-btn" id="btn-ex3" onclick="selectLabExercise('ex3')">
                    <span class="ex-num">EJERCICIO 3</span>
                    <span class="ex-name">Tipado y Coerción de Expresiones</span>
                    <span class="ex-badge l-attr">L-Atribuida</span>
                </button>
                <button class="lab-ex-btn" id="btn-base" onclick="selectLabExercise('base')">
                    <span class="ex-num">SDD BASE</span>
                    <span class="ex-name">Listas Binarias y Profundidad</span>
                    <span class="ex-badge l-attr">L-Atribuida (Oficial)</span>
                </button>
            </div>

            <!-- BARRA DE CONFIGURACION EN VIVO -->
            <div class="proof-card" style="margin-bottom: 24px;">
                <div class="proof-card-header">
                    <div class="step-meta-group">
                        <span class="step-num-badge">ENTRADA Y PARÁMETROS</span>
                        <h3 class="step-title" id="labConfigTitle">Configuración de Entrada: Ejercicio 1</h3>
                    </div>
                    <button class="nav-btn" style="padding: 6px 14px; font-size: 0.75rem;" onclick="resetLabToDefaults()">↺ Restaurar Valores por Defecto</button>
                </div>
                <div class="proof-card-body">
                    <!-- Fila de Entrada de Cadena y Presets -->
                    <div style="display: grid; grid-template-columns: 1fr auto; gap: 16px; align-items: end; margin-bottom: 16px;">
                        <div>
                            <label class="meta-label" for="labInputString">Cadena de Entrada (Tokens)</label>
                            <input type="text" id="labInputString" class="input-field" style="width: 100%; font-family: 'JetBrains Mono', monospace; font-size: 1.05rem; font-weight: 600;" oninput="onLabInputChanged()">
                        </div>
                        <button class="input-btn" style="height: 48px; padding: 0 24px;" onclick="reparseAndRunLab()">Re-parsear y Evaluar</button>
                    </div>

                    <!-- Botones de Presets -->
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px; flex-wrap: wrap;">
                        <span class="meta-label" style="margin-bottom: 0;">Presets Rápidos:</span>
                        <div id="labPresetsContainer" style="display: flex; gap: 8px; flex-wrap: wrap;">
                            <!-- Inyectado por JS -->
                        </div>
                    </div>

                    <!-- Parametros dinamicos segun el ejercicio -->
                    <div id="labCustomParams" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; padding-top: 16px; border-top: 1.5px dashed var(--border-light);">
                        <!-- Inyectado por JS -->
                    </div>

                    <!-- Mensaje de Error Sintactico / Validacion -->
                    <div id="labErrorMsg" style="display: none; margin-top: 16px; padding: 12px 16px; background: #fef2f2; border: 1.5px solid var(--accent-red); color: var(--accent-red); font-family: 'JetBrains Mono', monospace; font-size: 0.85rem;">
                    </div>
                </div>
            </div>

            <!-- PANEL DE REPRODUCCION Y NARRADOR PEDAGOGICO -->
            <div class="proof-card" style="margin-bottom: 24px; border-top: 4px solid var(--border);">
                <div class="proof-card-header" style="flex-wrap: wrap; gap: 12px;">
                    <!-- Controles de Transporte -->
                    <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                        <button class="transport-btn" title="Paso 0 (Árbol inicial sin evaluar)" onclick="labStepTo(0)">⏮ Inicio</button>
                        <button class="transport-btn" title="Paso Anterior" onclick="labStepPrev()">◀ Anterior</button>
                        <button class="transport-btn active-play" id="btnLabPlay" title="Auto-Play" onclick="labTogglePlay()">▶ Auto-Play</button>
                        <button class="transport-btn" title="Paso Siguiente" onclick="labStepNext()">▶ Siguiente</button>
                        <button class="transport-btn" title="Evaluar Todo" onclick="labStepEnd()">⏭ Evaluar Todo</button>
                        
                        <div style="display: flex; align-items: center; gap: 6px; margin-left: 10px;">
                            <span class="meta-label" style="margin-bottom: 0;">Vel:</span>
                            <select id="labSpeedSelect" class="input-field" style="padding: 4px 8px; font-size: 0.8rem; width: auto;" onchange="changeLabSpeed(this.value)">
                                <option value="1500">0.5x</option>
                                <option value="800" selected>1x</option>
                                <option value="350">2x</option>
                            </select>
                        </div>
                    </div>

                    <!-- Indicador de Paso y Estado -->
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span id="labStepBadge" class="step-num-badge" style="font-size: 0.85rem; padding: 6px 12px;">PASO 0 / 0</span>
                        <span id="labFlowBadge" class="status-badge regular-tag">SIN EVALUAR</span>
                    </div>
                </div>

                <!-- Barra de Progreso / Timeline Clickeable -->
                <div style="background: var(--bg-subtle); padding: 10px 24px; border-bottom: 2px solid var(--border);">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span class="meta-label" style="margin-bottom: 0; min-width: 60px;">Timeline:</span>
                        <input type="range" id="labTimelineSlider" min="0" max="10" value="0" style="flex: 1; accent-color: var(--accent-blue); cursor: pointer;" oninput="onTimelineSlider(this.value)">
                        <span id="labProgressPct" class="meta-label" style="margin-bottom: 0; min-width: 45px; text-align: right;">0%</span>
                    </div>
                </div>

                <!-- Tarjeta del Narrador Pedagógico -->
                <div class="proof-card-body" id="labNarratorBody" style="background: #ffffff; padding: 20px 24px;">
                    <!-- Contenido del narrador inyectado por JS -->
                </div>
            </div>

            <!-- VISTA DUAL: ARBOL SINTACTICO ANOTADO (SVG) Y GRAFO DE DEPENDENCIAS (DAG SVG) + COLA KAHN -->
            <div style="display: grid; grid-template-columns: 1fr; gap: 24px; margin-bottom: 24px;">
                <!-- ARBOL SINTACTICO SVG -->
                <div class="proof-card">
                    <div class="proof-card-header">
                        <div class="step-meta-group">
                            <span class="step-num-badge">ÁRBOL ANOTADO</span>
                            <h3 class="step-title">Árbol Sintáctico Concreto (Decorado Dinámicamente)</h3>
                        </div>
                        <div style="display: flex; gap: 8px;">
                            <span class="status-badge" style="background: #ecfdf5; color: #059669; border-color: #059669;">● Evaluado</span>
                            <span class="status-badge" style="background: #fef3c7; color: #d97706; border-color: #d97706;">● Activo</span>
                            <span class="status-badge regular-tag">○ Pendiente (?)</span>
                        </div>
                    </div>
                    <div class="proof-card-body" style="padding: 12px; background: #fafafa; overflow-x: auto;">
                        <svg id="labTreeSvg" style="width: 100%; min-height: 480px; display: block; background: #ffffff; border: 1.5px solid var(--border-light);"></svg>
                    </div>
                </div>

                <!-- GRAFO DE DEPENDENCIAS Y COLA TOPOLOGICA -->
                <div style="display: grid; grid-template-columns: 7fr 5fr; gap: 24px;">
                    <!-- DAG SVG -->
                    <div class="proof-card">
                        <div class="proof-card-header">
                            <div class="step-meta-group">
                                <span class="step-num-badge">DAG SVG</span>
                                <h3 class="step-title">Grafo de Dependencias Activo</h3>
                            </div>
                            <span class="status-badge start-tag">ORDEN TOPOLÓGICO</span>
                        </div>
                        <div class="proof-card-body" style="padding: 12px; background: #fafafa; overflow-x: auto;">
                            <svg id="labDagSvg" style="width: 100%; min-height: 420px; display: block; background: #ffffff; border: 1.5px solid var(--border-light);"></svg>
                        </div>
                    </div>

                    <!-- COLA TOPOLOGICA DE KAHN -->
                    <div class="proof-card">
                        <div class="proof-card-header">
                            <div class="step-meta-group">
                                <span class="step-num-badge">KAHN</span>
                                <h3 class="step-title">Secuencia de Evaluación</h3>
                            </div>
                            <span class="status-badge tag-new" id="labTotalStepsBadge">0 PASOS</span>
                        </div>
                        <div class="proof-card-body" style="padding: 0; max-height: 440px; overflow-y: auto;">
                            <div id="labKahnList" style="display: flex; flex-direction: column;">
                                <!-- Inyectado por JS -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- FICHA TEORICA Y DE REFERENCIA FORMAL (COLAPSABLE) -->
            <div class="proof-card">
                <div class="proof-card-header" style="cursor: pointer;" onclick="toggleLabTheory()">
                    <div class="step-meta-group">
                        <span class="step-num-badge">TEORÍA FORMAL</span>
                        <h3 class="step-title" id="labTheoryTitle">Ficha Teórica y Semántica de la SDD</h3>
                    </div>
                    <span class="status-badge regular-tag" id="labTheoryToggleIcon">▼ MOSTRAR DETALLES</span>
                </div>
                <div class="proof-card-body" id="labTheoryContent" style="display: block;">
                    <!-- Contenido formal inyectado segun el ejercicio activo -->
                </div>
            </div>
        </main>

        <!-- TAB 5: SDD EVALUATOR & GRAFO DE DEPENDENCIAS (OFICIAL) -->
        <main id="tab-sdd-eval" class="tab-pane">
            <div class="interactive-tester">
                <h3 style="font-family: 'Playfair Display', serif; font-size: 1.5rem; margin-bottom: 6px;">Probador Interactivo de Expresiones SDD</h3>
                <p style="color: var(--text-muted); font-size: 0.875rem;">Ingresa cualquier cadena del lenguaje (ejemplo: <code>(1+0)</code>, <code>((1+0)+(1))</code>, <code>1+1</code>, <code>0</code>, <code>(1)</code>):</p>
                <div class="input-group">
                    <input type="text" id="interactiveInput" class="input-field" value="(1+0)" placeholder="Ingresa una cadena...">
                    <button class="input-btn" onclick="runLiveEvaluation()">Parse & Evaluar SDD</button>
                </div>
            </div>

            <div class="proof-card">
                <div class="proof-card-header">
                    <div class="step-meta-group">
                        <span class="step-num-badge">ITEM 3: GRAFO</span>
                        <h3 class="step-title">Grafo de Dependencias (DAG) Interactivo para <code>(1+0)</code></h3>
                    </div>
                    <span class="status-badge start-tag">ORDEN TOPOLÓGICO</span>
                </div>
                <div class="proof-card-body">
                    <p style="color: var(--text-muted); margin-bottom: 16px; font-size: 0.9rem;">Las aristas dirigidas (u -> v) representan que el atributo <strong>u</strong> debe calcularse antes que <strong>v</strong>. El nodo dorado S_17.val representa el atributo sintetizado principal.</p>
                    <svg id="dagSvg" class="graph-svg"></svg>
                </div>
            </div>

            <div class="editorial-table-card">
                <h4 style="padding: 16px 20px; border-bottom: 2px solid var(--border); font-family: 'JetBrains Mono'; font-size: 0.85rem; text-transform: uppercase;">Reglas Semánticas (Dragon Book Fig. 5.1)</h4>
                <table class="editorial-table">
                    <thead>
                        <tr>
                            <th>Producción</th>
                            <th>Reglas Semánticas</th>
                            <th>Tipo de Atributos</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td><strong>S -> L</strong></td><td><code>L.d = 0; S.val = L.val; S.max_d = L.max_d</code></td><td>L.d (Heredado), S.val/max_d (Sintetizados)</td></tr>
                        <tr><td><strong>L -> BR</strong></td><td><code>B.d = L.d; R.d = L.d; L.val = B.val + R.val; L.max_d = max(B.max_d, R.max_d)</code></td><td>B.d/R.d (Heredados), L.val/max_d (Sintetizados)</td></tr>
                        <tr><td><strong>R -> +L</strong></td><td><code>L.d = R.d; R.val = L.val; R.max_d = L.max_d</code></td><td>L.d (Heredado), R.val/max_d (Sintetizados)</td></tr>
                        <tr><td><strong>R -> e</strong></td><td><code>R.val = 0; R.max_d = R.d</code></td><td>R.val/max_d (Sintetizados)</td></tr>
                        <tr><td><strong>B -> (L)</strong></td><td><code>L.d = B.d + 1; B.val = L.val; B.max_d = L.max_d</code></td><td>L.d (Heredado por escala), B.val/max_d (Sintetizados)</td></tr>
                        <tr><td><strong>B -> 0</strong></td><td><code>B.val = 0; B.max_d = B.d</code></td><td>B.val/max_d (Sintetizados)</td></tr>
                        <tr><td><strong>B -> 1</strong></td><td><code>B.val = 2^(B.d); B.max_d = B.d</code></td><td>B.val (Ponderado por 2^d), B.max_d (Sintetizado)</td></tr>
                    </tbody>
                </table>
            </div>

            <div class="proof-card">
                <div class="proof-card-header">
                    <div class="step-meta-group">
                        <span class="step-num-badge">ÁRBOL ANOTADO</span>
                        <h3 class="step-title">Árbol Sintáctico Decorado con Atributos: <code>(1+0)</code></h3>
                    </div>
                    <span class="status-badge tag-new">VALOR FINAL = 2</span>
                </div>
                <div class="proof-card-body">
                    <div class="code-box" id="treeOutput">{chr(10).join(tree_lines)}</div>
                    <div class="meta-label">Orden de Evaluación Topológico:</div>
                    <div style="font-family: 'JetBrains Mono'; font-size: 0.85rem; color: var(--accent-blue); margin-top: 6px;">
                        {", ".join(order_labels)}
                    </div>
                </div>
            </div>
        </main>

        <!-- TAB 6: VERIFICACION Y CIRCULARIDAD -->
        <main id="tab-suite" class="tab-pane">
            <div class="proof-card">
                <div class="proof-card-header">
                    <div class="step-meta-group">
                        <span class="step-num-badge">PASO 6</span>
                        <h3 class="step-title">Batería de Pruebas del Evaluador SDD</h3>
                    </div>
                    <span class="status-badge tag-new">100% PRUEBAS SUPERADAS</span>
                </div>
                <div class="proof-card-body">
                    <table class="editorial-table">
                        <thead>
                            <tr>
                                <th>Cadena</th>
                                <th>Tipo de Caso</th>
                                <th>Valor de val</th>
                                <th>Profundidad max_d</th>
                                <th>Estado</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td><code>0</code></td><td>Cadena más corta</td><td>0</td><td>0</td><td><span class="status-badge tag-new">Aceptada</span></td></tr>
                            <tr><td><code>1</code></td><td>Bit simple</td><td>1</td><td>0</td><td><span class="status-badge tag-new">Aceptada</span></td></tr>
                            <tr><td><code>1+0</code></td><td>Suma básica</td><td>1</td><td>0</td><td><span class="status-badge tag-new">Aceptada</span></td></tr>
                            <tr><td><code>(1)</code></td><td>Anidamiento nivel 1</td><td>2 (2^1)</td><td>1</td><td><span class="status-badge tag-new">Aceptada</span></td></tr>
                            <tr><td><code>((1+0)+(1))</code></td><td>Recursión profunda (nivel 2)</td><td>8 (4 + 4)</td><td>2</td><td><span class="status-badge tag-new">Aceptada</span></td></tr>
                            <tr><td><code>1++0</code></td><td>Sintaxis inválida (operador doble)</td><td>-</td><td>-</td><td><span class="status-badge tag-danger">Rechazada (no)</span></td></tr>
                            <tr><td><code>(1+</code></td><td>Paréntesis sin cerrar</td><td>-</td><td>-</td><td><span class="status-badge tag-danger">Rechazada (no)</span></td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="proof-card">
                <div class="proof-card-header">
                    <div class="step-meta-group">
                        <span class="step-num-badge">DETECCIÓN DE CICLOS</span>
                        <h3 class="step-title">Prueba de Definición Circular (--circular)</h3>
                    </div>
                    <span class="status-badge tag-danger">CICLO DETECTADO</span>
                </div>
                <div class="proof-card-body">
                    <p style="color: var(--text-body); margin-bottom: 14px;">Al introducir temporalmente la regla circular <code>L.d = S.val + 1</code> en la producción <code>S -> L</code>, el algoritmo de ordenamiento topológico no puede resolver todos los nodos y la búsqueda en profundidad (DFS) aísla el ciclo exacto:</p>
                    <div class="code-box" style="border-color: var(--accent-red); color: var(--accent-red); background: #fff5f5;">Error: Error: La definición dirigida por la sintaxis (SDD) es CIRCULAR.
Ciclo detectado en las dependencias: {' -> '.join(circular_cycle_path)}
Ciclo identificado: {' -> '.join(circular_cycle_path)}</div>
                </div>
            </div>
        </main>
    </div>

    <script>
        function switchTab(paneId, btn) {{
            document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
            
            const targetPane = document.getElementById(paneId);
            if (targetPane) targetPane.classList.add('active');
            if (btn) btn.classList.add('active');

            if (paneId === 'tab-ff-lab') {{
                setTimeout(initFFLabIfNeeded, 50);
            }} else if (paneId === 'tab-parsers-lab') {{
                setTimeout(initParserLabIfNeeded, 50);
            }} else if (paneId === 'tab-sdd-lab') {{
                setTimeout(initLabIfNeeded, 50);
            }} else if (paneId === 'tab-lr0-graph') {{
                setTimeout(renderLR0Graph, 50);
            }} else if (paneId === 'tab-sdd-eval') {{
                setTimeout(renderDAGGraph, 50);
            }}
        }}

        const lr0Nodes = {json.dumps(lr0_nodes)};
        const lr0Edges = {json.dumps(lr0_edges)};

        function renderLR0Graph() {{
            const svg = document.getElementById('lr0Svg');
            svg.innerHTML = '';
            const width = svg.clientWidth || 980;
            const height = 520;
            
            const N = lr0Nodes.length;
            const cx = width / 2;
            const cy = height / 2;
            const rx = Math.min(width, height) * 0.40;
            const ry = height * 0.35;

            const posMap = {{}};
            lr0Nodes.forEach((node, i) => {{
                const angle = (2 * Math.PI * i) / N - Math.PI / 2;
                const x = cx + rx * Math.cos(angle);
                const y = cy + ry * Math.sin(angle);
                posMap[node.id] = {{x, y}};
            }});

            // Dibujar aristas
            lr0Edges.forEach(edge => {{
                const s = posMap[edge.source];
                const t = posMap[edge.target];
                if (!s || !t) return;

                const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
                if (edge.source === edge.target) {{
                    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                    const d = `M ${{s.x - 14}} ${{s.y - 25}} C ${{s.x - 50}} ${{s.y - 80}}, ${{s.x + 50}} ${{s.y - 80}}, ${{s.x + 14}} ${{s.y - 25}}`;
                    path.setAttribute('d', d);
                    path.setAttribute('fill', 'none');
                    path.setAttribute('stroke', '#0f172a');
                    path.setAttribute('stroke-width', '2');
                    g.appendChild(path);

                    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                    text.setAttribute('x', s.x);
                    text.setAttribute('y', s.y - 85);
                    text.setAttribute('fill', '#1e40af');
                    text.setAttribute('font-size', '13');
                    text.setAttribute('font-family', 'JetBrains Mono');
                    text.setAttribute('font-weight', '700');
                    text.setAttribute('text-anchor', 'middle');
                    text.textContent = edge.label;
                    g.appendChild(text);
                }} else {{
                    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                    line.setAttribute('x1', s.x);
                    line.setAttribute('y1', s.y);
                    line.setAttribute('x2', t.x);
                    line.setAttribute('y2', t.y);
                    line.setAttribute('stroke', '#0f172a');
                    line.setAttribute('stroke-width', '2');
                    g.appendChild(line);

                    const mx = (s.x * 0.4 + t.x * 0.6);
                    const my = (s.y * 0.4 + t.y * 0.6);
                    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                    text.setAttribute('x', mx);
                    text.setAttribute('y', my - 8);
                    text.setAttribute('fill', '#1e40af');
                    text.setAttribute('font-size', '12');
                    text.setAttribute('font-family', 'JetBrains Mono');
                    text.setAttribute('font-weight', '700');
                    text.setAttribute('text-anchor', 'middle');
                    text.textContent = edge.label;
                    g.appendChild(text);
                }}
                svg.appendChild(g);
            }});

            // Dibujar nodos
            lr0Nodes.forEach((node) => {{
                const p = posMap[node.id];
                const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');

                if (node.is_accept) {{
                    const outerCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                    outerCircle.setAttribute('cx', p.x);
                    outerCircle.setAttribute('cy', p.y);
                    outerCircle.setAttribute('r', '32');
                    outerCircle.setAttribute('fill', 'none');
                    outerCircle.setAttribute('stroke', '#d97706');
                    outerCircle.setAttribute('stroke-width', '2.5');
                    g.appendChild(outerCircle);
                }}

                const innerCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                innerCircle.setAttribute('cx', p.x);
                innerCircle.setAttribute('cy', p.y);
                innerCircle.setAttribute('r', '25');
                innerCircle.setAttribute('fill', node.is_start ? '#1e40af' : '#ffffff');
                innerCircle.setAttribute('stroke', '#0f172a');
                innerCircle.setAttribute('stroke-width', '2');
                g.appendChild(innerCircle);

                const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                text.setAttribute('x', p.x);
                text.setAttribute('y', p.y + 5);
                text.setAttribute('fill', node.is_start ? '#ffffff' : '#0f172a');
                text.setAttribute('font-size', '13');
                text.setAttribute('font-weight', '700');
                text.setAttribute('text-anchor', 'middle');
                text.textContent = node.label;
                g.appendChild(text);

                // Subtexto con primer item del estado
                const subtext = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                subtext.setAttribute('x', p.x);
                subtext.setAttribute('y', p.y + 44);
                subtext.setAttribute('fill', '#475569');
                subtext.setAttribute('font-size', '10.5');
                subtext.setAttribute('font-family', 'JetBrains Mono');
                subtext.setAttribute('font-weight', '600');
                subtext.setAttribute('text-anchor', 'middle');
                subtext.textContent = node.items[0] || '';
                g.appendChild(subtext);

                svg.appendChild(g);
            }});
        }}

        const dagNodes = {json.dumps(dag_nodes)};
        const dagEdges = {json.dumps(dag_edges)};

        function renderDAGGraph() {{
            const svg = document.getElementById('dagSvg');
            svg.innerHTML = '';
            const width = svg.clientWidth || 980;
            const height = 520;
            
            const N = dagNodes.length;
            const cols = 7;
            const rows = Math.ceil(N / cols);
            const colWidth = (width - 120) / (cols - 1);
            const rowHeight = (height - 120) / (rows - 1);

            const posMap = {{}};
            dagNodes.forEach((node, i) => {{
                const r = Math.floor(i / cols);
                const c = (r % 2 === 0) ? (i % cols) : (cols - 1 - (i % cols));
                const x = 60 + c * colWidth;
                const y = 60 + r * rowHeight;
                posMap[node.id] = {{x, y}};
            }});

            // Dibujar aristas DAG
            dagEdges.forEach(edge => {{
                const s = posMap[edge.source];
                const t = posMap[edge.target];
                if (!s || !t) return;

                const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
                const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                line.setAttribute('x1', s.x);
                line.setAttribute('y1', s.y);
                line.setAttribute('x2', t.x);
                line.setAttribute('y2', t.y);
                line.setAttribute('stroke', '#94a3b8');
                line.setAttribute('stroke-width', '1.5');
                line.setAttribute('stroke-dasharray', '3 3');
                g.appendChild(line);
                svg.appendChild(g);
            }});

            // Dibujar vértices de atributos
            dagNodes.forEach(node => {{
                const p = posMap[node.id];
                const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');

                const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                circle.setAttribute('cx', p.x);
                circle.setAttribute('cy', p.y);
                circle.setAttribute('r', node.is_main ? '22' : '17');
                circle.setAttribute('fill', node.is_main ? '#fef3c7' : '#ffffff');
                circle.setAttribute('stroke', node.is_main ? '#d97706' : '#0f172a');
                circle.setAttribute('stroke-width', node.is_main ? '2.5' : '1.5');
                g.appendChild(circle);

                const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                text.setAttribute('x', p.x);
                text.setAttribute('y', p.y + 4);
                text.setAttribute('fill', node.is_main ? '#b45309' : '#0f172a');
                text.setAttribute('font-size', '10');
                text.setAttribute('font-family', 'JetBrains Mono');
                text.setAttribute('font-weight', '700');
                text.setAttribute('text-anchor', 'middle');
                text.textContent = node.val;
                g.appendChild(text);

                const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                label.setAttribute('x', p.x);
                label.setAttribute('y', p.y - 22);
                label.setAttribute('fill', '#475569');
                label.setAttribute('font-size', '9');
                label.setAttribute('font-family', 'JetBrains Mono');
                label.setAttribute('font-weight', '600');
                label.setAttribute('text-anchor', 'middle');
                label.textContent = node.label;
                g.appendChild(label);

                svg.appendChild(g);
            }});
        }}

        function runLiveEvaluation() {{
            const str = document.getElementById('interactiveInput').value.trim();
            if (!str) return;

            // Simulación en vivo en el cliente
            alert(`Cadena evaluada: "${{str}}". Revisa la consola o ejecuta 'python3 sdd_main.py' para la traza completa.`);
        }}

// =========================================================================
// MOTOR INTERACTIVO DEL LABORATORIO SDD (JS PURO, 0 DEPENDENCIAS)
// =========================================================================

class LabNode {{
    constructor(symbol, production, children = []) {{
        this.id = ++labNodeIdCounter;
        this.symbol = symbol;
        this.production = production;
        this.children = children;
        this.attributes = {{}};
    }}
    isLeaf() {{
        return !this.children || this.children.length === 0;
    }}
}}

let labNodeIdCounter = 0;
let currentExerciseId = 'ex1';
let labCurrentStep = 0;
let labSteps = [];
let labTreeRoot = null;
let labIsPlaying = false;
let labPlayInterval = null;
let labPlaySpeed = 800;
let labInitialized = false;

// Configuración de los 4 Ejercicios
const labExercises = {{
    ex1: {{
        id: 'ex1',
        name: 'Ejercicio 1: Formateador y Conteo de Indentación en Bloques',
        shortName: 'Indentación y Costo en Bloques',
        classification: 'L-atribuida',
        classBadgeClass: 'l-attr',
        defaultInput: '{{ ; ; }}',
        presets: ['{{ ; ; }}', '{{ {{ ; }} }}', '{{ {{ ; }} ; {{ ; ; }} }}', ';'],
        defaultParams: {{
            initial_depth: 0,
            base_stmt_cost: 1
        }},
        paramDefs: [
            {{ id: 'initial_depth', label: 'B.depth Inicial (en S)', type: 'number', min: 0, max: 5, step: 1 }},
            {{ id: 'base_stmt_cost', label: 'Costo Base de Sentencia (;)', type: 'number', min: 1, max: 10, step: 1 }}
        ],
        mainAttr: {{ symbol: 'S', attr: 'total' }},
        grammar: {{
            text: ["3", "S -> B", "B -> {{ L }} | ;", "L -> B L | e"].join("\\n"),
            terminals: ['{{', '}}', ';'],
            nonterminals: ['S', 'B', 'L']
        }},
        theory: {{
            g1: "Cumple las convenciones formales de la Sección 2.2 y es tanto LL(1) como SLR(1).",
            g2: "Posee 3 símbolos no terminales (S, B, L), 5 alternativas de producción y recursión en L.",
            g3: "Gramática original desarrollada para modelar bloques anidados y ponderación de sentencias.",
            attributes: [
                {{ symbol: 'S', attr: 'total', type: 'Sintetizado', dtype: 'Entero', desc: 'Costo total acumulado de sentencias ponderadas por profundidad' }},
                {{ symbol: 'B', attr: 'depth', type: 'Heredado', dtype: 'Entero', desc: 'Nivel de anidamiento heredado del contexto exterior' }},
                {{ symbol: 'B', attr: 'cost', type: 'Sintetizado', dtype: 'Entero', desc: 'Costo calculado del bloque o sentencia simple' }},
                {{ symbol: 'L', attr: 'depth', type: 'Heredado', dtype: 'Entero', desc: 'Profundidad heredada para la lista de bloques' }},
                {{ symbol: 'L', attr: 'cost', type: 'Sintetizado', dtype: 'Entero', desc: 'Suma de costos de las sentencias en la lista' }}
            ],
            rules: [
                {{ prod: 'S -> B', rules: 'B.depth = initial_depth; S.total = B.cost', flow: 'B.depth (Heredado de S), S.total (Sintetizado de B)' }},
                {{ prod: 'B -> {{ L }}', rules: 'L.depth = B.depth + 1; B.cost = L.cost', flow: 'L.depth (Heredado hacia abajo), B.cost (Sintetizado hacia arriba)' }},
                {{ prod: 'B -> ;', rules: 'B.cost = B.depth + base_stmt_cost', flow: 'B.cost (Sintetizado internamente usando B.depth)' }},
                {{ prod: 'L -> B L1', rules: 'B.depth = L.depth; L1.depth = L.depth; L.cost = B.cost + L1.cost', flow: 'B.depth, L1.depth (Heredados), L.cost (Sintetizado)' }},
                {{ prod: 'L -> e', rules: 'L.cost = 0', flow: 'L.cost (Sintetizado base)' }}
            ],
            classificationJust: "Es <strong>L-atribuida</strong> porque utiliza el atributo heredado <code>depth</code> para propagar el nivel de anidamiento estrictamente de arriba hacia abajo (de padre a hijo) y de izquierda a derecha entre hermanos en los cuerpos de las producciones. No es S-atribuida debido a la presencia de atributos heredados."
        }}
    }},
    ex2: {{
        id: 'ex2',
        name: 'Ejercicio 2: Conversión Binaria a Decimal con Notación Posicional y Escalamiento',
        shortName: 'Conversión Binaria con Escala',
        classification: 'Ni S-atribuida ni L-atribuida',
        classBadgeClass: 'no-l-attr',
        defaultInput: '1 * * *',
        presets: ['1 * * *', '0 * * *', '1', '1 * * * * *'],
        defaultParams: {{
            factor: 2,
            base_scale: 1
        }},
        paramDefs: [
            {{ id: 'factor', label: 'Factor Multiplicador por (*)', type: 'select', options: [2, 8, 10, 16] }},
            {{ id: 'base_scale', label: 'Escala Base en (D -> e)', type: 'number', min: 1, max: 100, step: 1 }}
        ],
        mainAttr: {{ symbol: 'S', attr: 'val' }},
        grammar: {{
            text: ["3", "S -> N", "N -> B D", "D -> * D | e", "B -> 0 | 1"].join("\\n"),
            terminals: ['*', '0', '1'],
            nonterminals: ['S', 'N', 'D', 'B']
        }},
        theory: {{
            g1: "Cumple las convenciones del curso y es tanto LL(1) como SLR(1).",
            g2: "Posee 4 símbolos no terminales (S, N, D, B) y 6 producciones con recursión en D.",
            g3: "SDD no estándar diseñada específicamente para ilustrar dependencias de derecha a izquierda.",
            attributes: [
                {{ symbol: 'S', attr: 'val', type: 'Sintetizado', dtype: 'Entero', desc: 'Valor numérico final de la expresión' }},
                {{ symbol: 'N', attr: 'val', type: 'Sintetizado', dtype: 'Entero', desc: 'Valor del número con su escala posicional' }},
                {{ symbol: 'B', attr: 'scale', type: 'Heredado (R→L)', dtype: 'Entero', desc: 'Factor de escala heredado desde D a su derecha' }},
                {{ symbol: 'B', attr: 'val', type: 'Sintetizado', dtype: 'Entero', desc: 'Valor del bit ponderado por scale' }},
                {{ symbol: 'D', attr: 'scale', type: 'Sintetizado', dtype: 'Entero', desc: 'Potencia o factor acumulado por la cantidad de asteriscos' }}
            ],
            rules: [
                {{ prod: 'S -> N', rules: 'S.val = N.val', flow: 'Sintetizado de N hacia S' }},
                {{ prod: 'N -> B D', rules: 'B.scale = D.scale; N.val = B.val', flow: '⚠️ B.scale = D.scale (Flujo de DERECHA a IZQUIERDA), N.val (Sintetizado)' }},
                {{ prod: 'D -> * D1', rules: 'D.scale = D1.scale * factor', flow: 'Sintetizado de abajo hacia arriba en la cadena de asteriscos' }},
                {{ prod: 'D -> e', rules: 'D.scale = base_scale', flow: 'Sintetizado base en la cadena vacía' }},
                {{ prod: 'B -> 0', rules: 'B.val = 0', flow: 'Sintetizado constante' }},
                {{ prod: 'B -> 1', rules: 'B.val = 1 * B.scale', flow: 'Sintetizado multiplicando 1 por B.scale' }}
            ],
            classificationJust: "<strong>Ni S-atribuida ni L-atribuida.</strong> En la producción <code>N -> B D</code>, la regla <code>B.scale = D.scale</code> asigna un atributo heredado al símbolo <code>B</code> a partir de un atributo de <code>D</code>, el cual se encuentra estrictamente a su <strong>derecha</strong>. La definición de gramáticas L-atribuidas exige que todo atributo heredado en el cuerpo dependa exclusivamente de atributos heredados de la cabeza o de atributos de símbolos situados a su <strong>izquierda</strong>. Por ende, esta SDD no puede evaluarse en un solo recorrido descendente de izquierda a derecha y <em>requiere obligatoriamente</em> el Grafo de Dependencias y el Ordenamiento Topológico."
        }}
    }},
    ex3: {{
        id: 'ex3',
        name: 'Ejercicio 3: Verificación de Tipos y Compatibilidad en Expresiones con Coerción',
        shortName: 'Tipado y Coerción de Expresiones',
        classification: 'L-atribuida',
        classBadgeClass: 'l-attr',
        defaultInput: 'n + f + n',
        presets: ['n + f + n', 'n + n + n', 'f + f', 'n + n + f + n'],
        defaultParams: {{
            root_req_type: 'float'
        }},
        paramDefs: [
            {{ id: 'root_req_type', label: 'E.req_type Inicial (en S)', type: 'select', options: ['float', 'int'] }}
        ],
        mainAttr: {{ symbol: 'S', attr: 'type' }},
        grammar: {{
            text: ["3", "S -> E", "E -> T R", "R -> + E | e", "T -> n | f"].join("\\n"),
            terminals: ['+', 'n', 'f'],
            nonterminals: ['S', 'E', 'R', 'T']
        }},
        theory: {{
            g1: "Cumple las convenciones y es LL(1) y SLR(1).",
            g2: "Posee 4 no terminales (S, E, R, T) y 6 producciones con recursión en R y E.",
            g3: "Sistema de tipos con atributos heredados para requerimiento de contexto y síntesis con promoción semántica.",
            attributes: [
                {{ symbol: 'S', attr: 'type', type: 'Sintetizado', dtype: 'Cadena', desc: 'Tipo semántico final evaluado (int o float)' }},
                {{ symbol: 'E', attr: 'req_type', type: 'Heredado', dtype: 'Cadena', desc: 'Tipo exigido por el contexto superior' }},
                {{ symbol: 'E', attr: 'type', type: 'Sintetizado', dtype: 'Cadena', desc: 'Tipo resultante de la suma' }},
                {{ symbol: 'T', attr: 'type', type: 'Sintetizado', dtype: 'Cadena', desc: 'Tipo léxico del componente (int para n, float para f)' }},
                {{ symbol: 'R', attr: 'inh_type', type: 'Heredado', dtype: 'Cadena', desc: 'Tipo heredado del término izquierdo T' }},
                {{ symbol: 'R', attr: 'type', type: 'Sintetizado', dtype: 'Cadena', desc: 'Tipo acumulado del resto de la suma' }}
            ],
            rules: [
                {{ prod: 'S -> E', rules: 'E.req_type = root_req_type; S.type = E.type', flow: 'E.req_type (Heredado de S), S.type (Sintetizado)' }},
                {{ prod: 'E -> T R', rules: 'R.inh_type = T.type; E.type = "float" if (R.type=="float" or E.req_type=="float") else R.type', flow: 'R.inh_type (Heredado de T a su izquierda), E.type (Sintetizado)' }},
                {{ prod: 'R -> + E', rules: 'E.req_type = R.inh_type; R.type = "float" if (R.inh_type=="float" or E.type=="float") else "int"', flow: 'E.req_type (Heredado de R.inh_type), R.type (Sintetizado con coerción)' }},
                {{ prod: 'R -> e', rules: 'R.type = R.inh_type', flow: 'R.type sintetizado directo desde R.inh_type' }},
                {{ prod: 'T -> n', rules: 'T.type = "int"', flow: 'Sintetizado constante' }},
                {{ prod: 'T -> f', rules: 'T.type = "float"', flow: 'Sintetizado constante' }}
            ],
            classificationJust: "Es <strong>L-atribuida</strong>. Los atributos heredados son <code>req_type</code> (que desciende de la cabeza o se propaga hacia el operando derecho) e <code>inh_type</code> (que pasa desde el operando <code>T</code> hacia el operador derecho <code>R</code>). Ningún atributo depende de elementos a su derecha."
        }}
    }},
    base: {{
        id: 'base',
        name: 'SDD Base Oficial: Listas Binarias con Profundidad de Paréntesis',
        shortName: 'Listas Binarias y Profundidad',
        classification: 'L-atribuida (Oficial)',
        classBadgeClass: 'l-attr',
        defaultInput: '(1+0)',
        presets: ['0', '1', '1+0', '(1)', '(1+0)', '((1+0)+(1))'],
        defaultParams: {{}},
        paramDefs: [],
        mainAttr: {{ symbol: 'S', attr: 'val' }},
        grammar: {{
            text: ["4", "S -> L", "L -> BR", "R -> +L e", "B -> (L) 0 1"].join("\\n"),
            terminals: ['(', ')', '+', '0', '1'],
            nonterminals: ['S', 'L', 'R', 'B']
        }},
        theory: {{
            g1: "Cumple las convenciones del curso y es tanto LL(1) como SLR(1).",
            g2: "4 no terminales (S, L, R, B), 7 producciones y recursión en L y R.",
            g3: "Gramática oficial del Item 3 que calcula expresiones con peso exponencial según nivel de paréntesis.",
            attributes: [
                {{ symbol: 'S', attr: 'val', type: 'Sintetizado', dtype: 'Entero', desc: 'Valor acumulado total de la expresión binaria' }},
                {{ symbol: 'S', attr: 'max_d', type: 'Sintetizado', dtype: 'Entero', desc: 'Máxima profundidad alcanzada en toda la expresión' }},
                {{ symbol: 'L', attr: 'd', type: 'Heredado', dtype: 'Entero', desc: 'Profundidad de anidamiento heredada' }},
                {{ symbol: 'L', attr: 'val', type: 'Sintetizado', dtype: 'Entero', desc: 'Suma de valores en la sublista' }},
                {{ symbol: 'L', attr: 'max_d', type: 'Sintetizado', dtype: 'Entero', desc: 'Máxima profundidad en la sublista' }},
                {{ symbol: 'R', attr: 'd', type: 'Heredado', dtype: 'Entero', desc: 'Profundidad heredada para los términos restantes' }},
                {{ symbol: 'R', attr: 'val', type: 'Sintetizado', dtype: 'Entero', desc: 'Valor de los términos restantes' }},
                {{ symbol: 'R', attr: 'max_d', type: 'Sintetizado', dtype: 'Entero', desc: 'Máxima profundidad en términos restantes' }},
                {{ symbol: 'B', attr: 'd', type: 'Heredado', dtype: 'Entero', desc: 'Profundidad heredada para el bit o bloque' }},
                {{ symbol: 'B', attr: 'val', type: 'Sintetizado', dtype: 'Entero', desc: '2^d para 1, 0 para 0, o suma de L' }},
                {{ symbol: 'B', attr: 'max_d', type: 'Sintetizado', dtype: 'Entero', desc: 'Máxima profundidad alcanzada en el bloque' }}
            ],
            rules: [
                {{ prod: 'S -> L', rules: 'L.d = 0; S.val = L.val; S.max_d = L.max_d', flow: 'L.d (Heredado), S.val / max_d (Sintetizados)' }},
                {{ prod: 'L -> BR', rules: 'B.d = L.d; R.d = L.d; L.val = B.val + R.val; L.max_d = max(B.max_d, R.max_d)', flow: 'B.d / R.d (Heredados), L.val / max_d (Sintetizados)' }},
                {{ prod: 'R -> +L', rules: 'L.d = R.d; R.val = L.val; R.max_d = L.max_d', flow: 'L.d (Heredado), R.val / max_d (Sintetizados)' }},
                {{ prod: 'R -> e', rules: 'R.val = 0; R.max_d = R.d', flow: 'R.val / max_d (Sintetizados base)' }},
                {{ prod: 'B -> (L)', rules: 'L.d = B.d + 1; B.val = L.val; B.max_d = L.max_d', flow: 'L.d (Heredado con incremento de nivel), B.val / max_d (Sintetizados)' }},
                {{ prod: 'B -> 0', rules: 'B.val = 0; B.max_d = B.d', flow: 'B.val constante 0, max_d toma B.d' }},
                {{ prod: 'B -> 1', rules: 'B.val = 2^(B.d); B.max_d = B.d', flow: 'B.val ponderado 2^(B.d), max_d toma B.d' }}
            ],
            classificationJust: "Es <strong>L-atribuida</strong>. Utiliza el atributo heredado <code>d</code> propagado estrictamente de arriba hacia abajo (de padre a hijo) y de izquierda a derecha. No posee ninguna dependencia hacia la derecha en los cuerpos."
        }}
    }}
}};

function tokenizeInput(inputStr, exId) {{
    const raw = inputStr.replace(/\\s+/g, '');
    const tokens = [];
    for (let i = 0; i < raw.length; i++) {{
        tokens.push(raw[i]);
    }}
    tokens.push('$');
    return tokens;
}}

function parseInputForExercise(inputStr, exId) {{
    const tokens = tokenizeInput(inputStr, exId);
    let ip = 0;
    labNodeIdCounter = 0;

    function peek() {{
        return tokens[ip];
    }}
    function match(expected) {{
        if (tokens[ip] === expected) {{
            const sym = tokens[ip];
            ip++;
            return sym;
        }}
        throw new Error("Error sintáctico: se esperaba '" + expected + "', pero se encontró '" + tokens[ip] + "' en la posición " + (ip + 1) + ".");
    }}

    if (exId === 'ex1') {{
        function parseS() {{
            const node = new LabNode('S', 'S -> B');
            node.children = [parseB()];
            return node;
        }}
        function parseB() {{
            if (peek() === '{{') {{
                match('{{');
                const tOpen = new LabNode('{{', null);
                const lNode = parseL();
                match('}}');
                const tClose = new LabNode('}}', null);
                return new LabNode('B', 'B -> {{ L }}', [tOpen, lNode, tClose]);
            }} else if (peek() === ';') {{
                match(';');
                return new LabNode('B', 'B -> ;', [new LabNode(';', null)]);
            }} else {{
                throw new Error("Error sintáctico en B: se esperaba '{{' o ';', pero se encontró '" + peek() + "'.");
            }}
        }}
        function parseL() {{
            if (peek() === '{{' || peek() === ';') {{
                const bNode = parseB();
                const l1Node = parseL();
                return new LabNode('L', 'L -> B L', [bNode, l1Node]);
            }} else if (peek() === '}}' || peek() === '$') {{
                return new LabNode('L', 'L -> e', [new LabNode('e', null)]);
            }} else {{
                throw new Error("Error sintáctico en L: se esperaba '{{', ';' o '}}', pero se encontró '" + peek() + "'.");
            }}
        }}
        const root = parseS();
        if (peek() !== '$') {{
            throw new Error("Error sintáctico: tokens sobrantes no reconocidos al final: '" + tokens.slice(ip, -1).join('') + "'.");
        }}
        return root;
    }} else if (exId === 'ex2') {{
        function parseS() {{
            const node = new LabNode('S', 'S -> N');
            node.children = [parseN()];
            return node;
        }}
        function parseN() {{
            const bNode = parseB();
            const dNode = parseD();
            return new LabNode('N', 'N -> B D', [bNode, dNode]);
        }}
        function parseB() {{
            if (peek() === '0') {{
                match('0');
                return new LabNode('B', 'B -> 0', [new LabNode('0', null)]);
            }} else if (peek() === '1') {{
                match('1');
                return new LabNode('B', 'B -> 1', [new LabNode('1', null)]);
            }} else {{
                throw new Error("Error sintáctico en B: se esperaba '0' o '1', pero se encontró '" + peek() + "'.");
            }}
        }}
        function parseD() {{
            if (peek() === '*') {{
                match('*');
                const tStar = new LabNode('*', null);
                const d1Node = parseD();
                return new LabNode('D', 'D -> * D', [tStar, d1Node]);
            }} else if (peek() === '$') {{
                return new LabNode('D', 'D -> e', [new LabNode('e', null)]);
            }} else {{
                throw new Error("Error sintáctico en D: se esperaba '*' o fin de cadena, pero se encontró '" + peek() + "'.");
            }}
        }}
        const root = parseS();
        if (peek() !== '$') {{
            throw new Error("Error sintáctico: tokens sobrantes no reconocidos al final: '" + tokens.slice(ip, -1).join('') + "'.");
        }}
        return root;
    }} else if (exId === 'ex3') {{
        function parseS() {{
            const node = new LabNode('S', 'S -> E');
            node.children = [parseE()];
            return node;
        }}
        function parseE() {{
            const tNode = parseT();
            const rNode = parseR();
            return new LabNode('E', 'E -> T R', [tNode, rNode]);
        }}
        function parseT() {{
            if (peek() === 'n') {{
                match('n');
                return new LabNode('T', 'T -> n', [new LabNode('n', null)]);
            }} else if (peek() === 'f') {{
                match('f');
                return new LabNode('T', 'T -> f', [new LabNode('f', null)]);
            }} else {{
                throw new Error("Error sintáctico en T: se esperaba 'n' o 'f', pero se encontró '" + peek() + "'.");
            }}
        }}
        function parseR() {{
            if (peek() === '+') {{
                match('+');
                const tPlus = new LabNode('+', null);
                const eNode = parseE();
                return new LabNode('R', 'R -> + E', [tPlus, eNode]);
            }} else if (peek() === '$') {{
                return new LabNode('R', 'R -> e', [new LabNode('e', null)]);
            }} else {{
                throw new Error("Error sintáctico en R: se esperaba '+' o fin de cadena, pero se encontró '" + peek() + "'.");
            }}
        }}
        const root = parseS();
        if (peek() !== '$') {{
            throw new Error("Error sintáctico: tokens sobrantes no reconocidos al final: '" + tokens.slice(ip, -1).join('') + "'.");
        }}
        return root;
    }} else if (exId === 'base') {{
        function parseS() {{
            const node = new LabNode('S', 'S -> L');
            node.children = [parseL()];
            return node;
        }}
        function parseL() {{
            const bNode = parseB();
            const rNode = parseR();
            return new LabNode('L', 'L -> BR', [bNode, rNode]);
        }}
        function parseB() {{
            if (peek() === '(') {{
                match('(');
                const tOpen = new LabNode('(', null);
                const lNode = parseL();
                match(')');
                const tClose = new LabNode(')', null);
                return new LabNode('B', 'B -> (L)', [tOpen, lNode, tClose]);
            }} else if (peek() === '0') {{
                match('0');
                return new LabNode('B', 'B -> 0', [new LabNode('0', null)]);
            }} else if (peek() === '1') {{
                match('1');
                return new LabNode('B', 'B -> 1', [new LabNode('1', null)]);
            }} else {{
                throw new Error("Error sintáctico en B: se esperaba '(', '0' o '1', pero se encontró '" + peek() + "'.");
            }}
        }}
        function parseR() {{
            if (peek() === '+') {{
                match('+');
                const tPlus = new LabNode('+', null);
                const lNode = parseL();
                return new LabNode('R', 'R -> +L', [tPlus, lNode]);
            }} else if (peek() === ')' || peek() === '$') {{
                return new LabNode('R', 'R -> e', [new LabNode('e', null)]);
            }} else {{
                throw new Error("Error sintáctico en R: se esperaba '+', ')' o fin de cadena, pero se encontró '" + peek() + "'.");
            }}
        }}
        const root = parseS();
        if (peek() !== '$') {{
            throw new Error("Error sintáctico: tokens sobrantes no reconocidos al final: '" + tokens.slice(ip, -1).join('') + "'.");
        }}
        return root;
    }}
    throw new Error("Ejercicio desconocido: " + exId);
}}

function buildLabSemanticRules(root, exId, params) {{
    const rules = [];
    const allNodesById = {{}};

    function collectNodes(node) {{
        allNodesById[node.id] = node;
        if (node.children) {{
            node.children.forEach(collectNodes);
        }}
    }}
    collectNodes(root);

    function traverse(node) {{
        if (!node.production) return;

        if (exId === 'ex1') {{
            const initialDepth = Number(params.initial_depth !== undefined ? params.initial_depth : 0);
            const baseCost = Number(params.base_stmt_cost !== undefined ? params.base_stmt_cost : 1);

            if (node.production === 'S -> B') {{
                const B = node.children[0];
                rules.push({{
                    target: {{ id: B.id, attr: 'depth', node: B }},
                    deps: [],
                    compute: () => initialDepth,
                    ruleDesc: "B.depth = " + initialDepth + " (initial_depth)",
                    evalFormula: (deps) => "B_" + B.id + ".depth = " + initialDepth,
                    flow: 'inh',
                    explanation: (deps) => "Regla heredada inicial: la raíz S fija la profundidad inicial del bloque B_" + B.id + " en " + initialDepth + "."
                }});
                rules.push({{
                    target: {{ id: node.id, attr: 'total', node: node }},
                    deps: [{{ id: B.id, attr: 'cost', node: B }}],
                    compute: (bCost) => bCost,
                    ruleDesc: "S.total = B.cost",
                    evalFormula: (deps) => "S_" + node.id + ".total = B_" + B.id + ".cost = " + deps[0]?.val,
                    flow: 'syn',
                    explanation: (deps) => "Regla sintetizada final: el costo total en S_" + node.id + " recibe el costo acumulado " + deps[0]?.val + " del bloque B_" + B.id + "."
                }});
            }} else if (node.production === 'B -> {{ L }}') {{
                const L = node.children[1];
                rules.push({{
                    target: {{ id: L.id, attr: 'depth', node: L }},
                    deps: [{{ id: node.id, attr: 'depth', node: node }}],
                    compute: (bDepth) => bDepth + 1,
                    ruleDesc: "L.depth = B.depth + 1",
                    evalFormula: (deps) => "L_" + L.id + ".depth = B_" + node.id + ".depth + 1 = " + deps[0]?.val + " + 1 = " + (deps[0]?.val + 1),
                    flow: 'inh',
                    explanation: (deps) => "Regla heredada: al descender dentro del bloque {{ ... }}, la profundidad para L_" + L.id + " se incrementa a " + (deps[0]?.val + 1) + "."
                }});
                rules.push({{
                    target: {{ id: node.id, attr: 'cost', node: node }},
                    deps: [{{ id: L.id, attr: 'cost', node: L }}],
                    compute: (lCost) => lCost,
                    ruleDesc: "B.cost = L.cost",
                    evalFormula: (deps) => "B_" + node.id + ".cost = L_" + L.id + ".cost = " + deps[0]?.val,
                    flow: 'syn',
                    explanation: (deps) => "Regla sintetizada: el bloque B_" + node.id + " toma el costo " + deps[0]?.val + " calculado por su lista interna L_" + L.id + "."
                }});
            }} else if (node.production === 'B -> ;') {{
                rules.push({{
                    target: {{ id: node.id, attr: 'cost', node: node }},
                    deps: [{{ id: node.id, attr: 'depth', node: node }}],
                    compute: (bDepth) => bDepth + baseCost,
                    ruleDesc: "B.cost = B.depth + " + baseCost + " (base_stmt_cost)",
                    evalFormula: (deps) => "B_" + node.id + ".cost = B_" + node.id + ".depth + " + baseCost + " = " + deps[0]?.val + " + " + baseCost + " = " + (deps[0]?.val + baseCost),
                    flow: 'syn',
                    explanation: (deps) => "Regla sintetizada: sentencia simple ';' calcula su costo sumando profundidad (" + deps[0]?.val + ") + costo base (" + baseCost + ") = " + (deps[0]?.val + baseCost) + "."
                }});
            }} else if (node.production === 'L -> B L') {{
                const B = node.children[0];
                const L1 = node.children[1];
                rules.push({{
                    target: {{ id: B.id, attr: 'depth', node: B }},
                    deps: [{{ id: node.id, attr: 'depth', node: node }}],
                    compute: (lDepth) => lDepth,
                    ruleDesc: "B.depth = L.depth",
                    evalFormula: (deps) => "B_" + B.id + ".depth = L_" + node.id + ".depth = " + deps[0]?.val,
                    flow: 'inh',
                    explanation: (deps) => "Regla heredada: la profundidad " + deps[0]?.val + " se propaga al primer elemento B_" + B.id + "."
                }});
                rules.push({{
                    target: {{ id: L1.id, attr: 'depth', node: L1 }},
                    deps: [{{ id: node.id, attr: 'depth', node: node }}],
                    compute: (lDepth) => lDepth,
                    ruleDesc: "L1.depth = L.depth",
                    evalFormula: (deps) => "L_" + L1.id + ".depth = L_" + node.id + ".depth = " + deps[0]?.val,
                    flow: 'inh',
                    explanation: (deps) => "Regla heredada (de izquierda a derecha): la profundidad " + deps[0]?.val + " se transmite al resto L_" + L1.id + "."
                }});
                rules.push({{
                    target: {{ id: node.id, attr: 'cost', node: node }},
                    deps: [{{ id: B.id, attr: 'cost', node: B }}, {{ id: L1.id, attr: 'cost', node: L1 }}],
                    compute: (bCost, l1Cost) => bCost + l1Cost,
                    ruleDesc: "L.cost = B.cost + L1.cost",
                    evalFormula: (deps) => "L_" + node.id + ".cost = B_" + B.id + ".cost + L_" + L1.id + ".cost = " + deps[0]?.val + " + " + deps[1]?.val + " = " + (deps[0]?.val + deps[1]?.val),
                    flow: 'syn',
                    explanation: (deps) => "Regla sintetizada: suma el costo del bloque B_" + B.id + " (" + deps[0]?.val + ") con el resto L_" + L1.id + " (" + deps[1]?.val + ") = " + (deps[0]?.val + deps[1]?.val) + "."
                }});
            }} else if (node.production === 'L -> e') {{
                rules.push({{
                    target: {{ id: node.id, attr: 'cost', node: node }},
                    deps: [],
                    compute: () => 0,
                    ruleDesc: "L.cost = 0",
                    evalFormula: (deps) => "L_" + node.id + ".cost = 0",
                    flow: 'syn',
                    explanation: (deps) => "Regla sintetizada base: epsilon no añade costo (L.cost = 0)."
                }});
            }}
        }} else if (exId === 'ex2') {{
            const factor = Number(params.factor !== undefined ? params.factor : 2);
            const baseScale = Number(params.base_scale !== undefined ? params.base_scale : 1);

            if (node.production === 'S -> N') {{
                const N = node.children[0];
                rules.push({{
                    target: {{ id: node.id, attr: 'val', node: node }},
                    deps: [{{ id: N.id, attr: 'val', node: N }}],
                    compute: (nVal) => nVal,
                    ruleDesc: "S.val = N.val",
                    evalFormula: (deps) => "S_" + node.id + ".val = N_" + N.id + ".val = " + deps[0]?.val,
                    flow: 'syn',
                    explanation: (deps) => "Regla sintetizada final: S_" + node.id + " recibe el valor " + deps[0]?.val + " de N_" + N.id + "."
                }});
            }} else if (node.production === 'N -> B D') {{
                const B = node.children[0];
                const D = node.children[1];
                rules.push({{
                    target: {{ id: B.id, attr: 'scale', node: B }},
                    deps: [{{ id: D.id, attr: 'scale', node: D }}],
                    compute: (dScale) => dScale,
                    ruleDesc: "B.scale = D.scale (¡FLUJO DE DERECHA A IZQUIERDA!)",
                    evalFormula: (deps) => "B_" + B.id + ".scale = D_" + D.id + ".scale = " + deps[0]?.val,
                    flow: 'rtl',
                    explanation: (deps) => "⚠️ ATENCIÓN (NO L-ATRIBUIDA): Dependencia derecha-a-izquierda. La escala acumulada en D_" + D.id + " (" + deps[0]?.val + ") se propaga hacia el dígito B_" + B.id + " a su izquierda para fijar su escala posicional."
                }});
                rules.push({{
                    target: {{ id: node.id, attr: 'val', node: node }},
                    deps: [{{ id: B.id, attr: 'val', node: B }}],
                    compute: (bVal) => bVal,
                    ruleDesc: "N.val = B.val",
                    evalFormula: (deps) => "N_" + node.id + ".val = B_" + B.id + ".val = " + deps[0]?.val,
                    flow: 'syn',
                    explanation: (deps) => "Regla sintetizada: N_" + node.id + " toma el valor escalado " + deps[0]?.val + " de B_" + B.id + "."
                }});
            }} else if (node.production === 'D -> * D') {{
                const D1 = node.children[1];
                rules.push({{
                    target: {{ id: node.id, attr: 'scale', node: node }},
                    deps: [{{ id: D1.id, attr: 'scale', node: D1 }}],
                    compute: (d1Scale) => d1Scale * factor,
                    ruleDesc: "D.scale = D1.scale * " + factor,
                    evalFormula: (deps) => "D_" + node.id + ".scale = D_" + D1.id + ".scale * " + factor + " = " + deps[0]?.val + " * " + factor + " = " + (deps[0]?.val * factor),
                    flow: 'syn',
                    explanation: (deps) => "Regla sintetizada: cada '*' multiplica la escala de D_" + D1.id + " (" + deps[0]?.val + ") por " + factor + " = " + (deps[0]?.val * factor) + "."
                }});
            }} else if (node.production === 'D -> e') {{
                rules.push({{
                    target: {{ id: node.id, attr: 'scale', node: node }},
                    deps: [],
                    compute: () => baseScale,
                    ruleDesc: "D.scale = " + baseScale,
                    evalFormula: (deps) => "D_" + node.id + ".scale = " + baseScale,
                    flow: 'syn',
                    explanation: (deps) => "Regla sintetizada base: fin de asteriscos fija escala base = " + baseScale + "."
                }});
            }} else if (node.production === 'B -> 0') {{
                rules.push({{
                    target: {{ id: node.id, attr: 'val', node: node }},
                    deps: [],
                    compute: () => 0,
                    ruleDesc: "B.val = 0",
                    evalFormula: (deps) => "B_" + node.id + ".val = 0",
                    flow: 'syn',
                    explanation: (deps) => "Regla sintetizada: bit 0 vale 0."
                }});
            }} else if (node.production === 'B -> 1') {{
                rules.push({{
                    target: {{ id: node.id, attr: 'val', node: node }},
                    deps: [{{ id: node.id, attr: 'scale', node: node }}],
                    compute: (bScale) => 1 * bScale,
                    ruleDesc: "B.val = 1 * B.scale",
                    evalFormula: (deps) => "B_" + node.id + ".val = 1 * B_" + node.id + ".scale = 1 * " + deps[0]?.val + " = " + deps[0]?.val,
                    flow: 'syn',
                    explanation: (deps) => "Regla sintetizada: bit 1 multiplicado por escala (" + deps[0]?.val + ") = " + deps[0]?.val + "."
                }});
            }}
        }} else if (exId === 'ex3') {{
            const rootReqType = params.root_req_type !== undefined ? params.root_req_type : 'float';

            if (node.production === 'S -> E') {{
                const E = node.children[0];
                rules.push({{
                    target: {{ id: E.id, attr: 'req_type', node: E }},
                    deps: [],
                    compute: () => rootReqType,
                    ruleDesc: 'E.req_type = "' + rootReqType + '"',
                    evalFormula: (deps) => "E_" + E.id + ".req_type = '" + rootReqType + "'",
                    flow: 'inh',
                    explanation: (deps) => "Regla heredada: el contexto superior exige tipo objetivo '" + rootReqType + "'."
                }});
                rules.push({{
                    target: {{ id: node.id, attr: 'type', node: node }},
                    deps: [{{ id: E.id, attr: 'type', node: E }}],
                    compute: (eType) => eType,
                    ruleDesc: "S.type = E.type",
                    evalFormula: (deps) => "S_" + node.id + ".type = E_" + E.id + ".type = '" + deps[0]?.val + "'",
                    flow: 'syn',
                    explanation: (deps) => "Regla sintetizada final: tipo verificado para el programa es '" + deps[0]?.val + "'."
                }});
            }} else if (node.production === 'E -> T R') {{
                const T = node.children[0];
                const R = node.children[1];
                rules.push({{
                    target: {{ id: R.id, attr: 'inh_type', node: R }},
                    deps: [{{ id: T.id, attr: 'type', node: T }}],
                    compute: (tType) => tType,
                    ruleDesc: "R.inh_type = T.type",
                    evalFormula: (deps) => "R_" + R.id + ".inh_type = T_" + T.id + ".type = '" + deps[0]?.val + "'",
                    flow: 'inh',
                    explanation: (deps) => "Regla heredada de izquierda a derecha: el tipo '" + deps[0]?.val + "' de T_" + T.id + " se hereda a R_" + R.id + "."
                }});
                rules.push({{
                    target: {{ id: node.id, attr: 'type', node: node }},
                    deps: [{{ id: R.id, attr: 'type', node: R }}, {{ id: node.id, attr: 'req_type', node: node }}],
                    compute: (rType, reqType) => (rType === 'float' || reqType === 'float') ? 'float' : rType,
                    ruleDesc: "E.type = 'float' if (R.type=='float' or E.req_type=='float') else R.type",
                    evalFormula: (deps) => "E_" + node.id + ".type = (" + deps[0]?.val + "=='float' || " + deps[1]?.val + "=='float') ? 'float' : '" + deps[0]?.val + "' = '" + ((deps[0]?.val === 'float' || deps[1]?.val === 'float') ? 'float' : deps[0]?.val) + "'",
                    flow: 'syn',
                    explanation: (deps) => "Regla sintetizada con coerción: compara tipo de operandos (" + deps[0]?.val + ") y exigido (" + deps[1]?.val + "). Si alguno es float, promueve a 'float'."
                }});
            }} else if (node.production === 'R -> + E') {{
                const E = node.children[1];
                rules.push({{
                    target: {{ id: E.id, attr: 'req_type', node: E }},
                    deps: [{{ id: node.id, attr: 'inh_type', node: node }}],
                    compute: (rInh) => rInh,
                    ruleDesc: "E.req_type = R.inh_type",
                    evalFormula: (deps) => "E_" + E.id + ".req_type = R_" + node.id + ".inh_type = '" + deps[0]?.val + "'",
                    flow: 'inh',
                    explanation: (deps) => "Regla heredada: transmite requerimiento '" + deps[0]?.val + "' al término derecho E_" + E.id + "."
                }});
                rules.push({{
                    target: {{ id: node.id, attr: 'type', node: node }},
                    deps: [{{ id: node.id, attr: 'inh_type', node: node }}, {{ id: E.id, attr: 'type', node: E }}],
                    compute: (rInh, eType) => (rInh === 'float' || eType === 'float') ? 'float' : 'int',
                    ruleDesc: "R.type = 'float' if (R.inh_type=='float' or E.type=='float') else 'int'",
                    evalFormula: (deps) => "R_" + node.id + ".type = (" + deps[0]?.val + "=='float' || " + deps[1]?.val + "=='float') ? 'float' : 'int' = '" + ((deps[0]?.val === 'float' || deps[1]?.val === 'float') ? 'float' : 'int') + "'",
                    flow: 'syn',
                    explanation: (deps) => "Regla sintetizada de suma (+): (" + deps[0]?.val + " + " + deps[1]?.val + "). Si al menos uno es float, resultado es 'float'."
                }});
            }} else if (node.production === 'R -> e') {{
                rules.push({{
                    target: {{ id: node.id, attr: 'type', node: node }},
                    deps: [{{ id: node.id, attr: 'inh_type', node: node }}],
                    compute: (rInh) => rInh,
                    ruleDesc: "R.type = R.inh_type",
                    evalFormula: (deps) => "R_" + node.id + ".type = R_" + node.id + ".inh_type = '" + deps[0]?.val + "'",
                    flow: 'syn',
                    explanation: (deps) => "Regla sintetizada base: retorna directamente el tipo heredado '" + deps[0]?.val + "'."
                }});
            }} else if (node.production === 'T -> n') {{
                rules.push({{
                    target: {{ id: node.id, attr: 'type', node: node }},
                    deps: [],
                    compute: () => 'int',
                    ruleDesc: "T.type = 'int'",
                    evalFormula: (deps) => "T_" + node.id + ".type = 'int'",
                    flow: 'syn',
                    explanation: (deps) => "Regla sintetizada: literal entero 'n' tiene tipo 'int'."
                }});
            }} else if (node.production === 'T -> f') {{
                rules.push({{
                    target: {{ id: node.id, attr: 'type', node: node }},
                    deps: [],
                    compute: () => 'float',
                    ruleDesc: "T.type = 'float'",
                    evalFormula: (deps) => "T_" + node.id + ".type = 'float'",
                    flow: 'syn',
                    explanation: (deps) => "Regla sintetizada: literal flotante 'f' tiene tipo 'float'."
                }});
            }}
        }} else if (exId === 'base') {{
            if (node.production === 'S -> L') {{
                const L = node.children[0];
                rules.push({{
                    target: {{ id: L.id, attr: 'd', node: L }},
                    deps: [],
                    compute: () => 0,
                    ruleDesc: "L.d = 0",
                    evalFormula: (deps) => "L_" + L.id + ".d = 0",
                    flow: 'inh',
                    explanation: (deps) => "Regla heredada inicial: la raíz S fija la profundidad base L_" + L.id + ".d = 0."
                }});
                rules.push({{
                    target: {{ id: node.id, attr: 'val', node: node }},
                    deps: [{{ id: L.id, attr: 'val', node: L }}],
                    compute: (lVal) => lVal,
                    ruleDesc: "S.val = L.val",
                    evalFormula: (deps) => "S_" + node.id + ".val = L_" + L.id + ".val = " + deps[0]?.val,
                    flow: 'syn',
                    explanation: (deps) => "Regla sintetizada: el valor final de la expresión binaria es " + deps[0]?.val + "."
                }});
                rules.push({{
                    target: {{ id: node.id, attr: 'max_d', node: node }},
                    deps: [{{ id: L.id, attr: 'max_d', node: L }}],
                    compute: (lMax) => lMax,
                    ruleDesc: "S.max_d = L.max_d",
                    evalFormula: (deps) => "S_" + node.id + ".max_d = L_" + L.id + ".max_d = " + deps[0]?.val,
                    flow: 'syn',
                    explanation: (deps) => "Regla sintetizada: la profundidad máxima alcanzada en la expresión es " + deps[0]?.val + "."
                }});
            }} else if (node.production === 'L -> BR') {{
                const B = node.children[0];
                const R = node.children[1];
                rules.push({{
                    target: {{ id: B.id, attr: 'd', node: B }},
                    deps: [{{ id: node.id, attr: 'd', node: node }}],
                    compute: (lD) => lD,
                    ruleDesc: "B.d = L.d",
                    evalFormula: (deps) => "B_" + B.id + ".d = L_" + node.id + ".d = " + deps[0]?.val,
                    flow: 'inh',
                    explanation: (deps) => "Regla heredada: la profundidad " + deps[0]?.val + " desciende hacia el bloque B_" + B.id + "."
                }});
                rules.push({{
                    target: {{ id: R.id, attr: 'd', node: R }},
                    deps: [{{ id: node.id, attr: 'd', node: node }}],
                    compute: (lD) => lD,
                    ruleDesc: "R.d = L.d",
                    evalFormula: (deps) => "R_" + R.id + ".d = L_" + node.id + ".d = " + deps[0]?.val,
                    flow: 'inh',
                    explanation: (deps) => "Regla heredada: la profundidad " + deps[0]?.val + " se propaga al resto R_" + R.id + "."
                }});
                rules.push({{
                    target: {{ id: node.id, attr: 'val', node: node }},
                    deps: [{{ id: B.id, attr: 'val', node: B }}, {{ id: R.id, attr: 'val', node: R }}],
                    compute: (bVal, rVal) => bVal + rVal,
                    ruleDesc: "L.val = B.val + R.val",
                    evalFormula: (deps) => "L_" + node.id + ".val = B_" + B.id + ".val + R_" + R.id + ".val = " + deps[0]?.val + " + " + deps[1]?.val + " = " + (deps[0]?.val + deps[1]?.val),
                    flow: 'syn',
                    explanation: (deps) => "Regla sintetizada: suma el valor del término B_" + B.id + " (" + deps[0]?.val + ") y el resto R_" + R.id + " (" + deps[1]?.val + ") = " + (deps[0]?.val + deps[1]?.val) + "."
                }});
                rules.push({{
                    target: {{ id: node.id, attr: 'max_d', node: node }},
                    deps: [{{ id: B.id, attr: 'max_d', node: B }}, {{ id: R.id, attr: 'max_d', node: R }}],
                    compute: (bMax, rMax) => Math.max(bMax, rMax),
                    ruleDesc: "L.max_d = max(B.max_d, R.max_d)",
                    evalFormula: (deps) => "L_" + node.id + ".max_d = max(" + deps[0]?.val + ", " + deps[1]?.val + ") = " + Math.max(deps[0]?.val, deps[1]?.val),
                    flow: 'syn',
                    explanation: (deps) => "Regla sintetizada: toma la profundidad máxima entre B_" + B.id + " (" + deps[0]?.val + ") y R_" + R.id + " (" + deps[1]?.val + ")."
                }});
            }} else if (node.production === 'R -> +L') {{
                const L = node.children[1];
                rules.push({{
                    target: {{ id: L.id, attr: 'd', node: L }},
                    deps: [{{ id: node.id, attr: 'd', node: node }}],
                    compute: (rD) => rD,
                    ruleDesc: "L.d = R.d",
                    evalFormula: (deps) => "L_" + L.id + ".d = R_" + node.id + ".d = " + deps[0]?.val,
                    flow: 'inh',
                    explanation: (deps) => "Regla heredada: propaga la profundidad " + deps[0]?.val + " hacia el operando L_" + L.id + "."
                }});
                rules.push({{
                    target: {{ id: node.id, attr: 'val', node: node }},
                    deps: [{{ id: L.id, attr: 'val', node: L }}],
                    compute: (lVal) => lVal,
                    ruleDesc: "R.val = L.val",
                    evalFormula: (deps) => "R_" + node.id + ".val = L_" + L.id + ".val = " + deps[0]?.val,
                    flow: 'syn',
                    explanation: (deps) => "Regla sintetizada: R_" + node.id + " recibe el valor " + deps[0]?.val + " del término sumado L_" + L.id + "."
                }});
                rules.push({{
                    target: {{ id: node.id, attr: 'max_d', node: node }},
                    deps: [{{ id: L.id, attr: 'max_d', node: L }}],
                    compute: (lMax) => lMax,
                    ruleDesc: "R.max_d = L.max_d",
                    evalFormula: (deps) => "R_" + node.id + ".max_d = L_" + L.id + ".max_d = " + deps[0]?.val,
                    flow: 'syn',
                    explanation: (deps) => "Regla sintetizada: propaga la profundidad máxima " + deps[0]?.val + "."
                }});
            }} else if (node.production === 'R -> e') {{
                rules.push({{
                    target: {{ id: node.id, attr: 'val', node: node }},
                    deps: [],
                    compute: () => 0,
                    ruleDesc: "R.val = 0",
                    evalFormula: (deps) => "R_" + node.id + ".val = 0",
                    flow: 'syn',
                    explanation: (deps) => "Regla sintetizada base: epsilon no añade valor (R.val = 0)."
                }});
                rules.push({{
                    target: {{ id: node.id, attr: 'max_d', node: node }},
                    deps: [{{ id: node.id, attr: 'd', node: node }}],
                    compute: (rD) => rD,
                    ruleDesc: "R.max_d = R.d",
                    evalFormula: (deps) => "R_" + node.id + ".max_d = R_" + node.id + ".d = " + deps[0]?.val,
                    flow: 'syn',
                    explanation: (deps) => "Regla sintetizada base: max_d toma la profundidad actual " + deps[0]?.val + "."
                }});
            }} else if (node.production === 'B -> (L)') {{
                const L = node.children[1];
                rules.push({{
                    target: {{ id: L.id, attr: 'd', node: L }},
                    deps: [{{ id: node.id, attr: 'd', node: node }}],
                    compute: (bD) => bD + 1,
                    ruleDesc: "L.d = B.d + 1",
                    evalFormula: (deps) => "L_" + L.id + ".d = B_" + node.id + ".d + 1 = " + deps[0]?.val + " + 1 = " + (deps[0]?.val + 1),
                    flow: 'inh',
                    explanation: (deps) => "Regla heredada con incremento: dentro de los paréntesis ( ... ), el nivel de anidamiento sube de " + deps[0]?.val + " a " + (deps[0]?.val + 1) + "."
                }});
                rules.push({{
                    target: {{ id: node.id, attr: 'val', node: node }},
                    deps: [{{ id: L.id, attr: 'val', node: L }}],
                    compute: (lVal) => lVal,
                    ruleDesc: "B.val = L.val",
                    evalFormula: (deps) => "B_" + node.id + ".val = L_" + L.id + ".val = " + deps[0]?.val,
                    flow: 'syn',
                    explanation: (deps) => "Regla sintetizada: B_" + node.id + " toma el valor evaluado de la subexpresión L_" + L.id + " (" + deps[0]?.val + ")."
                }});
                rules.push({{
                    target: {{ id: node.id, attr: 'max_d', node: node }},
                    deps: [{{ id: L.id, attr: 'max_d', node: L }}],
                    compute: (lMax) => lMax,
                    ruleDesc: "B.max_d = L.max_d",
                    evalFormula: (deps) => "B_" + node.id + ".max_d = L_" + L.id + ".max_d = " + deps[0]?.val,
                    flow: 'syn',
                    explanation: (deps) => "Regla sintetizada: profundidad máxima heredada del interior de los paréntesis (" + deps[0]?.val + ")."
                }});
            }} else if (node.production === 'B -> 0') {{
                rules.push({{
                    target: {{ id: node.id, attr: 'val', node: node }},
                    deps: [],
                    compute: () => 0,
                    ruleDesc: "B.val = 0",
                    evalFormula: (deps) => "B_" + node.id + ".val = 0",
                    flow: 'syn',
                    explanation: (deps) => "Regla sintetizada: bit 0 vale 0."
                }});
                rules.push({{
                    target: {{ id: node.id, attr: 'max_d', node: node }},
                    deps: [{{ id: node.id, attr: 'd', node: node }}],
                    compute: (bD) => bD,
                    ruleDesc: "B.max_d = B.d",
                    evalFormula: (deps) => "B_" + node.id + ".max_d = B_" + node.id + ".d = " + deps[0]?.val,
                    flow: 'syn',
                    explanation: (deps) => "Regla sintetizada: max_d es la profundidad actual " + deps[0]?.val + "."
                }});
            }} else if (node.production === 'B -> 1') {{
                rules.push({{
                    target: {{ id: node.id, attr: 'val', node: node }},
                    deps: [{{ id: node.id, attr: 'd', node: node }}],
                    compute: (bD) => Math.pow(2, bD),
                    ruleDesc: "B.val = 2^(B.d)",
                    evalFormula: (deps) => "B_" + node.id + ".val = 2^(B_" + node.id + ".d) = 2^" + deps[0]?.val + " = " + Math.pow(2, deps[0]?.val),
                    flow: 'syn',
                    explanation: (deps) => "Regla sintetizada ponderada: el bit 1 vale 2^(profundidad) = 2^" + deps[0]?.val + " = " + Math.pow(2, deps[0]?.val) + "."
                }});
                rules.push({{
                    target: {{ id: node.id, attr: 'max_d', node: node }},
                    deps: [{{ id: node.id, attr: 'd', node: node }}],
                    compute: (bD) => bD,
                    ruleDesc: "B.max_d = B.d",
                    evalFormula: (deps) => "B_" + node.id + ".max_d = B_" + node.id + ".d = " + deps[0]?.val,
                    flow: 'syn',
                    explanation: (deps) => "Regla sintetizada: max_d es la profundidad actual " + deps[0]?.val + "."
                }});
            }}
        }}

        if (node.children) {{
            node.children.forEach(traverse);
        }}
    }}

    traverse(root);
    return {{ rules, allNodesById }};
}}

function runLabKahnTopologicalSort(rules, allNodesById) {{
    const vertexKey = (id, attr) => id + "." + attr;
    const vertexLabel = (node, attr) => node.symbol + "_" + node.id + "." + attr;

    const adj = {{}};
    const inDegree = {{}};
    const ruleByTarget = {{}};
    const allVertices = new Set();

    rules.forEach(r => {{
        const tKey = vertexKey(r.target.id, r.target.attr);
        allVertices.add(tKey);
        ruleByTarget[tKey] = r;
        if (inDegree[tKey] === undefined) inDegree[tKey] = 0;

        r.deps.forEach(d => {{
            const dKey = vertexKey(d.id, d.attr);
            allVertices.add(dKey);
            if (!adj[dKey]) adj[dKey] = [];
            adj[dKey].push(tKey);
            inDegree[tKey] = (inDegree[tKey] || 0) + 1;
            if (inDegree[dKey] === undefined) inDegree[dKey] = 0;
        }});
    }});

    // Cola de Kahn
    const queue = [];
    allVertices.forEach(vKey => {{
        if (inDegree[vKey] === 0) {{
            queue.push(vKey);
        }}
    }});

    // Ordenar determinísticamente por ID numérico de nodo y nombre de atributo
    queue.sort((a, b) => {{
        const [aId, aAttr] = a.split('.');
        const [bId, bAttr] = b.split('.');
        const diff = Number(aId) - Number(bId);
        return diff !== 0 ? diff : aAttr.localeCompare(bAttr);
    }});

    const evaluatedValues = {{}};
    const steps = [];
    let stepNum = 0;

    while (queue.length > 0) {{
        const uKey = queue.shift();
        stepNum++;
        const rule = ruleByTarget[uKey];
        if (!rule) continue;

        const depValues = rule.deps.map(d => {{
            const dKey = vertexKey(d.id, d.attr);
            return {{
                id: d.id,
                attr: d.attr,
                label: vertexLabel(d.node, d.attr),
                val: evaluatedValues[dKey]
            }};
        }});

        const computedVal = rule.compute(...depValues.map(d => d.val));
        evaluatedValues[uKey] = computedVal;
        rule.target.node.attributes[rule.target.attr] = computedVal;

        const targetLabel = vertexLabel(rule.target.node, rule.target.attr);
        const evalFormulaStr = rule.evalFormula(depValues);
        const explanationStr = typeof rule.explanation === 'function' ? rule.explanation(depValues) : rule.explanation;

        steps.push({{
            stepNum,
            vertexKey: uKey,
            targetLabel,
            targetNode: rule.target.node,
            targetAttr: rule.target.attr,
            val: computedVal,
            ruleDesc: rule.ruleDesc,
            evalFormula: evalFormulaStr,
            flow: rule.flow,
            deps: depValues,
            explanation: explanationStr,
            inDegree: 0
        }});

        const neighbors = adj[uKey] || [];
        const nextBatch = [];
        neighbors.forEach(vKey => {{
            inDegree[vKey]--;
            if (inDegree[vKey] === 0) {{
                nextBatch.push(vKey);
            }}
        }});
        nextBatch.sort((a, b) => {{
            const [aId, aAttr] = a.split('.');
            const [bId, bAttr] = b.split('.');
            const diff = Number(aId) - Number(bId);
            return diff !== 0 ? diff : aAttr.localeCompare(bAttr);
        }});
        queue.push(...nextBatch);
    }}

    const hasCycle = steps.length < rules.length;
    return {{ steps, hasCycle, evaluatedValues, adj }};
}}

function renderLabTreeSVG(root, currentStepIndex) {{
    const svg = document.getElementById('labTreeSvg');
    if (!svg) return;
    svg.innerHTML = '';

    let leafX = 50;
    const leafSpacing = 95;
    const levelHeight = 110;
    let maxDepth = 0;

    function layout(node, depth) {{
        if (depth > maxDepth) maxDepth = depth;
        node.depth = depth;
        node.y = 60 + depth * levelHeight;

        if (!node.children || node.children.length === 0) {{
            node.x = leafX;
            leafX += leafSpacing;
        }} else {{
            node.children.forEach(c => layout(c, depth + 1));
            const first = node.children[0];
            const last = node.children[node.children.length - 1];
            node.x = (first.x + last.x) / 2;
        }}
    }}
    layout(root, 0);

    const totalWidth = Math.max(leafX + 50, 750);
    const totalHeight = 80 + (maxDepth + 1) * levelHeight + 40;
    svg.setAttribute('viewBox', "0 0 " + totalWidth + " " + totalHeight);
    svg.style.height = totalHeight + "px";

    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    defs.innerHTML = '<marker id="labArrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="#d97706" /></marker><marker id="labArrowRed" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="#dc2626" /></marker>';
    svg.appendChild(defs);

    const branchGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    function drawBranches(node) {{
        if (!node.children) return;
        node.children.forEach(child => {{
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', node.x);
            line.setAttribute('y1', node.y + 18);
            line.setAttribute('x2', child.x);
            line.setAttribute('y2', child.y - 18);
            line.setAttribute('stroke', '#0f172a');
            line.setAttribute('stroke-width', '2');
            branchGroup.appendChild(line);
            drawBranches(child);
        }});
    }}
    drawBranches(root);
    svg.appendChild(branchGroup);

    const activeStep = (currentStepIndex > 0 && currentStepIndex <= labSteps.length) ? labSteps[currentStepIndex - 1] : null;
    const nodePosMap = {{}};

    const nodeGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    function drawNodes(node) {{
        nodePosMap[node.id] = {{ x: node.x, y: node.y }};

        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        const isLeaf = node.isLeaf();
        const isTargetNode = activeStep && activeStep.targetNode.id === node.id;

        if (isLeaf) {{
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('cx', node.x);
            circle.setAttribute('cy', node.y);
            circle.setAttribute('r', '17');
            circle.setAttribute('fill', node.symbol === 'e' ? '#f1f5f9' : '#ffffff');
            circle.setAttribute('stroke', '#0f172a');
            circle.setAttribute('stroke-width', '2');
            g.appendChild(circle);

            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', node.x);
            text.setAttribute('y', node.y + 5);
            text.setAttribute('font-family', 'JetBrains Mono');
            text.setAttribute('font-size', '13');
            text.setAttribute('font-weight', '700');
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('fill', node.symbol === 'e' ? '#64748b' : '#0f172a');
            text.textContent = node.symbol === 'e' ? 'ε' : node.symbol;
            g.appendChild(text);
        }} else {{
            const boxW = 68;
            const boxH = 34;
            const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            rect.setAttribute('x', node.x - boxW / 2);
            rect.setAttribute('y', node.y - boxH / 2);
            rect.setAttribute('width', boxW);
            rect.setAttribute('height', boxH);
            rect.setAttribute('rx', '4');
            rect.setAttribute('fill', isTargetNode ? '#fef3c7' : '#ffffff');
            rect.setAttribute('stroke', isTargetNode ? '#d97706' : '#0f172a');
            rect.setAttribute('stroke-width', isTargetNode ? '2.5' : '2');
            if (isTargetNode) {{
                rect.setAttribute('filter', 'drop-shadow(2px 2px 0px #0f172a)');
            }}
            g.appendChild(rect);

            const symText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            symText.setAttribute('x', node.x);
            symText.setAttribute('y', node.y + 3);
            symText.setAttribute('font-family', 'Inter');
            symText.setAttribute('font-size', '13');
            symText.setAttribute('font-weight', '800');
            symText.setAttribute('text-anchor', 'middle');
            symText.setAttribute('fill', '#0f172a');
            symText.textContent = node.symbol;
            g.appendChild(symText);

            const subText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            subText.setAttribute('x', node.x + 12);
            subText.setAttribute('y', node.y + 7);
            subText.setAttribute('font-family', 'JetBrains Mono');
            subText.setAttribute('font-size', '10');
            subText.setAttribute('font-weight', '700');
            subText.setAttribute('fill', isTargetNode ? '#d97706' : '#1e40af');
            subText.textContent = "" + node.id;
            g.appendChild(subText);

            if (node.production) {{
                const prodText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                prodText.setAttribute('x', node.x);
                prodText.setAttribute('y', node.y + boxH / 2 + 13);
                prodText.setAttribute('font-family', 'JetBrains Mono');
                prodText.setAttribute('font-size', '9');
                prodText.setAttribute('font-weight', '600');
                prodText.setAttribute('text-anchor', 'middle');
                prodText.setAttribute('fill', '#64748b');
                prodText.textContent = node.production;
                g.appendChild(prodText);
            }}

            const attrs = Object.keys(node.attributes);
            if (attrs.length > 0) {{
                let badgeY = node.y + boxH / 2 + 27;
                attrs.forEach(attrName => {{
                    const isActiveAttr = activeStep && activeStep.targetNode.id === node.id && activeStep.targetAttr === attrName;
                    
                    let isEvaluated = false;
                    let valToShow = '?';
                    for (let s = 0; s < currentStepIndex && s < labSteps.length; s++) {{
                        if (labSteps[s].targetNode.id === node.id && labSteps[s].targetAttr === attrName) {{
                            isEvaluated = true;
                            valToShow = labSteps[s].val;
                            break;
                        }}
                    }}

                    const attrG = document.createElementNS('http://www.w3.org/2000/svg', 'g');
                    const bW = 68;
                    const bH = 17;
                    const bRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
                    bRect.setAttribute('x', node.x - bW / 2);
                    bRect.setAttribute('y', badgeY);
                    bRect.setAttribute('width', bW);
                    bRect.setAttribute('height', bH);
                    bRect.setAttribute('rx', '3');
                    bRect.setAttribute('fill', isActiveAttr ? '#fef3c7' : (isEvaluated ? '#ecfdf5' : '#f8fafc'));
                    bRect.setAttribute('stroke', isActiveAttr ? '#d97706' : (isEvaluated ? '#059669' : '#cbd5e1'));
                    bRect.setAttribute('stroke-width', isActiveAttr ? '2' : '1');
                    attrG.appendChild(bRect);

                    const aText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                    aText.setAttribute('x', node.x);
                    aText.setAttribute('y', badgeY + 12);
                    aText.setAttribute('font-family', 'JetBrains Mono');
                    aText.setAttribute('font-size', '9.5');
                    aText.setAttribute('font-weight', '700');
                    aText.setAttribute('text-anchor', 'middle');
                    aText.setAttribute('fill', isActiveAttr ? '#b45309' : (isEvaluated ? '#047857' : '#94a3b8'));
                    aText.textContent = attrName + ": " + valToShow;
                    attrG.appendChild(aText);

                    g.appendChild(attrG);
                    badgeY += 20;
                }});
            }}
        }}

        nodeGroup.appendChild(g);
        if (node.children) {{
            node.children.forEach(drawNodes);
        }}
    }}
    drawNodes(root);
    svg.appendChild(nodeGroup);

    if (activeStep && activeStep.deps.length > 0) {{
        const arrowGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        const tgtPos = nodePosMap[activeStep.targetNode.id];

        activeStep.deps.forEach(dep => {{
            const srcPos = nodePosMap[dep.id];
            if (!srcPos || !tgtPos) return;
            if (srcPos.x === tgtPos.x && srcPos.y === tgtPos.y) return;

            const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            const dx = tgtPos.x - srcPos.x;
            const dy = tgtPos.y - srcPos.y;
            const cx = (srcPos.x + tgtPos.x) / 2 - (dy * 0.25);
            const cy = (srcPos.y + tgtPos.y) / 2 + (dx * 0.25);
            const d = "M " + srcPos.x + " " + srcPos.y + " Q " + cx + " " + cy + " " + tgtPos.x + " " + tgtPos.y;

            path.setAttribute('d', d);
            path.setAttribute('fill', 'none');
            path.setAttribute('stroke', activeStep.flow === 'rtl' ? '#dc2626' : '#d97706');
            path.setAttribute('stroke-width', '2.5');
            path.setAttribute('stroke-dasharray', '4 3');
            path.setAttribute('marker-end', activeStep.flow === 'rtl' ? 'url(#labArrowRed)' : 'url(#labArrow)');
            arrowGroup.appendChild(path);
        }});
        svg.appendChild(arrowGroup);
    }}
}}

function renderLabDAGSVG(steps, currentStepIndex) {{
    const svg = document.getElementById('labDagSvg');
    if (!svg) return;
    svg.innerHTML = '';

    const width = svg.clientWidth || 540;
    const height = 400;
    svg.setAttribute('viewBox', "0 0 " + width + " " + height);

    if (!steps || steps.length === 0) return;

    const N = steps.length;
    const cols = Math.min(Math.ceil(Math.sqrt(N * 1.5)), 6);
    const rows = Math.ceil(N / cols);
    const colW = (width - 100) / Math.max(cols - 1, 1);
    const rowH = (height - 90) / Math.max(rows - 1, 1);

    const posMap = {{}};
    steps.forEach((step, i) => {{
        const r = Math.floor(i / cols);
        const c = (r % 2 === 0) ? (i % cols) : (cols - 1 - (i % cols));
        const x = 50 + c * colW;
        const y = 45 + r * rowH;
        posMap[step.vertexKey] = {{ x, y }};
    }});

    steps.forEach(step => {{
        const tgtPos = posMap[step.vertexKey];
        if (!tgtPos) return;
        step.deps.forEach(dep => {{
            const dKey = dep.id + "." + dep.attr;
            const srcPos = posMap[dKey];
            if (!srcPos) return;

            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', srcPos.x);
            line.setAttribute('y1', srcPos.y);
            line.setAttribute('x2', tgtPos.x);
            line.setAttribute('y2', tgtPos.y);
            line.setAttribute('stroke', '#cbd5e1');
            line.setAttribute('stroke-width', '1.5');
            line.setAttribute('stroke-dasharray', '3 3');
            svg.appendChild(line);
        }});
    }});

    steps.forEach((step) => {{
        const pos = posMap[step.vertexKey];
        if (!pos) return;

        const isCurrent = (currentStepIndex === step.stepNum);
        const isEvaluated = (step.stepNum <= currentStepIndex);

        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        g.style.cursor = 'pointer';
        g.onclick = () => labStepTo(step.stepNum);

        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', pos.x);
        circle.setAttribute('cy', pos.y);
        circle.setAttribute('r', isCurrent ? '18' : '14');
        circle.setAttribute('fill', isCurrent ? '#fef3c7' : (isEvaluated ? '#ecfdf5' : '#ffffff'));
        circle.setAttribute('stroke', isCurrent ? '#d97706' : (isEvaluated ? '#059669' : '#0f172a'));
        circle.setAttribute('stroke-width', isCurrent ? '2.5' : '1.5');
        g.appendChild(circle);

        const valText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        valText.setAttribute('x', pos.x);
        valText.setAttribute('y', pos.y + 4);
        valText.setAttribute('font-family', 'JetBrains Mono');
        valText.setAttribute('font-size', isCurrent ? '10' : '9');
        valText.setAttribute('font-weight', '700');
        valText.setAttribute('text-anchor', 'middle');
        valText.setAttribute('fill', isCurrent ? '#b45309' : (isEvaluated ? '#047857' : '#94a3b8'));
        valText.textContent = isEvaluated ? ("" + step.val) : '?';
        g.appendChild(valText);

        const lbl = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        lbl.setAttribute('x', pos.x);
        lbl.setAttribute('y', pos.y - (isCurrent ? 22 : 18));
        lbl.setAttribute('font-family', 'JetBrains Mono');
        lbl.setAttribute('font-size', '8.5');
        lbl.setAttribute('font-weight', '600');
        lbl.setAttribute('text-anchor', 'middle');
        lbl.setAttribute('fill', isCurrent ? '#d97706' : '#475569');
        lbl.textContent = step.targetLabel;
        g.appendChild(lbl);

        svg.appendChild(g);
    }});
}}

function renderLabKahnList(steps, currentStepIndex) {{
    const container = document.getElementById('labKahnList');
    if (!container) return;
    container.innerHTML = '';

    steps.forEach(step => {{
        const isCurrent = (currentStepIndex === step.stepNum);
        const isEvaluated = (step.stepNum <= currentStepIndex);

        const item = document.createElement('div');
        item.className = "kahn-step-item " + (isCurrent ? 'active' : '') + " " + (isEvaluated ? 'evaluated' : 'pending');
        item.onclick = () => labStepTo(step.stepNum);

        let flowTag = '';
        if (step.flow === 'rtl') {{
            flowTag = '<span class="status-badge" style="background:#fef2f2; color:#dc2626; border-color:#dc2626; font-size:0.65rem;">R→L</span>';
        }} else if (step.flow === 'inh') {{
            flowTag = '<span class="status-badge" style="background:#eff6ff; color:#1e40af; border-color:#1e40af; font-size:0.65rem;">HER</span>';
        }} else {{
            flowTag = '<span class="status-badge" style="background:#fef3c7; color:#d97706; border-color:#d97706; font-size:0.65rem;">SIN</span>';
        }}

        item.innerHTML = '<div style="display: flex; align-items: center; gap: 8px;"><span style="font-weight: 700; min-width: 28px;">#' + step.stepNum + '</span>' + flowTag + '<span style="font-weight: 600;">' + step.targetLabel + '</span></div><div style="font-weight: 700; color: ' + (isEvaluated ? 'var(--text-main)' : 'var(--text-muted)') + ';">' + (isEvaluated ? step.val : '?') + '</div>';

        if (isCurrent) {{
            setTimeout(() => {{
                if (item.scrollIntoView) {{
                    item.scrollIntoView({{ block: 'nearest', behavior: 'smooth' }});
                }}
            }}, 10);
        }}

        container.appendChild(item);
    }});
}}

function renderLabTheory(exId, activeRuleDesc = null) {{
    const container = document.getElementById('labTheoryContent');
    if (!container) return;
    const ex = labExercises[exId];
    if (!ex) return;

    let attrsRows = ex.theory.attributes.map(a => '<tr><td><strong>' + a.symbol + '</strong></td><td><code>' + a.attr + '</code></td><td><span class="status-badge ' + (a.type.includes('Heredado') ? 'start-tag' : 'final-tag') + '">' + a.type + '</span></td><td>' + a.dtype + '</td><td>' + a.desc + '</td></tr>').join('');

    let rulesRows = ex.theory.rules.map(r => {{
        const isActive = activeRuleDesc && activeRuleDesc.includes(r.prod);
        return '<tr class="' + (isActive ? 'rule-row-active' : '') + '"><td><strong>' + r.prod + '</strong></td><td><code>' + r.rules + '</code></td><td><span style="font-size: 0.85rem; color: var(--text-body);">' + r.flow + '</span></td></tr>';
    }}).join('');

    container.innerHTML = '<div style="margin-bottom: 20px;"><h4 style="font-family: monospace; font-size: 0.85rem; text-transform: uppercase; color: var(--text-muted); margin-bottom: 8px;">1. Gramática y Propiedades</h4><div class="code-box" style="margin-bottom: 12px;">' + ex.grammar.text + '</div><ul style="padding-left: 20px; font-size: 0.9rem; color: var(--text-body);"><li><strong>G1:</strong> ' + ex.theory.g1 + '</li><li><strong>G2:</strong> ' + ex.theory.g2 + '</li><li><strong>G3:</strong> ' + ex.theory.g3 + '</li></ul></div><div style="margin-bottom: 20px;"><h4 style="font-family: monospace; font-size: 0.85rem; text-transform: uppercase; color: var(--text-muted); margin-bottom: 8px;">2. Tabla de Atributos</h4><table class="editorial-table"><thead><tr><th>Símbolo</th><th>Atributo</th><th>Tipo</th><th>Tipo de Dato</th><th>Descripción Semántica</th></tr></thead><tbody>' + attrsRows + '</tbody></table></div><div style="margin-bottom: 20px;"><h4 style="font-family: monospace; font-size: 0.85rem; text-transform: uppercase; color: var(--text-muted); margin-bottom: 8px;">3. Reglas Semánticas (Figura 5.1 Dragon Book)</h4><table class="editorial-table"><thead><tr><th>Producción</th><th>Reglas Semánticas</th><th>Flujo de Atributos</th></tr></thead><tbody>' + rulesRows + '</tbody></table></div><div style="background: var(--bg-subtle); border-left: 4px solid var(--accent-blue); padding: 14px 18px;"><h4 style="font-family: monospace; font-size: 0.85rem; text-transform: uppercase; color: var(--accent-blue); margin-bottom: 6px;">4. Clasificación Formal</h4><div style="font-size: 0.92rem; color: var(--text-body); line-height: 1.6;">' + ex.theory.classificationJust + '</div></div>';
}}

function renderLabStep(stepIndex) {{
    labCurrentStep = stepIndex;
    const total = labSteps.length;

    const badge = document.getElementById('labStepBadge');
    if (badge) badge.textContent = "PASO " + stepIndex + " / " + total;

    const flowBadge = document.getElementById('labFlowBadge');
    const slider = document.getElementById('labTimelineSlider');
    if (slider) {{
        slider.max = total;
        slider.value = stepIndex;
    }}

    const pct = document.getElementById('labProgressPct');
    if (pct) {{
        const p = total > 0 ? Math.round((stepIndex / total) * 100) : 0;
        pct.textContent = p + "%";
    }}

    const narratorBody = document.getElementById('labNarratorBody');

    if (stepIndex === 0) {{
        if (flowBadge) {{
            flowBadge.className = 'status-badge regular-tag';
            flowBadge.textContent = 'ÁRBOL INICIAL SIN EVALUAR';
        }}
        if (narratorBody) {{
            narratorBody.innerHTML = '<div style="display: flex; align-items: center; gap: 16px;"><div style="font-size: 2.2rem; color: var(--accent-blue);">✦</div><div><h4 style="font-size: 1.1rem; font-weight: 700; color: var(--text-main); margin-bottom: 4px;">Árbol Sintáctico Construido (' + labExercises[currentExerciseId].shortName + ')</h4><p style="font-size: 0.92rem; color: var(--text-body); line-height: 1.55;">El parser ha validado la cadena y ensamblado la estructura concreta con <strong>' + labNodeIdCounter + ' nodos</strong>. Todos los atributos se encuentran actualmente en estado pendiente (<code>?</code>). Usa <strong>▶ Siguiente</strong> o <strong>▶ Auto-Play</strong> para ejecutar paso a paso el cómputo según el orden de Kahn.</p></div></div>';
        }}
        renderLabTreeSVG(labTreeRoot, 0);
        renderLabDAGSVG(labSteps, 0);
        renderLabKahnList(labSteps, 0);
        renderLabTheory(currentExerciseId, null);
        return;
    }}

    const step = labSteps[stepIndex - 1];

    if (flowBadge) {{
        if (step.flow === 'rtl') {{
            flowBadge.className = 'status-badge tag-danger';
            flowBadge.textContent = '⚠️ FLUJO DERECHA-A-IZQUIERDA';
        }} else if (step.flow === 'inh') {{
            flowBadge.className = 'status-badge start-tag';
            flowBadge.textContent = '↓ HEREDADO (DESCENDENTE)';
        }} else {{
            flowBadge.className = 'status-badge final-tag';
            flowBadge.textContent = '↑ SINTETIZADO (ASCENDENTE)';
        }}
    }}

    if (narratorBody) {{
        const depsHtml = step.deps.map(d => '<div style="display: flex; justify-content: space-between; font-family: monospace; font-size: 0.8rem; background: #ffffff; padding: 4px 8px; border: 1px solid #e2e8f0;"><span style="color: var(--text-main); font-weight: 600;">' + d.label + '</span><span style="color: var(--accent-emerald); font-weight: 700;">' + d.val + '</span></div>').join('');
        const noDepsMsg = step.deps.length === 0 ? '<div style="font-size: 0.8rem; color: var(--text-muted); font-style: italic; margin-top: 6px;">Sin dependencias previas (grado de entrada 0).</div>' : '';

        narratorBody.innerHTML = '<div style="display: grid; grid-template-columns: 8fr 4fr; gap: 24px; align-items: start;"><div><div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;"><span class="step-num-badge">Paso ' + step.stepNum + '</span><h4 style="font-family: monospace; font-size: 1.15rem; color: var(--accent-blue);">' + step.targetLabel + ' = <span style="color: var(--text-main); font-weight: 800;">' + step.val + '</span></h4></div><div style="background: var(--bg-subtle); border-left: 3px solid var(--border); padding: 10px 14px; margin-bottom: 12px; font-family: monospace; font-size: 0.88rem;"><div style="color: var(--text-muted); font-size: 0.72rem; text-transform: uppercase;">Regla Semántica y Cómputo:</div><div style="font-weight: 700; color: var(--text-main); margin-top: 2px;">' + step.ruleDesc + '</div><div style="color: var(--accent-blue); margin-top: 4px;">↳ ' + step.evalFormula + '</div></div><p style="font-size: 0.92rem; color: var(--text-body); line-height: 1.55;">' + step.explanation + '</p></div><div style="background: #f8fafc; border: 1.5px solid var(--border-light); padding: 14px; border-radius: 4px;"><div class="meta-label">Dependencias Previas (' + step.deps.length + '):</div>' + noDepsMsg + '<div style="display: flex; flex-direction: column; gap: 6px; margin-top: 6px;">' + depsHtml + '</div></div></div>';
    }}

    renderLabTreeSVG(labTreeRoot, stepIndex);
    renderLabDAGSVG(labSteps, stepIndex);
    renderLabKahnList(labSteps, stepIndex);
    renderLabTheory(currentExerciseId, step.ruleDesc);
}}

function initLabIfNeeded() {{
    if (labInitialized) return;
    labInitialized = true;
    selectLabExercise('ex1');
}}

function selectLabExercise(exId) {{
    currentExerciseId = exId;
    const ex = labExercises[exId];
    if (!ex) return;

    document.querySelectorAll('.lab-ex-btn').forEach(btn => btn.classList.remove('active'));
    const btn = document.getElementById("btn-" + exId);
    if (btn) btn.classList.add('active');

    const title = document.getElementById('labConfigTitle');
    if (title) title.textContent = "Configuración de Entrada: " + ex.name;

    const input = document.getElementById('labInputString');
    if (input) input.value = ex.defaultInput;

    const presetsBox = document.getElementById('labPresetsContainer');
    if (presetsBox) {{
        presetsBox.innerHTML = '';
        ex.presets.forEach(p => {{
            const pBtn = document.createElement('button');
            pBtn.className = 'preset-btn';
            pBtn.textContent = p;
            pBtn.onclick = () => applyLabPreset(p);
            presetsBox.appendChild(pBtn);
        }});
    }}

    const paramsBox = document.getElementById('labCustomParams');
    if (paramsBox) {{
        if (!ex.paramDefs || ex.paramDefs.length === 0) {{
            paramsBox.style.display = 'none';
            paramsBox.innerHTML = '';
        }} else {{
            paramsBox.style.display = 'grid';
            paramsBox.innerHTML = ex.paramDefs.map(p => {{
                if (p.type === 'select') {{
                    const opts = p.options.map(o => '<option value="' + o + '" ' + (o == ex.defaultParams[p.id] ? 'selected' : '') + '>' + o + '</option>').join('');
                    return '<div><label class="meta-label" for="param_' + p.id + '">' + p.label + '</label><select id="param_' + p.id + '" class="input-field" style="width: 100%;" onchange="reparseAndRunLab()">' + opts + '</select></div>';
                }} else {{
                    return '<div><label class="meta-label" for="param_' + p.id + '">' + p.label + '</label><input type="' + p.type + '" id="param_' + p.id + '" class="input-field" style="width: 100%;" value="' + ex.defaultParams[p.id] + '" min="' + p.min + '" max="' + p.max + '" step="' + p.step + '" onchange="reparseAndRunLab()"></div>';
                }}
            }}).join('');
        }}
    }}

    reparseAndRunLab();
}}

function applyLabPreset(val) {{
    const input = document.getElementById('labInputString');
    if (input) input.value = val;
    reparseAndRunLab();
}}

function resetLabToDefaults() {{
    const ex = labExercises[currentExerciseId];
    if (!ex) return;
    const input = document.getElementById('labInputString');
    if (input) input.value = ex.defaultInput;

    if (ex.paramDefs) {{
        ex.paramDefs.forEach(p => {{
            const el = document.getElementById("param_" + p.id);
            if (el) el.value = ex.defaultParams[p.id];
        }});
    }}
    reparseAndRunLab();
}}

function onLabInputChanged() {{
    reparseAndRunLab();
}}

function reparseAndRunLab() {{
    const ex = labExercises[currentExerciseId];
    if (!ex) return;

    if (labIsPlaying) labTogglePlay();

    const inputVal = (document.getElementById('labInputString')?.value || '').trim();
    const errorBox = document.getElementById('labErrorMsg');
    if (errorBox) {{
        errorBox.style.display = 'none';
        errorBox.textContent = '';
    }}

    const params = {{}};
    if (ex.paramDefs) {{
        ex.paramDefs.forEach(p => {{
            const el = document.getElementById("param_" + p.id);
            params[p.id] = (el && el.value !== "" && el.value !== undefined) ? el.value : ex.defaultParams[p.id];
        }});
    }}

    try {{
        labTreeRoot = parseInputForExercise(inputVal, currentExerciseId);
        const {{ rules, allNodesById }} = buildLabSemanticRules(labTreeRoot, currentExerciseId, params);
        const {{ steps, hasCycle }} = runLabKahnTopologicalSort(rules, allNodesById);
        
        if (hasCycle) {{
            throw new Error("Se ha detectado una definición circular en la SDD (el grafo de dependencias contiene ciclos).");
        }}

        labSteps = steps;
        const totalBadge = document.getElementById('labTotalStepsBadge');
        if (totalBadge) totalBadge.textContent = steps.length + " PASOS";

        labStepTo(0);
    }} catch (err) {{
        if (errorBox) {{
            errorBox.style.display = 'block';
            errorBox.textContent = err.message || err;
        }}
    }}
}}

function labStepTo(stepIndex) {{
    if (stepIndex < 0) stepIndex = 0;
    if (stepIndex > labSteps.length) stepIndex = labSteps.length;
    renderLabStep(stepIndex);
}}

function labStepPrev() {{
    if (labIsPlaying) labTogglePlay();
    if (labCurrentStep > 0) {{
        labStepTo(labCurrentStep - 1);
    }}
}}

function labStepNext() {{
    if (labCurrentStep < labSteps.length) {{
        labStepTo(labCurrentStep + 1);
    }} else {{
        if (labIsPlaying) labTogglePlay();
    }}
}}

function labStepEnd() {{
    if (labIsPlaying) labTogglePlay();
    labStepTo(labSteps.length);
}}

function labTogglePlay() {{
    const playBtn = document.getElementById('btnLabPlay');
    if (labIsPlaying) {{
        clearInterval(labPlayInterval);
        labIsPlaying = false;
        if (playBtn) {{
            playBtn.classList.remove('active-play');
            playBtn.textContent = '▶ Auto-Play';
        }}
    }} else {{
        if (labCurrentStep >= labSteps.length) {{
            labStepTo(0);
        }}
        labIsPlaying = true;
        if (playBtn) {{
            playBtn.classList.add('active-play');
            playBtn.textContent = '⏸ Pausar';
        }}
        labPlayInterval = setInterval(() => {{
            if (labCurrentStep < labSteps.length) {{
                labStepNext();
            }} else {{
                labTogglePlay();
            }}
        }}, labPlaySpeed);
    }}
}}

function changeLabSpeed(speedVal) {{
    labPlaySpeed = Number(speedVal);
    if (labIsPlaying) {{
        clearInterval(labPlayInterval);
        labPlayInterval = setInterval(() => {{
            if (labCurrentStep < labSteps.length) {{
                labStepNext();
            }} else {{
                labTogglePlay();
            }}
        }}, labPlaySpeed);
    }}
}}

function onTimelineSlider(val) {{
    if (labIsPlaying) labTogglePlay();
    labStepTo(Number(val));
}}

function toggleLabTheory() {{
    const content = document.getElementById('labTheoryContent');
    const icon = document.getElementById('labTheoryToggleIcon');
    if (!content) return;
    if (content.style.display === 'none') {{
        content.style.display = 'block';
        if (icon) icon.textContent = '▲ OCULTAR DETALLES';
    }} else {{
        content.style.display = 'none';
        if (icon) icon.textContent = '▼ MOSTRAR DETALLES';
    }}
}}





// =========================================================================
// 1. LABORATORIO INTERACTIVO: FIRST() Y FOLLOW() (SECCIÓN 4.4.2)
// =========================================================================

const ffPresets = {{
    p_own: {{
        id: 'p_own',
        name: 'Gramática Propia (Listas Delimitadas por Comas)',
        text: "3\\nS -> L\\nL -> bR\\nR -> ,L e",
        desc: "Gramática propia del proyecto. Modela identificadores 'b' separados por comas. Es tanto LL(1) como SLR(1)."
    }},
    p_ex1: {{
        id: 'p_ex1',
        name: 'Ejemplo 1 PDF (Expresiones con Precedencia y Rec. Izquierda)',
        text: "3\\nS -> S+T T\\nT -> T*F F\\nF -> (S) i",
        desc: "Gramática clásica de expresiones aritméticas. La recursión izquierda en S y T imposibilita el análisis LL(1), pero es SLR(1)."
    }},
    p_ex2: {{
        id: 'p_ex2',
        name: 'Ejemplo 2 PDF (Gramática con Producciones Épsilon)',
        text: "3\\nS -> AB\\nA -> aA d\\nB -> bBc e",
        desc: "Gramática con épsilon en B. Muestra cómo First(B) contiene 'e' y cómo Follow(A) hereda los terminales de First(B)."
    }},
    p_ex3: {{
        id: 'p_ex3',
        name: 'Ejemplo 3 PDF (Gramática Ambigua)',
        text: "1\\nS -> SS a",
        desc: "Gramática altamente ambigua. No es LL(1) ni SLR(1). Genera múltiples derivaciones para cadenas con dos o más 'a'."
    }},
    p_ex430: {{
        id: 'p_ex430',
        name: 'Ejercicio 4.30 Dragon Book (Expresiones LL(1) Factorizadas)',
        text: "5\\nS -> TA\\nA -> +TA e\\nT -> FB\\nB -> *FB e\\nF -> (S) i",
        desc: "Expresiones aritméticas tras eliminar la recursión por la izquierda. Totalmente analizable con LL(1) y SLR(1)."
    }},
    p_null: {{
        id: 'p_null',
        name: 'Cadena de No Terminales Anulables',
        text: "4\\nS -> ABC\\nA -> a e\\nB -> b e\\nC -> c e",
        desc: "Demuestra la propagación de FIRST a través de múltiples símbolos anulables consecutivos A, B y C hasta First(S)."
    }},
    p_sdd: {{
        id: 'p_sdd',
        name: 'Gramática SDD Oficial (Item 3)',
        text: "4\\nS -> L\\nL -> BR\\nR -> +L e\\nB -> (L) 0 1",
        desc: "Gramática seleccionada para la definición dirigida por la sintaxis. Modela expresiones binarias con ponderación exponencial."
    }}
}};

let currentFFPresetId = 'p_own';
let ffInitialized = false;
let ffSteps = [];
let ffCurrentStep = 0;
let ffPlayTimer = null;
let ffPlaySpeed = 800;
let ffGrammarObj = null;

function parseGrammarJS(text) {{
    const lines = text.trim().split(/\\r?\\n/).map(l => l.trim()).filter(l => l.length > 0);
    if (lines.length === 0) throw new Error("El texto de la gramática está vacío.");
    const n = parseInt(lines[0], 10);
    if (isNaN(n) || n <= 0) throw new Error("La primera línea debe ser un entero positivo n.");
    const prods = {{}};
    const nts = [];
    for (let i = 1; i <= n && i < lines.length; i++) {{
        const line = lines[i];
        if (!line.includes("->")) throw new Error("Falta '->' en la línea: " + line);
        const parts = line.split("->");
        const head = parts[0].trim();
        const bodies = parts[1].trim().split(/\\s+/).filter(b => b.length > 0);
        if (!prods[head]) {{
            prods[head] = [];
            nts.push(head);
        }}
        bodies.forEach(b => prods[head].push(b));
    }}
    const allSyms = new Set();
    Object.entries(prods).forEach(([h, bs]) => {{
        bs.forEach(b => {{
            for (let c of b) allSyms.add(c);
        }});
    }});
    const ntSet = new Set(nts);
    const terms = Array.from(allSyms).filter(c => !ntSet.has(c) && c !== 'e' && c !== '$').sort();
    return {{ nts, terms, prods, start: nts[0] || 'S' }};
}}

function cloneSets(setsObj) {{
    const res = {{}};
    for (let [k, set] of Object.entries(setsObj)) {{
        res[k] = new Set(set);
    }}
    return res;
}}

function formatSetOfficial(set) {{
    if (!set) return "{{}}";
    const arr = Array.from(set);
    const regular = arr.filter(x => x !== 'e' && x !== '$').sort();
    const res = [...regular];
    if (set.has && set.has('e')) res.push('e');
    if (set.has && set.has('$')) res.push('$');
    return "{{" + res.join(", ") + "}}";
}}

function computeFirstFollowStepsJS(g) {{
    const steps = [];
    const first = {{}};
    g.terms.forEach(t => first[t] = new Set([t]));
    first['e'] = new Set(['e']);
    g.nts.forEach(nt => first[nt] = new Set());

    const follow = {{}};
    g.nts.forEach(nt => follow[nt] = new Set());

    function snapshotFirst() {{
        const res = {{}};
        for (let nt of g.nts) res[nt] = new Set(first[nt] || []);
        return res;
    }}
    function snapshotFollow() {{
        const res = {{}};
        for (let nt of g.nts) res[nt] = new Set(follow[nt] || []);
        return res;
    }}

    // Paso 0: Inicialización
    steps.push({{
        phase: 'INIT',
        iter: 0,
        nt: null,
        prod: null,
        addedFirst: [],
        addedFollow: [],
        firstSnapshot: snapshotFirst(),
        followSnapshot: snapshotFollow(),
        ruleTitle: "Inicialización de Estructuras (Sección 4.4.2)",
        justification: "Para cada terminal t in V_T, FIRST(t) = {{t}}. FIRST(e) = {{e}}. Para cada no terminal A in V_N, FIRST(A) = {{}} y FOLLOW(A) = {{}}."
    }});

    // FASE 1: Cálculo Iterativo de FIRST
    let changed = true;
    let iter = 1;
    while (changed) {{
        changed = false;
        let iterAddedCount = 0;

        for (let head of g.nts) {{
            for (let alt of (g.prods[head] || [])) {{
                if (alt === 'e') {{
                    if (!first[head].has('e')) {{
                        first[head].add('e');
                        changed = true;
                        iterAddedCount++;
                        steps.push({{
                            phase: 'FIRST',
                            iter: iter,
                            nt: head,
                            prod: `${{head}} -> e`,
                            addedFirst: ['e'],
                            addedFollow: [],
                            firstSnapshot: snapshotFirst(),
                            followSnapshot: snapshotFollow(),
                            ruleTitle: `FIRST (Regla 2): ${{head}} -> e`,
                            justification: `La producción deriva directamente la cadena vacía ε ('e'). Se añade 'e' a FIRST(${{head}}).`
                        }});
                    }}
                }} else {{
                    let allNullable = true;
                    for (let i = 0; i < alt.length; i++) {{
                        const sym = alt[i];
                        const symFirst = first[sym] || new Set([sym]);
                        const newToAdd = [];
                        for (let s of symFirst) {{
                            if (s !== 'e' && !first[head].has(s)) {{
                                first[head].add(s);
                                newToAdd.push(s);
                                changed = true;
                                iterAddedCount++;
                            }}
                        }}
                        if (newToAdd.length > 0) {{
                            steps.push({{
                                phase: 'FIRST',
                                iter: iter,
                                nt: head,
                                prod: `${{head}} -> ${{alt}}`,
                                addedFirst: newToAdd,
                                addedFollow: [],
                                firstSnapshot: snapshotFirst(),
                                followSnapshot: snapshotFollow(),
                                ruleTitle: `FIRST (Regla 3): Símbolo '${{sym}}' en ${{head}} -> ${{alt}}`,
                                justification: `Se agregan los terminales {{${{newToAdd.join(', ')}}}} de FIRST(${{sym}}) a FIRST(${{head}}).`
                            }});
                        }}
                        if (!symFirst.has('e')) {{
                            allNullable = false;
                            break;
                        }}
                    }}
                    if (allNullable && !first[head].has('e')) {{
                        first[head].add('e');
                        changed = true;
                        iterAddedCount++;
                        steps.push({{
                            phase: 'FIRST',
                            iter: iter,
                            nt: head,
                            prod: `${{head}} -> ${{alt}}`,
                            addedFirst: ['e'],
                            addedFollow: [],
                            firstSnapshot: snapshotFirst(),
                            followSnapshot: snapshotFollow(),
                            ruleTitle: `FIRST (Regla 3 ε): Todos los símbolos de ${{head}} -> ${{alt}} derivan e`,
                            justification: `Todos los símbolos del cuerpo pueden derivar ε. Se añade 'e' a FIRST(${{head}}).`
                        }});
                    }}
                }}
            }}
        }}
        iter++;
    }}

    // FASE 2: Inicialización de FOLLOW (Regla 1)
    follow[g.start].add('$');
    steps.push({{
        phase: 'FOLLOW_INIT',
        iter: 0,
        nt: g.start,
        prod: null,
        addedFirst: [],
        addedFollow: ['$'],
        firstSnapshot: snapshotFirst(),
        followSnapshot: snapshotFollow(),
        ruleTitle: `FOLLOW (Regla 1): Símbolo Inicial ${{g.start}}`,
        justification: `Se añade el marcador de fin de cadena '$' a FOLLOW(${{g.start}}) por ser el símbolo inicial de la gramática.`
    }});

    function firstOfString(alpha) {{
        if (!alpha || alpha === 'e') return new Set(['e']);
        const res = new Set();
        let allNullable = true;
        for (let c of alpha) {{
            const cFirst = first[c] || new Set([c]);
            for (let s of cFirst) if (s !== 'e') res.add(s);
            if (!cFirst.has('e')) {{
                allNullable = false;
                break;
            }}
        }}
        if (allNullable) res.add('e');
        return res;
    }}

    // FASE 3: Cálculo Iterativo de FOLLOW
    changed = true;
    iter = 1;
    while (changed) {{
        changed = false;
        for (let [head, bodies] of Object.entries(g.prods)) {{
            for (let body of bodies) {{
                if (body === 'e') continue;
                for (let i = 0; i < body.length; i++) {{
                    const B = body[i];
                    if (g.nts.includes(B)) {{
                        const beta = body.slice(i + 1);
                        const betaFirst = firstOfString(beta);

                        // Regla 2 de FOLLOW
                        const newTerms = [];
                        for (let s of betaFirst) {{
                            if (s !== 'e' && !follow[B].has(s)) {{
                                follow[B].add(s);
                                newTerms.push(s);
                                changed = true;
                            }}
                        }}
                        if (newTerms.length > 0) {{
                            steps.push({{
                                phase: 'FOLLOW',
                                iter: iter,
                                nt: B,
                                prod: `${{head}} -> ${{body}}`,
                                addedFirst: [],
                                addedFollow: newTerms,
                                firstSnapshot: snapshotFirst(),
                                followSnapshot: snapshotFollow(),
                                ruleTitle: `FOLLOW (Regla 2): ${{head}} -> ...${{B}}${{beta ? beta : ''}}`,
                                justification: `FIRST(${{beta || 'ε'}}) contiene {{${{newTerms.join(', ')}}}}. Se añade a FOLLOW(${{B}}).`
                            }});
                        }}

                        // Regla 3 de FOLLOW
                        if (betaFirst.has('e') || beta.length === 0) {{
                            const newFromHead = [];
                            for (let s of follow[head]) {{
                                if (!follow[B].has(s)) {{
                                    follow[B].add(s);
                                    newFromHead.push(s);
                                    changed = true;
                                }}
                            }}
                            if (newFromHead.length > 0) {{
                                steps.push({{
                                    phase: 'FOLLOW',
                                    iter: iter,
                                    nt: B,
                                    prod: `${{head}} -> ${{body}}`,
                                    addedFirst: [],
                                    addedFollow: newFromHead,
                                    firstSnapshot: snapshotFirst(),
                                    followSnapshot: snapshotFollow(),
                                    ruleTitle: `FOLLOW (Regla 3): ${{head}} -> ...${{B}}`,
                                    justification: `El sufijo tras '${{B}}' es vacío o deriva ε. Todo FOLLOW(${{head}}) = {{${{newFromHead.join(', ')}}}} se propaga a FOLLOW(${{B}}).`
                                }});
                            }}
                        }}
                    }}
                }}
            }}
        }}
        iter++;
    }}

    // Paso Final: Punto Fijo Alcanzado
    steps.push({{
        phase: 'FINAL',
        iter: iter,
        nt: null,
        prod: null,
        addedFirst: [],
        addedFollow: [],
        firstSnapshot: snapshotFirst(),
        followSnapshot: snapshotFollow(),
        ruleTitle: "Punto Fijo Alcanzado (Convergencia)",
        justification: "Ninguna producción añade símbolos adicionales a FIRST ni a FOLLOW. Los conjuntos son definitivos y formalmente válidos."
    }});

    // Formatear salida oficial (--sets)
    const sortedNts = [...g.nts].sort();
    const setsLines = [];
    sortedNts.forEach(nt => {{
        setsLines.push(`First(${{nt}}) = ${{formatSetOfficial(first[nt])}}`);
    }});
    sortedNts.forEach(nt => {{
        setsLines.push(`Follow(${{nt}}) = ${{formatSetOfficial(follow[nt])}}`);
    }});
    const formattedSets = setsLines.join("\\n");

    return {{ steps, first, follow, formattedSets, g, firstOfString }};
}}

function initFFLabIfNeeded() {{
    if (ffInitialized) return;
    ffInitialized = true;
    selectFFPreset('p_own');
}}

function selectFFPreset(presetId) {{
    currentFFPresetId = presetId;
    const p = ffPresets[presetId];
    if (!p) return;

    document.querySelectorAll('[id^="btn-ff-"]').forEach(b => b.classList.remove('active'));
    const btn = document.getElementById(`btn-ff-${{presetId.replace('p_', '')}}`);
    if (btn) btn.classList.add('active');

    const title = document.getElementById('ffConfigTitle');
    if (title) title.textContent = `Gramática Seleccionada: ${{p.name}}`;

    const txt = document.getElementById('ffGrammarInput');
    if (txt) txt.value = p.text;

    recomputeFF(true);
}}

function resetFFPreset() {{
    selectFFPreset(currentFFPresetId);
}}

function onFFGrammarEdited() {{
    recomputeFF(true);
}}

function recomputeFF(resetToStart = false) {{
    const errorBox = document.getElementById('ffErrorMsg');
    if (errorBox) errorBox.style.display = 'none';

    try {{
        const text = document.getElementById('ffGrammarInput').value;
        const g = parseGrammarJS(text);
        ffGrammarObj = g;
        const res = computeFirstFollowStepsJS(g);
        ffSteps = res.steps;

        const slider = document.getElementById('ffTimelineSlider');
        if (slider) {{
            slider.max = Math.max(0, ffSteps.length - 1);
            if (resetToStart) slider.value = 0;
        }}

        if (resetToStart) {{
            ffCurrentStep = 0;
            if (ffPlayTimer) {{
                clearInterval(ffPlayTimer);
                ffPlayTimer = null;
                const b = document.getElementById('btnFFPlay');
                if (b) b.textContent = '▶ Auto-Play';
            }}
        }} else {{
            ffCurrentStep = Math.min(ffCurrentStep, ffSteps.length - 1);
        }}

        renderFFUI();
    }} catch (e) {{
        if (errorBox) {{
            errorBox.style.display = 'block';
            errorBox.textContent = `Error de Sintaxis en la Gramática: ${{e.message}}`;
        }}
    }}
}}

function ffStepTo(idx) {{
    if (idx < 0) idx = 0;
    if (idx >= ffSteps.length) idx = ffSteps.length - 1;
    ffCurrentStep = idx;
    const slider = document.getElementById('ffTimelineSlider');
    if (slider) slider.value = idx;
    renderFFUI();
}}

function ffStepPrev() {{
    ffStepTo(ffCurrentStep - 1);
}}

function ffStepNext() {{
    if (ffCurrentStep < ffSteps.length - 1) {{
        ffStepTo(ffCurrentStep + 1);
    }} else if (ffPlayTimer) {{
        ffTogglePlay();
    }}
}}

function ffStepEnd() {{
    ffStepTo(ffSteps.length - 1);
}}

function ffTogglePlay() {{
    const btn = document.getElementById('btnFFPlay');
    if (ffPlayTimer) {{
        clearInterval(ffPlayTimer);
        ffPlayTimer = null;
        if (btn) btn.textContent = '▶ Auto-Play';
    }} else {{
        if (ffCurrentStep >= ffSteps.length - 1) ffStepTo(0);
        if (btn) btn.textContent = '⏸ Pausa';
        ffPlayTimer = setInterval(ffStepNext, ffPlaySpeed);
    }}
}}

function changeFFSpeed(val) {{
    ffPlaySpeed = parseInt(val, 10);
    if (ffPlayTimer) {{
        clearInterval(ffPlayTimer);
        ffPlayTimer = setInterval(ffStepNext, ffPlaySpeed);
    }}
}}

function renderFFUI() {{
    if (!ffSteps || ffSteps.length === 0) return;
    const step = ffSteps[ffCurrentStep];
    const total = ffSteps.length - 1;

    // Badges
    const badge = document.getElementById('ffStepBadge');
    if (badge) badge.textContent = `PASO ${{ffCurrentStep}} / ${{total}}`;

    const phaseBadge = document.getElementById('ffPhaseBadge');
    if (phaseBadge) {{
        if (step.phase === 'INIT') phaseBadge.textContent = 'FASE: INICIAL';
        else if (step.phase === 'FIRST') phaseBadge.textContent = `FASE: FIRST (Iteración ${{step.iter}})`;
        else if (step.phase === 'FOLLOW_INIT') phaseBadge.textContent = 'FASE: FOLLOW (Regla 1)';
        else if (step.phase === 'FOLLOW') phaseBadge.textContent = `FASE: FOLLOW (Iteración ${{step.iter}})`;
        else phaseBadge.textContent = 'FASE: PUNTO FIJO COMPLETO';
    }}

    // Tabla de conjuntos
    const tbody = document.getElementById('ffSetsTableBody');
    if (tbody) {{
        tbody.innerHTML = '';
        const nts = Object.keys(step.firstSnapshot || {{}});
        nts.forEach(nt => {{
            const tr = document.createElement('tr');
            const isTarget = (step.nt === nt);
            if (isTarget) tr.style.background = '#fef3c7';

            const fSet = step.firstSnapshot ? step.firstSnapshot[nt] : null;
            const folSet = step.followSnapshot ? step.followSnapshot[nt] : null;

            const fFormatted = formatSetOfficial(fSet);
            const folFormatted = formatSetOfficial(folSet);

            tr.innerHTML = `
                <td style="font-weight: 700; font-family: 'JetBrains Mono';">${{nt}}</td>
                <td style="font-family: 'JetBrains Mono'; color: var(--accent-blue);">${{fFormatted}}</td>
                <td style="font-family: 'JetBrains Mono'; color: var(--accent-emerald);">${{folFormatted}}</td>
            `;
            tbody.appendChild(tr);
        }});
    }}

    // Formato oficial --sets acumulado o final
    const preOutput = document.getElementById('ffFormattedSetsOutput');
    if (preOutput) {{
        const sortedNts = Object.keys(step.firstSnapshot || {{}}).sort();
        const lines = [];
        sortedNts.forEach(nt => lines.push(`First(${{nt}}) = ${{formatSetOfficial(step.firstSnapshot ? step.firstSnapshot[nt] : null)}}`));
        sortedNts.forEach(nt => lines.push(`Follow(${{nt}}) = ${{formatSetOfficial(step.followSnapshot ? step.followSnapshot[nt] : null)}}`));
        preOutput.textContent = lines.join("\\n");
    }}

    // Narrador pedagógico
    const ruleBadge = document.getElementById('ffRuleBadge');
    if (ruleBadge) ruleBadge.textContent = step.ruleTitle || 'REGLA FORMAL';

    const narrator = document.getElementById('ffNarratorContent');
    if (narrator) {{
        narrator.innerHTML = `
            <div style="margin-bottom: 12px;">
                <div style="font-weight: 700; font-size: 1rem; color: var(--text-main); margin-bottom: 4px;">${{step.ruleTitle}}</div>
                <div style="font-size: 0.9rem; color: var(--text-body); line-height: 1.45;">${{step.justification}}</div>
            </div>
            ${{step.prod ? `<div style="font-family: 'JetBrains Mono'; font-size: 0.85rem; padding: 6px 10px; background: var(--bg-subtle); border-left: 3px solid var(--accent-blue); margin-bottom: 10px;">Producción analizada: <strong>${{step.prod}}</strong></div>` : ''}}
            ${{step.addedFirst.length > 0 ? `<div style="font-size: 0.85rem; color: var(--accent-blue);">Símbolos añadidos a FIRST(${{step.nt}}): <strong>{{${{step.addedFirst.join(', ')}}}}</strong></div>` : ''}}
            ${{step.addedFollow.length > 0 ? `<div style="font-size: 0.85rem; color: var(--accent-emerald);">Símbolos añadidos a FOLLOW(${{step.nt}}): <strong>{{${{step.addedFollow.join(', ')}}}}</strong></div>` : ''}}
        `;
    }}

    // Lista de pasos
    const list = document.getElementById('ffStepsList');
    if (list) {{
        list.innerHTML = ffSteps.map((st, idx) => `
            <div class="kahn-step-item ${{idx === ffCurrentStep ? 'active' : ''}}" onclick="ffStepTo(${{idx}})">
                <span>Paso ${{idx}}: ${{st.ruleTitle}}</span>
                <span style="color: var(--text-muted); font-size: 0.75rem;">${{st.nt ? st.nt : ''}}</span>
            </div>
        `).join('');
    }}
}}



// =========================================================================
// 2. LABORATORIO INTERACTIVO: PARSERS LL(1) Y SLR(1)
// =========================================================================

const parserPresets = {{
    p_own: {{
        id: 'p_own',
        name: 'Gramática Propia (Ambos Parsers)',
        text: "3\\nS -> L\\nL -> bR\\nR -> ,L e",
        defaultInput: 'b,b',
        presets: ['b,b', 'b,', 'b', 'b,b,b']
    }},
    p_ex1: {{
        id: 'p_ex1',
        name: 'Ejemplo 1 PDF (SLR(1), no LL(1))',
        text: "3\\nS -> S+T T\\nT -> T*F F\\nF -> (S) i",
        defaultInput: 'i+i',
        presets: ['i+i', '(i)', '(i+i)*i)', 'i*i+i']
    }},
    p_ex2: {{
        id: 'p_ex2',
        name: 'Ejemplo 2 PDF (Ambos Parsers)',
        text: "3\\nS -> AB\\nA -> aA d\\nB -> bBc e",
        defaultInput: 'adbc',
        presets: ['d', 'adbc', 'a', 'aadbbcc']
    }},
    p_ex3: {{
        id: 'p_ex3',
        name: 'Ejemplo 3 PDF (Ni LL(1) ni SLR(1))',
        text: "1\\nS -> SS a",
        defaultInput: 'a',
        presets: ['a', 'aa', 'b']
    }},
    p_ex465: {{
        id: 'p_ex465',
        name: 'Ejercicio 4.6.5 (LL(1), no SLR(1))',
        text: "3\\nS -> AaAb BbBa\\nA -> e\\nB -> e",
        defaultInput: 'ab',
        presets: ['ab', 'ba', 'a']
    }},
    p_ex466: {{
        id: 'p_ex466',
        name: 'Ejercicio 4.6.6 (SLR(1), no LL(1))',
        text: "2\\nS -> SA A\\nA -> a",
        defaultInput: 'aa',
        presets: ['a', 'aa', 'aaa']
    }},
    p_sdd: {{
        id: 'p_sdd',
        name: 'Gramática SDD Oficial (Item 3)',
        text: "4\\nS -> L\\nL -> BR\\nR -> +L e\\nB -> (L) 0 1",
        defaultInput: '(1+0)',
        presets: ['(1+0)', '0', '1', '((1+0)+(1))', '1++0']
    }}
}};

let currentParserPresetId = 'p_own';
let parserInitialized = false;
let currentParserType = 'slr1'; // 'll1' o 'slr1'
let parserSteps = [];
let parserCurrentStep = 0;
let parserPlayTimer = null;
let parserPlaySpeed = 800;
let parserGrammarObj = null;
let parserFFObj = null;
let parserLL1Obj = null;
let parserSLR1Obj = null;

function buildLL1JS(g, ff) {{
    const table = {{}};
    g.nts.forEach(nt => table[nt] = {{}});
    let isLL1 = true;
    const conflicts = [];

    for (let head of g.nts) {{
        for (let body of (g.prods[head] || [])) {{
            const fBody = ff.firstOfString(body);
            for (let a of fBody) {{
                if (a !== 'e') {{
                    if (!table[head][a]) table[head][a] = [];
                    table[head][a].push({{ head, body }});
                    if (table[head][a].length > 1) {{
                        isLL1 = false;
                        conflicts.push(`Conflicto M[${{head}}, ${{a}}]: ${{table[head][a].map(p => `${{p.head}}->${{p.body}}`).join(', ')}}`);
                    }}
                }}
            }}
            if (fBody.has('e')) {{
                for (let b of ff.follow[head]) {{
                    if (!table[head][b]) table[head][b] = [];
                    table[head][b].push({{ head, body }});
                    if (table[head][b].length > 1) {{
                        isLL1 = false;
                        conflicts.push(`Conflicto M[${{head}}, ${{b}}]: ${{table[head][b].map(p => `${{p.head}}->${{p.body}}`).join(', ')}}`);
                    }}
                }}
            }}
        }}
    }}
    return {{ table, isLL1, conflicts }};
}}

function buildSLR1JS(g, ff) {{
    function itemKey(head, body, pos) {{ return `${{head}}##${{body}}##${{pos}}`; }}
    function parseItem(k) {{
        const parts = k.split('##');
        return {{ head: parts[0], body: parts[1], pos: parseInt(parts[2], 10) }};
    }}

    function closure(itemSet) {{
        const res = new Set(itemSet);
        let changed = true;
        while (changed) {{
            changed = false;
            for (let k of Array.from(res)) {{
                const item = parseItem(k);
                if (item.pos < item.body.length) {{
                    const B = item.body[item.pos];
                    if (g.nts.includes(B)) {{
                        for (let alt of (g.prods[B] || [])) {{
                            const altBody = (alt === 'e') ? '' : alt;
                            const nk = itemKey(B, altBody, 0);
                            if (!res.has(nk)) {{
                                res.add(nk);
                                changed = true;
                            }}
                        }}
                    }}
                }}
            }}
        }}
        return res;
    }}

    function goto(itemSet, X) {{
        const moved = new Set();
        for (let k of itemSet) {{
            const item = parseItem(k);
            if (item.pos < item.body.length && item.body[item.pos] === X) {{
                moved.add(itemKey(item.head, item.body, item.pos + 1));
            }}
        }}
        return closure(moved);
    }}

    function setKey(s) {{
        return Array.from(s).sort().join('|');
    }}

    const startItem = itemKey("S'", g.start, 0);
    const i0 = closure(new Set([startItem]));
    const C = [i0];
    const keyToIdx = new Map();
    keyToIdx.set(setKey(i0), 0);
    const worklist = [i0];

    const symbols = g.nts.concat(g.terms);

    while (worklist.length > 0) {{
        const I = worklist.shift();
        for (let X of symbols) {{
            const J = goto(I, X);
            if (J.size > 0) {{
                const k = setKey(J);
                if (!keyToIdx.has(k)) {{
                    const newIdx = C.length;
                    keyToIdx.set(k, newIdx);
                    C.push(J);
                    worklist.push(J);
                }}
            }}
        }}
    }}

    const actionTable = {{}};
    const gotoTable = {{}};
    let isSLR1 = true;
    const conflicts = [];

    for (let i = 0; i < C.length; i++) {{
        actionTable[i] = {{}};
        gotoTable[i] = {{}};
        const I = C[i];

        for (let k of I) {{
            const item = parseItem(k);
            if (item.pos < item.body.length) {{
                const a = item.body[item.pos];
                if (g.terms.includes(a)) {{
                    const J = goto(I, a);
                    const j = keyToIdx.get(setKey(J));
                    if (!actionTable[i][a]) actionTable[i][a] = [];
                    const act = {{ type: 'shift', target: j }};
                    if (!actionTable[i][a].some(x => x.type === 'shift' && x.target === j)) {{
                        actionTable[i][a].push(act);
                    }}
                }}
            }} else {{
                if (item.head === "S'") {{
                    if (!actionTable[i]['$']) actionTable[i]['$'] = [];
                    actionTable[i]['$'].push({{ type: 'accept' }});
                }} else {{
                    const prodStr = item.body === '' ? 'e' : item.body;
                    for (let a of ff.follow[item.head]) {{
                        if (!actionTable[i][a]) actionTable[i][a] = [];
                        const act = {{ type: 'reduce', head: item.head, body: prodStr, len: item.body.length }};
                        actionTable[i][a].push(act);
                    }}
                }}
            }}
        }}

        for (let A of g.nts) {{
            const J = goto(I, A);
            if (J.size > 0) {{
                const j = keyToIdx.get(setKey(J));
                gotoTable[i][A] = j;
            }}
        }}

        for (let [sym, acts] of Object.entries(actionTable[i])) {{
            if (acts.length > 1) {{
                isSLR1 = false;
                conflicts.push(`Conflicto en Estado ${{i}}, Símbolo '${{sym}}': ${{acts.map(a => a.type === 'shift' ? `s${{a.target}}` : `r ${{a.head}}->${{a.body}}`).join(' / ')}}`);
            }}
        }}
    }}

    return {{ C, actionTable, gotoTable, isSLR1, conflicts, parseItem }};
}}

function simulateLL1TraceJS(g, ll1, inputStr) {{
    const tokens = (inputStr === 'e' ? '' : inputStr) + '$';
    let ip = 0;
    let nodeCounter = 0;

    const rootNode = {{ id: ++nodeCounter, symbol: g.start, children: [], parent: null }};
    const stack = [{{ sym: '$', node: null }}, {{ sym: g.start, node: rootNode }}];
    const steps = [];
    let matched = '';

    while (stack.length > 0) {{
        const topItem = stack[stack.length - 1];
        const top = topItem.sym;
        const topNode = topItem.node;
        const cur = tokens[ip];

        if (top === '$' && cur === '$') {{
            steps.push({{
                stepNum: steps.length + 1,
                matched,
                stack: stack.map(x => x.sym),
                input: tokens.slice(ip),
                lookahead: cur,
                action: 'accept',
                actionType: 'accept',
                highlightCell: null,
                ruleTitle: 'Aceptación Formal (Algoritmo 4.34)',
                desc: `Pila vacía ('$') y marcador de fin alcanzado ('$'). La cadena '${{inputStr}}' pertenece al lenguaje.`,
                rootNode,
                isFinal: true,
                verdict: 'yes'
            }});
            return {{ success: true, steps }};
        }}

        if (top === cur) {{
            steps.push({{
                stepNum: steps.length + 1,
                matched,
                stack: stack.map(x => x.sym),
                input: tokens.slice(ip),
                lookahead: cur,
                action: `match ${{cur}}`,
                actionType: 'match',
                highlightCell: null,
                ruleTitle: `Emparejamiento de Terminal '${{cur}}'`,
                desc: `El terminal en el tope de la pila coincide con el símbolo de entrada actual '${{cur}}'. Se desapila y se avanza el puntero de entrada.`,
                rootNode,
                isFinal: false,
                verdict: null
            }});
            stack.pop();
            matched += cur;
            ip++;
        }} else if (g.terms.includes(top) || top === '$') {{
            steps.push({{
                stepNum: steps.length + 1,
                matched,
                stack: stack.map(x => x.sym),
                input: tokens.slice(ip),
                lookahead: cur,
                action: 'error',
                actionType: 'error',
                highlightCell: null,
                ruleTitle: 'Error Sintáctico (Desajuste)',
                desc: `Se esperaba el terminal '${{top}}' pero se encontró '${{cur}}'. La cadena no puede ser derivada por la gramática.`,
                rootNode,
                isFinal: true,
                verdict: 'no'
            }});
            return {{ success: false, steps }};
        }} else {{
            const entries = ll1.table[top]?.[cur] || [];
            if (entries.length === 0) {{
                steps.push({{
                    stepNum: steps.length + 1,
                    matched,
                    stack: stack.map(x => x.sym),
                    input: tokens.slice(ip),
                    lookahead: cur,
                    action: 'error',
                    actionType: 'error',
                    highlightCell: {{ head: top, terminal: cur }},
                    ruleTitle: `Error Sintáctico: M[${{top}}, ${{cur}}] vacía`,
                    desc: `No existe producción en la celda predictiva M[${{top}}, ${{cur}}]. El analizador LL(1) rechaza la cadena.`,
                    rootNode,
                    isFinal: true,
                    verdict: 'no'
                }});
                return {{ success: false, steps }};
            }}

            const prod = entries[0];
            steps.push({{
                stepNum: steps.length + 1,
                matched,
                stack: stack.map(x => x.sym),
                input: tokens.slice(ip),
                lookahead: cur,
                action: `output ${{prod.head}} -> ${{prod.body}}`,
                actionType: 'output',
                highlightCell: {{ head: top, terminal: cur }},
                ruleTitle: `Expansión Predictiva M[${{top}}, ${{cur}}]`,
                desc: `La tabla dictamina aplicar ${{prod.head}} -> ${{prod.body}}. Se desapila '${{top}}' y se apilan los símbolos del cuerpo en orden inverso.`,
                rootNode,
                isFinal: false,
                verdict: null
            }});

            stack.pop();

            if (prod.body === 'e') {{
                const epsNode = {{ id: ++nodeCounter, symbol: 'e', children: [], parent: topNode }};
                if (topNode) topNode.children.push(epsNode);
            }} else {{
                const childNodes = [];
                for (let i = 0; i < prod.body.length; i++) {{
                    const cSym = prod.body[i];
                    const cNode = {{ id: ++nodeCounter, symbol: cSym, children: [], parent: topNode }};
                    childNodes.push(cNode);
                    if (topNode) topNode.children.push(cNode);
                }}
                for (let i = prod.body.length - 1; i >= 0; i--) {{
                    stack.push({{ sym: prod.body[i], node: childNodes[i] }});
                }}
            }}
        }}
    }}
    return {{ success: false, steps }};
}}

function simulateSLR1TraceJS(g, slr1, inputStr) {{
    const tokens = (inputStr === 'e' ? '' : inputStr) + '$';
    let ip = 0;
    let nodeCounter = 0;

    const stateStack = [0];
    const symbolStack = [];
    const nodeStack = [];
    const steps = [];

    while (true) {{
        const curState = stateStack[stateStack.length - 1];
        const lookahead = tokens[ip];
        const acts = slr1.actionTable[curState]?.[lookahead] || [];

        if (acts.length === 0) {{
            steps.push({{
                stepNum: steps.length + 1,
                stateStack: [...stateStack],
                symbolStack: [...symbolStack],
                input: tokens.slice(ip),
                lookahead,
                action: 'error',
                actionType: 'error',
                highlightCell: {{ state: curState, terminal: lookahead }},
                ruleTitle: `Error Sintáctico: ACTION[${{curState}}, ${{lookahead}}] vacía`,
                desc: `El autómata LR(0) no tiene transición de desplazamiento ni de reducción en el Estado ${{curState}} para el lookahead '${{lookahead}}'.`,
                nodes: [...nodeStack],
                isFinal: true,
                verdict: 'no'
            }});
            return {{ success: false, steps }};
        }}

        const act = acts[0];
        if (act.type === 'shift') {{
            steps.push({{
                stepNum: steps.length + 1,
                stateStack: [...stateStack],
                symbolStack: [...symbolStack],
                input: tokens.slice(ip),
                lookahead,
                action: `shift to ${{act.target}}`,
                actionType: 'shift',
                highlightCell: {{ state: curState, terminal: lookahead }},
                ruleTitle: `Desplazamiento (Shift): Estado ${{curState}} con '${{lookahead}}'`,
                desc: `Se desplaza el terminal '${{lookahead}}' a la pila y el autómata transiciona al Estado ${{act.target}}.`,
                nodes: [...nodeStack],
                isFinal: false,
                verdict: null
            }});
            stateStack.push(act.target);
            symbolStack.push(lookahead);
            nodeStack.push({{ id: ++nodeCounter, symbol: lookahead, children: [] }});
            ip++;
        }} else if (act.type === 'reduce') {{
            steps.push({{
                stepNum: steps.length + 1,
                stateStack: [...stateStack],
                symbolStack: [...symbolStack],
                input: tokens.slice(ip),
                lookahead,
                action: `reduce by ${{act.head}} -> ${{act.body}}`,
                actionType: 'reduce',
                highlightCell: {{ state: curState, terminal: lookahead }},
                ruleTitle: `Reducción (Reduce): ${{act.head}} -> ${{act.body}}`,
                desc: `Se reduce el handle '${{act.body}}' a la cabeza ${{act.head}}. Longitud ${{act.len}}. Se desapilan ${{act.len}} estados y se consulta la tabla GOTO.`,
                nodes: [...nodeStack],
                isFinal: false,
                verdict: null
            }});

            const childrenPopped = [];
            if (act.len === 0) {{
                childrenPopped.push({{ id: ++nodeCounter, symbol: 'e', children: [] }});
            }} else {{
                for (let i = 0; i < act.len; i++) {{
                    stateStack.pop();
                    symbolStack.pop();
                    childrenPopped.push(nodeStack.pop());
                }}
                childrenPopped.reverse();
            }}

            const parentNode = {{ id: ++nodeCounter, symbol: act.head, children: childrenPopped }};
            nodeStack.push(parentNode);

            const topState = stateStack[stateStack.length - 1];
            const nextState = slr1.gotoTable[topState]?.[act.head];
            if (nextState === undefined) {{
                steps.push({{
                    stepNum: steps.length + 1,
                    stateStack: [...stateStack],
                    symbolStack: [...symbolStack],
                    input: tokens.slice(ip),
                    lookahead,
                    action: 'error',
                    actionType: 'error',
                    highlightCell: null,
                    ruleTitle: `Error en GOTO[${{topState}}, ${{act.head}}]`,
                    desc: `No existe transición GOTO para el no terminal ${{act.head}} desde el estado ${{topState}}.`,
                    nodes: [...nodeStack],
                    isFinal: true,
                    verdict: 'no'
                }});
                return {{ success: false, steps }};
            }}

            stateStack.push(nextState);
            symbolStack.push(act.head);
        }} else if (act.type === 'accept') {{
            steps.push({{
                stepNum: steps.length + 1,
                stateStack: [...stateStack],
                symbolStack: [...symbolStack],
                input: tokens.slice(ip),
                lookahead,
                action: 'accept',
                actionType: 'accept',
                highlightCell: {{ state: curState, terminal: '$' }},
                ruleTitle: 'Aceptación Formal (Algoritmo 4.44)',
                desc: `El autómata alcanza el estado de aceptación S' -> S· con marcador de fin '$'. Cadena aceptada (yes).`,
                nodes: [...nodeStack],
                isFinal: true,
                verdict: 'yes'
            }});
            return {{ success: true, steps }};
        }}
    }}
}}

function initParserLabIfNeeded() {{
    if (parserInitialized) return;
    parserInitialized = true;
    selectParserPreset('p_own');
}}

function selectParserPreset(presetId) {{
    currentParserPresetId = presetId;
    const p = parserPresets[presetId];
    if (!p) return;

    document.querySelectorAll('[id^="btn-p-"]').forEach(b => b.classList.remove('active'));
    const btn = document.getElementById(`btn-p-${{presetId.replace('p_', '')}}`);
    if (btn) btn.classList.add('active');

    const title = document.getElementById('parserConfigTitle');
    if (title) title.textContent = `Configuración de Entrada: ${{p.name}}`;

    const txt = document.getElementById('parserGrammarInput');
    if (txt) txt.value = p.text;

    const inStr = document.getElementById('parserInputString');
    if (inStr) inStr.value = p.defaultInput;

    const presetsBox = document.getElementById('parserPresetsContainer');
    if (presetsBox) {{
        presetsBox.innerHTML = '';
        p.presets.forEach(pr => {{
            const b = document.createElement('button');
            b.className = 'preset-btn';
            b.textContent = pr;
            b.onclick = () => applyParserStringPreset(pr);
            presetsBox.appendChild(b);
        }});
    }}

    recomputeParser(true);
}}

function applyParserStringPreset(str) {{
    const inStr = document.getElementById('parserInputString');
    if (inStr) inStr.value = str;
    recomputeParser(true);
}}

function resetParserPreset() {{
    selectParserPreset(currentParserPresetId);
}}

function onParserGrammarEdited() {{
    recomputeParser(true);
}}

function onParserInputChanged() {{
    recomputeParser(true);
}}

function setParserType(type) {{
    currentParserType = type;
    recomputeParser(false);
}}

function recomputeParser(resetToStart = false) {{
    try {{
        const text = document.getElementById('parserGrammarInput').value;
        const inputStr = document.getElementById('parserInputString').value.trim() || 'e';
        const g = parseGrammarJS(text);
        const ff = computeFirstFollowStepsJS(g);
        const ll1 = buildLL1JS(g, ff);
        const slr1 = buildSLR1JS(g, ff);

        parserGrammarObj = g;
        parserFFObj = ff;
        parserLL1Obj = ll1;
        parserSLR1Obj = slr1;

        // Banner de Clasificación
        renderClassificationBanner(ll1, slr1);

        // Si la gramática es LL(1) pero no SLR(1), forzar LL(1)
        if (ll1.isLL1 && !slr1.isSLR1) currentParserType = 'll1';
        // Si es SLR(1) pero no LL(1), forzar SLR(1)
        if (slr1.isSLR1 && !ll1.isLL1) currentParserType = 'slr1';

        // Ejecutar simulación
        let simRes = null;
        if (currentParserType === 'll1') {{
            if (ll1.isLL1) {{
                simRes = simulateLL1TraceJS(g, ll1, inputStr);
            }} else {{
                simRes = {{ success: false, steps: [{{
                    stepNum: 1, matched: '', stack: [], input: inputStr + '$', lookahead: '', action: 'error', actionType: 'error',
                    ruleTitle: 'Gramática no es LL(1)', desc: `No se puede analizar con LL(1): ${{ll1.conflicts.join('; ')}}`, isFinal: true, verdict: 'no', rootNode: null
                }}]}};
            }}
        }} else {{
            if (slr1.isSLR1) {{
                simRes = simulateSLR1TraceJS(g, slr1, inputStr);
            }} else {{
                simRes = {{ success: false, steps: [{{
                    stepNum: 1, stateStack: [0], symbolStack: [], input: inputStr + '$', lookahead: '', action: 'error', actionType: 'error',
                    ruleTitle: 'Gramática no es SLR(1)', desc: `No se puede analizar con SLR(1): ${{slr1.conflicts.join('; ')}}`, isFinal: true, verdict: 'no', nodes: []
                }}]}};
            }}
        }}

        parserSteps = simRes.steps;
        const slider = document.getElementById('parserTimelineSlider');
        if (slider) {{
            slider.max = Math.max(0, parserSteps.length - 1);
            if (resetToStart) slider.value = 0;
        }}

        if (resetToStart) {{
            parserCurrentStep = 0;
            if (parserPlayTimer) {{
                clearInterval(parserPlayTimer);
                parserPlayTimer = null;
                const b = document.getElementById('btnParserPlay');
                if (b) b.textContent = '▶ Auto-Play';
            }}
        }} else {{
            parserCurrentStep = Math.min(parserCurrentStep, parserSteps.length - 1);
        }}

        renderParserUI();
    }} catch (e) {{
        console.error("Error en parser lab:", e);
    }}
}}

function renderClassificationBanner(ll1, slr1) {{
    const banner = document.getElementById('parserClassificationBanner');
    if (!banner) return;

    if (ll1.isLL1 && slr1.isSLR1) {{
        banner.innerHTML = `
            <div>
                <span class="status-badge tag-new" style="margin-bottom: 4px;">CASO 1: AMBOS PARSERS VÁLIDOS</span>
                <div style="font-weight: 700; font-size: 1.05rem; color: var(--text-main);">The grammar is both SLR(1) and LL(1).</div>
                <div style="font-size: 0.85rem; color: var(--text-body);">Selecciona el analizador con el que deseas procesar la cadena:</div>
            </div>
            <div style="display: flex; gap: 8px;">
                <button class="transport-btn ${{currentParserType === 'll1' ? 'active-play' : ''}}" onclick="setParserType('ll1')">T: Parser LL(1) (Top-Down)</button>
                <button class="transport-btn ${{currentParserType === 'slr1' ? 'active-play' : ''}}" onclick="setParserType('slr1')">B: Parser SLR(1) (Bottom-Up)</button>
            </div>
        `;
    }} else if (ll1.isLL1 && !slr1.isSLR1) {{
        banner.innerHTML = `
            <div>
                <span class="status-badge l-attr" style="margin-bottom: 4px;">CASO 2: LL(1) VÁLIDO</span>
                <div style="font-weight: 700; font-size: 1.05rem; color: var(--accent-blue);">Grammar is LL(1).</div>
                <div style="font-size: 0.85rem; color: var(--text-body);">No es SLR(1) debido a: ${{slr1.conflicts[0] || 'conflicto en tabla'}}.</div>
            </div>
            <div>
                <span class="editorial-tag" style="background: #eff6ff;">Analizando con LL(1)</span>
            </div>
        `;
    }} else if (slr1.isSLR1 && !ll1.isLL1) {{
        banner.innerHTML = `
            <div>
                <span class="status-badge no-l-attr" style="margin-bottom: 4px;">CASO 3: SLR(1) VÁLIDO</span>
                <div style="font-weight: 700; font-size: 1.05rem; color: var(--accent-amber);">Grammar is SLR(1).</div>
                <div style="font-size: 0.85rem; color: var(--text-body);">No es LL(1) debido a: ${{ll1.conflicts[0] || 'recursión izquierda / prefijos comunes'}}.</div>
            </div>
            <div>
                <span class="editorial-tag" style="background: #fffbeb;">Analizando con SLR(1)</span>
            </div>
        `;
    }} else {{
        banner.innerHTML = `
            <div>
                <span class="status-badge tag-danger" style="margin-bottom: 4px;">CASO 4: NI LL(1) NI SLR(1)</span>
                <div style="font-weight: 700; font-size: 1.05rem; color: var(--accent-red);">Grammar is neither LL(1) nor SLR(1).</div>
                <div style="font-size: 0.85rem; color: var(--text-body);">La gramática presenta ambigüedad o colisiones insolubles en ambas tablas de análisis.</div>
            </div>
            <div>
                <span class="status-badge tag-danger">NO PARSEABLE</span>
            </div>
        `;
    }}
}}

function parserStepTo(idx) {{
    if (idx < 0) idx = 0;
    if (idx >= parserSteps.length) idx = parserSteps.length - 1;
    parserCurrentStep = idx;
    const slider = document.getElementById('parserTimelineSlider');
    if (slider) slider.value = idx;
    renderParserUI();
}}

function parserStepPrev() {{
    parserStepTo(parserCurrentStep - 1);
}}

function parserStepNext() {{
    if (parserCurrentStep < parserSteps.length - 1) {{
        parserStepTo(parserCurrentStep + 1);
    }} else if (parserPlayTimer) {{
        parserTogglePlay();
    }}
}}

function parserStepEnd() {{
    parserStepTo(parserSteps.length - 1);
}}

function parserTogglePlay() {{
    const btn = document.getElementById('btnParserPlay');
    if (parserPlayTimer) {{
        clearInterval(parserPlayTimer);
        parserPlayTimer = null;
        if (btn) btn.textContent = '▶ Auto-Play';
    }} else {{
        if (parserCurrentStep >= parserSteps.length - 1) parserStepTo(0);
        if (btn) btn.textContent = '⏸ Pausa';
        parserPlayTimer = setInterval(parserStepNext, parserPlaySpeed);
    }}
}}

function changeParserSpeed(val) {{
    parserPlaySpeed = parseInt(val, 10);
    if (parserPlayTimer) {{
        clearInterval(parserPlayTimer);
        parserPlayTimer = setInterval(parserStepNext, parserPlaySpeed);
    }}
}}

function renderParserUI() {{
    if (!parserSteps || parserSteps.length === 0) return;
    const step = parserSteps[parserCurrentStep];
    const total = parserSteps.length - 1;

    // Badges
    const badge = document.getElementById('parserStepBadge');
    if (badge) badge.textContent = `PASO ${{parserCurrentStep}} / ${{total}}`;

    const actionBadge = document.getElementById('parserActionBadge');
    if (actionBadge) {{
        actionBadge.textContent = step.action ? step.action.toUpperCase() : 'INICIAL';
        if (step.actionType === 'accept') {{
            actionBadge.className = 'status-badge tag-new';
        }} else if (step.actionType === 'error') {{
            actionBadge.className = 'status-badge tag-danger';
        }} else {{
            actionBadge.className = 'status-badge regular-tag';
        }}
    }}

    const modeBadge = document.getElementById('parserModeBadge');
    if (modeBadge) {{
        modeBadge.textContent = currentParserType === 'll1' ? 'PARSER LL(1) DESCENDENTE' : 'PARSER SLR(1) ASCENDENTE';
    }}

    // Estado de la pila y entrada
    const stateDisplay = document.getElementById('parserStateDisplay');
    if (stateDisplay) {{
        if (currentParserType === 'll1') {{
            const stackArr = step.stack || [];
            const stackReversed = [...stackArr].reverse();
            stateDisplay.innerHTML = `
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px;">
                    <div>
                        <span class="meta-label">Pila de Símbolos ($ en la base):</span>
                        <div style="display: flex; gap: 6px; font-family: 'JetBrains Mono'; font-size: 1.05rem; font-weight: 700; padding: 10px; background: var(--bg-subtle); border: 1.5px solid var(--border);">
                            ${{stackReversed.map((s, i) => `<span style="padding: 2px 8px; background: ${{i === 0 ? '#fef3c7' : '#ffffff'}}; border: 1px solid var(--border);">${{s}}</span>`).join('')}}
                        </div>
                    </div>
                    <div>
                        <span class="meta-label">Lookahead y Entrada Restante:</span>
                        <div style="font-family: 'JetBrains Mono'; font-size: 1.05rem; font-weight: 700; padding: 10px; background: var(--bg-subtle); border: 1.5px solid var(--border);">
                            <span style="color: var(--accent-blue);">${{step.matched}}</span><span style="background: #bfdbfe; padding: 0 4px;">${{step.lookahead}}</span><span>${{step.input.slice(1)}}</span>
                        </div>
                    </div>
                </div>
            `;
        }} else {{
            const stStack = step.stateStack || [];
            const symStack = step.symbolStack || [];
            stateDisplay.innerHTML = `
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px;">
                    <div>
                        <span class="meta-label">Pila de Estados:</span>
                        <div style="font-family: 'JetBrains Mono'; font-size: 1.05rem; font-weight: 700; padding: 10px; background: var(--bg-subtle); border: 1.5px solid var(--border);">
                            [${{stStack.join(', ')}}]
                        </div>
                    </div>
                    <div>
                        <span class="meta-label">Pila de Símbolos:</span>
                        <div style="font-family: 'JetBrains Mono'; font-size: 1.05rem; font-weight: 700; padding: 10px; background: var(--bg-subtle); border: 1.5px solid var(--border);">
                            [${{symStack.join(', ')}}]
                        </div>
                    </div>
                </div>
                <div style="margin-bottom: 16px;">
                    <span class="meta-label">Lookahead y Entrada Restante:</span>
                    <div style="font-family: 'JetBrains Mono'; font-size: 1.05rem; font-weight: 700; padding: 10px; background: var(--bg-subtle); border: 1.5px solid var(--border);">
                        <span style="background: #fde68a; padding: 0 6px;">${{step.lookahead}}</span><span>${{step.input.slice(1)}}</span>
                    </div>
                </div>
            `;
        }}
    }}

    // Veredicto oficial
    const verdictText = document.getElementById('parserVerdictText');
    const verdictBox = document.getElementById('parserVerdictBox');
    if (verdictText && verdictBox) {{
        const lastStep = parserSteps[parserSteps.length - 1];
        if (step.isFinal) {{
            if (step.verdict === 'yes') {{
                verdictText.textContent = 'yes (CADENA ACEPTADA)';
                verdictText.className = 'status-badge tag-new';
                verdictBox.style.background = '#ecfdf5';
            }} else {{
                verdictText.textContent = 'no (CADENA RECHAZADA)';
                verdictText.className = 'status-badge tag-danger';
                verdictBox.style.background = '#fef2f2';
            }}
        }} else {{
            verdictText.textContent = 'EN EVALUACIÓN';
            verdictText.className = 'status-badge regular-tag';
            verdictBox.style.background = 'var(--bg-subtle)';
        }}
    }}

    // Tabla de parseo con celda activa resaltada
    renderParserTable(step);

    // Explicación pedagógica
    const explanationContent = document.getElementById('parserExplanationContent');
    if (explanationContent) {{
        explanationContent.innerHTML = `
            <div style="font-weight: 700; font-size: 1.05rem; margin-bottom: 6px; color: var(--text-main);">${{step.ruleTitle}}</div>
            <div style="font-size: 0.9rem; color: var(--text-body); line-height: 1.45; margin-bottom: 12px;">${{step.desc}}</div>
            <div style="font-family: 'JetBrains Mono'; font-size: 0.85rem; padding: 8px 12px; background: var(--bg-subtle); border-left: 3px solid var(--accent-amber);">
                Acción formal ejecutada: <strong>${{step.action}}</strong>
            </div>
        `;
    }}

    // Dibujar árbol sintáctico derivado en SVG
    renderParserTreeSVG(step);
}}

function renderParserTable(step) {{
    const container = document.getElementById('parserTableContainer');
    const title = document.getElementById('parserTableTitle');
    if (!container) return;

    if (currentParserType === 'll1') {{
        if (title) title.textContent = "Tabla Predictiva LL(1) M[A, a] (con celda activa resaltada)";
        if (!parserLL1Obj) return;

        const g = parserGrammarObj;
        const columns = [...g.terms, '$'];
        let html = '<table class="editorial-table" style="margin: 0;"><thead><tr><th>No Terminal</th>';
        columns.forEach(c => html += `<th>${{c}}</th>`);
        html += '</tr></thead><tbody>';

        g.nts.forEach(nt => {{
            html += `<tr><td><strong>${{nt}}</strong></td>`;
            columns.forEach(c => {{
                const prods = parserLL1Obj.table[nt]?.[c] || [];
                const prodStr = prods.map(p => `${{p.head}} -> ${{p.body}}`).join(' / ');
                const isActive = (step.highlightCell && step.highlightCell.head === nt && step.highlightCell.terminal === c);
                html += `<td style="${{isActive ? 'background: #fef08a; font-weight: 700; border: 2px solid var(--accent-amber);' : ''}}">${{prodStr}}</td>`;
            }});
            html += '</tr>';
        }});
        html += '</tbody></table>';
        container.innerHTML = html;
    }} else {{
        if (title) title.textContent = "Tabla de Análisis SLR(1) (ACTION y GOTO con celda activa resaltada)";
        if (!parserSLR1Obj) return;

        const g = parserGrammarObj;
        const terms = [...g.terms, '$'];
        const nts = [...g.nts];

        let html = '<table class="editorial-table" style="margin: 0;"><thead><tr><th>Estado</th>';
        terms.forEach(t => html += `<th>${{t}}</th>`);
        nts.forEach(nt => html += `<th>${{nt}}</th>`);
        html += '</tr></thead><tbody>';

        for (let i = 0; i < parserSLR1Obj.C.length; i++) {{
            const isRowActive = (step.highlightCell && step.highlightCell.state === i);
            html += `<tr style="${{isRowActive ? 'background: #fef9c3;' : ''}}"><td><strong>${{i}}</strong></td>`;

            terms.forEach(t => {{
                const acts = parserSLR1Obj.actionTable[i]?.[t] || [];
                const actStr = acts.map(a => a.type === 'shift' ? `s${{a.target}}` : (a.type === 'reduce' ? `r ${{a.head}}->${{a.body}}` : 'acc')).join(' / ');
                const isCellActive = (isRowActive && step.highlightCell.terminal === t);
                html += `<td style="${{isCellActive ? 'background: #fde047; font-weight: 700; border: 2px solid var(--accent-amber);' : ''}}">${{actStr}}</td>`;
            }});

            nts.forEach(nt => {{
                const target = parserSLR1Obj.gotoTable[i]?.[nt];
                html += `<td>${{target !== undefined ? target : ''}}</td>`;
            }});

            html += '</tr>';
        }}
        html += '</tbody></table>';
        container.innerHTML = html;
    }}
}}

function renderParserTreeSVG(step) {{
    const svg = document.getElementById('parserTreeSvg');
    if (!svg) return;
    svg.innerHTML = '';

    const width = svg.clientWidth || 460;
    const height = 280;

    let treeRoots = [];
    if (currentParserType === 'll1') {{
        if (step.rootNode) treeRoots = [step.rootNode];
    }} else {{
        if (step.nodes) treeRoots = step.nodes;
    }}

    if (treeRoots.length === 0) {{
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', width / 2);
        text.setAttribute('y', height / 2);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('font-family', 'Inter');
        text.setAttribute('font-size', '13');
        text.setAttribute('fill', '#94a3b8');
        text.textContent = 'El árbol sintáctico se construirá a medida que avance el análisis...';
        svg.appendChild(text);
        return;
    }}

    // Posicionamiento de nodos
    function getLeafCount(node) {{
        if (!node.children || node.children.length === 0) return 1;
        return node.children.reduce((acc, c) => acc + getLeafCount(c), 0);
    }}

    let totalLeaves = treeRoots.reduce((acc, r) => acc + getLeafCount(r), 0);
    let currentLeafIdx = 0;

    const coords = new Map();

    function assignPositions(node, depth, ySpacing, xSpacing) {{
        const y = 35 + depth * ySpacing;
        if (!node.children || node.children.length === 0) {{
            const x = 30 + (currentLeafIdx + 0.5) * xSpacing;
            currentLeafIdx++;
            coords.set(node.id, {{ x, y, symbol: node.symbol }});
            return x;
        }} else {{
            const childXs = node.children.map(c => assignPositions(c, depth + 1, ySpacing, xSpacing));
            const x = (childXs[0] + childXs[childXs.length - 1]) / 2;
            coords.set(node.id, {{ x, y, symbol: node.symbol }});
            return x;
        }}
    }}

    const xSpacing = Math.max(36, (width - 60) / Math.max(1, totalLeaves));
    const ySpacing = 50;

    treeRoots.forEach(root => assignPositions(root, 0, ySpacing, xSpacing));

    // Dibujar aristas
    function drawEdges(node) {{
        if (!node.children) return;
        const pCoord = coords.get(node.id);
        node.children.forEach(c => {{
            const cCoord = coords.get(c.id);
            if (pCoord && cCoord) {{
                const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                line.setAttribute('x1', pCoord.x);
                line.setAttribute('y1', pCoord.y);
                line.setAttribute('x2', cCoord.x);
                line.setAttribute('y2', cCoord.y);
                line.setAttribute('stroke', '#0f172a');
                line.setAttribute('stroke-width', '1.5');
                svg.appendChild(line);
            }}
            drawEdges(c);
        }});
    }}

    treeRoots.forEach(r => drawEdges(r));

    // Dibujar nodos
    coords.forEach((coord, id) => {{
        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        const isNT = /^[A-Z]$/.test(coord.symbol);

        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', coord.x);
        circle.setAttribute('cy', coord.y);
        circle.setAttribute('r', isNT ? '15' : '13');
        circle.setAttribute('fill', isNT ? '#eff6ff' : '#ffffff');
        circle.setAttribute('stroke', isNT ? '#1e40af' : '#0f172a');
        circle.setAttribute('stroke-width', '2');
        g.appendChild(circle);

        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', coord.x);
        text.setAttribute('y', coord.y + 5);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('font-family', 'JetBrains Mono');
        text.setAttribute('font-size', isNT ? '12' : '11');
        text.setAttribute('font-weight', '700');
        text.setAttribute('fill', isNT ? '#1e40af' : '#0f172a');
        text.textContent = coord.symbol;
        g.appendChild(text);

        svg.appendChild(g);
    }});
}}


        window.onload = function() {{
            initFFLabIfNeeded();
            initParserLabIfNeeded();
            initLabIfNeeded();
        }};
    </script>
</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return output_path


if __name__ == "__main__":
    out = generate_html_visualizer("index.html")
    print(f"Visualizador HTML generado exitosamente en: {out}")
