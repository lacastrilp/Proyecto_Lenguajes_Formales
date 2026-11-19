def _format_table(header, rows):
    all_rows = [header] + rows
    widths = [max(len(str(r[i])) for r in all_rows) for i in range(len(header))]
    lines = []
    for k, row in enumerate(all_rows):
        lines.append(" | ".join(str(c).ljust(widths[i]) for i, c in enumerate(row)))
        if k == 0:
            lines.append("-+-".join("-" * w for w in widths))
    return "\n".join(lines)


def format_ll1_table(ll1) -> str:
    columns = sorted(ll1.grammar.terminals) + ["$"]
    rows = []
    for nt in sorted(ll1.grammar.nonterminals):
        row = [nt]
        for a in columns:
            prods = sorted(ll1.table.get((nt, a), set()))
            row.append(" / ".join(f"{h}->{b}" for h, b in prods))
        rows.append(row)
    return "Tabla LL(1):\n" + _format_table(["M"] + columns, rows)


def _item_to_text(item) -> str:
    head, body, pos = item
    return f"{head} -> {body[:pos]}.{body[pos:]}"


def format_lr0_automaton(slr) -> str:
    symbols = slr.grammar.nonterminals + slr.grammar.terminals
    lines = ["Autómata LR(0):"]
    for i, state in enumerate(slr.canonical_collection):
        lines.append(f"Estado {i}:")
        for item in sorted(state):
            lines.append("    " + _item_to_text(item))
        for x in symbols:
            target = slr._goto(state, x)
            if target and target in slr.canonical_collection:
                lines.append(f"    --{x}--> {slr.canonical_collection.index(target)}")
    return "\n".join(lines)


def format_slr_tables(slr) -> str:
    terminals = sorted(slr.grammar.terminals) + ["$"]
    nonterminals = sorted(slr.grammar.nonterminals)
    rows = []
    for i in range(len(slr.canonical_collection)):
        row = [i]
        for a in terminals:
            cells = []
            for act in sorted(slr.action_table.get((i, a), set())):
                if act[0] == "shift":
                    cells.append(f"s{act[1]}")
                elif act[0] == "reduce":
                    cells.append(f"r {act[1]}->{act[2]}")
                else:
                    cells.append("acc")
            row.append(" / ".join(cells))
        for nt in nonterminals:
            row.append(slr.goto_table.get((i, nt), ""))
        rows.append(row)
    header = ["Estado"] + terminals + nonterminals
    return "Tablas SLR(1) (ACTION | GOTO):\n" + _format_table(header, rows)



def format_trace_ll1(rows) -> str:
    return _format_table(["MATCHED", "STACK", "INPUT", "ACTION"], rows)


def format_trace_slr(rows) -> str:
    return _format_table(["LINE", "STACK", "SYMBOLS", "INPUT", "ACTION"], rows)