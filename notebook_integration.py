"""
Math Expression Widget — Jupyter Notebook Integration
======================================================

Run Cell 1 (setup) once per kernel session, then Cell 2 (display) to show
the widget. Action buttons (Expand, Factor, Solve, Evaluate, Plot) send
requests to Python, compute results with SymPy, and return them to the widget.
The "Save to Cell" button sends the full session state to Python, which
builds a markdown cell and inserts it below the current cell.

Requirements
------------
    pip install comm sympy matplotlib

Cell 1 — Setup (run once per kernel session)
--------------------------------------------
    from notebook_integration import setup_math_widget
    setup_math_widget()

Cell 2 — Display the widget
----------------------------
    from IPython.display import display, HTML
    display(HTML(open("math_widget.html").read()))

Cell 3 — Access captured expressions
--------------------------------------
    from notebook_integration import received_expressions
    print(received_expressions)

    # Last expression as a SymPy object:
    from sympy.parsing.latex import parse_latex
    expr = parse_latex(received_expressions[-1])
    print(expr)
"""

from __future__ import annotations

import base64
import traceback
from io import BytesIO
from pathlib import Path

import comm
import sympy as sp
from sympy.parsing.latex import parse_latex

# ---------------------------------------------------------------------------
# Shared state
# ---------------------------------------------------------------------------
received_expressions: list[str] = []
_kernel_comm = None
_plot_counter = 0          # increments each time a plot is saved to disk


# ---------------------------------------------------------------------------
# Action handlers
# ---------------------------------------------------------------------------

def _handle_render(data: dict) -> None:
    """Acknowledge a render event; store the LaTeX."""
    latex = data.get("latex", "")
    received_expressions.append(latex)
    _kernel_comm.send({
        "type":   "ack",
        "status": "received",
        "latex":  latex,
        "count":  len(received_expressions),
    })


def _handle_action(data: dict) -> None:
    """Dispatch a math action and send the result back to the widget."""
    action = data.get("action", "")
    latex  = data.get("latex", "")

    try:
        expr = parse_latex(latex)

        if action == "expand":
            result = sp.expand(expr)
            _send_latex(action, sp.latex(result), latex)

        elif action == "factor":
            result = sp.factor(expr)
            _send_latex(action, sp.latex(result), latex)

        elif action == "solve":
            symbol_str = data.get("symbol", "x")
            symbol     = sp.Symbol(symbol_str)
            solutions  = sp.solve(expr, symbol)
            if not solutions:
                result_latex = r"\text{No solutions found}"
            elif len(solutions) == 1:
                result_latex = f"{symbol_str} = {sp.latex(solutions[0])}"
            else:
                result_latex = r",\quad ".join(
                    f"{symbol_str} = {sp.latex(s)}" for s in solutions
                )
            _send_latex(action, result_latex, latex)

        elif action == "evaluate":
            symbol_str = data.get("symbol", "x")
            value      = data.get("value", 0)
            symbol     = sp.Symbol(symbol_str)
            result     = sp.simplify(expr.subs(symbol, value))
            _send_latex(action, sp.latex(result), latex)

        elif action == "plot":
            _handle_plot(data, expr, latex)

        else:
            _send_error(action, f"Unknown action: {action}")

    except Exception as exc:
        _send_error(action, f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}")


def _handle_plot(data: dict, expr, input_latex: str) -> None:
    """Generate a matplotlib figure, save it to disk, and send base64 + filename."""
    global _plot_counter
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    symbol_str = data.get("symbol", "x")
    range_min  = float(data.get("range_min", -10))
    range_max  = float(data.get("range_max",  10))
    symbol     = sp.Symbol(symbol_str)

    f  = sp.lambdify(symbol, expr, modules=["numpy"])
    xs = np.linspace(range_min, range_max, 600)

    try:
        ys = f(xs)
        ys = np.where(np.isfinite(ys), ys, np.nan)
    except Exception as exc:
        _send_error("plot", f"Could not evaluate expression: {exc}")
        return

    fig, ax = plt.subplots(figsize=(7, 3.8))
    fig.patch.set_facecolor("#2a2a3e")
    ax.set_facecolor("#1e1e2e")
    ax.plot(xs, ys, color="#89b4fa", linewidth=2.0)
    ax.axhline(0, color="#6c7086", linewidth=0.8, zorder=0)
    ax.axvline(0, color="#6c7086", linewidth=0.8, zorder=0)
    ax.grid(True, color="#44445a", linewidth=0.5, alpha=0.6)
    for spine in ax.spines.values():
        spine.set_color("#44445a")
    ax.tick_params(colors="#cdd6f4", labelsize=9)
    ax.set_xlabel(symbol_str, color="#cdd6f4", fontsize=10)
    ax.set_ylabel("y", color="#cdd6f4", fontsize=10)
    try:
        ax.set_title(rf"$y = {sp.latex(expr)}$", color="#cdd6f4", fontsize=11, pad=10)
    except Exception:
        ax.set_title(f"y = {input_latex}", color="#cdd6f4", fontsize=11, pad=10)
    fig.tight_layout()

    # Save to disk so the generated markdown cell can reference it by filename
    _plot_counter += 1
    plot_filename = f"widget_plot_{_plot_counter}.png"
    fig.savefig(plot_filename, format="png", dpi=130,
                bbox_inches="tight", facecolor=fig.get_facecolor())

    # Also send base64 for immediate display inside the widget
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode()
    plt.close(fig)

    _kernel_comm.send({
        "type":          "result",
        "action":        "plot",
        "image":         img_b64,
        "plot_filename": plot_filename,
        "input_latex":   input_latex,
    })


# ---------------------------------------------------------------------------
# Save to Cell
# ---------------------------------------------------------------------------

def _handle_save_to_cell(data: dict) -> None:
    """
    Build a markdown string from the widget's current state and send it
    back to the frontend, which inserts it as a notebook cell.
    """
    try:
        state   = data.get("state", {})
        latex   = state.get("input", "")
        mode    = state.get("mode", "display")
        actions = state.get("actions", [])

        if not latex:
            _kernel_comm.send({"type": "save_error", "message": "No expression to save."})
            return

        lines: list[str] = []

        # ── Header ──
        lines.append(f"### Math Expression: `{latex}`")
        lines.append("")

        # ── Input ──
        lines.append("**Input**")
        lines.append("")
        if mode == "display":
            lines.append(f"$$\n{latex}\n$$")
        else:
            lines.append(f"${latex}$")
        lines.append("")

        # ── Action results ──
        action_labels = {
            "expand":   "Expanded",
            "factor":   "Factored",
            "solve":    "Solved",
            "evaluate": "Evaluated",
            "plot":     "Plot",
        }

        for entry in actions:
            action = entry.get("action", "")
            label  = action_labels.get(action, action.title())

            if action == "plot":
                fname  = entry.get("plot_filename", "")
                sym    = entry.get("symbol", "x")
                rmin   = entry.get("range_min", "-10")
                rmax   = entry.get("range_max", "10")
                lines.append(f"**{label}** &nbsp; ${sym} \\in [{rmin},\\, {rmax}]$")
                lines.append("")
                if fname and Path(fname).exists():
                    lines.append(f"![]({fname})")
                else:
                    lines.append("*(plot image not found — re-run the Plot action)*")
                lines.append("")

            elif action == "solve":
                sym = entry.get("symbol", "x")
                lines.append(f"**{label} for ${sym}$**")
                lines.append("")
                lines.append(f"$$\n{entry.get('result_latex', '')}\n$$")
                lines.append("")

            elif action == "evaluate":
                sym = entry.get("symbol", "x")
                val = entry.get("value", "0")
                lines.append(f"**{label}** &nbsp; ${sym} = {val}$")
                lines.append("")
                lines.append(f"$$\n{entry.get('result_latex', '')}\n$$")
                lines.append("")

            else:
                lines.append(f"**{label}**")
                lines.append("")
                lines.append(f"$$\n{entry.get('result_latex', '')}\n$$")
                lines.append("")

        markdown = "\n".join(lines)

        _kernel_comm.send({
            "type":     "insert_cell",
            "markdown": markdown,
        })

    except Exception as exc:
        _kernel_comm.send({
            "type":    "save_error",
            "message": f"{type(exc).__name__}: {exc}",
        })


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _send_latex(action: str, result_latex: str, input_latex: str) -> None:
    _kernel_comm.send({
        "type":         "result",
        "action":       action,
        "result_latex": result_latex,
        "input_latex":  input_latex,
    })


def _send_error(action: str, message: str) -> None:
    _kernel_comm.send({
        "type":    "error",
        "action":  action,
        "message": message,
    })


# ---------------------------------------------------------------------------
# Message router
# ---------------------------------------------------------------------------

def on_msg(msg: dict) -> None:
    """Route incoming widget messages to the correct handler."""
    data     = msg["content"]["data"]
    msg_type = data.get("type", "render")

    if msg_type == "action":
        _handle_action(data)
    elif msg_type == "save_to_cell":
        _handle_save_to_cell(data)
    else:
        _handle_render(data)


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

def setup_math_widget() -> None:
    """
    Register the comm target and message handler.

    Call this once per kernel session **before** displaying the widget.
    The widget (JS) opens the comm; Python answers — this is the correct
    direction so both sides connect to the same channel.
    """
    global _kernel_comm

    def _target_func(comm_obj, open_msg) -> None:
        global _kernel_comm
        _kernel_comm = comm_obj
        _kernel_comm.on_msg(on_msg)

    comm.get_comm_manager().register_target("math_widget", _target_func)
    print("✓ Math widget target registered.")
    print("  Run:  display(HTML(open('math_widget.html').read()))  to show the widget.")
