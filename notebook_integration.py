# Math Widget — Jupyter Notebook Integration
#
# Cell 1: Run this first to open the comm channel and register the handler.
#
#   from IPython.display import display, HTML
#   import comm
#
#   received_expressions = []
#
#   kernel_comm = comm.create_comm(target_name="math_widget")
#
#   def handle_msg(msg):
#       data = msg["content"]["data"]
#       latex = data.get("latex", "")
#       received_expressions.append(latex)
#       kernel_comm.send({
#           "status": "received",
#           "latex": latex,
#           "count": len(received_expressions),
#           # Optionally add sympy parsing:
#           # "sympy_result": str(parse_latex(latex)),
#       })
#
#   kernel_comm.on_msg(handle_msg)
#   print("Comm channel open. Widget ready to connect.")
#
#
# Cell 2: Display the widget.
#
#   display(HTML(open("math_widget.html").read()))
#
#
# Cell 3: Access captured expressions.
#
#   print(received_expressions)
#
#   # Parse the last expression with sympy:
#   from sympy.parsing.latex import parse_latex
#   expr = parse_latex(received_expressions[-1])
#   print(expr)
#
#
# NOTE: If you restart the kernel, re-run Cell 1 before using the widget.

from IPython.display import display, HTML
import comm

received_expressions = []
kernel_comm = comm.create_comm(target_name="math_widget")


def handle_msg(msg):
    """Handle a LaTeX expression sent from the widget."""
    data = msg["content"]["data"]
    latex = data.get("latex", "")
    received_expressions.append(latex)
    kernel_comm.send({
        "status": "received",
        "latex": latex,
        "count": len(received_expressions),
    })


kernel_comm.on_msg(handle_msg)


def show_widget():
    """Display the math expression widget in the current cell output."""
    display(HTML(open("math_widget.html").read()))
