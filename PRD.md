# Product Requirements Document (PRD)
# Digital Logic Design & Simulation Toolkit

---

| Field | Detail |
|-------|--------|
| **Product Name** | Digital Logic Design & Simulation Toolkit |
| **Version** | 1.0 |
| **Status** | Active — Course Project |
| **Course** | Digital Electronics — Units 1–3 |
| **Stack** | Python 3.8+ · Tkinter (stdlib only) |
| **Document Owner** | Team (4 Members) |
| **Last Updated** | October 2026 |

---

## 1. Executive Summary

The **Digital Logic Design & Simulation Toolkit** is a 4-module, cross-platform desktop application that enables students and educators to interactively simulate digital logic circuits — from Boolean minimization through gate-level combinational circuits, clocked sequential circuits, and programmable logic devices.

Unlike web-based tools or heavy EDA suites, this toolkit:
- Runs **entirely offline** with zero external dependencies
- Uses a **real gate-level simulation engine** (`gate_engine.py`) instead of hardcoded math
- Is structured as a **team project** — each member owns one module independently

---

## 2. Problem Statement

> "Understanding digital logic from a textbook is not enough — students need to *see* signals propagating through gates, *watch* flip-flop state change cycle by cycle, and *visualize* K-Map groupings to truly internalize the concepts."

### Pain Points Addressed

| Pain Point | How the Toolkit Solves It |
|-----------|--------------------------|
| K-Maps are confusing to draw by hand | Module 1 auto-draws K-Map with color-coded cells and Quine-McCluskey trace |
| Gate-level arithmetic is tedious to verify | Module 2 propagates real signals through Gate objects — output is computed, not assumed |
| Sequential circuits require clock-by-clock tracing | Module 3 shows a live waveform that grows with every Clock Pulse click |
| ASM/FSM state tracking is error-prone | Module 4 highlights active states in real time with a transition history trail |
| PLA fuse maps are abstract | Module 4 renders the AND-array/OR-array as a visual grid with programmed/blown markers |

---

## 3. Objectives & Goals

### Primary Goals
1. **Simulate** all major digital logic circuits covered in Units 1-3 of a standard Digital Electronics curriculum.
2. **Visualize** every simulation result on a canvas (K-Map grid, gate schematic, timing diagram, FSM chart, PLA fuse map).
3. **Educate** through step-by-step output that shows intermediate results (QM rounds, tick-by-tick state, etc.).
4. **Modularize** the codebase so each team member works independently on their own module.

### Secondary Goals
- Zero installation friction (pure Python stdlib, no pip required).
- Consistent dark-theme UI across all modules for a professional look.
- Each module runnable standalone for individual testing.

---

## 4. Users & Personas

### 4.1 Primary User — Engineering Student
| Attribute | Detail |
|-----------|--------|
| **Who** | 2nd/3rd year Electronics or Computer Engineering student |
| **Goal** | Verify homework answers, understand concepts visually |
| **Skill** | Basic digital logic theory; beginner Python |
| **Need** | Easy input entry, immediate visual output, step explanations |

### 4.2 Secondary User — Lab Instructor / Demonstrator
| Attribute | Detail |
|-----------|--------|
| **Who** | Lab TA or professor doing in-class demos |
| **Goal** | Show K-Maps, timing diagrams, FSM transitions live |
| **Skill** | Strong domain knowledge; moderate software comfort |
| **Need** | Large readable canvas, multiple windows open simultaneously |

---

## 5. System Architecture

```
digital_sim_project/
|
+-- main.py                    <- Home launcher (HomeApp)
|                                 Animated particle background, 4 module cards
|
+-- gate_engine.py             <- Shared simulation core
|                                 Wire, Gate, Circuit classes
|                                 Built-in: half/full adder, SR latch, SOP tree
|
+-- module1_kmap.py            <- Member 1: K-Map & Quine-McCluskey
+-- module2_combinational.py   <- Member 2: Combinational Circuit Simulator
+-- module3_sequential.py      <- Member 3: Sequential Circuit Simulator
+-- module4_asm_pld.py         <- Member 4: ASM/FSM & PLA/PAL Simulator
|
+-- PRD.md                     <- This document
+-- DECISIONS.md               <- Architecture & design decisions log
+-- README.md                  <- Setup & usage guide
```

### Data Flow

```
User Input (GUI widgets)
        |
        v
Module logic (parse, validate)
        |
        v
gate_engine: Circuit.propagate()   <--- Wire -> Gate -> Wire chain
        |
        v
Output rendered on tk.Canvas / tk.Text widget
        |
        v
Status bar updated with result summary
```

---

## 6. Functional Requirements

### 6.1 Home Menu (main.py)

| ID | Requirement |
|----|------------|
| H-01 | Display 4 animated module cards with title, subtitle, unit badge, and accent color |
| H-02 | Clicking a card opens the module in a new Toplevel window |
| H-03 | Multiple modules may be open simultaneously |
| H-04 | Home window shows animated particle background (drifting dots with connection lines) |
| H-05 | Header icon pulses with a sine-wave color animation |
| H-06 | Module cards show hover-glow animation (smooth interpolation over 16 ms ticks) |
| H-07 | Footer bar displays module count and stdlib badge |

---

### 6.2 Module 1 — K-Map & Quine-McCluskey (module1_kmap.py)

#### Inputs
| Input | Type | Constraints |
|-------|------|-------------|
| Number of variables | Radio button (2 / 3 / 4) | 2 <= n <= 4 |
| Minterms | Comma-separated integers | 0 <= m < 2^n; no overlap with don't-cares |
| Don't-care terms | Comma-separated integers | 0 <= dc < 2^n |

#### Outputs
| Output | Location | Format |
|--------|----------|--------|
| Truth table summary | Right panel (Text widget) | n variables + F column, color-coded rows |
| QM merging steps | Right panel | Round-by-round: `0010 + 0110 -> 0-10` |
| Prime implicants selected | Right panel | Bit pattern -> human expression |
| Minimized SOP | Right panel (highlighted amber) | `F = A'B + BC' + ACD'` |
| K-Map grid | Left canvas | Gray-code ordered cells; 1=green, x=amber, 0=dim |
| Gate schematic | Popup window | AND-OR 2-level diagram auto-drawn from SOP |
| Status bar | Bottom bar | `Solved * 4 vars * 10 minterms * 3 PIs * F = ...` |

#### Functional Rules
| ID | Rule |
|----|------|
| M1-01 | Minterms and don't-cares must not overlap |
| M1-02 | All terms must be in range [0, 2^n - 1] |
| M1-03 | QM algorithm uses greedy essential prime implicant cover |
| M1-04 | Schematic button shows info dialog if Solve has not been run |
| M1-05 | K-Map uses Gray code ordering: rows/cols are 00 01 11 10 |
| M1-06 | Clear button resets canvas, text panel, and status bar |

---

### 6.3 Module 2 — Combinational Circuit Simulator (module2_combinational.py)

#### Supported Circuits
| Circuit | Inputs | Outputs |
|---------|--------|---------|
| Half Adder | A, B | SUM, CARRY |
| Full Adder | A, B, CIN | SUM, COUT |
| Half Subtractor | A, B | DIFF, BORROW |
| Full Subtractor | A, B, BIN | DIFF, BOUT |
| 4-bit Ripple Carry Adder | A0-A3, B0-B3, CIN | SUM0-SUM3, COUT |
| Binary to Gray | B0-B3 (MSB first) | G0-G3 |
| Gray to Binary | G0-G3 (MSB first) | B0-B3 |

#### Functional Rules
| ID | Rule |
|----|------|
| M2-01 | All outputs computed via gate_engine.Circuit.propagate() — no hardcoded arithmetic |
| M2-02 | Rebuild Inputs dynamically recreates toggle switches for the selected circuit |
| M2-03 | Output displayed as colored cards: green = HIGH (1), red = LOW (0) |
| M2-04 | Status bar updates after each Simulate with circuit name and output values |
| M2-05 | 4-bit adder bit order is LSB-first (A0 = least significant) |

---

### 6.4 Module 3 — Sequential Circuit Simulator (module3_sequential.py)

#### Supported Circuits
| Category | Circuits |
|----------|---------|
| Flip-Flops | SR, JK, D, T |
| Shift Registers | 4-bit SISO, SIPO, PISO, PIPO |
| Counters | Async (mod-N), Sync (mod-N), Ring Counter, Johnson Counter |

#### Inputs
| Input | Control | Notes |
|-------|---------|-------|
| Circuit type | Dropdown | Resets history on change |
| Modulus / bit-width | Spinbox (2-16) | Used by counters and ring/Johnson |
| Input 1 | Toggle (0/1) | D for D-FF; S for SR; J for JK; serial-in for shift regs |
| Input 2 | Toggle (0/1) | R for SR; K for JK |
| Clock Pulse | Button | Advances one clock cycle |
| Reset | Button | Clears history, restores initial state |

#### Outputs
| Output | Location |
|--------|----------|
| State text | Label: `Tick N: J=1 K=0 Q=1` |
| Timing diagram | Canvas — grows left-to-right, one column per pulse |
| Binary signals | Drawn as HIGH/LOW step waveform with filled area under HIGH |
| Multi-bit state | Drawn as diamond (hex-style) boxes showing register content |
| Status bar | `Tick 3 | JK Flip-Flop | J=1 K=0 Q=1` |

#### Flip-Flop Truth Tables
**SR:** S=0,R=0 -> Hold | S=0,R=1 -> Reset | S=1,R=0 -> Set | S=1,R=1 -> Invalid
**JK:** J=0,K=0 -> Hold | J=0,K=1 -> Reset | J=1,K=0 -> Set | J=1,K=1 -> Toggle
**D:**  Q(next) = D
**T:**  Q(next) = Q XOR T

---

### 6.5 Module 4 — ASM/FSM & PLA/PAL Simulator (module4_asm_pld.py)

#### Tab 1: FSM / ASM Chart
**Built-in FSM:** Mealy machine detecting consecutive "11" pattern.

| State | Meaning |
|-------|---------|
| S0 | Initial / no '1' seen yet |
| S1 | One '1' seen |
| S2 | Two consecutive '1's -> output = 1 |

| Input | Output |
|-------|--------|
| Input bit radio (0 or 1) | Active state glows green with ACTIVE label |
| Apply Input button | Steps FSM; last-taken arrow highlighted in green |
| Reset button | Returns to S0 |
| Status bar | `FSM Step | Input=1 -> State=S2 | Output=1 | History=4` |

#### Tab 2: PLA / PAL Simulator
| Input | Format |
|-------|--------|
| Number of input variables | Radio (2 / 3 / 4) |
| F1 minterms | Comma-separated: `1,2,3,7` |
| F2 minterms | Comma-separated: `0,3,5,7` |

| Output | Description |
|--------|-------------|
| AND Array columns | True literal and complement per variable |
| OR Array columns | F1 and F2 connection dots |
| Filled dot | Programmed fuse (active connection) |
| Cross (x) | Blown fuse (disconnected) |
| Summary row | `F1 = Sum(1,2,3,7)  |  F2 = Sum(0,3,5,7)` |

---

## 7. Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NF-01 | Compatibility | Works on Windows 10+, Linux (Ubuntu 20+), macOS 12+ |
| NF-02 | Dependencies | Zero external packages — Python stdlib only |
| NF-03 | Startup time | Home window opens in < 2 seconds |
| NF-04 | Responsiveness | Card hover animations run at >= 30 fps (16 ms tick) |
| NF-05 | Resizability | Modules 1, 3, 4 are resizable; canvases respond to window resize |
| NF-06 | Visual consistency | All modules share identical color palette and typography |
| NF-07 | Error handling | Invalid inputs show messagebox.showerror() — never crash |
| NF-08 | Standalone mode | Each module can be run independently |
| NF-09 | Code ownership | Each module has no cross-module imports (except gate_engine) |

---

## 8. Design System

### Color Palette
| Token | Hex | Role |
|-------|-----|------|
| BG_DARK | #0a0f1e | Main background |
| BG_CARD | #111827 | Panel / card background |
| CANVAS_BG | #0d1526 | Canvas drawing area |
| ACCENT_CYAN | #06b6d4 | Module 1 / highlights |
| ACCENT_GREEN | #10b981 | Module 2 / HIGH signal / success |
| ACCENT_PURPLE | #8b5cf6 | Module 3 / waveform |
| ACCENT_AMBER | #f59e0b | Module 4 / don't-cares |
| ACCENT_RED | #ef4444 | LOW signal / errors |
| TEXT_PRIMARY | #f1f5f9 | Main readable text |
| TEXT_SECONDARY | #94a3b8 | Labels, subtitles |
| TEXT_DIM | #475569 | Hints, axis labels |

### Typography
- **Headings:** Segoe UI Bold (16-18 pt)
- **Body / Labels:** Segoe UI Regular (8-10 pt)
- **Code / Values:** Consolas (10-11 pt)
- **Icons:** Segoe UI Emoji (17-22 pt)

---

## 9. Constraints & Assumptions

| Constraint | Detail |
|-----------|--------|
| Platform | Desktop only (no web/mobile) |
| Python version | 3.8 minimum |
| No pip | All imports must be from Python stdlib |
| No persistence | No file save/load for session state (in-session only) |
| FSM is fixed | Module 4 FSM is hardcoded (11-detector Mealy machine) |
| 4-variable limit | K-Map supports maximum 4 variables |

---

## 10. Out of Scope (v1.0)

- Export of timing diagrams or schematics as PNG/SVG
- User-definable custom FSM states and transitions
- Multi-output K-Map minimization
- Gate-delay simulation
- Save/load circuit configurations
- Network/multi-user mode

---

## 11. Success Metrics

| Metric | Target |
|--------|--------|
| All 4 modules launch without error | 100% |
| K-Map Solve produces correct minimized SOP | Verified against manual Karnaugh solutions |
| Full Adder produces correct output for all 8 input combos | 8/8 correct |
| JK Flip-Flop follows truth table for all 4 input combos | 4/4 correct |
| FSM detects "11" correctly for at least 10 input sequences | 10/10 |
| PLA fuse map matches expected AND/OR array | Verified by inspection |

---

## 12. Future Roadmap

| Priority | Feature |
|----------|---------|
| High | Export timing diagram as PNG |
| High | User-editable FSM (custom states + transitions via GUI) |
| Medium | Feed Module 1 SOP into Module 2 to auto-simulate minimized circuits |
| Medium | XOR-based comparators, decoders, encoders in Module 2 |
| Low | Waveform scroll (horizontal scrollbar for long timing diagrams) |
| Low | Dark/Light theme toggle |
| Low | Session save/load (JSON format) |
