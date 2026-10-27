"""
module2_combinational.py
--------------------------
Member 2: Combinational Circuit Simulator (Unit 2A)

All circuits are built using gate_engine.Circuit / Gate so the output
is truly propagated through a gate graph, not hardcoded arithmetic.

Includes:
 - Half Adder, Full Adder
 - Half Subtractor, Full Subtractor
 - 4-bit Binary Adder (ripple carry, like IC 7483)
 - BCD to Excess-3, Binary to Gray, Gray to Binary code converters
 - Back button to return to Home
 - Auto circuit diagram on simulate
 - Knowledge panel for each circuit type
"""

import tkinter as tk
from tkinter import ttk, messagebox
from gate_engine import Circuit, Wire
import math

# ─── Color palette (shared dark theme) ──────────────────────────
BG_DARK        = "#0a0f1e"
BG_CARD        = "#111827"
ACCENT_CYAN    = "#06b6d4"
ACCENT_GREEN   = "#10b981"
ACCENT_RED     = "#ef4444"
ACCENT_AMBER   = "#f59e0b"
ACCENT_PURPLE  = "#8b5cf6"
TEXT_PRIMARY   = "#f1f5f9"
TEXT_SECONDARY = "#94a3b8"
TEXT_DIM       = "#475569"
BORDER_COLOR   = "#1e293b"
CANVAS_BG      = "#0d1526"


# ─── Knowledge content ──────────────────────────────────────────
CIRCUIT_KNOWLEDGE = {
    "Half Adder": {
        "color": ACCENT_CYAN,
        "body": (
            "Half Adder: Adds two 1-bit numbers (A and B).\n\n"
            "Outputs:\n"
            "  SUM   = A XOR B\n"
            "  CARRY = A AND B\n\n"
            "Truth Table:\n"
            "  A  B | SUM  CARRY\n"
            "  0  0 |  0     0\n"
            "  0  1 |  1     0\n"
            "  1  0 |  1     0\n"
            "  1  1 |  0     1\n\n"
            "Limitation: Cannot accept a carry-in from a previous stage.\n"
            "Use a Full Adder for multi-bit addition."
        )
    },
    "Full Adder": {
        "color": ACCENT_GREEN,
        "body": (
            "Full Adder: Adds three 1-bit numbers (A, B, and Carry-In).\n\n"
            "Outputs:\n"
            "  SUM  = A XOR B XOR CIN\n"
            "  COUT = (A AND B) OR (CIN AND (A XOR B))\n\n"
            "Truth Table:\n"
            "  A  B  CIN | SUM  COUT\n"
            "  0  0   0  |  0    0\n"
            "  0  1   0  |  1    0\n"
            "  1  0   0  |  1    0\n"
            "  1  1   0  |  0    1\n"
            "  0  0   1  |  1    0\n"
            "  0  1   1  |  0    1\n"
            "  1  0   1  |  0    1\n"
            "  1  1   1  |  1    1\n\n"
            "Chain multiple Full Adders to build a ripple-carry multi-bit adder."
        )
    },
    "Half Subtractor": {
        "color": ACCENT_AMBER,
        "body": (
            "Half Subtractor: Subtracts B from A (1-bit).\n\n"
            "Outputs:\n"
            "  DIFF   = A XOR B\n"
            "  BORROW = A' AND B  (1 when A < B)\n\n"
            "Truth Table:\n"
            "  A  B | DIFF  BORROW\n"
            "  0  0 |  0      0\n"
            "  0  1 |  1      1  <- borrows!\n"
            "  1  0 |  1      0\n"
            "  1  1 |  0      0\n\n"
            "When A=0 and B=1, result is 0-1 = -1, represented as DIFF=1, BORROW=1."
        )
    },
    "Full Subtractor": {
        "color": ACCENT_RED,
        "body": (
            "Full Subtractor: Subtracts B and Borrow-In from A.\n\n"
            "Outputs:\n"
            "  DIFF = A XOR B XOR BIN\n"
            "  BOUT = A'B + (A XOR B)'*BIN\n\n"
            "Extends the Half Subtractor to handle cascaded borrow from previous stage.\n\n"
            "Application: Used in ALUs (Arithmetic Logic Units) and multi-bit subtraction circuits."
        )
    },
    "4-bit Binary Adder": {
        "color": ACCENT_PURPLE,
        "body": (
            "4-bit Ripple Carry Adder (like IC 7483):\n\n"
            "Adds two 4-bit binary numbers plus a carry-in.\n\n"
            "Structure:\n"
            "  4 Full Adders connected in series.\n"
            "  The COUT of each stage becomes the CIN of the next.\n"
            "  This 'ripple' is why it's called a ripple-carry adder.\n\n"
            "Speed: The carry must ripple through all stages, so delay = 4 * FA delay.\n"
            "For faster addition, use Carry-Lookahead Adders (CLA).\n\n"
            "Inputs: A3..A0 (4-bit), B3..B0 (4-bit), CIN\n"
            "Outputs: SUM3..SUM0 (4-bit result), COUT (overflow carry)"
        )
    },
    "Binary to Gray": {
        "color": ACCENT_CYAN,
        "body": (
            "Binary to Gray Code Converter:\n\n"
            "Gray code (reflected binary code) changes only 1 bit at a time.\n\n"
            "Conversion rule:\n"
            "  G[0] = B[0]  (MSB stays the same)\n"
            "  G[i] = B[i-1] XOR B[i]  (for i > 0)\n\n"
            "Example (4-bit):\n"
            "  Binary 0110 -> Gray 0101\n"
            "  Binary 0111 -> Gray 0100  (only 1 bit changed!)\n\n"
            "Applications:\n"
            "  * Rotary encoders (mechanical position sensors)\n"
            "  * Error detection in digital communications\n"
            "  * K-Map cell ordering uses Gray code!"
        )
    },
    "Gray to Binary": {
        "color": ACCENT_GREEN,
        "body": (
            "Gray to Binary Code Converter:\n\n"
            "Inverse of Binary-to-Gray conversion.\n\n"
            "Conversion rule:\n"
            "  B[0] = G[0]  (MSB stays the same)\n"
            "  B[i] = B[i-1] XOR G[i]  (for i > 0)\n\n"
            "Note: Each binary bit depends on ALL previous bits -- not just adjacent Gray bits.\n\n"
            "Example:\n"
            "  Gray 0101 -> Binary 0110\n"
            "  Gray 0100 -> Binary 0111\n\n"
            "This conversion is used in shaft encoders and position detection systems."
        )
    },
}


def build_half_subtractor(a, b):
    c = Circuit("Half Subtractor")
    A = c.add_input("A", a)
    B = c.add_input("B", b)
    diff = c.add_gate("XOR", [A, B], name="DIFF")
    notA = c.add_gate("NOT", [A], name="notA")
    borrow = c.add_gate("AND", [notA.output, B], name="BORROW")
    c.mark_output("DIFF", diff.output)
    c.mark_output("BORROW", borrow.output)
    return c


def build_full_subtractor(a, b, bin_):
    c = Circuit("Full Subtractor")
    A = c.add_input("A", a)
    B = c.add_input("B", b)
    BIN = c.add_input("BIN", bin_)

    # DIFF = A XOR B XOR BIN
    x1 = c.add_gate("XOR", [A, B], name="x1")
    diff = c.add_gate("XOR", [x1.output, BIN], name="DIFF")

    # BOUT = A'B + A'BIN + B·BIN
    # (three product terms covering all cases where result is negative)
    notA = c.add_gate("NOT", [A], name="notA")
    t1 = c.add_gate("AND", [notA.output, B],   name="t1")   # A'B
    t2 = c.add_gate("AND", [notA.output, BIN], name="t2")   # A'BIN
    t3 = c.add_gate("AND", [B, BIN],           name="t3")   # B·BIN
    bout = c.add_gate("OR", [t1.output, t2.output, t3.output], name="BOUT")

    c.mark_output("DIFF", diff.output)
    c.mark_output("BOUT", bout.output)
    return c


def build_4bit_adder(a_bits, b_bits, cin=0):
    """a_bits, b_bits: list of 4 bits, LSB first. Returns (Circuit, sum_bits, cout)."""
    c = Circuit("4-bit Ripple Carry Adder (7483-style)")
    carry = c.add_input("CIN", cin)
    sum_outputs = []
    for i in range(4):
        A = c.add_input(f"A{i}", a_bits[i])
        B = c.add_input(f"B{i}", b_bits[i])
        x1 = c.add_gate("XOR", [A, B], name=f"xor1_{i}")
        s = c.add_gate("XOR", [x1.output, carry], name=f"SUM{i}")
        and1 = c.add_gate("AND", [A, B], name=f"and1_{i}")
        and2 = c.add_gate("AND", [x1.output, carry], name=f"and2_{i}")
        cout_gate = c.add_gate("OR", [and1.output, and2.output], name=f"carry{i}")
        c.mark_output(f"SUM{i}", s.output)
        sum_outputs.append(s.output)
        carry = cout_gate.output
    c.mark_output("COUT", carry)
    return c


def binary_to_gray_gates(bits):
    """bits: list MSB..LSB. Gray = B xor (B>>1). Built with XOR gates."""
    c = Circuit("Binary to Gray")
    n = len(bits)
    inputs = [c.add_input(f"B{i}", bits[i]) for i in range(n)]
    outputs = [inputs[0]]
    c.mark_output("G0", inputs[0])
    for i in range(1, n):
        g = c.add_gate("XOR", [inputs[i - 1], inputs[i]], name=f"XOR{i}")
        c.mark_output(f"G{i}", g.output)
    return c


def gray_to_binary_gates(bits):
    """bits: list MSB..LSB Gray code -> binary via successive XOR chain."""
    c = Circuit("Gray to Binary")
    n = len(bits)
    inputs = [c.add_input(f"G{i}", bits[i]) for i in range(n)]
    prev = inputs[0]
    c.mark_output("B0", inputs[0])
    for i in range(1, n):
        g = c.add_gate("XOR", [prev, inputs[i]], name=f"XOR{i}")
        c.mark_output(f"B{i}", g.output)
        prev = g.output
    return c


class ToggleSwitch(tk.Canvas):
    """Custom toggle switch widget."""
    def __init__(self, master, variable, label="", **kwargs):
        super().__init__(master, width=56, height=28, bg=BG_CARD,
                         highlightthickness=0, cursor="hand2", **kwargs)
        self.variable = variable
        self.label = label
        self.bind("<Button-1>", self._toggle)
        self.variable.trace_add("write", lambda *a: self._draw())
        self._draw()

    def _toggle(self, e=None):
        self.variable.set(1 - self.variable.get())

    def _draw(self):
        self.delete("all")
        on = self.variable.get() == 1
        track_color = ACCENT_GREEN if on else "#2a3a55"
        self.create_rectangle(2, 4, 54, 24, fill=track_color, outline="", width=0)
        knob_x = 40 if on else 14
        knob_color = TEXT_PRIMARY if on else TEXT_DIM
        self.create_oval(knob_x - 9, 5, knob_x + 9, 23, fill=knob_color, outline="")
        val_text = "1" if on else "0"
        txt_x = 18 if on else 42
        self.create_text(txt_x, 14, text=val_text, font=("Consolas", 8, "bold"),
                         fill=BG_DARK if on else TEXT_DIM)


class KnowledgePanel(tk.Toplevel):
    def __init__(self, master, circuit_name):
        super().__init__(master)
        info = CIRCUIT_KNOWLEDGE.get(circuit_name, {
            "color": ACCENT_CYAN,
            "body": f"No knowledge entry for '{circuit_name}' yet."
        })
        self.title(f"Knowledge: {circuit_name}")
        self.geometry("560x400")
        self.configure(bg=BG_DARK)
        self.resizable(False, False)
        self.lift()
        self.focus_force()

        color = info.get("color", ACCENT_CYAN)

        tk.Frame(self, bg=color, height=4).pack(fill="x")

        hdr2 = tk.Frame(self, bg=BG_CARD)
        hdr2.pack(fill="x")
        tk.Label(hdr2, text=f"  {circuit_name} — How it works",
                 font=("Segoe UI", 13, "bold"), bg=BG_CARD, fg=color).pack(
            pady=10, padx=16, anchor="w")

        tk.Frame(self, bg=color, height=1).pack(fill="x")

        body = tk.Text(self, font=("Consolas", 10), bg=BG_CARD, fg=TEXT_PRIMARY,
                       relief="flat", padx=14, pady=12, wrap="word",
                       highlightthickness=0)
        body.pack(fill="both", expand=True, padx=16, pady=10)
        body.insert("1.0", info["body"])
        body.configure(state="disabled")

        tk.Button(self, text="  Close  ", font=("Segoe UI", 9, "bold"),
                  bg=color, fg=BG_DARK, bd=0, padx=16, pady=6,
                  cursor="hand2", command=self.destroy, relief="flat").pack(pady=8)


class CombinationalModule(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master_ref = master
        self.title("Combinational Circuit Simulator")
        self.geometry("960x720")
        self.configure(bg=BG_DARK)

        # ── Top bar: Back + Header ──
        top_bar = tk.Frame(self, bg=BG_DARK)
        top_bar.pack(fill="x", padx=20, pady=(12, 0))

        back_btn = tk.Button(top_bar, text="<- Back to Home",
                             font=("Segoe UI", 9, "bold"),
                             bg="#1e293b", fg=ACCENT_GREEN,
                             activebackground=ACCENT_GREEN, activeforeground=BG_DARK,
                             bd=0, padx=14, pady=6, cursor="hand2",
                             command=self._go_back, relief="flat")
        back_btn.pack(side="left")
        back_btn.bind("<Enter>", lambda e: back_btn.configure(bg=ACCENT_GREEN, fg=BG_DARK))
        back_btn.bind("<Leave>", lambda e: back_btn.configure(bg="#1e293b", fg=ACCENT_GREEN))

        header_frame = tk.Frame(top_bar, bg=BG_DARK)
        header_frame.pack(side="left", padx=18)
        tk.Label(header_frame, text="[Gate]", font=("Segoe UI", 18),
                 bg=BG_DARK, fg=ACCENT_GREEN).pack(side="left", padx=(0, 10))
        title_f = tk.Frame(header_frame, bg=BG_DARK)
        title_f.pack(side="left")
        tk.Label(title_f, text="Combinational Circuit Simulator",
                 font=("Segoe UI", 17, "bold"), bg=BG_DARK,
                 fg=TEXT_PRIMARY).pack(anchor="w")
        tk.Label(title_f,
                 text="Gate-level simulation  *  Adders  *  Subtractors  *  Code converters  *  Real signal propagation",
                 font=("Segoe UI", 9), bg=BG_DARK, fg=TEXT_SECONDARY).pack(anchor="w")

        # ── Workflow indicator ──
        wf = tk.Frame(self, bg=BG_DARK)
        wf.pack(fill="x", padx=20, pady=(8, 0))
        for num, label, col in [("1", "Pick Circuit", ACCENT_CYAN),
                                  ("2", "Toggle Inputs", ACCENT_GREEN),
                                  ("3", "Simulate", ACCENT_AMBER),
                                  ("4", "See Diagram", ACCENT_PURPLE)]:
            sf = tk.Frame(wf, bg=BG_DARK)
            sf.pack(side="left", padx=2)
            tk.Label(sf, text=f" {num} ", font=("Segoe UI", 8, "bold"),
                     bg=col, fg=BG_DARK).pack(side="left")
            tk.Label(sf, text=f" {label} ", font=("Segoe UI", 8),
                     bg=BG_CARD, fg=TEXT_SECONDARY).pack(side="left")
            if num != "4":
                tk.Label(wf, text=" -> ", font=("Segoe UI", 8),
                         bg=BG_DARK, fg=TEXT_DIM).pack(side="left")

        # ── Circuit selector ──
        sel_panel = tk.Frame(self, bg=BG_CARD, highlightbackground=BORDER_COLOR,
                             highlightthickness=1)
        sel_panel.pack(fill="x", padx=20, pady=10)

        inner_sel = tk.Frame(sel_panel, bg=BG_CARD)
        inner_sel.pack(padx=15, pady=8)

        tk.Label(inner_sel, text="Circuit:", font=("Segoe UI", 10, "bold"),
                 bg=BG_CARD, fg=TEXT_SECONDARY).pack(side="left")

        self.choice = tk.StringVar(value="Full Adder")
        options = ["Half Adder", "Full Adder", "Half Subtractor", "Full Subtractor",
                   "4-bit Binary Adder", "Binary to Gray", "Gray to Binary"]

        combo = ttk.Combobox(inner_sel, textvariable=self.choice, values=options,
                             state="readonly", width=28, font=("Segoe UI", 10))
        combo.pack(side="left", padx=10)

        self._make_btn(inner_sel, "Rebuild", ACCENT_CYAN,
                       self.rebuild_inputs).pack(side="left", padx=5)
        self._make_btn(inner_sel, "Simulate", ACCENT_GREEN,
                       self.simulate).pack(side="left", padx=5)

        # Knowledge button (changes with circuit selection)
        self._know_btn = tk.Button(inner_sel, text="? Learn this circuit",
                                   font=("Segoe UI", 8, "bold"),
                                   bg=BG_CARD, fg=ACCENT_PURPLE, bd=0, padx=10, pady=4,
                                   cursor="hand2", relief="flat",
                                   command=self._show_knowledge)
        self._know_btn.pack(side="left", padx=8)
        self._know_btn.bind("<Enter>",
                            lambda e: self._know_btn.configure(bg=ACCENT_PURPLE, fg=BG_DARK))
        self._know_btn.bind("<Leave>",
                            lambda e: self._know_btn.configure(bg=BG_CARD, fg=ACCENT_PURPLE))

        # ── Input switches panel ──
        self.input_panel = tk.Frame(self, bg=BG_CARD, highlightbackground=BORDER_COLOR,
                                    highlightthickness=1)
        self.input_panel.pack(fill="x", padx=20, pady=(0, 6))

        self.input_inner = tk.Frame(self.input_panel, bg=BG_CARD)
        self.input_inner.pack(padx=15, pady=8)

        tk.Label(self.input_inner, text="  Inputs", font=("Segoe UI", 10, "bold"),
                 bg=BG_CARD, fg=TEXT_SECONDARY).pack(anchor="w")

        self.switches_frame = tk.Frame(self.input_inner, bg=BG_CARD)
        self.switches_frame.pack(pady=4)

        # ── Split: diagram left, result right ──
        content = tk.Frame(self, bg=BG_DARK)
        content.pack(fill="both", expand=True, padx=20, pady=(0, 0))

        # Circuit diagram panel
        diag_panel = tk.Frame(content, bg=BG_CARD, highlightbackground=BORDER_COLOR,
                              highlightthickness=1)
        diag_panel.pack(side="left", fill="both", expand=True, padx=(0, 5))

        diag_hdr = tk.Frame(diag_panel, bg="#0d1526")
        diag_hdr.pack(fill="x")
        tk.Label(diag_hdr, text="  Circuit Diagram", font=("Segoe UI", 10, "bold"),
                 bg="#0d1526", fg=ACCENT_GREEN, anchor="w").pack(side="left", padx=10, pady=7)
        tk.Label(diag_hdr, text="(auto-updates on Simulate)",
                 font=("Segoe UI", 8), bg="#0d1526", fg=TEXT_DIM).pack(side="left")

        self.diag_canvas = tk.Canvas(diag_panel, bg=CANVAS_BG, highlightthickness=0)
        self.diag_canvas.pack(fill="both", expand=True, padx=8, pady=8)
        self.diag_canvas.bind("<Configure>", self._draw_diag_placeholder)

        # Simulation result panel
        result_panel = tk.Frame(content, bg=BG_CARD, highlightbackground=BORDER_COLOR,
                                highlightthickness=1)
        result_panel.pack(side="left", fill="both", expand=True, padx=(5, 0))

        res_hdr = tk.Frame(result_panel, bg="#0d1526")
        res_hdr.pack(fill="x")
        tk.Label(res_hdr, text="  Simulation Output", font=("Segoe UI", 10, "bold"),
                 bg="#0d1526", fg=ACCENT_CYAN, anchor="w").pack(side="left", padx=10, pady=7)

        self.canvas = tk.Canvas(result_panel, bg=CANVAS_BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=8, pady=8)

        self.entries = {}
        self._last_outputs = {}
        self._last_choice = ""
        self.rebuild_inputs()

        # Status bar
        self._status = tk.Label(self,
                                text="  Ready  *  Select a circuit and click Simulate",
                                font=("Segoe UI", 8), bg="#0d1526",
                                fg=TEXT_SECONDARY, anchor="w", pady=5)
        self._status.pack(fill="x", side="bottom")

    def _go_back(self):
        self.destroy()
        try:
            self.master_ref.deiconify()
        except Exception:
            pass

    def _show_knowledge(self):
        KnowledgePanel(self, self.choice.get())

    def _draw_diag_placeholder(self, e=None):
        if self._last_outputs:
            return
        c = self.diag_canvas
        c.delete("placeholder")
        w, h = c.winfo_width(), c.winfo_height()
        if w < 10:
            return
        c.create_text(w // 2, h // 2 - 14, text="[Circuit]",
                      font=("Segoe UI", 20), fill=TEXT_DIM, tags="placeholder")
        c.create_text(w // 2, h // 2 + 20,
                      text="Circuit diagram will appear after Simulate",
                      font=("Segoe UI", 9), fill=TEXT_DIM, tags="placeholder")

    def _make_btn(self, parent, text, color, command):
        btn = tk.Button(parent, text=text, font=("Segoe UI", 10, "bold"),
                        bg=color, fg="#050a14", activebackground=TEXT_PRIMARY,
                        activeforeground="#050a14", bd=0, padx=14, pady=6,
                        cursor="hand2", command=command, relief="flat")
        btn.bind("<Enter>", lambda e: btn.configure(bg=TEXT_PRIMARY))
        btn.bind("<Leave>", lambda e: btn.configure(bg=color))
        return btn

    def rebuild_inputs(self):
        for w in self.switches_frame.winfo_children():
            w.destroy()
        self.entries = {}
        self._last_outputs = {}
        choice = self.choice.get()

        if choice in ("Half Adder", "Half Subtractor"):
            labels = ["A", "B"]
        elif choice in ("Full Adder", "Full Subtractor"):
            labels = ["A", "B", "CIN" if "Adder" in choice else "BIN"]
        elif choice == "4-bit Binary Adder":
            labels = [f"A{i}" for i in range(4)] + [f"B{i}" for i in range(4)] + ["CIN"]
        else:
            labels = [f"bit{i}" for i in range(4)]

        for i, lbl in enumerate(labels):
            frame = tk.Frame(self.switches_frame, bg=BG_CARD)
            frame.pack(side="left", padx=8, pady=3)

            tk.Label(frame, text=lbl, font=("Consolas", 10, "bold"),
                     bg=BG_CARD, fg=ACCENT_CYAN).pack()

            var = tk.IntVar(value=0)
            sw = ToggleSwitch(frame, var, label=lbl)
            sw.pack(pady=2)

            self.entries[lbl] = var

        self.diag_canvas.after(100, self._draw_diag_placeholder)

    def simulate(self):
        choice = self.choice.get()
        self.canvas.delete("all")
        outputs = {}

        if choice == "Half Adder":
            from gate_engine import build_half_adder
            c = build_half_adder(self.entries["A"].get(), self.entries["B"].get())
            c.propagate()
            outputs = c.get_all_outputs()
        elif choice == "Full Adder":
            from gate_engine import build_full_adder
            c = build_full_adder(self.entries["A"].get(), self.entries["B"].get(),
                                 self.entries["CIN"].get())
            c.propagate()
            outputs = c.get_all_outputs()
        elif choice == "Half Subtractor":
            c = build_half_subtractor(self.entries["A"].get(), self.entries["B"].get())
            c.propagate()
            outputs = c.get_all_outputs()
        elif choice == "Full Subtractor":
            c = build_full_subtractor(self.entries["A"].get(), self.entries["B"].get(),
                                      self.entries["BIN"].get())
            c.propagate()
            outputs = c.get_all_outputs()
        elif choice == "4-bit Binary Adder":
            a_bits = [self.entries[f"A{i}"].get() for i in range(4)]
            b_bits = [self.entries[f"B{i}"].get() for i in range(4)]
            cin = self.entries["CIN"].get()
            c = build_4bit_adder(a_bits, b_bits, cin)
            c.propagate()
            outputs = c.get_all_outputs()
        elif choice == "Binary to Gray":
            bits = [self.entries[f"bit{i}"].get() for i in range(4)]
            c = binary_to_gray_gates(bits)
            c.propagate()
            outputs = c.get_all_outputs()
        elif choice == "Gray to Binary":
            bits = [self.entries[f"bit{i}"].get() for i in range(4)]
            c = gray_to_binary_gates(bits)
            c.propagate()
            outputs = c.get_all_outputs()

        self._last_outputs = outputs
        self._last_choice = choice
        self.draw_result(choice, outputs)
        self.after(50, lambda: self.draw_circuit_diagram(choice, outputs))

    def draw_result(self, choice, outputs):
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()

        self.canvas.create_text(cw // 2, 22, text=f"{choice} — Gate-Level Result",
                                 font=("Segoe UI", 13, "bold"), fill=TEXT_PRIMARY)

        input_text = "Inputs:  " + "   ".join(
            f"{k}={v.get()}" for k, v in self.entries.items()
        )
        self.canvas.create_text(cw // 2, 46, text=input_text,
                                 font=("Consolas", 9), fill=TEXT_DIM)

        num_outputs = len(outputs)
        card_w = min(160, (cw - 60) // max(num_outputs, 1))
        card_h = 80
        total_w = num_outputs * card_w + (num_outputs - 1) * 15
        start_x = (cw - total_w) // 2
        y0 = 75

        for i, (k, v) in enumerate(outputs.items()):
            x = start_x + i * (card_w + 15)
            is_high = v == 1

            bg_color = "#1a4a3a" if is_high else "#3a1a1a"
            border_color = ACCENT_GREEN if is_high else ACCENT_RED
            self.canvas.create_rectangle(x, y0, x + card_w, y0 + card_h,
                                          fill=bg_color, outline=border_color, width=2)

            self.canvas.create_text(x + card_w // 2, y0 + 22, text=k,
                                     font=("Segoe UI", 10, "bold"), fill=TEXT_SECONDARY)

            val_color = ACCENT_GREEN if is_high else ACCENT_RED
            self.canvas.create_text(x + card_w // 2, y0 + 52, text=str(v),
                                     font=("Segoe UI", 20, "bold"), fill=val_color)

            dot_color = ACCENT_GREEN if is_high else ACCENT_RED
            self.canvas.create_oval(x + card_w - 15, y0 + 6,
                                     x + card_w - 7, y0 + 14,
                                     fill=dot_color, outline="")

        gate_y = y0 + card_h + 30
        self.canvas.create_text(cw // 2, gate_y, text=f"Circuit: {choice}",
                                 font=("Segoe UI", 10, "bold"), fill=TEXT_SECONDARY)

        tt_y = gate_y + 22
        self.canvas.create_text(cw // 2, tt_y,
                                 text="Output verified via gate-level propagation",
                                 font=("Segoe UI", 8, "italic"), fill=TEXT_DIM)

        tt_y2 = tt_y + 18
        self.canvas.create_text(cw // 2, tt_y2,
                                 text="Click '? Learn this circuit' for theory & truth table",
                                 font=("Segoe UI", 8, "italic"), fill=ACCENT_PURPLE)

        out_summary = "  ".join(f"{k}={v}" for k, v in outputs.items())
        if hasattr(self, '_status'):
            self._status.config(text=f"  Simulated: {choice}  |  {out_summary}",
                                fg=ACCENT_GREEN)

    def draw_circuit_diagram(self, choice, outputs):
        """Draw a simple schematic diagram for the selected circuit."""
        c = self.diag_canvas
        c.delete("all")
        cw = c.winfo_width()
        ch = c.winfo_height()
        if cw < 50:
            return

        inputs = {k: v.get() for k, v in self.entries.items()}

        # Title
        c.create_text(cw // 2, 18, text=f"{choice} — Schematic",
                      font=("Segoe UI", 11, "bold"), fill=TEXT_PRIMARY)

        if choice in ("Half Adder", "Full Adder", "Half Subtractor", "Full Subtractor"):
            self._draw_adder_sub_diagram(c, choice, inputs, outputs, cw, ch)
        elif choice == "4-bit Binary Adder":
            self._draw_4bit_adder_diagram(c, inputs, outputs, cw, ch)
        elif choice in ("Binary to Gray", "Gray to Binary"):
            self._draw_code_converter_diagram(c, choice, inputs, outputs, cw, ch)

    def _draw_gate(self, c, x, y, w, h, label, color, in_vals=None, out_val=None):
        """Draw a single gate box."""
        c.create_rectangle(x, y, x + w, y + h, fill=BG_CARD, outline=color, width=2)
        c.create_text(x + w // 2, y + h // 2, text=label,
                      font=("Segoe UI", 9, "bold"), fill=color)
        if out_val is not None:
            dot_c = ACCENT_GREEN if out_val == 1 else ACCENT_RED
            c.create_oval(x + w + 5, y + h // 2 - 5,
                          x + w + 15, y + h // 2 + 5,
                          fill=dot_c, outline="")

    def _draw_wire(self, c, x0, y0, x1, y1, val):
        color = ACCENT_GREEN if val == 1 else "#2a3a55"
        c.create_line(x0, y0, x1, y1, fill=color, width=2)

    def _draw_adder_sub_diagram(self, c, choice, inputs, outputs, cw, ch):
        ox = 60
        oy = 50
        gw, gh = 70, 30

        # Determine gate structure based on circuit
        if choice == "Half Adder":
            gates = [("XOR", ACCENT_CYAN, "SUM"), ("AND", ACCENT_GREEN, "CARRY")]
            in_labels = ["A", "B"]
        elif choice == "Full Adder":
            gates = [("XOR1", ACCENT_CYAN, ""), ("XOR2", ACCENT_CYAN, "SUM"),
                     ("AND1", ACCENT_GREEN, ""), ("AND2", ACCENT_GREEN, ""),
                     ("OR", ACCENT_AMBER, "COUT")]
            in_labels = ["A", "B", "CIN"]
        elif choice == "Half Subtractor":
            gates = [("XOR", ACCENT_AMBER, "DIFF"), ("NOT", ACCENT_RED, ""),
                     ("AND", ACCENT_RED, "BORROW")]
            in_labels = ["A", "B"]
        else:  # Full Subtractor
            gates = [("XOR1", ACCENT_AMBER, ""), ("XOR2", ACCENT_AMBER, "DIFF"),
                     ("NOT", ACCENT_RED, ""), ("AND1", ACCENT_RED, ""),
                     ("AND2", ACCENT_RED, ""), ("OR", ACCENT_RED, "BOUT")]
            in_labels = ["A", "B", "BIN"]

        # Draw input signals
        for i, lbl in enumerate(in_labels):
            iy = oy + i * 45
            val = inputs.get(lbl, 0)
            dot_c = ACCENT_GREEN if val == 1 else ACCENT_RED
            c.create_oval(ox - 12, iy - 6, ox, iy + 6, fill=dot_c, outline="")
            c.create_text(ox - 20, iy, text=lbl, anchor="e",
                          font=("Consolas", 10, "bold"), fill=dot_c)
            c.create_line(ox, iy, ox + 50, iy, fill=dot_c, width=2)

        # Draw output gates (simplified 2-gate view)
        out_items = list(outputs.items())
        for gi, (out_name, out_val) in enumerate(out_items):
            gx = ox + 80
            gy = oy + gi * 70

            gate_color = ACCENT_GREEN if out_val == 1 else ACCENT_RED
            c.create_rectangle(gx, gy, gx + gw, gy + gh,
                               fill=BG_CARD, outline=gate_color, width=2)
            c.create_text(gx + gw // 2, gy + gh // 2,
                          text=out_name, font=("Segoe UI", 9, "bold"), fill=gate_color)

            # Output wire
            c.create_line(gx + gw, gy + gh // 2,
                          gx + gw + 60, gy + gh // 2,
                          fill=gate_color, width=2)

            out_dot_c = ACCENT_GREEN if out_val == 1 else ACCENT_RED
            c.create_oval(gx + gw + 55, gy + gh // 2 - 8,
                          gx + gw + 71, gy + gh // 2 + 8,
                          fill=out_dot_c, outline="")
            c.create_text(gx + gw + 80, gy + gh // 2, text=str(out_val),
                          font=("Consolas", 11, "bold"), fill=out_dot_c)
            c.create_text(gx + gw + 95, gy + gh // 2, text=out_name,
                          anchor="w", font=("Segoe UI", 8), fill=TEXT_SECONDARY)

        # Input wire connections
        for i, lbl in enumerate(in_labels):
            iy = oy + i * 45
            val = inputs.get(lbl, 0)
            dot_c = ACCENT_GREEN if val == 1 else "#2a3a55"
            for gi in range(len(out_items)):
                gy = oy + gi * 70 + gh // 2
                c.create_line(ox + 50, iy, ox + 80, gy,
                              fill=dot_c, width=1, dash=(3, 4))

        # Legend
        ly = ch - 30
        c.create_text(20, ly, text="Green wire = HIGH (1)   Red/Dark = LOW (0)",
                      anchor="w", font=("Segoe UI", 8, "italic"), fill=TEXT_DIM)

    def _draw_4bit_adder_diagram(self, c, inputs, outputs, cw, ch):
        ox = 30
        oy = 40
        gw, gh = 60, 40
        spacing = (cw - ox * 2 - gw) // 4

        for i in range(4):
            gx = ox + i * spacing
            gy = oy + 30

            a_val = inputs.get(f"A{i}", 0)
            b_val = inputs.get(f"B{i}", 0)
            sum_val = outputs.get(f"SUM{i}", 0)

            gc = ACCENT_GREEN if sum_val == 1 else ACCENT_CYAN

            # Stage box
            c.create_rectangle(gx, gy, gx + gw, gy + gh,
                               fill=BG_CARD, outline=gc, width=2)
            c.create_text(gx + gw // 2, gy + 10, text=f"FA{i}",
                          font=("Segoe UI", 8, "bold"), fill=gc)
            c.create_text(gx + gw // 2, gy + 26,
                          text=f"A{i}={a_val} B{i}={b_val}",
                          font=("Consolas", 7), fill=TEXT_DIM)

            # Input wires
            c.create_line(gx + gw // 2 - 10, gy - 20, gx + gw // 2 - 10, gy,
                          fill=ACCENT_GREEN if a_val else "#2a3a55", width=2)
            c.create_text(gx + gw // 2 - 10, gy - 28, text=f"A{i}={a_val}",
                          font=("Consolas", 7), fill=TEXT_SECONDARY)
            c.create_line(gx + gw // 2 + 10, gy - 20, gx + gw // 2 + 10, gy,
                          fill=ACCENT_GREEN if b_val else "#2a3a55", width=2)
            c.create_text(gx + gw // 2 + 10, gy - 28, text=f"B{i}={b_val}",
                          font=("Consolas", 7), fill=TEXT_SECONDARY)

            # Sum output
            sum_c = ACCENT_GREEN if sum_val == 1 else ACCENT_RED
            c.create_line(gx + gw // 2, gy + gh, gx + gw // 2, gy + gh + 25,
                          fill=sum_c, width=2)
            c.create_text(gx + gw // 2, gy + gh + 36,
                          text=f"S{i}={sum_val}",
                          font=("Consolas", 9, "bold"), fill=sum_c)

            # Carry wire
            if i < 3:
                c.create_line(gx + gw, gy + gh // 2, gx + spacing, gy + gh // 2,
                              fill=ACCENT_AMBER, width=2, dash=(4, 3))

        # COUT
        cout_val = outputs.get("COUT", 0)
        cout_c = ACCENT_GREEN if cout_val == 1 else ACCENT_RED
        last_x = ox + 3 * spacing + gw
        c.create_text(last_x + 20, oy + 50, text=f"COUT={cout_val}",
                      font=("Consolas", 10, "bold"), fill=cout_c)

        # Legend
        c.create_text(30, ch - 25, text="FA = Full Adder stage   Dashed = carry ripple",
                      anchor="w", font=("Segoe UI", 8, "italic"), fill=TEXT_DIM)

    def _draw_code_converter_diagram(self, c, choice, inputs, outputs, cw, ch):
        n = 4
        ox = 60
        oy = 50
        spacing = min(100, (cw - 160) // n)

        in_labels = [f"bit{i}" for i in range(n)] if choice == "Binary to Gray" \
            else [f"bit{i}" for i in range(n)]

        out_labels = list(outputs.keys())

        for i in range(n):
            x = ox + i * spacing
            in_lbl = in_labels[i] if i < len(in_labels) else ""
            in_val = inputs.get(in_lbl, 0)
            in_c = ACCENT_GREEN if in_val == 1 else ACCENT_RED

            # Input
            c.create_oval(x - 8, oy - 8, x + 8, oy + 8, fill=in_c, outline="")
            c.create_text(x, oy - 22, text=f"B{i}={in_val}" if "Binary to Gray" in choice
                          else f"G{i}={in_val}",
                          font=("Consolas", 9, "bold"), fill=in_c)

            # XOR gate (except first)
            gy = oy + 60
            if i == 0:
                # Wire through
                c.create_line(x, oy + 8, x, gy + 30, fill=in_c, width=2)
            else:
                c.create_rectangle(x - 22, gy, x + 22, gy + 28,
                                   fill=BG_CARD, outline=ACCENT_CYAN, width=2)
                c.create_text(x, gy + 14, text="XOR",
                              font=("Segoe UI", 7, "bold"), fill=ACCENT_CYAN)
                c.create_line(x, oy + 8, x, gy, fill=in_c, width=2, dash=(2, 3))

            # Output
            if i < len(out_labels):
                out_val = outputs.get(out_labels[i], 0)
                out_c = ACCENT_GREEN if out_val == 1 else ACCENT_RED
                c.create_text(x, gy + 52,
                              text=f"{out_labels[i]}={out_val}",
                              font=("Consolas", 9, "bold"), fill=out_c)
                c.create_line(x, gy + 28, x, gy + 42, fill=out_c, width=2)
                c.create_oval(x - 7, gy + 42, x + 7, gy + 56, fill=out_c, outline="")

        c.create_text(cw // 2, ch - 25,
                      text=f"{choice}: Adjacent bits XOR'd to convert  (G[i] = B[i-1] XOR B[i])",
                      font=("Segoe UI", 8, "italic"), fill=TEXT_DIM)


def launch(master=None):
    root = master if master else tk.Tk()
    if master is None:
        root.withdraw()
    CombinationalModule(root)
    if master is None:
        root.mainloop()


if __name__ == "__main__":
    launch()
