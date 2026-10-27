"""
module3_sequential.py
-----------------------
Member 3: Sequential Circuit Simulator (Unit 2B)

Features:
 - SR, JK, D, T flip-flop simulation, one clock pulse at a time
 - Shift registers: SISO, SIPO, PISO, PIPO (4-bit)
 - Counters: Asynchronous (ripple), Synchronous, Ring, Johnson
 - Live timing-diagram drawn on Canvas, extended each clock pulse
 - Back button to return to Home
 - Flip-flop/counter state diagram shown on every clock pulse
 - Knowledge panel for each circuit type
"""

import tkinter as tk
from tkinter import ttk
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

WAVE_COLORS = [ACCENT_CYAN, ACCENT_GREEN, ACCENT_PURPLE, ACCENT_AMBER,
               ACCENT_RED, "#60a5fa", "#fb923c", "#e879f9"]

# ─── Knowledge content ──────────────────────────────────────────
SEQ_KNOWLEDGE = {
    "SR Flip-Flop": {
        "color": ACCENT_CYAN,
        "body": (
            "SR (Set-Reset) Flip-Flop:\n\n"
            "  S=1, R=0  -> Q=1  (Set)\n"
            "  S=0, R=1  -> Q=0  (Reset)\n"
            "  S=0, R=0  -> Q=Q  (Hold state)\n"
            "  S=1, R=1  -> INVALID (undefined/forbidden)\n\n"
            "The S=1,R=1 state is forbidden because it creates a race condition.\n\n"
            "Built from: Two cross-coupled NAND or NOR gates.\n"
            "It's the most basic memory element in digital circuits."
        )
    },
    "JK Flip-Flop": {
        "color": ACCENT_GREEN,
        "body": (
            "JK Flip-Flop: Improved version of SR that eliminates the forbidden state.\n\n"
            "  J=0, K=0  -> Q=Q  (Hold)\n"
            "  J=0, K=1  -> Q=0  (Reset)\n"
            "  J=1, K=0  -> Q=1  (Set)\n"
            "  J=1, K=1  -> Q=Q' (Toggle!) <- This is what makes JK special\n\n"
            "The toggle mode (J=K=1) is unique to JK and very useful for counters.\n\n"
            "A T flip-flop is just a JK flip-flop with J and K tied together."
        )
    },
    "D Flip-Flop": {
        "color": ACCENT_AMBER,
        "body": (
            "D (Data) Flip-Flop: The simplest and most common flip-flop.\n\n"
            "  On each rising clock edge: Q = D\n\n"
            "The output simply copies the input D on each clock cycle.\n\n"
            "Uses:\n"
            "  * Registers (storage elements)\n"
            "  * Shift registers\n"
            "  * Pipeline stages in CPUs\n"
            "  * Eliminating metastability (synchronizers)\n\n"
            "Essentially a 1-bit memory cell triggered by a clock."
        )
    },
    "T Flip-Flop": {
        "color": ACCENT_PURPLE,
        "body": (
            "T (Toggle) Flip-Flop:\n\n"
            "  T=0  -> Q=Q  (Hold — no change)\n"
            "  T=1  -> Q=Q' (Toggle — flips every clock)\n\n"
            "A T flip-flop toggles its output whenever T=1 and a clock edge occurs.\n\n"
            "Key Use: Binary counters.\n"
            "  * If T is always 1, the output toggles every clock = divide-by-2 counter.\n"
            "  * Chain of T flip-flops with T=1: each stage divides frequency by 2.\n\n"
            "Built from: JK flip-flop with J=K=T."
        )
    },
    "4-bit SISO": {
        "color": ACCENT_CYAN,
        "body": (
            "SISO (Serial-In, Serial-Out) Shift Register:\n\n"
            "  * Data enters one bit at a time (serial input)\n"
            "  * Data exits one bit at a time (serial output)\n"
            "  * 4 flip-flops connected in a chain\n\n"
            "Operation:\n"
            "  Each clock pulse: data shifts one position toward the output.\n"
            "  It takes 4 clock pulses to shift all 4 bits through.\n\n"
            "Uses:\n"
            "  * Time delay circuits (data delayed by N clocks)\n"
            "  * Serial data transmission\n"
            "  * CRC (Cyclic Redundancy Check) circuits"
        )
    },
    "4-bit SIPO": {
        "color": ACCENT_GREEN,
        "body": (
            "SIPO (Serial-In, Parallel-Out) Shift Register:\n\n"
            "  * Data enters serially (1 bit per clock)\n"
            "  * All 4 bits are available simultaneously at the output\n\n"
            "Operation:\n"
            "  After 4 clock pulses, all 4 flip-flops hold their values,\n"
            "  and all 4 outputs (Q0-Q3) are available at the same time.\n\n"
            "Uses:\n"
            "  * Serial-to-parallel conversion (e.g., receiving serial data)\n"
            "  * SPI/UART receiver circuits"
        )
    },
    "4-bit PISO": {
        "color": ACCENT_AMBER,
        "body": (
            "PISO (Parallel-In, Serial-Out) Shift Register:\n\n"
            "  * All 4 bits are loaded simultaneously (parallel load)\n"
            "  * Data shifts out one bit at a time (serial output)\n\n"
            "Operation:\n"
            "  1. Load: All 4 bits loaded in one clock pulse.\n"
            "  2. Shift: Each subsequent clock shifts one bit out.\n\n"
            "Uses:\n"
            "  * Parallel-to-serial conversion (e.g., transmitting data serially)\n"
            "  * SPI/UART transmitter circuits"
        )
    },
    "4-bit PIPO": {
        "color": ACCENT_PURPLE,
        "body": (
            "PIPO (Parallel-In, Parallel-Out) Shift Register:\n\n"
            "  * All bits loaded and available simultaneously\n"
            "  * Acts as a simple 4-bit register\n\n"
            "Operation:\n"
            "  On clock edge: all D inputs are captured simultaneously.\n\n"
            "Uses:\n"
            "  * CPU registers\n"
            "  * Data latching/buffering\n"
            "  * Pipeline registers between processing stages"
        )
    },
    "Async Counter (mod-N)": {
        "color": ACCENT_AMBER,
        "body": (
            "Asynchronous (Ripple) Counter:\n\n"
            "  * Flip-flops are NOT all clocked by the same signal.\n"
            "  * Output of each FF drives the clock input of the next.\n"
            "  * The count 'ripples' through — like dominoes.\n\n"
            "Modulus-N: Counter counts from 0 to N-1, then resets.\n\n"
            "Advantage: Simple design, fewer connections.\n"
            "Disadvantage: 'Glitches' — intermediate wrong states appear\n"
            "  as the ripple propagates. Not suitable for high-speed circuits.\n\n"
            "Example: 74HC93 is a 4-bit ripple counter IC."
        )
    },
    "Sync Counter (mod-N)": {
        "color": ACCENT_GREEN,
        "body": (
            "Synchronous Counter:\n\n"
            "  * ALL flip-flops are clocked by the SAME clock signal.\n"
            "  * All outputs change simultaneously (no ripple).\n\n"
            "Modulus-N: Counter counts from 0 to N-1, then resets.\n\n"
            "Advantage: No glitches, faster, more reliable.\n"
            "Disadvantage: More complex gate logic needed to control each FF.\n\n"
            "Example: 74HC163 is a 4-bit synchronous counter IC.\n\n"
            "Used in: Frequency dividers, digital clocks, CPU pipelines."
        )
    },
    "Ring Counter": {
        "color": ACCENT_CYAN,
        "body": (
            "Ring Counter:\n\n"
            "  * A shift register with the output of the last FF fed back to the first.\n"
            "  * Initial state: exactly one '1' bit, rest are '0'.\n"
            "  * The '1' bit circulates (rotates) through the register.\n\n"
            "N-bit ring counter has N states.\n\n"
            "Example (4-bit):\n"
            "  State 1: 1000\n"
            "  State 2: 0100\n"
            "  State 3: 0010\n"
            "  State 4: 0001  -> then back to 1000\n\n"
            "Uses: Sequence generators, time-division multiplexing."
        )
    },
    "Johnson Counter": {
        "color": ACCENT_PURPLE,
        "body": (
            "Johnson Counter (Twisted Ring Counter):\n\n"
            "  * Like a ring counter, but the COMPLEMENT of the last FF output\n"
            "    is fed back to the first FF input.\n\n"
            "N-bit Johnson counter has 2N states.\n\n"
            "Example (4-bit):\n"
            "  0000 -> 1000 -> 1100 -> 1110 -> 1111\n"
            "       -> 0111 -> 0011 -> 0001 -> 0000\n\n"
            "Advantage over ring counter: 2x more states for same number of FFs.\n\n"
            "Uses: Frequency division, waveform generation, BCD counters."
        )
    },
}


class FlipFlop:
    """Behavioral flip-flop model."""
    def __init__(self, kind="D"):
        self.kind = kind
        self.q = 0

    def clock(self, **inputs):
        if self.kind == "SR":
            s, r = inputs.get("S", 0), inputs.get("R", 0)
            if s and r:
                pass
            elif s:
                self.q = 1
            elif r:
                self.q = 0
        elif self.kind == "JK":
            j, k = inputs.get("J", 0), inputs.get("K", 0)
            if j and k:
                self.q = 1 - self.q
            elif j:
                self.q = 1
            elif k:
                self.q = 0
        elif self.kind == "D":
            self.q = inputs.get("D", 0)
        elif self.kind == "T":
            t = inputs.get("T", 0)
            if t:
                self.q = 1 - self.q
        return self.q


class KnowledgePanel(tk.Toplevel):
    def __init__(self, master, circuit_name):
        super().__init__(master)
        info = SEQ_KNOWLEDGE.get(circuit_name, {
            "color": ACCENT_CYAN,
            "body": f"No knowledge entry for '{circuit_name}'."
        })
        self.title(f"Knowledge: {circuit_name}")
        self.geometry("560x420")
        self.configure(bg=BG_DARK)
        self.resizable(False, False)
        self.lift()
        self.focus_force()

        color = info.get("color", ACCENT_CYAN)

        tk.Frame(self, bg=color, height=4).pack(fill="x")

        hdr2 = tk.Frame(self, bg=BG_CARD)
        hdr2.pack(fill="x")
        tk.Label(hdr2, text=f"  {circuit_name} — Theory & Truth Table",
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


class SeqModule(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master_ref = master
        self.title("Sequential Circuit Simulator")
        self.geometry("1050x760")
        self.configure(bg=BG_DARK)

        # ── Top bar: Back + Header ──
        top_bar = tk.Frame(self, bg=BG_DARK)
        top_bar.pack(fill="x", padx=20, pady=(12, 0))

        back_btn = tk.Button(top_bar, text="<- Back to Home",
                             font=("Segoe UI", 9, "bold"),
                             bg="#1e293b", fg=ACCENT_PURPLE,
                             activebackground=ACCENT_PURPLE, activeforeground=BG_DARK,
                             bd=0, padx=14, pady=6, cursor="hand2",
                             command=self._go_back, relief="flat")
        back_btn.pack(side="left")
        back_btn.bind("<Enter>", lambda e: back_btn.configure(bg=ACCENT_PURPLE, fg=BG_DARK))
        back_btn.bind("<Leave>", lambda e: back_btn.configure(bg="#1e293b", fg=ACCENT_PURPLE))

        header_frame = tk.Frame(top_bar, bg=BG_DARK)
        header_frame.pack(side="left", padx=18)
        tk.Label(header_frame, text="[Clock]", font=("Segoe UI", 18),
                 bg=BG_DARK, fg=ACCENT_PURPLE).pack(side="left", padx=(0, 10))
        title_f = tk.Frame(header_frame, bg=BG_DARK)
        title_f.pack(side="left")
        tk.Label(title_f, text="Sequential Circuit Simulator",
                 font=("Segoe UI", 17, "bold"), bg=BG_DARK,
                 fg=TEXT_PRIMARY).pack(anchor="w")
        tk.Label(title_f,
                 text="Flip-flops  *  Shift registers  *  Counters  *  Timing diagrams  *  State diagrams",
                 font=("Segoe UI", 9), bg=BG_DARK, fg=TEXT_SECONDARY).pack(anchor="w")

        # ── Workflow indicator ──
        wf = tk.Frame(self, bg=BG_DARK)
        wf.pack(fill="x", padx=20, pady=(8, 0))
        for num, label, col in [("1", "Pick Circuit", ACCENT_CYAN),
                                  ("2", "Set Inputs", ACCENT_GREEN),
                                  ("3", "Clock Pulse", ACCENT_PURPLE),
                                  ("4", "Read Waveform", ACCENT_AMBER)]:
            sf = tk.Frame(wf, bg=BG_DARK)
            sf.pack(side="left", padx=2)
            tk.Label(sf, text=f" {num} ", font=("Segoe UI", 8, "bold"),
                     bg=col, fg=BG_DARK).pack(side="left")
            tk.Label(sf, text=f" {label} ", font=("Segoe UI", 8),
                     bg=BG_CARD, fg=TEXT_SECONDARY).pack(side="left")
            if num != "4":
                tk.Label(wf, text=" -> ", font=("Segoe UI", 8),
                         bg=BG_DARK, fg=TEXT_DIM).pack(side="left")

        # ── Control panel ──
        ctrl_panel = tk.Frame(self, bg=BG_CARD, highlightbackground=BORDER_COLOR,
                              highlightthickness=1)
        ctrl_panel.pack(fill="x", padx=20, pady=10)

        ctrl_inner = tk.Frame(ctrl_panel, bg=BG_CARD)
        ctrl_inner.pack(padx=15, pady=8)

        row0 = tk.Frame(ctrl_inner, bg=BG_CARD)
        row0.pack(fill="x", pady=3)

        tk.Label(row0, text="Circuit:", font=("Segoe UI", 10, "bold"),
                 bg=BG_CARD, fg=TEXT_SECONDARY).pack(side="left")

        self.choice = tk.StringVar(value="D Flip-Flop")
        options = ["SR Flip-Flop", "JK Flip-Flop", "D Flip-Flop", "T Flip-Flop",
                   "4-bit SISO", "4-bit SIPO", "4-bit PISO", "4-bit PIPO",
                   "Async Counter (mod-N)", "Sync Counter (mod-N)",
                   "Ring Counter", "Johnson Counter"]
        combo = ttk.Combobox(row0, textvariable=self.choice, values=options,
                             state="readonly", width=26, font=("Segoe UI", 10))
        combo.pack(side="left", padx=8)
        combo.bind("<<ComboboxSelected>>", lambda e: self.reset())

        tk.Label(row0, text="Modulus:", font=("Segoe UI", 10, "bold"),
                 bg=BG_CARD, fg=TEXT_SECONDARY).pack(side="left", padx=(15, 5))
        self.mod_var = tk.IntVar(value=4)
        mod_spin = tk.Spinbox(row0, from_=2, to=16, textvariable=self.mod_var,
                              width=4, font=("Consolas", 10),
                              bg=BG_DARK, fg=ACCENT_CYAN,
                              buttonbackground=BG_CARD,
                              insertbackground=TEXT_PRIMARY,
                              highlightthickness=1, highlightbackground=BORDER_COLOR,
                              relief="flat")
        mod_spin.pack(side="left")

        # Knowledge button
        self._know_btn = tk.Button(row0, text="? Learn this circuit",
                                   font=("Segoe UI", 8, "bold"),
                                   bg=BG_CARD, fg=ACCENT_PURPLE, bd=0, padx=10, pady=4,
                                   cursor="hand2", relief="flat",
                                   command=self._show_knowledge)
        self._know_btn.pack(side="left", padx=12)
        self._know_btn.bind("<Enter>",
                            lambda e: self._know_btn.configure(bg=ACCENT_PURPLE, fg=BG_DARK))
        self._know_btn.bind("<Leave>",
                            lambda e: self._know_btn.configure(bg=BG_CARD, fg=ACCENT_PURPLE))

        row1 = tk.Frame(ctrl_inner, bg=BG_CARD)
        row1.pack(fill="x", pady=5)

        tk.Label(row1, text="Input 1:", font=("Segoe UI", 10, "bold"),
                 bg=BG_CARD, fg=TEXT_SECONDARY).pack(side="left")
        self.input_bit = tk.IntVar(value=0)
        self._make_toggle(row1, self.input_bit).pack(side="left", padx=5)

        tk.Label(row1, text="Input 2:", font=("Segoe UI", 10, "bold"),
                 bg=BG_CARD, fg=TEXT_SECONDARY).pack(side="left", padx=(15, 0))
        self.input_bit2 = tk.IntVar(value=0)
        self._make_toggle(row1, self.input_bit2).pack(side="left", padx=5)

        btn_frame = tk.Frame(row1, bg=BG_CARD)
        btn_frame.pack(side="right")
        self._make_btn(btn_frame, "Reset", ACCENT_AMBER, self.reset).pack(side="left", padx=4)
        self._make_btn(btn_frame, "Clock Pulse", ACCENT_CYAN, self.clock_pulse).pack(side="left", padx=4)

        # ── State display ──
        self.state_frame = tk.Frame(self, bg=BG_DARK)
        self.state_frame.pack(fill="x", padx=20, pady=(0, 4))

        self.state_label = tk.Label(self.state_frame,
                                    text="State: Ready -- Click 'Clock Pulse' to step",
                                    font=("Consolas", 11), bg=BG_DARK, fg=ACCENT_GREEN)
        self.state_label.pack(anchor="w")

        # ── Split: State diagram (left) + Timing diagram (right) ──
        content = tk.Frame(self, bg=BG_DARK)
        content.pack(fill="both", expand=True, padx=20, pady=(0, 0))

        # State diagram panel (left)
        state_panel = tk.Frame(content, bg=BG_CARD, highlightbackground=BORDER_COLOR,
                               highlightthickness=1)
        state_panel.pack(side="left", fill="both", expand=True, padx=(0, 5))

        state_hdr = tk.Frame(state_panel, bg="#0d1526")
        state_hdr.pack(fill="x")
        tk.Label(state_hdr, text="  State / Register Diagram",
                 font=("Segoe UI", 10, "bold"), bg="#0d1526", fg=ACCENT_PURPLE,
                 anchor="w").pack(side="left", padx=10, pady=7)
        tk.Label(state_hdr, text="(auto-updates on each clock)",
                 font=("Segoe UI", 8), bg="#0d1526", fg=TEXT_DIM).pack(side="left")

        self.state_canvas = tk.Canvas(state_panel, bg=CANVAS_BG, highlightthickness=0)
        self.state_canvas.pack(fill="both", expand=True, padx=8, pady=8)
        self.state_canvas.bind("<Configure>", self._draw_state_placeholder)

        # Timing diagram panel (right)
        wave_panel = tk.Frame(content, bg=BG_CARD, highlightbackground=BORDER_COLOR,
                              highlightthickness=1)
        wave_panel.pack(side="left", fill="both", expand=True, padx=(5, 0))

        wave_hdr = tk.Frame(wave_panel, bg="#0d1526")
        wave_hdr.pack(fill="x")
        tk.Label(wave_hdr, text="  Timing Diagram",
                 font=("Segoe UI", 10, "bold"), bg="#0d1526", fg=ACCENT_CYAN,
                 anchor="w").pack(side="left", padx=10, pady=7)

        self.canvas = tk.Canvas(wave_panel, bg=CANVAS_BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=8, pady=8)

        self.history = []
        self.tick = 0
        self.ff = None
        self.reg_bits = [0, 0, 0, 0]
        self.reset()

        # ── Status bar ──
        self._status = tk.Label(self,
                                text="  Ready  *  Select a circuit and click Clock Pulse to start",
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

    def _draw_state_placeholder(self, e=None):
        if self.history:
            return
        c = self.state_canvas
        c.delete("placeholder")
        w, h = c.winfo_width(), c.winfo_height()
        if w < 10:
            return
        c.create_text(w // 2, h // 2 - 14, text="[State Diagram]",
                      font=("Segoe UI", 18), fill=TEXT_DIM, tags="placeholder")
        c.create_text(w // 2, h // 2 + 18,
                      text="State diagram will appear here after Clock Pulse",
                      font=("Segoe UI", 9), fill=TEXT_DIM, tags="placeholder")

    def _make_btn(self, parent, text, color, command):
        btn = tk.Button(parent, text=text, font=("Segoe UI", 10, "bold"),
                        bg=color, fg="#050a14", activebackground=TEXT_PRIMARY,
                        activeforeground="#050a14", bd=0, padx=14, pady=6,
                        cursor="hand2", command=command, relief="flat")
        btn.bind("<Enter>", lambda e: btn.configure(bg=TEXT_PRIMARY))
        btn.bind("<Leave>", lambda e: btn.configure(bg=color))
        return btn

    def _make_toggle(self, parent, variable):
        frame = tk.Frame(parent, bg=BG_CARD)
        for val, text in [(0, "0"), (1, "1")]:
            rb = tk.Radiobutton(frame, text=text, variable=variable, value=val,
                                font=("Consolas", 10, "bold"),
                                bg=BG_CARD, fg=TEXT_PRIMARY,
                                selectcolor=BG_DARK,
                                activebackground=BG_CARD,
                                activeforeground=ACCENT_CYAN,
                                indicatoron=0, padx=10, pady=2, bd=0,
                                highlightthickness=1,
                                highlightbackground=BORDER_COLOR)
            rb.pack(side="left", padx=1)
        return frame

    def reset(self):
        self.history = []
        self.tick = 0
        choice = self.choice.get()
        if "Flip-Flop" in choice:
            kind = choice.split()[0]
            self.ff = FlipFlop(kind)
        self.reg_bits = [0, 0, 0, 0]
        for attr in ("_count", "_ring", "_johnson"):
            if hasattr(self, attr):
                delattr(self, attr)
        self.canvas.delete("all")
        self.state_canvas.delete("all")
        self.state_label.config(text="State: Reset -- Click 'Clock Pulse' to step",
                                fg=ACCENT_AMBER)
        self.state_canvas.after(100, self._draw_state_placeholder)

    def clock_pulse(self):
        choice = self.choice.get()
        record = {}

        if "Flip-Flop" in choice:
            kind = choice.split()[0]
            in1 = self.input_bit.get()
            in2 = self.input_bit2.get()
            if kind == "SR":
                q = self.ff.clock(S=in1, R=in2)
                record = {"S": in1, "R": in2, "Q": q}
            elif kind == "JK":
                q = self.ff.clock(J=in1, K=in2)
                record = {"J": in1, "K": in2, "Q": q}
            elif kind == "D":
                q = self.ff.clock(D=in1)
                record = {"D": in1, "Q": q}
            elif kind == "T":
                q = self.ff.clock(T=in1)
                record = {"T": in1, "Q": q}
            self.state_label.config(
                text=f"  Tick {self.tick+1}:  " + "  ".join(f"{k}={v}" for k, v in record.items()),
                fg=ACCENT_GREEN
            )

        elif choice == "4-bit SISO":
            new_bit = self.input_bit.get()
            self.reg_bits = [new_bit] + self.reg_bits[:-1]
            record = {"SerialIn": new_bit, "Reg": "".join(map(str, self.reg_bits)),
                      "SerialOut": self.reg_bits[-1]}
            self.state_label.config(
                text=f"  Tick {self.tick+1}:  Reg = {record['Reg']}   SerialOut = {record['SerialOut']}",
                fg=ACCENT_GREEN
            )

        elif choice == "4-bit SIPO":
            new_bit = self.input_bit.get()
            self.reg_bits = [new_bit] + self.reg_bits[:-1]
            record = {"SerialIn": new_bit, "ParallelOut": "".join(map(str, self.reg_bits))}
            self.state_label.config(
                text=f"  Tick {self.tick+1}:  ParallelOut = {record['ParallelOut']}",
                fg=ACCENT_GREEN
            )

        elif choice == "4-bit PISO":
            if self.tick == 0:
                self.reg_bits = [self.input_bit.get(), self.input_bit2.get(), 0, 1]
            out = self.reg_bits.pop(0)
            self.reg_bits.append(0)
            record = {"Reg": "".join(map(str, self.reg_bits)), "SerialOut": out}
            self.state_label.config(
                text=f"  Tick {self.tick+1}:  SerialOut = {out}   Reg = {record['Reg']}",
                fg=ACCENT_GREEN
            )

        elif choice == "4-bit PIPO":
            if self.tick == 0:
                self.reg_bits = [self.input_bit.get(), self.input_bit2.get(), 1, 0]
            record = {"ParallelOut": "".join(map(str, self.reg_bits))}
            self.state_label.config(
                text=f"  Tick {self.tick+1}:  ParallelOut = {record['ParallelOut']}",
                fg=ACCENT_GREEN
            )

        elif choice in ("Async Counter (mod-N)", "Sync Counter (mod-N)"):
            mod = self.mod_var.get()
            current = getattr(self, "_count", 0)
            current = (current + 1) % mod
            self._count = current
            record = {"Count": current}
            self.state_label.config(
                text=f"  Tick {self.tick+1}:  Count = {current}  (mod {mod})",
                fg=ACCENT_GREEN
            )

        elif choice == "Ring Counter":
            n = self.mod_var.get()
            if not hasattr(self, "_ring") or len(self._ring) != n:
                self._ring = [1] + [0] * (n - 1)
            else:
                self._ring = [self._ring[-1]] + self._ring[:-1]
            record = {"Ring": "".join(map(str, self._ring))}
            self.state_label.config(
                text=f"  Tick {self.tick+1}:  {record['Ring']}",
                fg=ACCENT_GREEN
            )

        elif choice == "Johnson Counter":
            n = self.mod_var.get()
            if not hasattr(self, "_johnson") or len(self._johnson) != n:
                self._johnson = [0] * n
            inv = 1 - self._johnson[-1]
            self._johnson = [inv] + self._johnson[:-1]
            record = {"Johnson": "".join(map(str, self._johnson))}
            self.state_label.config(
                text=f"  Tick {self.tick+1}:  {record['Johnson']}",
                fg=ACCENT_GREEN
            )

        self.tick += 1
        self.history.append(record)

        if hasattr(self, '_status'):
            summary = "  ".join(f"{k}={v}" for k, v in record.items())
            self._status.config(
                text=f"  Tick {self.tick}  |  {choice}  |  {summary}",
                fg=ACCENT_GREEN
            )

        self.draw_waveform()
        self.after(30, lambda: self.draw_state_diagram(choice, record))

    def draw_state_diagram(self, choice, record):
        """Draw a visual state/register diagram for the current tick."""
        c = self.state_canvas
        c.delete("all")
        cw = c.winfo_width()
        ch = c.winfo_height()
        if cw < 50:
            return

        c.create_text(cw // 2, 18, text=f"Tick {self.tick}  |  {choice}",
                      font=("Segoe UI", 11, "bold"), fill=TEXT_PRIMARY)

        if "Flip-Flop" in choice:
            self._draw_ff_diagram(c, choice, record, cw, ch)
        elif "bit" in choice:
            self._draw_register_diagram(c, choice, record, cw, ch)
        elif "Counter" in choice:
            self._draw_counter_diagram(c, choice, record, cw, ch)

    def _draw_ff_diagram(self, c, choice, record, cw, ch):
        """Draw flip-flop state box."""
        q_val = record.get("Q", 0)
        q_color = ACCENT_GREEN if q_val == 1 else ACCENT_RED

        # FF box
        bx, by = cw // 2 - 60, ch // 2 - 50
        bw, bh = 120, 80
        c.create_rectangle(bx, by, bx + bw, by + bh,
                           fill="#0f172a", outline=q_color, width=3)
        c.create_text(bx + bw // 2, by + 16,
                      text=f"{choice.split()[0]} FF",
                      font=("Segoe UI", 10, "bold"), fill=TEXT_SECONDARY)
        c.create_text(bx + bw // 2, by + bh // 2 + 10,
                      text=f"Q = {q_val}",
                      font=("Consolas", 18, "bold"), fill=q_color)

        # Inputs on left
        input_labels = {k: v for k, v in record.items() if k != "Q"}
        for i, (k, v) in enumerate(input_labels.items()):
            ic = ACCENT_GREEN if v == 1 else ACCENT_RED
            iy = by + 25 + i * 25
            c.create_text(bx - 40, iy, text=f"{k}={v}",
                          font=("Consolas", 10, "bold"), fill=ic)
            c.create_line(bx - 10, iy, bx, iy, fill=ic, width=2,
                          arrow=tk.LAST, arrowshape=(8, 10, 3))

        # Q on right
        c.create_line(bx + bw, by + bh // 2, bx + bw + 40, by + bh // 2,
                      fill=q_color, width=3, arrow=tk.LAST, arrowshape=(10, 12, 4))
        c.create_text(bx + bw + 55, by + bh // 2,
                      text=f"Q={q_val}", font=("Consolas", 10, "bold"), fill=q_color)

        # Clock edge symbol
        cx = bx + bw // 2
        cy = by + bh
        c.create_line(cx - 10, cy + 5, cx - 10, cy + 20, cx + 10, cy + 20,
                      fill=ACCENT_CYAN, width=2)
        c.create_text(cx, cy + 32, text="CLK", font=("Segoe UI", 8), fill=ACCENT_CYAN)

        # History trail
        hist_y = ch - 50
        c.create_text(20, hist_y, text="History: Q =", anchor="w",
                      font=("Segoe UI", 9), fill=TEXT_DIM)
        for i, h in enumerate(self.history[-12:]):
            qh = h.get("Q", 0)
            hc = ACCENT_GREEN if qh == 1 else ACCENT_RED
            c.create_oval(120 + i * 28, hist_y - 8, 136 + i * 28, hist_y + 8,
                          fill=hc, outline="")
            c.create_text(128 + i * 28, hist_y, text=str(qh),
                          font=("Consolas", 8, "bold"), fill=BG_DARK)

    def _draw_register_diagram(self, c, choice, record, cw, ch):
        """Draw shift register bit cells."""
        reg_str = None
        for k, v in record.items():
            if "Reg" in k or "Parallel" in k or "Serial" in k:
                if isinstance(v, str) and len(v) > 1:
                    reg_str = v
                    break

        bits = [int(b) for b in reg_str] if reg_str else self.reg_bits[:]
        n = len(bits)

        cell_w = min(70, (cw - 80) // max(n, 1))
        cell_h = 50
        ox = (cw - n * cell_w) // 2
        oy = ch // 2 - 40

        c.create_text(cw // 2, oy - 24, text="Shift Register State",
                      font=("Segoe UI", 10), fill=TEXT_SECONDARY)

        for i, b in enumerate(bits):
            x = ox + i * cell_w
            bc = ACCENT_GREEN if b == 1 else "#1a2540"
            border_c = ACCENT_GREEN if b == 1 else ACCENT_RED
            c.create_rectangle(x + 2, oy, x + cell_w - 2, oy + cell_h,
                               fill=bc, outline=border_c, width=2)
            c.create_text(x + cell_w // 2, oy + cell_h // 2,
                          text=str(b), font=("Segoe UI", 18, "bold"),
                          fill=TEXT_PRIMARY if b == 1 else TEXT_DIM)
            c.create_text(x + cell_w // 2, oy + cell_h + 16,
                          text=f"D{i}", font=("Consolas", 8), fill=TEXT_DIM)

        # Arrow showing shift direction
        arr_y = oy + cell_h // 2
        c.create_line(ox - 30, arr_y, ox - 5, arr_y,
                      fill=ACCENT_CYAN, width=2, arrow=tk.LAST, arrowshape=(8, 10, 3))
        c.create_text(ox - 50, arr_y, text="IN", font=("Consolas", 8), fill=ACCENT_CYAN)

        out_x = ox + n * cell_w + 5
        c.create_line(out_x, arr_y, out_x + 30, arr_y,
                      fill=ACCENT_AMBER, width=2, arrow=tk.LAST, arrowshape=(8, 10, 3))
        c.create_text(out_x + 46, arr_y, text="OUT", font=("Consolas", 8), fill=ACCENT_AMBER)

        # Tick label
        c.create_text(cw // 2, oy + cell_h + 40,
                      text=f"After Tick {self.tick}: {''.join(map(str, bits))} (binary)",
                      font=("Consolas", 10, "bold"), fill=ACCENT_AMBER)

    def _draw_counter_diagram(self, c, choice, record, cw, ch):
        """Draw counter state as a binary circle display."""
        count = record.get("Count", 0)
        ring = record.get("Ring", "")
        johnson = record.get("Johnson", "")

        if ring:
            bits = [int(b) for b in ring]
            label = f"Ring: {ring}"
        elif johnson:
            bits = [int(b) for b in johnson]
            label = f"Johnson: {johnson}"
        else:
            mod = self.mod_var.get()
            n_bits = max(4, math.ceil(math.log2(mod + 1)))
            bits = [int(b) for b in format(count, f'0{n_bits}b')]
            label = f"Count = {count} = {format(count, f'0{n_bits}b')}b"

        n = len(bits)
        cell_w = min(70, (cw - 80) // max(n, 1))
        cell_h = 50
        ox = (cw - n * cell_w) // 2
        oy = ch // 2 - 40

        c.create_text(cw // 2, oy - 24, text="Counter State",
                      font=("Segoe UI", 10), fill=TEXT_SECONDARY)

        for i, b in enumerate(bits):
            x = ox + i * cell_w
            bc = ACCENT_AMBER if b == 1 else "#1a2540"
            border_c = ACCENT_AMBER if b == 1 else BORDER_COLOR
            c.create_rectangle(x + 2, oy, x + cell_w - 2, oy + cell_h,
                               fill=bc, outline=border_c, width=2)
            c.create_text(x + cell_w // 2, oy + cell_h // 2,
                          text=str(b), font=("Segoe UI", 18, "bold"),
                          fill=TEXT_PRIMARY if b == 1 else TEXT_DIM)
            c.create_text(x + cell_w // 2, oy + cell_h + 16,
                          text=f"Q{i}", font=("Consolas", 8), fill=TEXT_DIM)

        c.create_text(cw // 2, oy + cell_h + 40,
                      text=label, font=("Consolas", 10, "bold"), fill=ACCENT_AMBER)

        # Sequence so far
        if not ring and not johnson:
            hist_counts = [list(h.values())[0] for h in self.history
                           if isinstance(list(h.values())[0], int)]
            seq_text = " -> ".join(str(v) for v in hist_counts[-10:])
            c.create_text(cw // 2, oy + cell_h + 68,
                          text=f"Sequence: {seq_text}",
                          font=("Segoe UI", 9), fill=TEXT_DIM)

    def draw_waveform(self):
        self.canvas.delete("all")
        if not self.history:
            return

        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()

        keys = list(self.history[0].keys())
        num_signals = len(keys)
        row_h = min(70, max(40, (ch - 30) // max(num_signals, 1)))
        x_step = min(65, max(30, (cw - 110) // max(len(self.history), 1)))
        ox = 110
        oy = 15

        for i in range(len(self.history) + 1):
            x = ox + i * x_step
            self.canvas.create_line(x, oy, x, oy + num_signals * row_h,
                                     fill="#1a2540", width=1, dash=(2, 4))
            if i < len(self.history):
                self.canvas.create_text(x + x_step // 2, oy + num_signals * row_h + 12,
                                         text=str(i + 1), font=("Consolas", 7),
                                         fill=TEXT_DIM)

        self.canvas.create_text(ox + len(self.history) * x_step // 2,
                                 oy + num_signals * row_h + 25,
                                 text="Clock Tick", font=("Segoe UI", 8),
                                 fill=TEXT_DIM)

        for row_i, key in enumerate(keys):
            color = WAVE_COLORS[row_i % len(WAVE_COLORS)]
            y = oy + row_i * row_h

            self.canvas.create_rectangle(8, y + 4, 12, y + row_h - 10,
                                          fill=color, outline="")
            self.canvas.create_text(18, y + row_h // 2 - 3, text=key,
                                     anchor="w", font=("Consolas", 9, "bold"),
                                     fill=color)

            self.canvas.create_line(ox, y + row_h - 2, ox + len(self.history) * x_step,
                                     y + row_h - 2, fill="#1a2540", width=1)

            for i, rec in enumerate(self.history):
                val = rec.get(key, 0)
                is_binary = isinstance(val, int) and val in (0, 1)
                x0 = ox + i * x_step
                x1 = x0 + x_step

                if is_binary:
                    high_y = y + 8
                    low_y = y + row_h - 12
                    y_level = high_y if val == 1 else low_y

                    if val == 1:
                        self.canvas.create_rectangle(x0, high_y, x1, low_y,
                                                      fill="#0d2030", outline="")

                    self.canvas.create_line(x0, y_level, x1, y_level,
                                             width=2, fill=color)

                    if i > 0:
                        prev_val = self.history[i - 1].get(key, 0)
                        if isinstance(prev_val, int) and prev_val in (0, 1):
                            prev_level = high_y if prev_val == 1 else low_y
                            self.canvas.create_line(x0, prev_level, x0, y_level,
                                                     width=2, fill=color)
                else:
                    mx = (x0 + x1) / 2
                    my = y + row_h // 2 - 3
                    points = [x0 + 4, my, mx, my - 12, x1 - 4, my,
                              mx, my + 12]
                    self.canvas.create_polygon(points, fill=BG_CARD,
                                               outline=color, width=1)
                    self.canvas.create_text(mx, my, text=str(val),
                                             font=("Consolas", 8, "bold"),
                                             fill=color)


def launch(master=None):
    root = master if master else tk.Tk()
    if master is None:
        root.withdraw()
    SeqModule(root)
    if master is None:
        root.mainloop()


if __name__ == "__main__":
    launch()
