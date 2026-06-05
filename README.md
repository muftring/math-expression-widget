# Math Expression Widget

A self-contained HTML widget for composing and rendering LaTeX math expressions inside Jupyter Notebooks. It provides a symbol palette, expression templates, live MathJax rendering, and optional two-way communication with the Python kernel.

![screenshot placeholder](https://via.placeholder.com/800x400?text=Math+Expression+Widget)

---

## Features

### Input
- LaTeX textarea with syntax-aware cursor placement
- **Inline (IL)** and **Display (DL)** mode toggle
- `Shift+Enter` keyboard shortcut to render

### Symbol Palette
Click any symbol to insert it at the cursor:
- **Greek** — α β γ δ ε θ λ μ π σ φ ω … Γ Δ Σ Ω and more
- **Operators** — fractions, roots, sums, products, integrals (single/double/triple/contour), limits, superscripts, subscripts, ± × ÷ ≠ ≤ ≥ ≈ ≡ ∂ ∇
- **Logic / Sets** — ∞ ∈ ∉ ⊂ ⊆ ∪ ∩ ∅ ∀ ∃ ¬ ∧ ∨ ⇒ ⟺ ℝ ℤ ℕ ℚ ℂ
- **Matrices** — 2×2, 3×3, determinant, column vector, bold/arrow/hat vector notation, ellipsis symbols

### Expression Templates
Pre-built LaTeX templates organized by category:

| Category | Examples |
|---|---|
| 🟣 **Algebraic** | Quadratic equation, Quadratic formula, System of equations, Polynomial, Rational equation, Factored form, Log/Exp equation, Binomial theorem, Matrix equation |
| 🟡 **Inequalities** | Linear, Compound AND/OR, Quadratic, Absolute value, Rational, Interval notation, Set builder notation |
| 🟢 **Geometry** | Pythagorean theorem, Circle, Distance, Midpoint, Slope, Line equation, Law of Cosines/Sines, Ellipse, Parabola, Sphere, Trig identity |

### Output
- Live MathJax rendering
- LaTeX source displayed beneath the rendered output
- Execution counter (matches Jupyter cell style)

### History
- Last 6 rendered expressions shown below the input cell
- Click any history item to reload it into the input

### Python Kernel Communication
- Two-way comm channel via `ipywidgets` / `comm`
- Widget sends LaTeX to Python on every render
- Python can reply with computed results (e.g. SymPy output)

---

## Installation

No package installation is required. The widget is a single HTML file that uses CDN-hosted MathJax.

1. Clone or download this repository:
   ```bash
   git clone https://github.com/muftring/math-expression-widget.git
   ```

2. Copy `math_widget.html` into the same directory as your Jupyter Notebook.

---

## Usage

### Option 1 — Simplest (render HTML in a cell)

```python
from IPython.display import HTML, display

with open("math_widget.html") as f:
    display(HTML(f.read()))
```

### Option 2 — Sandboxed iframe

```python
from IPython.display import IFrame
IFrame("math_widget.html", width="900", height="950")
```

### Option 3 — Two-way Python communication

Run this in **Cell 1** to open the comm channel:

```python
from IPython.display import display, HTML
import comm

received_expressions = []
kernel_comm = comm.create_comm(target_name="math_widget")

def handle_msg(msg):
    data = msg["content"]["data"]
    latex = data.get("latex", "")
    received_expressions.append(latex)
    kernel_comm.send({
        "status": "received",
        "latex": latex,
        "count": len(received_expressions),
    })

kernel_comm.on_msg(handle_msg)
print("Comm channel open. Widget ready to connect.")
```

Run this in **Cell 2** to display the widget:

```python
display(HTML(open("math_widget.html").read()))
```

Then access captured expressions in any later cell:

```python
print(received_expressions)

# Parse the last expression with SymPy:
from sympy.parsing.latex import parse_latex
expr = parse_latex(received_expressions[-1])
print(expr)
```

> **Note:** If you restart the kernel, re-run Cell 1 before using the widget again.

---

## Requirements

- Jupyter Notebook (classic) or JupyterLab
- Internet connection (MathJax loaded from CDN)
- For two-way comm: `comm` package (`pip install comm`)
- For SymPy parsing: `sympy` (`pip install sympy`)

---

## License

MIT
