# DECISIONS.md
# Architecture & Design Decision Log
# Digital Logic Design & Simulation Toolkit

---

> This document records all major design and architecture decisions made during
> the development of the Digital Logic Design & Simulation Toolkit. Each entry
> explains the **context**, the **decision taken**, the **alternatives considered**,
> and the **rationale**.

---

## Decision Index

| ID | Title | Category | Date |
|----|-------|----------|------|
| D-01 | Use Python + Tkinter (stdlib only) | Technology | Oct 2026 |
| D-02 | Build a shared gate_engine.py simulation core | Architecture | Oct 2026 |
| D-03 | One module per team member, one file each | Team Structure | Oct 2026 |
| D-04 | Use tk.Canvas for all visual output | UI Rendering | Oct 2026 |
| D-05 | Quine-McCluskey over Petrick's method | Algorithm | Oct 2026 |
| D-06 | Behavioral FlipFlop model (not gate-level) | Simulation | Oct 2026 |
| D-07 | Hardcoded FSM (11-detector Mealy) | Scope | Oct 2026 |
| D-08 | Dark theme unified color palette | Design | Oct 2026 |
| D-09 | Particle animation on home screen | Design | Oct 2026 |
| D-10 | Status bar pattern on every module | UX | Oct 2026 |
| D-11 | Greedy essential PI cover (not Petrick exact) | Algorithm | Oct 2026 |
| D-12 | Feed-forward propagation with iteration for latches | Simulation | Oct 2026 |

---

## D-01 — Use Python + Tkinter (stdlib only)

**Category:** Technology Stack

**Context:**
The project is a course submission. It needs to run on the lab machines and
on students' personal Windows/Linux/macOS setups with minimal setup friction.

**Decision:**
Use Python 3.8+ with Tkinter from the standard library only. No pip packages.

**Alternatives Considered:**

| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| PyQt5 / PySide6 | Better widgets, native look | Requires pip install; LGPL licensing | Installation friction |
| Web app (Flask + HTML5 Canvas) | Cross-platform browser-based | Network server needed; JS canvas for gates | Over-engineered for a course project |
| tkinter + matplotlib | Better plots | Extra pip dependency | Violates zero-dep constraint |
| wxPython | Native widgets | pip required; complex install on Linux | Same as PyQt |

**Rationale:**
- Tkinter ships with CPython — `python main.py` works out of the box
- Sufficient canvas drawing primitives for all our visualization needs
- Team is familiar with Python; Tkinter is taught in some lab sessions
- Zero friction for the examiner / demo environment

---

## D-02 — Build a shared gate_engine.py simulation core

**Category:** Architecture

**Context:**
Modules 1 and 2 both needed to compute logic gate outputs. Without a shared
engine, each module would have implemented its own hardcoded arithmetic (e.g.,
`SUM = A XOR B`) which would not constitute a "simulation".

**Decision:**
Create `gate_engine.py` containing `Wire`, `Gate`, and `Circuit` classes.
All modules import from this file. Gate outputs are computed by calling
`Gate.evaluate()` which reads input wire values and writes to its output wire.

**Architecture:**

```
Wire (carries 1-bit value)
  |
Gate (gate_type: AND/OR/NOT/XOR/NAND/NOR/XNOR/BUF)
  |  inputs: [Wire...]
  |  output: Wire
  |  evaluate(): reads inputs, writes output
  |
Circuit (container)
  |  input_wires: {name -> Wire}
  |  gates: [Gate...]  -- insertion order = evaluation order
  |  output_wires: {name -> Wire}
  |  propagate(): calls evaluate() on every gate once
```

**Alternatives Considered:**

| Alternative | Why Rejected |
|-------------|-------------|
| Each module defines its own gate classes | Code duplication; inconsistency |
| Hardcode arithmetic (sum = a^b) | Not a simulation — just a calculator |
| NumPy boolean arrays | External dependency; overkill |

**Rationale:**
- A genuine simulation engine makes the project academically stronger
- `propagate()` in insertion order works perfectly for feed-forward (DAG) circuits
- SR latch feedback is handled by iterating 4 rounds until stable (standard trick)
- `sop_to_gate_tree()` lets Module 1 build a real AND-OR circuit from its minimized SOP

---

## D-03 — One module per team member, one file each

**Category:** Team Structure

**Context:**
4-member team. Each member is responsible for one unit of the syllabus.
Parallel development is needed to meet deadlines.

**Decision:**
Each member owns exactly one Python file:
- `module1_kmap.py` — Member 1
- `module2_combinational.py` — Member 2
- `module3_sequential.py` — Member 3
- `module4_asm_pld.py` — Member 4

Each module file is self-contained — can be run standalone (`python module1_kmap.py`).
The only shared dependency is `gate_engine.py`.

**Rationale:**
- Minimizes merge conflicts (each file is owned by one person)
- Standalone runability allows each member to demo their work independently
- `main.py` integrates all 4 by calling each module's `launch(master)` function
- Clear ownership for grading and code review

---

## D-04 — Use tk.Canvas for all visual output

**Category:** UI Rendering

**Context:**
The project requires drawing K-Map grids, gate schematics, timing waveforms,
FSM state diagrams, and PLA fuse maps. Tkinter's standard widget set (Label,
Entry, etc.) cannot handle arbitrary 2D drawing.

**Decision:**
Use `tk.Canvas` as the drawing surface for all visual outputs. All shapes,
lines, text, and waveforms are drawn with canvas primitives (`create_rectangle`,
`create_line`, `create_text`, `create_oval`, `create_polygon`).

**Rationale:**
- Canvas is part of Tkinter stdlib — no extra dependency
- Supports all needed primitives: rectangles, arcs (for FSM self-loops), polygons (rounded rects)
- Canvas items can be deleted and redrawn, enabling live updates per Clock Pulse
- `create_polygon(..., smooth=True)` gives smooth rounded rectangle shapes for cards

**Trade-off:**
- Canvas is not resolution-independent (no vector export)
- Waveform redraw on each tick is full-canvas clear + redraw (simple but not optimal for large histories)

---

## D-05 — Quine-McCluskey over Petrick's Method

**Category:** Algorithm (Module 1)

**Context:**
Boolean minimization requires: (1) finding all prime implicants (PI), and
(2) selecting a minimum cover from those PIs.

**Decision:**
- **Finding PIs:** Full Quine-McCluskey (QM) tabulation — iteratively merge
  terms that differ in exactly one bit position, using '-' as the don't-care placeholder.
- **Selecting cover:** Greedy essential PI selection:
  1. Find essential PIs (only PI covering a given minterm)
  2. Add all essential PIs to the solution
  3. For remaining uncovered minterms, greedily pick the PI that covers the most

**Alternatives Considered:**

| Alternative | Pros | Cons |
|-------------|------|------|
| Petrick's Method | Guaranteed minimum cover | Complex to implement; exponential worst case |
| ESPRESSO heuristic | Industrial-grade minimization | Far too complex for a course project |
| Brute-force enumerate all covers | Simple | Exponential in number of PIs |

**Rationale:**
- QM tabulation is exactly what the syllabus teaches — students can follow the output
- Greedy cover is sufficient for 4-variable functions (max 16 minterms)
- The step-by-step QM output in the text panel is the educational value
- Exact minimality is less important than pedagogical clarity for this use case

---

## D-06 — Behavioral FlipFlop Model (not gate-level) for Module 3

**Category:** Simulation (Module 3)

**Context:**
Module 3 simulates SR, JK, D, T flip-flops plus shift registers and counters.
Two implementation approaches were possible.

**Decision:**
Use a **behavioral model** — `FlipFlop.clock(**inputs)` applies the flip-flop
truth table directly in Python:

```python
if kind == "JK":
    if j and k:  self.q = 1 - self.q   # toggle
    elif j:      self.q = 1
    elif k:      self.q = 0
```

**Alternatives Considered:**

| Alternative | Pros | Cons |
|-------------|------|------|
| Gate-level (NAND SR latch + steering gates for JK) | Truly gate-level | Complex feedback; requires multiple settle iterations per clock |
| Behavioral (chosen) | Simple, fast, correct | Hides internal gate structure |

**Rationale:**
- Module 3's educational value is in *timing diagrams and state sequences*, not gate internals
- Gate-level flip-flop simulation (with feedback loops) is complex to implement correctly
- The behavioral model exactly matches the flip-flop truth tables taught in the course
- Gate-level is already demonstrated in Module 2 for combinational circuits

---

## D-07 — Hardcoded FSM (11-detector Mealy machine) in Module 4

**Category:** Scope (Module 4)

**Context:**
Module 4 needed an FSM example. Options: built-in example vs. user-definable FSM.

**Decision:**
Ship a hardcoded Mealy FSM that detects consecutive '1' pairs ("11") as the
built-in example. The FSM has 3 states: S0, S1, S2.

```
Transitions:
(S0, 0) -> (S0, out=0)   (S0, 1) -> (S1, out=0)
(S1, 0) -> (S0, out=0)   (S1, 1) -> (S2, out=1)
(S2, 0) -> (S0, out=0)   (S2, 1) -> (S2, out=1)
```

**Rationale:**
- "11 detector" is a classic textbook FSM problem — students already know it
- A user-editable FSM GUI (state editor, transition editor) would be a major
  additional feature requiring significant extra work
- The hardcoded FSM still demonstrates: state diagram drawing, transition
  animation, Mealy output, history tracking
- Noted in roadmap as a v2.0 feature

---

## D-08 — Unified Dark Theme Color Palette

**Category:** Design

**Context:**
4 separate module files, 4 team members, potential for visual inconsistency.

**Decision:**
Define the same color token set in every file:

```python
BG_DARK        = "#0a0f1e"
BG_CARD        = "#111827"
CANVAS_BG      = "#0d1526"
ACCENT_CYAN    = "#06b6d4"   # Module 1
ACCENT_GREEN   = "#10b981"   # Module 2 / HIGH
ACCENT_PURPLE  = "#8b5cf6"   # Module 3
ACCENT_AMBER   = "#f59e0b"   # Module 4
ACCENT_RED     = "#ef4444"   # LOW / error
TEXT_PRIMARY   = "#f1f5f9"
TEXT_SECONDARY = "#94a3b8"
TEXT_DIM       = "#475569"
```

Each module has **one accent color** that is its visual identity. The background
and text tokens are identical across all modules.

**Rationale:**
- Prevents "4 random apps bolted together" appearance
- Dark theme reduces eye strain in lab environments
- Module-specific accent colors (cyan/green/purple/amber) help users
  visually distinguish which window belongs to which module
- Consistent palette defined per-file (no shared config) avoids cross-module import issues

---

## D-09 — Animated Particle Background on Home Screen

**Category:** Design (main.py)

**Context:**
The home screen is the first thing users see. A plain dark window with 4 buttons
felt generic and low-effort.

**Decision:**
Add a `ParticleBG` canvas layer with 45 drifting dots. Each dot has:
- Random position, velocity, size (1.0-2.8 px radius)
- Random accent color
- Alpha fade-out (resets when reaching top or alpha <= 0)
- Faint connection lines drawn between dots within 90px of each other

**Rationale:**
- Creates an immediately striking first impression
- Subtle enough not to distract from the module cards
- Implemented in pure Tkinter (no PIL/Pygame) using alpha-blended hex colors computed manually
- The "circuit network" aesthetic (dots + connection lines) is thematically appropriate
  for a digital logic simulator

**Trade-off:**
- Adds ~5 ms of CPU load per 28 ms frame on the home screen
- Resolved by using `after(28)` (approximately 35 fps) and only drawing particles
  while the home window exists

---

## D-10 — Status Bar Pattern on Every Module Window

**Category:** UX

**Context:**
Users needed feedback on what the last simulation computed without having to read
the full canvas or text panel. Module windows had no persistent feedback area.

**Decision:**
Add a fixed-height status bar (`tk.Label`) packed at `side="bottom"` on every
module window. It shows:

| Module | Status bar content after action |
|--------|--------------------------------|
| M1 K-Map | `Solved * 4 vars * 10 minterms * 3 PIs * F = A'B + BC'` |
| M2 Combinational | `Simulated: Full Adder | SUM=0  COUT=1` |
| M3 Sequential | `Tick 3 | JK Flip-Flop | J=1 K=0 Q=1` |
| M4 FSM | `FSM Step | Input=1 -> State=S2 | Output=1 | History=4` |

**Rationale:**
- Status bar is a standard desktop UI pattern (VS Code, GIMP, browser)
- Gives instant scannable feedback without requiring the user to find the result on canvas
- Dark (#0d1526) background distinguishes it visually from the canvas area

---

## D-11 — Greedy PI Cover (not Exact Minimum)

**Category:** Algorithm (Module 1)

**Context:**
After finding all prime implicants via QM, the optimal cover selection is NP-hard
in the general case (set cover problem).

**Decision:**
Use a two-phase greedy approach:
1. Find all **essential** prime implicants (a PI is essential if it is the only one covering some minterm).
2. For remaining uncovered minterms, greedily pick the PI that covers the most.

**Trade-off:**
- May not always produce the globally minimum SOP (can be suboptimal for degenerate cases)
- For 2-4 variable functions (max 16 minterms, small PI sets), it almost always produces the minimum

**Rationale:**
- Correct for all standard textbook examples with 2-4 variables
- Simple enough to understand and verify manually
- The QM step trace (shown in the UI) is the primary educational output —
  the exact vs. near-exact minimality of the cover is secondary

---

## D-12 — Feed-Forward Propagation with Iteration for Latches

**Category:** Simulation (gate_engine.py)

**Context:**
The `Circuit.propagate()` method evaluates gates in insertion order once.
This works perfectly for combinational (DAG) circuits.
However, an SR latch has a feedback loop: the output of gate_Q feeds into gate_Qn
and vice versa. Feed-forward evaluation (one pass) may not settle to the correct state.

**Decision:**
For circuits with feedback (e.g., SR latch), iterate the evaluation loop 4 times:

```python
for _ in range(4):
    gate_q.evaluate()
    gate_qn.evaluate()
```

This is sufficient to settle any 2-gate cross-coupled latch.

**Alternatives Considered:**

| Alternative | Pros | Cons |
|-------------|------|------|
| Event-driven simulation (change propagation) | Correct for any topology | Complex to implement; overkill for 2 feedback gates |
| Single-pass propagate() | Simple | Wrong for latches with feedback |
| 4-iteration settle (chosen) | Correct, simple | Only works for small feedback loops; not general |

**Rationale:**
- 4 iterations is mathematically proven sufficient for a 2-gate feedback loop to settle
  (it matches the behavior of real cross-coupled NAND gates)
- This pattern is a standard trick in simplified gate simulators
- All combinational circuits in the project are feed-forward DAGs, so their
  `propagate()` (single pass) is always correct

---

*End of DECISIONS.md*
