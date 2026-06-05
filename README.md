# Math Expression Widget

A self-contained HTML widget for composing, rendering, and analyzing LaTeX math expressions inside Jupyter Notebooks. It provides a symbol palette, expression templates, live MathJax rendering, SymPy-powered math actions (expand, factor, solve, evaluate, plot), and two-way communication with the Python kernel.

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

### Math Actions
After rendering an expression, an **Actions** toolbar appears. Each button sends the current LaTeX to Python, computes the result with SymPy, and displays it in a result panel directly below the output — with a color-coded badge and MathJax-rendered LaTeX (or an inline chart for plots).

| Button | Parameters | Description |
|---|---|---|
| **Expand** | — | Distributes and expands all terms |
| **Factor** | — | Fully factors the expression |
| **Solve for** | symbol (default `x`) | Finds all solutions; displays as `x = ...` |
| **Evaluate** | symbol, value | Substitutes the value and simplifies |
| **Plot** | symbol, range min/max | Plots the expression over the given range |

Plots are rendered in matplotlib using the widget's dark theme and displayed as inline images — no separate output cell needed.

### History
- Last 6 rendered expressions shown below the input cell
- Click any history item to reload it into the input

### Python Kernel Communication
- Two-way comm channel via the `comm` package
- Widget sends LaTeX and action parameters to Python on every render or action
- Python computes results with SymPy and sends them back for display
- All rendered expressions are accessible in Python for further processing

---

## Installation

1. Clone or download this repository:
   ```bash
   git clone https://github.com/muftring/math-expression-widget.git
   ```

2. Copy `math_widget.html` and `notebook_integration.py` into the same directory as your Jupyter Notebook.

3. Install dependencies:
   ```bash
   pip install comm sympy matplotlib
   ```

> The widget uses CDN-hosted MathJax, so an internet connection is required.

---

## Usage

### Option 1 — Display only (no Python actions)

```python
from IPython.display import HTML, display

display(HTML(open("math_widget.html").read()))
```

The widget renders fully in the browser. The action buttons are disabled until a Python comm channel is connected.

### Option 2 — Sandboxed iframe

```python
from IPython.display import IFrame
IFrame("math_widget.html", width="900", height="950")
```

### Option 3 — Full two-way communication with math actions ✨

**Cell 1** — Set up the comm channel (run once per kernel session):

```python
from notebook_integration import setup_math_widget
setup_math_widget()
```

**Cell 2** — Display the widget:

```python
from IPython.display import display, HTML
display(HTML(open("math_widget.html").read()))
```

Now use the widget:
- Type or select a LaTeX expression and click **▶ Render**
- Use the **Actions** toolbar to expand, factor, solve, evaluate, or plot
- Results appear inline in the widget — no extra cells needed

**Cell 3** — Access captured expressions from Python:

```python
from notebook_integration import received_expressions
print(received_expressions)

# Parse the last expression with SymPy:
from sympy.parsing.latex import parse_latex
expr = parse_latex(received_expressions[-1])
print(expr)
```

> **Note:** If you restart the kernel, re-run Cell 1 before using the widget again.

---

## Example Workflow

```
1. Select template:   🟣 Algebraic → Quadratic Eq.
   → inserts:         x^2 - 5x + 6 = 0

2. Click ▶ Render
   → displays rendered equation

3. Click Expand
   → result:  x² - 5x + 6

4. Click Factor
   → result:  (x - 2)(x - 3)

5. Click Solve for  x
   → result:  x = 2,  x = 3

6. Click Evaluate   x = 2
   → result:  0

7. Click Plot   x  from -2  to  6
   → inline dark-theme chart of y = x² - 5x + 6
```

---

## Requirements

- Jupyter Notebook (classic) or JupyterLab
- Internet connection (MathJax loaded from CDN)
- Python packages: `comm`, `sympy`, `matplotlib`

```bash
pip install comm sympy matplotlib
```

---

## License

MIT
