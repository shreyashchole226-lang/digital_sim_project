"""
module4_asm_pld.py
--------------------
Member 4: ASM & PLD Simulator (Unit 3)

Features:
 - Define a simple FSM (states, transitions on input 0/1, outputs)
 - Auto-draw an ASM-style chart (state boxes + decision diamonds)
 - Step through FSM: click "Apply Input" to move state-by-state,
   current state highlighted
 - PLA/PAL simulator: enter Boolean functions as minterms, tool shows
   which AND-OR array connections ("fuses") would be programmed,
   and lets user verify outputs against a truth table
 - Back button to return to Home
 - Knowledge panel for FSM and PLA concepts
"""

import tkinter as tk
from tkinter import ttk, messagebox
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

# state colors for FSM
STATE_COLORS = ["#38bdf8", "#34d399", "#a78bfa", "#fbbf24", "#f87171",
                "#60a5fa", "#fb923c", "#e879f9"]
STATE_ACTIVE  = "#34d399"
STATE_INACTIVE = "#1e2e4a"

# ─── Knowledge content ───────────────────────────────────────────
ASM_KNOWLEDGE = {
    "fsm": {
        "title": "FSM / ASM Chart",
        "color": ACCENT_CYAN,
        "body": (
            "FSM (Finite State Machine) / ASM (Algorithmic State Machine):\n\n"
            "An FSM consists of:\n"
            "  * A finite set of STATES\n"
            "  * INPUTS that cause transitions between states\n"
            "  * OUTPUTS produced in each state or on transitions\n"
            "  * A START state\n\n"
            "Types:\n"
            "  * Moore Machine: outputs depend only on current state\n"
            "  * Mealy Machine: outputs depend on state AND current input\n\n"
            "This example: Sequence detector for '11' (Mealy)\n"
            "  S0 --(1)--> S1 --(1)--> S2 (output=1, pattern detected!)\n"
            "  Any 0 input returns to S0\n\n"
            "ASM charts use boxes (states) and diamonds (decision points).\n"
            "They are equivalent to flowcharts but specifically for hardware."
        )
    },
    "pla": {
        "title": "PLA / PAL (Programmable Logic)",
        "color": ACCENT_AMBER,
        "body": (
            "PLA (Programmable Logic Array):\n\n"
            "A PLA has two programmable planes:\n"
            "  1. AND Array: Creates product terms (minterms)\n"
            "  2. OR Array: Combines product terms into output functions\n\n"
            "Programming:\n"
            "  * Intact fuse (filled dot) = connection active\n"
            "  * Blown fuse (x) = disconnected\n\n"
            "PAL (Programmable Array Logic):\n"
            "  * AND array is programmable (same as PLA)\n"
            "  * OR array is FIXED (each output has a fixed set of AND gates)\n\n"
            "Fuse Map:\n"
            "  Rows = product terms (AND gates)\n"
            "  Columns = input literals (true and complement)\n"
            "  Circles = programmed connections\n"
            "  x = blown fuse (no connection)\n\n"
            "Modern equivalents: CPLD, FPGA."
        )
    },
}


class KnowledgePanel(tk.Toplevel):
    def __init__(self, master, topic_key):
        super().__init__(master)
        info = ASM_KNOWLEDGE.get(topic_key, {
            "title": "Info", "color": ACCENT_CYAN,
            "body": "No knowledge entry."
        })
        self.title("Knowledge: " + info["title"])
        self.geometry("560x420")
        self.configure(bg=BG_DARK)
        self.resizable(False, False)
        self.lift()
        self.focus_force()

        color = info.get("color", ACCENT_CYAN)

        tk.Frame(self, bg=color, height=4).pack(fill="x")
        hdr2 = tk.Frame(self, bg=BG_CARD)
        hdr2.pack(fill="x")
        tk.Label(hdr2, text=f"  {info['title']} -- Theory",
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


# ────────────── FSM Engine ──────────────

class FSM:
    """
    transitions: dict[(state, input_bit)] = (next_state, output_bit)
    """
    def __init__(self, states, start_state, transitions):
        self.states = states
        self.start_state = start_state
        self.current = start_state
        self.transitions = transitions
        self.history = [start_state]

    def step(self, input_bit):
        key = (self.current, input_bit)
        if key not in self.transitions:
            return None, None
        nxt, out = self.transitions[key]
        self.current = nxt
        self.history.append(nxt)
        return nxt, out

    def reset(self):
        self.current = self.start_state
        self.history = [self.start_state]


def default_fsm():
    """Simple example: sequence detector for '11' using Moore-ish FSM."""
    states = ["S0", "S1", "S2"]
    transitions = {
        ("S0", 0): ("S0", 0),
        ("S0", 1): ("S1", 0),
        ("S1", 0): ("S0", 0),
        ("S1", 1): ("S2", 1),
        ("S2", 0): ("S0", 0),
        ("S2", 1): ("S2", 1),
    }
    return FSM(states, "S0", transitions)


# ────────────── GUI ──────────────

class ASMPLDModule(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master_ref = master
        self.title("ASM/FSM & PLA-PAL Simulator")
        self.geometry("1050x780")
        self.configure(bg=BG_DARK)

        # ── Back button + header ──
        top_bar = tk.Frame(self, bg=BG_DARK)
        top_bar.pack(fill="x", padx=20, pady=(12, 0))

        back_btn = tk.Button(top_bar, text="<- Back to Home",
                             font=("Segoe UI", 9, "bold"),
                             bg="#1e293b", fg=ACCENT_AMBER,
                             activebackground=ACCENT_AMBER, activeforeground=BG_DARK,
                             bd=0, padx=14, pady=6, cursor="hand2",
                             command=self._go_back, relief="flat")
        back_btn.pack(side="left")
        back_btn.bind("<Enter>", lambda e: back_btn.configure(bg=ACCENT_AMBER, fg=BG_DARK))
        back_btn.bind("<Leave>", lambda e: back_btn.configure(bg="#1e293b", fg=ACCENT_AMBER))

        hf = tk.Frame(top_bar, bg=BG_DARK)
        hf.pack(side="left", padx=18)
        tk.Label(hf, text="[FSM]", font=("Segoe UI", 18),
                 bg=BG_DARK, fg=ACCENT_AMBER).pack(side="left", padx=(0, 10))
        tf = tk.Frame(hf, bg=BG_DARK)
        tf.pack(side="left")
        tk.Label(tf, text="ASM/FSM & PLA-PAL Simulator",
                 font=("Segoe UI", 17, "bold"), bg=BG_DARK,
                 fg=TEXT_PRIMARY).pack(anchor="w")
        tk.Label(tf,
                 text="State machines  *  ASM/FSM charts  *  PLA fuse programming  *  Sequence detection",
                 font=("Segoe UI", 9), bg=BG_DARK, fg=TEXT_SECONDARY).pack(anchor="w")

        # Knowledge buttons
        know_row = tk.Frame(self, bg=BG_DARK)
        know_row.pack(fill="x", padx=20, pady=(6, 0))
        tk.Label(know_row, text="Learn:", font=("Segoe UI", 9, "bold"),
                 bg=BG_DARK, fg=TEXT_DIM).pack(side="left")
        for label, key, color in [("  FSM / ASM  ", "fsm", ACCENT_CYAN),
                                    ("  PLA / PAL  ", "pla", ACCENT_AMBER)]:
            b = tk.Button(know_row, text="? " + label, font=("Segoe UI", 8, "bold"),
                          bg=BG_CARD, fg=color, bd=0, padx=10, pady=3,
                          cursor="hand2", relief="flat",
                          command=lambda k=key: KnowledgePanel(self, k))
            b.pack(side="left", padx=4)
            b.bind("<Enter>", lambda e, btn=b, c=color: btn.configure(bg=c, fg=BG_DARK))
            b.bind("<Leave>", lambda e, btn=b, c=color: btn.configure(bg=BG_CARD, fg=c))



        # ── Workflow indicator ──
        wf = tk.Frame(self, bg=BG_DARK)
        wf.pack(fill="x", padx=20, pady=(6, 0))
        for num, label, col in [("1", "FSM: Pick Input", ACCENT_CYAN),
                                 ("2", "Apply Input", ACCENT_AMBER),
                                 ("3", "PLA: Set Minterms", ACCENT_PURPLE),
                                 ("4", "Program PLA", ACCENT_GREEN)]:
            sf = tk.Frame(wf, bg=BG_DARK)
            sf.pack(side="left", padx=2)
            tk.Label(sf, text=f" {num} ", font=("Segoe UI", 8, "bold"),
                     bg=col, fg=BG_DARK).pack(side="left")
            tk.Label(sf, text=f" {label} ", font=("Segoe UI", 8),
                     bg=BG_CARD, fg=TEXT_SECONDARY).pack(side="left")
            if num != "4":
                tk.Label(wf, text=" * ", font=("Segoe UI", 8),
                         bg=BG_DARK, fg=TEXT_DIM).pack(side="left")

        # ── Tab notebook (custom styled) ──
        style = ttk.Style()
        style.configure("Dark.TNotebook", background=BG_DARK)
        style.configure("Dark.TNotebook.Tab", background=BG_CARD,
                        foreground=TEXT_PRIMARY, padding=[15, 6],
                        font=("Segoe UI", 10, "bold"))
        style.map("Dark.TNotebook.Tab",
                  background=[("selected", ACCENT_AMBER)],
                  foreground=[("selected", BG_DARK)])

        notebook = ttk.Notebook(self, style="Dark.TNotebook")
        notebook.pack(fill="both", expand=True, padx=20, pady=12)

        self.fsm_tab = tk.Frame(notebook, bg=BG_DARK)
        self.pld_tab = tk.Frame(notebook, bg=BG_DARK)
        notebook.add(self.fsm_tab, text="  FSM / ASM Chart  ")
        notebook.add(self.pld_tab, text="  PLA / PAL Simulator  ")

        self.build_fsm_tab()
        self.build_pld_tab()

    def _go_back(self):
        self.destroy()
        try:
            self.master_ref.deiconify()
        except Exception:
            pass

    def _make_btn(self, parent, text, color, command):
        btn = tk.Button(parent, text=text, font=("Segoe UI", 10, "bold"),
                        bg=color, fg="#050a14", activebackground=TEXT_PRIMARY,
                        activeforeground="#050a14", bd=0, padx=14, pady=6,
                        cursor="hand2", command=command, relief="flat")
        btn.bind("<Enter>", lambda e: btn.configure(bg=TEXT_PRIMARY))
        btn.bind("<Leave>", lambda e: btn.configure(bg=color))
        return btn

    # ──────── FSM TAB ────────
    def build_fsm_tab(self):
        # info bar
        info = tk.Frame(self.fsm_tab, bg=BG_CARD, highlightbackground=BORDER_COLOR,
                        highlightthickness=1)
        info.pack(fill="x", padx=10, pady=(10, 5))

        info_inner = tk.Frame(info, bg=BG_CARD)
        info_inner.pack(padx=12, pady=8)

        tk.Label(info_inner,
                 text="📋 Example: Sequence detector for pattern '11' (Mealy machine)",
                 font=("Segoe UI", 10), bg=BG_CARD,
                 fg=ACCENT_CYAN).pack(side="left")

        # controls
        ctrl = tk.Frame(self.fsm_tab, bg=BG_CARD, highlightbackground=BORDER_COLOR,
                        highlightthickness=1)
        ctrl.pack(fill="x", padx=10, pady=5)

        ctrl_inner = tk.Frame(ctrl, bg=BG_CARD)
        ctrl_inner.pack(padx=12, pady=8)

        tk.Label(ctrl_inner, text="Next input:", font=("Segoe UI", 10, "bold"),
                 bg=BG_CARD, fg=TEXT_SECONDARY).pack(side="left")

        self.input_bit_var = tk.IntVar(value=1)
        for val, text in [(0, "0"), (1, "1")]:
            rb = tk.Radiobutton(ctrl_inner, text=text, variable=self.input_bit_var,
                                value=val, font=("Consolas", 11, "bold"),
                                bg=BG_CARD, fg=TEXT_PRIMARY,
                                selectcolor=BG_DARK,
                                activebackground=BG_CARD,
                                activeforeground=ACCENT_CYAN,
                                indicatoron=0, padx=12, pady=3, bd=0,
                                highlightthickness=1,
                                highlightbackground=BORDER_COLOR)
            rb.pack(side="left", padx=3)

        self._make_btn(ctrl_inner, "⚡ Apply Input", ACCENT_CYAN,
                       self.fsm_step).pack(side="left", padx=(15, 5))
        self._make_btn(ctrl_inner, "🔄 Reset", ACCENT_AMBER,
                       self.fsm_reset).pack(side="left", padx=5)

        # status
        self.fsm_status = tk.Label(self.fsm_tab, text="", font=("Consolas", 11),
                                   bg=BG_DARK, fg=ACCENT_GREEN)
        self.fsm_status.pack(pady=5, padx=10, anchor="w")

        # FSM canvas
        canvas_panel = tk.Frame(self.fsm_tab, bg=BG_CARD,
                                highlightbackground=BORDER_COLOR,
                                highlightthickness=1)
        canvas_panel.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        tk.Label(canvas_panel, text="  State Diagram", font=("Segoe UI", 10, "bold"),
                 bg=BG_CARD, fg=TEXT_SECONDARY).pack(anchor="w", padx=10, pady=(8, 0))

        self.fsm_canvas = tk.Canvas(canvas_panel, bg=CANVAS_BG, highlightthickness=0)
        self.fsm_canvas.pack(fill="both", expand=True, padx=8, pady=8)

        self.fsm = default_fsm()
        self.state_positions = {"S0": (180, 140), "S1": (480, 140), "S2": (780, 140)}
        self.draw_asm_chart()

    def draw_asm_chart(self):
        self.fsm_canvas.delete("all")
        r = 50

        # draw connecting lines first (behind circles)
        for (s_from, bit), (s_to, out) in self.fsm.transitions.items():
            self._draw_transition(s_from, s_to, f"{bit}/{out}", r)

        # draw state circles
        for i, (s, (x, y)) in enumerate(self.state_positions.items()):
            is_current = (s == self.fsm.current)
            color = STATE_COLORS[i % len(STATE_COLORS)]

            if is_current:
                # outer glow ring
                for offset in range(8, 0, -2):
                    alpha_hex = format(int(30 + offset * 8), '02x')
                    glow_color = color[:7]
                    self.fsm_canvas.create_oval(
                        x - r - offset, y - r - offset,
                        x + r + offset, y + r + offset,
                        outline=color, width=1
                    )

                # filled circle
                self.fsm_canvas.create_oval(x - r, y - r, x + r, y + r,
                                             fill="#1a4a3a", outline=ACCENT_GREEN, width=3)
            else:
                self.fsm_canvas.create_oval(x - r, y - r, x + r, y + r,
                                             fill=STATE_INACTIVE, outline=color, width=2)

            # state name
            self.fsm_canvas.create_text(x, y, text=s,
                                         font=("Segoe UI", 15, "bold"),
                                         fill=TEXT_PRIMARY if is_current else color)

            # active indicator
            if is_current:
                self.fsm_canvas.create_text(x, y + r + 18, text="● ACTIVE",
                                             font=("Segoe UI", 8, "bold"),
                                             fill=ACCENT_GREEN)

        # update status
        hist_text = " → ".join(self.fsm.history[-8:])  # last 8 states
        if len(self.fsm.history) > 8:
            hist_text = "... → " + hist_text
        self.fsm_status.config(
            text=f"  Current: {self.fsm.current}   │   History: {hist_text}"
        )

    def _draw_transition(self, s_from, s_to, label, r):
        x0, y0 = self.state_positions[s_from]
        x1, y1 = self.state_positions[s_to]

        color = TEXT_DIM
        # check if this was the last transition taken
        if len(self.fsm.history) >= 2:
            prev_state = self.fsm.history[-2]
            curr_state = self.fsm.history[-1]
            if s_from == prev_state and s_to == curr_state:
                color = ACCENT_GREEN

        if s_from == s_to:
            # self loop - draw arc above
            arc_r = 30
            self.fsm_canvas.create_arc(x0 - arc_r, y0 - r - arc_r * 2,
                                        x0 + arc_r, y0 - r + 5,
                                        start=200, extent=320, style="arc",
                                        outline=color, width=2)
            self.fsm_canvas.create_text(x0, y0 - r - arc_r - 8, text=label,
                                         font=("Consolas", 9, "bold"), fill=color)
        else:
            # determine if we need curve offset (for bidirectional)
            reverse_key = None
            for (sf, b), (st, o) in self.fsm.transitions.items():
                if sf == s_to and st == s_from:
                    reverse_key = True
                    break

            curve = 25 if reverse_key else 0

            # check direction
            if x1 > x0:
                # forward (curve up)
                mid_x = (x0 + x1) / 2
                mid_y = (y0 + y1) / 2 - curve
            else:
                # backward (curve down)
                mid_x = (x0 + x1) / 2
                mid_y = (y0 + y1) / 2 + curve

            self.fsm_canvas.create_line(x0 + r, y0, mid_x, mid_y,
                                         x1 - r, y1,
                                         smooth=True, arrow=tk.LAST,
                                         width=2, fill=color,
                                         arrowshape=(12, 14, 5))
            self.fsm_canvas.create_text(mid_x, mid_y - 14, text=label,
                                         font=("Consolas", 9, "bold"), fill=color)

    def fsm_step(self):
        bit = self.input_bit_var.get()
        nxt, out = self.fsm.step(bit)
        if nxt is None:
            messagebox.showwarning("No transition", "No transition defined for this input.")
            return
        self.draw_asm_chart()
        # update status bar
        if hasattr(self, '_status'):
            self._status.config(
                text=f"  ⚡ FSM Step  │  Input={bit}  →  State={nxt}  │  Output={out}  │  History length={len(self.fsm.history)}",
                fg=ACCENT_GREEN
            )

    def fsm_reset(self):
        self.fsm.reset()
        self.draw_asm_chart()

    # ──────── PLA/PAL TAB ────────
    def build_pld_tab(self):
        # input panel
        input_panel = tk.Frame(self.pld_tab, bg=BG_CARD,
                               highlightbackground=BORDER_COLOR,
                               highlightthickness=1)
        input_panel.pack(fill="x", padx=10, pady=10)

        inner = tk.Frame(input_panel, bg=BG_CARD)
        inner.pack(padx=15, pady=10)

        tk.Label(inner, text="Input variables:", font=("Segoe UI", 10, "bold"),
                 bg=BG_CARD, fg=TEXT_SECONDARY).grid(row=0, column=0, sticky="w", pady=3)
        self.pla_nvars = tk.IntVar(value=3)
        var_frame = tk.Frame(inner, bg=BG_CARD)
        var_frame.grid(row=0, column=1, sticky="w", padx=10)
        for val in [2, 3, 4]:
            rb = tk.Radiobutton(var_frame, text=str(val), variable=self.pla_nvars,
                                value=val, font=("Consolas", 10, "bold"),
                                bg=BG_CARD, fg=TEXT_PRIMARY,
                                selectcolor=BG_DARK,
                                activebackground=BG_CARD,
                                activeforeground=ACCENT_CYAN,
                                indicatoron=0, padx=12, pady=3, bd=0,
                                highlightthickness=1,
                                highlightbackground=BORDER_COLOR)
            rb.pack(side="left", padx=2)

        tk.Label(inner, text="F1 minterms:", font=("Segoe UI", 10, "bold"),
                 bg=BG_CARD, fg=TEXT_SECONDARY).grid(row=1, column=0, sticky="w", pady=3)
        self.f1_entry = tk.Entry(inner, width=35, font=("Consolas", 11),
                                 bg=BG_DARK, fg=ACCENT_RED,
                                 insertbackground=ACCENT_RED,
                                 relief="flat", highlightthickness=1,
                                 highlightbackground=BORDER_COLOR,
                                 highlightcolor=ACCENT_CYAN)
        self.f1_entry.grid(row=1, column=1, padx=10, pady=3, sticky="w")
        self.f1_entry.insert(0, "1,2,3,7")

        tk.Label(inner, text="F2 minterms:", font=("Segoe UI", 10, "bold"),
                 bg=BG_CARD, fg=TEXT_SECONDARY).grid(row=2, column=0, sticky="w", pady=3)
        self.f2_entry = tk.Entry(inner, width=35, font=("Consolas", 11),
                                 bg=BG_DARK, fg=ACCENT_CYAN,
                                 insertbackground=ACCENT_CYAN,
                                 relief="flat", highlightthickness=1,
                                 highlightbackground=BORDER_COLOR,
                                 highlightcolor=ACCENT_CYAN)
        self.f2_entry.grid(row=2, column=1, padx=10, pady=3, sticky="w")
        self.f2_entry.insert(0, "0,3,5,7")

        self._make_btn(inner, "⚡ Program PLA", ACCENT_AMBER,
                       self.program_pla).grid(row=0, column=2, rowspan=3, padx=(20, 0))

        # PLA canvas
        canvas_panel = tk.Frame(self.pld_tab, bg=BG_CARD,
                                highlightbackground=BORDER_COLOR,
                                highlightthickness=1)
        canvas_panel.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        tk.Label(canvas_panel, text="  PLA Fuse Map", font=("Segoe UI", 10, "bold"),
                 bg=BG_CARD, fg=TEXT_SECONDARY).pack(anchor="w", padx=10, pady=(8, 0))

        self.pla_canvas = tk.Canvas(canvas_panel, bg=CANVAS_BG, highlightthickness=0)
        self.pla_canvas.pack(fill="both", expand=True, padx=8, pady=8)

    def program_pla(self):
        n = self.pla_nvars.get()
        try:
            f1 = [int(x) for x in self.f1_entry.get().split(",") if x.strip() != ""]
            f2 = [int(x) for x in self.f2_entry.get().split(",") if x.strip() != ""]
        except ValueError:
            messagebox.showerror("Error", "Enter valid comma-separated minterms.")
            return

        var_names = [chr(ord('A') + i) for i in range(n)]
        all_terms = sorted(set(f1) | set(f2))

        self.pla_canvas.delete("all")

        # Title
        self.pla_canvas.create_text(450, 20,
                                     text="PLA Fuse Map: AND Array → OR Array",
                                     font=("Segoe UI", 12, "bold"), fill=TEXT_PRIMARY)

        # Column headers - AND array
        x_start = 120
        col_w = 45

        # header background
        header_y = 38
        total_and_w = len(var_names) * col_w * 2
        self.pla_canvas.create_rectangle(x_start - 20, header_y - 12,
                                          x_start + total_and_w + 10, header_y + 12,
                                          fill=BG_CARD, outline=BORDER_COLOR)

        # AND array section label
        self.pla_canvas.create_text(x_start + total_and_w // 2, header_y - 22,
                                     text="── AND Array ──",
                                     font=("Segoe UI", 8), fill=TEXT_DIM)

        for i, v in enumerate(var_names):
            cx_true = x_start + i * col_w * 2
            cx_false = cx_true + col_w
            self.pla_canvas.create_text(cx_true, header_y, text=v,
                                         font=("Consolas", 10, "bold"), fill=ACCENT_GREEN)
            self.pla_canvas.create_text(cx_false, header_y, text=v + "'",
                                         font=("Consolas", 10, "bold"), fill=ACCENT_AMBER)

        # OR array headers
        or_x1 = x_start + len(var_names) * col_w * 2 + 50
        or_x2 = or_x1 + 50

        or_header_w = 110
        self.pla_canvas.create_rectangle(or_x1 - 20, header_y - 12,
                                          or_x2 + 20, header_y + 12,
                                          fill=BG_CARD, outline=BORDER_COLOR)
        self.pla_canvas.create_text((or_x1 + or_x2) // 2, header_y - 22,
                                     text="── OR Array ──",
                                     font=("Segoe UI", 8), fill=TEXT_DIM)

        self.pla_canvas.create_text(or_x1, header_y, text="F1",
                                     font=("Consolas", 10, "bold"), fill=ACCENT_RED)
        self.pla_canvas.create_text(or_x2, header_y, text="F2",
                                     font=("Consolas", 10, "bold"), fill=ACCENT_CYAN)

        # vertical grid lines
        y_grid_start = header_y + 15
        y_grid_end = header_y + 15 + len(all_terms) * 30 + 10
        for i in range(len(var_names)):
            cx_true = x_start + i * col_w * 2
            cx_false = cx_true + col_w
            self.pla_canvas.create_line(cx_true, y_grid_start, cx_true, y_grid_end,
                                         fill="#1a2540", width=1, dash=(2, 4))
            self.pla_canvas.create_line(cx_false, y_grid_start, cx_false, y_grid_end,
                                         fill="#1a2540", width=1, dash=(2, 4))
        self.pla_canvas.create_line(or_x1, y_grid_start, or_x1, y_grid_end,
                                     fill="#1a2540", width=1, dash=(2, 4))
        self.pla_canvas.create_line(or_x2, y_grid_start, or_x2, y_grid_end,
                                     fill="#1a2540", width=1, dash=(2, 4))

        # product term rows
        y = header_y + 30
        for m in all_terms:
            bits = format(m, f'0{n}b')

            # row label
            self.pla_canvas.create_text(50, y, text=f"P{m}",
                                         font=("Consolas", 9, "bold"), fill=TEXT_SECONDARY)

            # row background
            self.pla_canvas.create_rectangle(x_start - 20, y - 11,
                                              or_x2 + 20, y + 11,
                                              fill="#141e30", outline="")

            # horizontal grid line
            self.pla_canvas.create_line(x_start - 20, y, or_x2 + 20, y,
                                         fill="#1a2540", width=1, dash=(1, 6))

            for i, b in enumerate(bits):
                cx_true = x_start + i * col_w * 2
                cx_false = cx_true + col_w

                if b == '1':
                    # programmed fuse (kept) on true literal
                    self.pla_canvas.create_oval(cx_true - 7, y - 7, cx_true + 7, y + 7,
                                                fill=ACCENT_GREEN, outline="")
                    # intact fuse marker on complement
                    self.pla_canvas.create_text(cx_false, y, text="×",
                                                font=("Consolas", 8), fill=TEXT_DIM)
                else:
                    # blown fuse on true literal
                    self.pla_canvas.create_text(cx_true, y, text="×",
                                                font=("Consolas", 8), fill=TEXT_DIM)
                    # programmed fuse on complement
                    self.pla_canvas.create_oval(cx_false - 7, y - 7, cx_false + 7, y + 7,
                                                fill=ACCENT_AMBER, outline="")

            # OR array connections
            if m in f1:
                self.pla_canvas.create_oval(or_x1 - 7, y - 7, or_x1 + 7, y + 7,
                                             fill=ACCENT_RED, outline="")
            else:
                self.pla_canvas.create_text(or_x1, y, text="·",
                                             font=("Consolas", 10), fill=TEXT_DIM)

            if m in f2:
                self.pla_canvas.create_oval(or_x2 - 7, y - 7, or_x2 + 7, y + 7,
                                             fill=ACCENT_CYAN, outline="")
            else:
                self.pla_canvas.create_text(or_x2, y, text="·",
                                             font=("Consolas", 10), fill=TEXT_DIM)

            y += 28

        # legend
        y += 25
        legends = [
            ("●", ACCENT_GREEN, "Programmed fuse (literal kept)"),
            ("●", ACCENT_AMBER, "Complement fuse (literal kept)"),
            ("●", ACCENT_RED, "OR → F1 connection"),
            ("●", ACCENT_CYAN, "OR → F2 connection"),
            ("×", TEXT_DIM, "Blown fuse (disconnected)"),
        ]

        lx = 80
        for symbol, color, desc in legends:
            self.pla_canvas.create_text(lx, y, text=symbol,
                                         font=("Consolas", 10), fill=color)
            self.pla_canvas.create_text(lx + 15, y, text=desc, anchor="w",
                                         font=("Segoe UI", 8), fill=TEXT_SECONDARY)
            lx += 180

        # summary
        y += 25
        self.pla_canvas.create_text(450, y,
                                     text=f"F1 = Σm({','.join(map(str, f1))})    │    F2 = Σm({','.join(map(str, f2))})",
                                     font=("Consolas", 10, "bold"), fill=TEXT_PRIMARY)


def launch(master=None):
    root = master if master else tk.Tk()
    if master is None:
        root.withdraw()
    mod = ASMPLDModule(root)
    # Add status bar after build
    mod._status = tk.Label(mod, text="  Ready  •  Use FSM tab to step a state machine  •  Use PLA tab to program arrays",
                           font=("Segoe UI", 8), bg="#0d1526",
                           fg=TEXT_SECONDARY, anchor="w", pady=5)
    mod._status.pack(fill="x", side="bottom")
    if master is None:
        root.mainloop()


if __name__ == "__main__":
    launch()
