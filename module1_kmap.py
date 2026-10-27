"""
module1_kmap.py
-----------------
Member 1: Logic Minimization Engine (Unit 1)

Features:
 - Input minterms + don't-cares for 2,3,4 variables
 - K-Map drawn on Canvas, groupings highlighted step by step
 - Quine-McCluskey tabulation method (text trace) as cross-check
 - Minimized SOP expression shown
 - "Build Schematic" button uses gate_engine.sop_to_gate_tree() to
   auto-draw the resulting AND-OR gate circuit on a second canvas
 - Back button to return to Home
 - Knowledge panel explaining concepts
"""

import tkinter as tk
from tkinter import ttk, messagebox
from itertools import combinations
from gate_engine import sop_to_gate_tree
import math

# ─── Color palette (shared dark theme) ──────────────────────────
BG_DARK        = "#0a0f1e"
BG_CARD        = "#111827"
BG_CARD_HOVER  = "#1a2540"
ACCENT_CYAN    = "#06b6d4"
ACCENT_GREEN   = "#10b981"
ACCENT_AMBER   = "#f59e0b"
ACCENT_RED     = "#ef4444"
ACCENT_PURPLE  = "#8b5cf6"
TEXT_PRIMARY   = "#f1f5f9"
TEXT_SECONDARY = "#94a3b8"
TEXT_DIM       = "#475569"
BORDER_COLOR   = "#1e293b"
CANVAS_BG      = "#0d1526"
CELL_ON        = "#064e3b"
CELL_OFF       = "#0f172a"
CELL_DC        = "#44370a"
CELL_ON_BORDER = "#10b981"
CELL_DC_BORDER = "#f59e0b"
CELL_OFF_BORDER = "#1e293b"

# ─── Knowledge content ──────────────────────────────────────────
KNOWLEDGE = {
    "kmap": {
        "title": "K-Map (Karnaugh Map)",
        "color": ACCENT_CYAN,
        "body": (
            "A Karnaugh Map (K-Map) is a visual method for simplifying Boolean algebra.\n\n"
            "Key Rules:\n"
            "  * Cells are arranged in Gray code order — adjacent cells differ by exactly 1 bit.\n"
            "  * Group 1s (minterms) into power-of-2 rectangles (1, 2, 4, or 8 cells).\n"
            "  * Larger groups = simpler expressions (fewer literals).\n"
            "  * Don't-care (x) cells can be included to enlarge groups.\n"
            "  * Wrap-around groups are valid — the K-Map wraps like a torus.\n\n"
            "Goal: Cover all 1s with fewest, largest possible groups → Minimized SOP.\n\n"
            "Example (2-var):\n"
            "     B=0  B=1\n"
            "A=0 [ 0 ][ 1 ]\n"
            "A=1 [ 1 ][ 1 ]\n"
            "Grouping the three 1s: F = A + B"
        )
    },
    "qm": {
        "title": "Quine-McCluskey (QM) Algorithm",
        "color": ACCENT_GREEN,
        "body": (
            "QM is a tabular, systematic Boolean minimization method — equivalent to K-Maps but works for any number of variables.\n\n"
            "Steps:\n"
            "  1. Group minterms by the count of 1-bits in their binary form.\n"
            "  2. Compare adjacent groups: if two terms differ by exactly 1 bit, merge them (replace that bit with '-').\n"
            "  3. Repeat until no more merges are possible — all un-merged terms are prime implicants.\n"
            "  4. Build a prime implicant chart and select a minimal cover.\n\n"
            "Example:\n"
            "  Minterms 0(00) and 1(01) differ in 1 bit → merge to 0-(covers 0,1)\n"
            "  This represents the term: A' (A is 0, B is don't care)\n\n"
            "Advantage: Algorithmic — easily automated and scales to many variables."
        )
    },
    "sop": {
        "title": "Sum of Products (SOP) Expression",
        "color": ACCENT_PURPLE,
        "body": (
            "SOP (Sum of Products) is a canonical Boolean form:\n"
            "  Example: F = AB' + AC + B'C'D\n\n"
            "Explanation:\n"
            "  * '+' = OR operation (the 'sum')\n"
            "  * Each group (AB', AC, ...) = AND operation (a 'product term')\n"
            "  * A' means NOT A (complement)\n\n"
            "Gate Implementation:\n"
            "  * Each product term → one AND gate\n"
            "  * All AND gates → one final OR gate\n"
            "  * This is a 2-level AND-OR circuit\n\n"
            "K-Map minimization finds the fewest, simplest product terms,\n"
            "which directly gives you the most efficient 2-level gate circuit."
        )
    },
}


# ────────────── Quine-McCluskey core logic ──────────────

def qm_minimize(minterms, dontcares, num_vars):
    all_terms = sorted(set(minterms) | set(dontcares))
    if not all_terms:
        return [], []

    def to_bits(n):
        return format(n, f'0{num_vars}b')

    groups = {}
    for t in all_terms:
        ones = to_bits(t).count('1')
        groups.setdefault(ones, []).append((to_bits(t), {t}))

    all_steps = []
    prime_implicants = set()

    while True:
        new_groups = {}
        used = set()
        keys = sorted(groups.keys())
        step_log = []
        for i in range(len(keys) - 1):
            g1 = groups[keys[i]]
            g2 = groups[keys[i + 1]]
            for b1, src1 in g1:
                for b2, src2 in g2:
                    diff = sum(1 for a, b in zip(b1, b2) if a != b)
                    if diff == 1:
                        combined = ''.join(
                            a if a == b else '-' for a, b in zip(b1, b2)
                        )
                        merged_src = src1 | src2
                        ones = combined.count('1')
                        new_groups.setdefault(ones, [])
                        if (combined, frozenset(merged_src)) not in [
                            (x, frozenset(y)) for x, y in new_groups[ones]
                        ]:
                            new_groups[ones].append((combined, merged_src))
                        used.add((b1, frozenset(src1)))
                        used.add((b2, frozenset(src2)))
                        step_log.append(f"{b1} + {b2} -> {combined}")

        for key, lst in groups.items():
            for b, src in lst:
                if (b, frozenset(src)) not in used:
                    prime_implicants.add((b, frozenset(src)))

        if not new_groups:
            break
        groups = new_groups
        all_steps.append(step_log)

    pi_list = list(prime_implicants)
    chart = {m: [] for m in minterms}
    for term, (bits, src) in enumerate(pi_list):
        pass
    for idx, (bits, src) in enumerate(pi_list):
        for m in src:
            if m in chart:
                chart[m].append(idx)

    essential = set()
    covered = set()
    for m, pis in chart.items():
        if len(pis) == 1:
            essential.add(pis[0])

    for idx in essential:
        covered |= (pi_list[idx][1] & set(minterms))

    remaining = set(minterms) - covered
    chosen = set(essential)
    while remaining:
        best_idx, best_cov = None, set()
        for idx, (bits, src) in enumerate(pi_list):
            if idx in chosen:
                continue
            cov = (src & set(minterms)) & remaining
            if len(cov) > len(best_cov):
                best_idx, best_cov = idx, cov
        if best_idx is None:
            break
        chosen.add(best_idx)
        remaining -= best_cov

    final_terms = [pi_list[i][0] for i in chosen]
    return final_terms, all_steps


def bits_to_expr(bits, var_names):
    lits = []
    for ch, v in zip(bits, var_names):
        if ch == '1':
            lits.append(v)
        elif ch == '0':
            lits.append(v + "'")
    return "".join(lits) if lits else "1"


# ────────────── Knowledge Panel ──────────────

class KnowledgePanel(tk.Toplevel):
    def __init__(self, master, topic_key):
        super().__init__(master)
        info = KNOWLEDGE.get(topic_key, {"title": "Info", "body": "No info.", "color": ACCENT_CYAN})
        self.title("Knowledge: " + info["title"])
        self.geometry("580x400")
        self.configure(bg=BG_DARK)
        self.resizable(False, False)
        self.lift()
        self.focus_force()

        color = info.get("color", ACCENT_CYAN)

        hdr = tk.Frame(self, bg=color, height=4)
        hdr.pack(fill="x")

        hdr2 = tk.Frame(self, bg=BG_CARD)
        hdr2.pack(fill="x")
        tk.Label(hdr2, text="📚  " + info["title"],
                 font=("Segoe UI", 13, "bold"),
                 bg=BG_CARD, fg=color).pack(pady=10, padx=16, anchor="w")

        sep = tk.Frame(self, bg=color, height=1)
        sep.pack(fill="x")

        body_f = tk.Frame(self, bg=BG_DARK)
        body_f.pack(fill="both", expand=True, padx=16, pady=10)

        body = tk.Text(body_f, font=("Consolas", 10), bg=BG_CARD, fg=TEXT_PRIMARY,
                       relief="flat", padx=14, pady=12, wrap="word",
                       highlightthickness=1, highlightbackground=BORDER_COLOR)
        body.pack(fill="both", expand=True)
        body.insert("1.0", info["body"])
        body.configure(state="disabled")

        tk.Button(self, text="  Close  ", font=("Segoe UI", 9, "bold"),
                  bg=color, fg=BG_DARK, bd=0, padx=16, pady=6,
                  cursor="hand2", command=self.destroy,
                  relief="flat").pack(pady=10)


# ────────────── GUI ──────────────

class KMapModule(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master_ref = master
        self.title("K-Map & Quine-McCluskey Minimizer")
        self.geometry("1200x840")
        self.configure(bg=BG_DARK)
        self.resizable(True, True)

        # ── Top bar: Back button + header ──
        top_bar = tk.Frame(self, bg=BG_DARK)
        top_bar.pack(fill="x", padx=20, pady=(12, 0))

        back_btn = tk.Button(top_bar, text="<- Back to Home",
                             font=("Segoe UI", 9, "bold"),
                             bg="#1e293b", fg=ACCENT_CYAN,
                             activebackground=ACCENT_CYAN, activeforeground=BG_DARK,
                             bd=0, padx=14, pady=6, cursor="hand2",
                             command=self._go_back, relief="flat")
        back_btn.pack(side="left")
        back_btn.bind("<Enter>", lambda e: back_btn.configure(bg=ACCENT_CYAN, fg=BG_DARK))
        back_btn.bind("<Leave>", lambda e: back_btn.configure(bg="#1e293b", fg=ACCENT_CYAN))

        header_frame = tk.Frame(top_bar, bg=BG_DARK)
        header_frame.pack(side="left", padx=18)
        tk.Label(header_frame, text="Map", font=("Segoe UI", 22),
                 bg=BG_DARK, fg=ACCENT_CYAN).pack(side="left", padx=(0, 10))
        title_f = tk.Frame(header_frame, bg=BG_DARK)
        title_f.pack(side="left")
        tk.Label(title_f, text="K-Map & Quine-McCluskey Minimizer",
                 font=("Segoe UI", 17, "bold"), bg=BG_DARK,
                 fg=TEXT_PRIMARY).pack(anchor="w")
        tk.Label(title_f,
                 text="Boolean minimization  *  K-Map visualization  *  Step-by-step QM trace  *  Gate schematic",
                 font=("Segoe UI", 9), bg=BG_DARK, fg=TEXT_SECONDARY).pack(anchor="w")

        # Knowledge buttons row
        know_row = tk.Frame(self, bg=BG_DARK)
        know_row.pack(fill="x", padx=20, pady=(8, 0))
        tk.Label(know_row, text="Learn:", font=("Segoe UI", 9, "bold"),
                 bg=BG_DARK, fg=TEXT_DIM).pack(side="left")
        for label, key, color in [("  K-Map  ", "kmap", ACCENT_CYAN),
                                    ("  QM Algorithm  ", "qm", ACCENT_GREEN),
                                    ("  SOP Form  ", "sop", ACCENT_PURPLE)]:
            b = tk.Button(know_row, text="? " + label, font=("Segoe UI", 8, "bold"),
                          bg=BG_CARD, fg=color, bd=0, padx=10, pady=3,
                          cursor="hand2", relief="flat",
                          command=lambda k=key: KnowledgePanel(self, k))
            b.pack(side="left", padx=4)
            b.bind("<Enter>", lambda e, btn=b, c=color: btn.configure(bg=c, fg=BG_DARK))
            b.bind("<Leave>", lambda e, btn=b, c=color: btn.configure(bg=BG_CARD, fg=c))

        # ── Workflow steps indicator ──
        wf = tk.Frame(self, bg=BG_DARK)
        wf.pack(fill="x", padx=20, pady=(8, 0))
        steps = [("1", "Set Variables", ACCENT_CYAN),
                 ("2", "Enter Minterms", ACCENT_GREEN),
                 ("3", "Click Solve", ACCENT_AMBER),
                 ("4", "View Diagram", ACCENT_PURPLE)]
        for num, label, col in steps:
            step_f = tk.Frame(wf, bg=BG_DARK)
            step_f.pack(side="left", padx=2)
            tk.Label(step_f, text=f" {num} ", font=("Segoe UI", 8, "bold"),
                     bg=col, fg=BG_DARK).pack(side="left")
            tk.Label(step_f, text=f" {label} ", font=("Segoe UI", 8),
                     bg=BG_CARD, fg=TEXT_SECONDARY).pack(side="left")
            if num != "4":
                tk.Label(wf, text=" -> ", font=("Segoe UI", 8),
                         bg=BG_DARK, fg=TEXT_DIM).pack(side="left")

        # ── Input panel ──
        input_panel = tk.Frame(self, bg=BG_CARD, highlightbackground=BORDER_COLOR,
                               highlightthickness=1)
        input_panel.pack(fill="x", padx=20, pady=10)

        inner = tk.Frame(input_panel, bg=BG_CARD)
        inner.pack(padx=15, pady=10)

        tk.Label(inner, text="Variables:", font=("Segoe UI", 10, "bold"),
                 bg=BG_CARD, fg=TEXT_SECONDARY).grid(row=0, column=0, sticky="w", pady=3)
        self.var_count = tk.IntVar(value=4)
        var_frame = tk.Frame(inner, bg=BG_CARD)
        var_frame.grid(row=0, column=1, sticky="w", padx=10)
        for val in [2, 3, 4]:
            rb = tk.Radiobutton(var_frame, text=str(val), variable=self.var_count,
                                value=val, font=("Segoe UI", 10),
                                bg=BG_CARD, fg=TEXT_PRIMARY,
                                selectcolor=BG_DARK, activebackground=BG_CARD,
                                activeforeground=ACCENT_CYAN,
                                indicatoron=0, padx=14, pady=4, bd=0,
                                highlightthickness=1, highlightbackground=BORDER_COLOR)
            rb.pack(side="left", padx=3)

        tk.Label(inner, text="Minterms:", font=("Segoe UI", 10, "bold"),
                 bg=BG_CARD, fg=TEXT_SECONDARY).grid(row=1, column=0, sticky="w", pady=3)
        self.minterm_entry = tk.Entry(inner, width=45, font=("Consolas", 11),
                                      bg=BG_DARK, fg=ACCENT_GREEN,
                                      insertbackground=ACCENT_GREEN,
                                      relief="flat", highlightthickness=1,
                                      highlightbackground=BORDER_COLOR,
                                      highlightcolor=ACCENT_CYAN)
        self.minterm_entry.grid(row=1, column=1, padx=10, pady=3, sticky="w")
        self.minterm_entry.insert(0, "0,1,2,5,6,7,8,9,10,14")

        tk.Label(inner, text="Don't cares:", font=("Segoe UI", 10, "bold"),
                 bg=BG_CARD, fg=TEXT_SECONDARY).grid(row=2, column=0, sticky="w", pady=3)
        self.dc_entry = tk.Entry(inner, width=45, font=("Consolas", 11),
                                 bg=BG_DARK, fg=ACCENT_AMBER,
                                 insertbackground=ACCENT_AMBER,
                                 relief="flat", highlightthickness=1,
                                 highlightbackground=BORDER_COLOR,
                                 highlightcolor=ACCENT_CYAN)
        self.dc_entry.grid(row=2, column=1, padx=10, pady=3, sticky="w")
        self.dc_entry.insert(0, "3,15")

        btn_frame = tk.Frame(inner, bg=BG_CARD)
        btn_frame.grid(row=0, column=2, rowspan=3, padx=(20, 0))
        self._make_btn(btn_frame, "Solve", ACCENT_CYAN, self.solve).pack(pady=4, fill="x")
        self._make_btn(btn_frame, "Schematic", ACCENT_GREEN, self.build_schematic).pack(pady=4, fill="x")
        self._make_btn(btn_frame, "Clear", ACCENT_RED, self._clear).pack(pady=4, fill="x")

        # ── Content area ──
        content = tk.Frame(self, bg=BG_DARK)
        content.pack(fill="both", expand=True, padx=20, pady=(0, 0))

        # K-Map canvas (left)
        left_panel = tk.Frame(content, bg=BG_CARD, highlightbackground=BORDER_COLOR,
                              highlightthickness=1)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 6))

        kmap_hdr = tk.Frame(left_panel, bg="#0d1526")
        kmap_hdr.pack(fill="x")
        tk.Label(kmap_hdr, text="  K-Map Visualization", font=("Segoe UI", 10, "bold"),
                 bg="#0d1526", fg=ACCENT_CYAN, anchor="w").pack(side="left", padx=10, pady=7)
        tk.Label(kmap_hdr, text="(auto-updates on Solve)",
                 font=("Segoe UI", 8), bg="#0d1526", fg=TEXT_DIM).pack(side="left")

        self.kmap_canvas = tk.Canvas(left_panel, bg=CANVAS_BG, highlightthickness=0)
        self.kmap_canvas.pack(fill="both", expand=True, padx=8, pady=(4, 8))

        # Right side: QM text
        right_col = tk.Frame(content, bg=BG_DARK)
        right_col.pack(side="left", fill="both", expand=True, padx=(6, 0))

        right_panel = tk.Frame(right_col, bg=BG_CARD, highlightbackground=BORDER_COLOR,
                               highlightthickness=1)
        right_panel.pack(fill="both", expand=True)

        qm_hdr = tk.Frame(right_panel, bg="#0d1526")
        qm_hdr.pack(fill="x")
        tk.Label(qm_hdr, text="  QM Steps & Result", font=("Segoe UI", 10, "bold"),
                 bg="#0d1526", fg=ACCENT_GREEN, anchor="w").pack(side="left", padx=10, pady=7)

        self.result_text = tk.Text(right_panel, font=("Consolas", 10),
                                   bg=CANVAS_BG, fg=TEXT_PRIMARY,
                                   insertbackground=TEXT_PRIMARY,
                                   relief="flat", wrap="word",
                                   selectbackground=ACCENT_CYAN,
                                   selectforeground=BG_DARK,
                                   padx=12, pady=8)
        self.result_text.pack(fill="both", expand=True, padx=8, pady=8)

        self.result_text.tag_configure("heading", foreground=ACCENT_CYAN,
                                       font=("Segoe UI", 11, "bold"))
        self.result_text.tag_configure("step", foreground=ACCENT_GREEN)
        self.result_text.tag_configure("result", foreground=ACCENT_AMBER,
                                       font=("Consolas", 11, "bold"))
        self.result_text.tag_configure("info", foreground=TEXT_DIM,
                                       font=("Segoe UI", 9, "italic"))

        self.last_terms = []
        self.last_num_vars = 4

        # ── Status bar ──
        self._status_bar = tk.Label(self,
                                    text="  Ready  *  Enter minterms and click Solve  *  K-Map diagram will appear automatically",
                                    font=("Segoe UI", 8), bg="#0d1526",
                                    fg=TEXT_SECONDARY, anchor="w", pady=5)
        self._status_bar.pack(fill="x", side="bottom", padx=0)

        self.kmap_canvas.bind("<Configure>", self._draw_kmap_placeholder)

    def _go_back(self):
        self.destroy()
        try:
            self.master_ref.deiconify()
        except Exception:
            pass

    def _draw_kmap_placeholder(self, e=None):
        if self.last_terms:
            return
        c = self.kmap_canvas
        c.delete("placeholder")
        w, h = c.winfo_width(), c.winfo_height()
        if w < 10:
            return
        c.create_text(w // 2, h // 2 - 16,
                      text="[K-Map]",
                      font=("Segoe UI", 22), fill=TEXT_DIM, tags="placeholder")
        c.create_text(w // 2, h // 2 + 24,
                      text="K-Map diagram will appear here after solving",
                      font=("Segoe UI", 10), fill=TEXT_DIM, tags="placeholder")

    def _make_btn(self, parent, text, color, command):
        btn = tk.Button(parent, text=text, font=("Segoe UI", 10, "bold"),
                        bg=color, fg="#050a14", activebackground=TEXT_PRIMARY,
                        activeforeground="#050a14", bd=0, padx=16, pady=7,
                        cursor="hand2", command=command, relief="flat")
        btn.bind("<Enter>", lambda e: btn.configure(bg=TEXT_PRIMARY))
        btn.bind("<Leave>", lambda e: btn.configure(bg=color))
        return btn

    def _clear(self):
        self.result_text.delete("1.0", tk.END)
        self.kmap_canvas.delete("all")
        self.last_terms = []
        self._status_bar.config(text="  Cleared  *  Enter new minterms and click Solve",
                                fg=TEXT_SECONDARY)
        self.kmap_canvas.after(100, self._draw_kmap_placeholder)

    def parse_list(self, s):
        s = s.strip()
        if not s:
            return []
        return [int(x.strip()) for x in s.split(",") if x.strip() != ""]

    def solve(self):
        try:
            n = self.var_count.get()
            minterms = self.parse_list(self.minterm_entry.get())
            dcs = self.parse_list(self.dc_entry.get())
            for m in minterms + dcs:
                if m < 0 or m >= 2 ** n:
                    raise ValueError(f"Term {m} out of range for {n} variables")
        except ValueError as e:
            messagebox.showerror("Input error", str(e))
            return

        final_terms, steps = qm_minimize(minterms, dcs, n)
        var_names = [chr(ord('A') + i) for i in range(n)]
        exprs = [bits_to_expr(t, var_names) for t in final_terms]
        sop = " + ".join(exprs) if exprs else "0"

        self.last_terms = final_terms
        self.last_num_vars = n

        self.result_text.delete("1.0", tk.END)

        # Knowledge tip
        self.result_text.insert(tk.END,
            "Tip: Click the 'Learn' buttons above to understand K-Map and QM concepts.\n\n",
            "info")

        # Truth table summary
        self.result_text.insert(tk.END, "Truth Table Summary\n", "heading")
        self.result_text.insert(tk.END, "-" * 35 + "\n")
        header_row = "  " + "  ".join(var_names) + "  |  F\n"
        self.result_text.insert(tk.END, header_row, "step")
        self.result_text.insert(tk.END, "  " + "-" * (len(var_names)*3 + 5) + "\n")
        for m in range(2**n):
            bits = format(m, f'0{n}b')
            val = "1" if m in minterms else ("x" if m in dcs else "0")
            row = "  " + "  ".join(bits) + f"  |  {val}\n"
            tag = "result" if m in minterms else ("step" if m in dcs else "")
            self.result_text.insert(tk.END, row, tag if tag else None)
        self.result_text.insert(tk.END, "\n")

        # QM steps
        self.result_text.insert(tk.END, "Quine-McCluskey Steps\n", "heading")
        self.result_text.insert(tk.END, "-" * 35 + "\n\n")
        for i, step in enumerate(steps):
            self.result_text.insert(tk.END, f"  Round {i+1}:\n", "step")
            for line in step:
                self.result_text.insert(tk.END, f"    {line}\n")
            self.result_text.insert(tk.END, "\n")

        self.result_text.insert(tk.END, "\nPrime Implicants Selected\n", "heading")
        self.result_text.insert(tk.END, "-" * 35 + "\n")
        for t, e in zip(final_terms, exprs):
            self.result_text.insert(tk.END, f"  {t}  ->  {e}\n", "step")

        self.result_text.insert(tk.END, "\n\nMinimized SOP\n", "heading")
        self.result_text.insert(tk.END, "-" * 35 + "\n")
        self.result_text.insert(tk.END, f"  F = {sop}\n", "result")
        self.result_text.insert(tk.END,
            "\n  Each product term = one AND gate.\n"
            "  The + (OR) = the final OR gate.\n"
            "  Click 'Schematic' to see the gate diagram.\n",
            "info")

        pi_count = len(final_terms)
        self._status_bar.config(
            text=(f"  Solved  *  {n} vars  *  {len(minterms)} minterms  *  "
                  f"{pi_count} prime implicants  *  F = {sop}  *  K-Map drawn"),
            fg=ACCENT_GREEN
        )
        self.after(50, lambda: self.draw_kmap(minterms, dcs, n))

    def draw_kmap(self, minterms, dcs, n):
        self.kmap_canvas.delete("all")
        cw = self.kmap_canvas.winfo_width()
        ch = self.kmap_canvas.winfo_height()

        if n == 2:
            rows, cols = 2, 2
            row_labels = ["0", "1"]
            col_labels = ["0", "1"]
            row_header = "A"
            col_header = "B"
            def idx(r, c): return r * 2 + c
        elif n == 3:
            rows, cols = 2, 4
            row_labels = ["0", "1"]
            col_labels = ["00", "01", "11", "10"]
            row_header = "A"
            col_header = "BC"
            def idx(r, c):
                cc = [0, 1, 3, 2][c]
                return r * 4 + cc
        else:
            rows, cols = 4, 4
            row_labels = ["00", "01", "11", "10"]
            col_labels = ["00", "01", "11", "10"]
            row_header = "AB"
            col_header = "CD"
            gray = [0, 1, 3, 2]
            def idx(r, c):
                rr, cc = gray[r], gray[c]
                return rr * 4 + cc

        max_cell_w = max(50, (cw - 90) // max(cols, 1))
        max_cell_h = max(40, (ch - 90) // max(rows, 1))
        cell_w = min(max_cell_w, 85)
        cell_h = min(max_cell_h, 65)
        ox = 75
        oy = 60

        # Title with SOP result
        var_names = [chr(ord('A') + i) for i in range(n)]
        exprs = [bits_to_expr(t, var_names) for t in self.last_terms]
        sop = " + ".join(exprs) if exprs else "0"
        self.kmap_canvas.create_text(ox + cols * cell_w // 2, 18,
                                      text=f"F = {sop}",
                                      font=("Consolas", 11, "bold"), fill=ACCENT_AMBER)

        self.kmap_canvas.create_text(ox - 30, oy - 30, text=f"{col_header}->",
                                      font=("Segoe UI", 9, "bold"), fill=ACCENT_CYAN)
        self.kmap_canvas.create_text(ox - 45, oy + 10, text=f"{row_header}\nv",
                                      font=("Segoe UI", 9, "bold"), fill=ACCENT_CYAN)

        for c in range(cols):
            self.kmap_canvas.create_text(ox + c * cell_w + cell_w / 2, oy - 12,
                                          text=col_labels[c],
                                          font=("Consolas", 10, "bold"), fill=TEXT_SECONDARY)
        for r in range(rows):
            self.kmap_canvas.create_text(ox - 18, oy + r * cell_h + cell_h / 2,
                                          text=row_labels[r],
                                          font=("Consolas", 10, "bold"), fill=TEXT_SECONDARY)

        mset, dcset = set(minterms), set(dcs)
        for r in range(rows):
            for c in range(cols):
                m = idx(r, c)
                x0, y0 = ox + c * cell_w, oy + r * cell_h
                x1, y1 = x0 + cell_w, y0 + cell_h

                if m in mset:
                    color, border = CELL_ON, CELL_ON_BORDER
                elif m in dcset:
                    color, border = CELL_DC, CELL_DC_BORDER
                else:
                    color, border = CELL_OFF, CELL_OFF_BORDER

                self.kmap_canvas.create_rectangle(x0 + 1, y0 + 1, x1 - 1, y1 - 1,
                                                   fill=color, outline=border, width=2)
                self.kmap_canvas.create_text(x1 - 10, y0 + 10, text=str(m),
                                              font=("Consolas", 7), fill=TEXT_DIM)
                if m in mset:
                    self.kmap_canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2,
                                                  text="1", font=("Segoe UI", 16, "bold"),
                                                  fill=ACCENT_GREEN)
                elif m in dcset:
                    self.kmap_canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2,
                                                  text="x", font=("Segoe UI", 16, "bold"),
                                                  fill=ACCENT_AMBER)
                else:
                    self.kmap_canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2,
                                                  text="0", font=("Segoe UI", 13),
                                                  fill=TEXT_DIM)

        # Legend
        ly = oy + rows * cell_h + 16
        legends = [("1 = Minterm", ACCENT_GREEN), ("x = Don't care", ACCENT_AMBER),
                   ("0 = Not used", TEXT_DIM)]
        lx = ox
        for txt, col in legends:
            self.kmap_canvas.create_rectangle(lx, ly, lx + 12, ly + 12,
                                               fill=col, outline="")
            self.kmap_canvas.create_text(lx + 18, ly + 6, text=txt, anchor="w",
                                          font=("Segoe UI", 8), fill=TEXT_SECONDARY)
            lx += 120

        # Hint
        hint_y = ly + 28
        self.kmap_canvas.create_text(ox, hint_y,
            text="Tip: Group adjacent 1s into power-of-2 rectangles to find prime implicants",
            anchor="w", font=("Segoe UI", 8, "italic"), fill=TEXT_DIM)

    def build_schematic(self):
        if not self.last_terms:
            messagebox.showinfo("Info", "Run Solve first.")
            return
        win = tk.Toplevel(self)
        win.title("Gate Schematic -- Minimized SOP")
        win.geometry("820x540")
        win.configure(bg=BG_DARK)

        tk.Label(win, text="AND-OR Gate Realization",
                 font=("Segoe UI", 14, "bold"), bg=BG_DARK,
                 fg=TEXT_PRIMARY).pack(pady=(15, 2))
        tk.Label(win, text="Auto-generated from minimized SOP  *  Each product term = one AND gate",
                 font=("Segoe UI", 9), bg=BG_DARK, fg=TEXT_SECONDARY).pack()

        info_f = tk.Frame(win, bg=BG_CARD, highlightbackground=ACCENT_PURPLE,
                          highlightthickness=1)
        info_f.pack(fill="x", padx=15, pady=6)
        tk.Label(info_f,
                 text="Knowledge: SOP -> 2-level AND-OR circuit. Each product term drives one AND gate; all ANDs feed into one OR gate.",
                 font=("Segoe UI", 9, "italic"), bg=BG_CARD, fg=ACCENT_PURPLE,
                 wraplength=750, justify="left").pack(padx=12, pady=6, anchor="w")

        canvas = tk.Canvas(win, bg=CANVAS_BG, highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=15, pady=10)

        n = self.last_num_vars
        var_names = [chr(ord('A') + i) for i in range(n)]

        y = 50
        x_and = 280
        or_inputs_y = []

        gate_colors = [ACCENT_CYAN, ACCENT_GREEN, ACCENT_PURPLE, ACCENT_AMBER,
                       ACCENT_RED, "#60a5fa", "#fb923c"]
        gw = 70
        gh = 30

        for term_i, bits in enumerate(self.last_terms):
            gc = gate_colors[term_i % len(gate_colors)]
            lits = []
            for ch, v in zip(bits, var_names):
                if ch == '1':
                    lits.append(v)
                elif ch == '0':
                    lits.append(v + "'")

            for j, lit in enumerate(lits):
                lx = 60
                ly = y + j * 18
                canvas.create_text(lx, ly, text=lit, anchor="w",
                                   font=("Consolas", 10, "bold"), fill=gc)
                canvas.create_line(lx + 25, ly, x_and - 5, y + 8,
                                   fill=gc, width=1, dash=(3, 3))

            canvas.create_rectangle(x_and, y - 8, x_and + gw, y + gh - 8,
                                     fill=BG_CARD, outline=gc, width=2)
            canvas.create_text(x_and + gw // 2, y + gh // 2 - 8, text="AND",
                               font=("Segoe UI", 9, "bold"), fill=gc)

            or_y_target = 210
            canvas.create_line(x_and + gw, y + gh // 2 - 8,
                               x_and + gw + 80, or_y_target,
                               fill=gc, width=2)
            or_inputs_y.append(y + gh // 2 - 8)
            y += max(45, 18 * len(lits) + 22)

        or_x = x_and + gw + 80
        canvas.create_rectangle(or_x, 190, or_x + 80, 230,
                                 fill=BG_CARD, outline=ACCENT_AMBER, width=2)
        canvas.create_text(or_x + 40, 210, text="OR",
                           font=("Segoe UI", 11, "bold"), fill=ACCENT_AMBER)

        canvas.create_line(or_x + 80, 210, or_x + 140, 210,
                           fill=ACCENT_AMBER, width=3)
        canvas.create_oval(or_x + 140, 204, or_x + 152, 216,
                           fill=ACCENT_AMBER, outline="")
        canvas.create_text(or_x + 168, 210, text="F",
                           font=("Segoe UI", 14, "bold"), fill=ACCENT_AMBER)

        exprs = [bits_to_expr(t, var_names) for t in self.last_terms]
        sop = " + ".join(exprs) if exprs else "0"
        canvas.create_text(or_x + 40, 260, text=f"F = {sop}",
                           font=("Consolas", 10, "bold"), fill=TEXT_PRIMARY)


def launch(master=None):
    root = master if master else tk.Tk()
    if master is None:
        root.withdraw()
    KMapModule(root)
    if master is None:
        root.mainloop()


if __name__ == "__main__":
    launch()
