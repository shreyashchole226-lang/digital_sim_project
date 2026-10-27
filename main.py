"""
main.py
--------
Digital Logic Design & Simulation Toolkit
Home menu -> launches each member's module in its own window.

Run with:
    python main.py
(Requires only the Python standard library: tkinter)
"""

import tkinter as tk
from tkinter import ttk
import math, random

import module1_kmap
import module2_combinational
import module3_sequential
import module4_asm_pld


# ─── Color palette ───────────────────────────────────────────────
BG_DARK        = "#0a0f1e"
BG_DEEP        = "#070c18"
BG_CARD        = "#111827"
BG_CARD_HOVER  = "#1a2540"
ACCENT_BLUE    = "#3b82f6"
ACCENT_CYAN    = "#06b6d4"
ACCENT_GREEN   = "#10b981"
ACCENT_PURPLE  = "#8b5cf6"
ACCENT_AMBER   = "#f59e0b"
ACCENT_PINK    = "#ec4899"
TEXT_PRIMARY   = "#f1f5f9"
TEXT_SECONDARY = "#94a3b8"
TEXT_DIM       = "#475569"
BORDER_DARK    = "#1e293b"
BORDER_GLOW    = "#334155"


# ─── Particle dot for animated background ────────────────────────
class Particle:
    def __init__(self, w, h):
        self.reset(w, h)

    def reset(self, w, h):
        self.x  = random.randint(0, w)
        self.y  = random.randint(0, h)
        self.r  = random.uniform(1.0, 2.8)
        self.vx = random.uniform(-0.3, 0.3)
        self.vy = random.uniform(-0.25, -0.05)
        self.alpha = random.uniform(0.2, 0.8)
        self.color = random.choice([ACCENT_CYAN, ACCENT_BLUE, ACCENT_PURPLE,
                                    ACCENT_GREEN, "#60a5fa"])

    def step(self, w, h):
        self.x += self.vx
        self.y += self.vy
        self.alpha -= 0.003
        if self.y < 0 or self.alpha <= 0:
            self.reset(w, h)
            self.y = h

    def hex_with_alpha(self, base_hex):
        r = int(base_hex[1:3], 16)
        g = int(base_hex[3:5], 16)
        b = int(base_hex[5:7], 16)
        t = max(0.0, min(1.0, self.alpha))
        bg_r, bg_g, bg_b = 10, 15, 30
        R = int(bg_r + (r - bg_r) * t)
        G = int(bg_g + (g - bg_g) * t)
        B = int(bg_b + (b - bg_b) * t)
        return f"#{R:02x}{G:02x}{B:02x}"


class ParticleBG(tk.Canvas):
    NUM = 45

    def __init__(self, master, **kw):
        super().__init__(master, highlightthickness=0, bg=BG_DARK, **kw)
        self.parts = []
        self.bind("<Configure>", self._init_particles)
        self._running = True
        self._loop()

    def _init_particles(self, e=None):
        w, h = self.winfo_width(), self.winfo_height()
        if w < 10:
            return
        if not self.parts:
            self.parts = [Particle(w, h) for _ in range(self.NUM)]

    def _loop(self):
        if not self._running:
            return
        w, h = self.winfo_width(), self.winfo_height()
        if w > 10 and self.parts:
            self.delete("particles")
            for p in self.parts:
                p.step(w, h)
                col = p.hex_with_alpha(p.color)
                r = p.r
                self.create_oval(p.x - r, p.y - r, p.x + r, p.y + r,
                                 fill=col, outline="", tags="particles")
            # draw faint connection lines
            for i, a in enumerate(self.parts):
                for b in self.parts[i+1:]:
                    dist = math.hypot(a.x - b.x, a.y - b.y)
                    if dist < 90:
                        t = max(0, 1 - dist / 90) * 0.18
                        v = int(255 * t)
                        lc = f"#{v:02x}{v+5:02x}{v+15:02x}"
                        self.create_line(a.x, a.y, b.x, b.y, fill=lc,
                                         width=1, tags="particles")
        self.after(28, self._loop)

    def stop(self):
        self._running = False


# ─── Animated Module Card ─────────────────────────────────────────
class AnimatedCard(tk.Canvas):
    def __init__(self, master, title, subtitle, icon_char, accent_color,
                 badge_text="", command=None, **kwargs):
        super().__init__(master, highlightthickness=0, bg=BG_DARK,
                         cursor="hand2", **kwargs)
        self.title_text    = title
        self.subtitle_text = subtitle
        self.icon_char     = icon_char
        self.accent        = accent_color
        self.badge_text    = badge_text
        self.command       = command
        self._glow_alpha   = 0.0
        self._anim_id      = None
        self._click_scale  = 1.0

        self.bind("<Enter>",     self._on_enter)
        self.bind("<Leave>",     self._on_leave)
        self.bind("<Button-1>",  self._on_click)
        self.bind("<Configure>", self._draw)

    def _on_enter(self, e=None):
        self._animate(1.0)

    def _on_leave(self, e=None):
        self._animate(0.0)

    def _on_click(self, e=None):
        if self.command:
            self._click_flash()
            self.after(140, self.command)

    def _click_flash(self):
        orig = self._glow_alpha
        self.configure(bg="#0e1a30")
        self.after(140, lambda: self.configure(bg=BG_DARK))

    def _animate(self, target):
        if self._anim_id:
            self.after_cancel(self._anim_id)
        self._step(target, 0.10 if target > self._glow_alpha else -0.10)

    def _step(self, target, step):
        self._glow_alpha = max(0.0, min(1.0, self._glow_alpha + step))
        self._draw()
        done = (step > 0 and self._glow_alpha >= target) or \
               (step < 0 and self._glow_alpha <= target)
        if not done:
            self._anim_id = self.after(16, lambda: self._step(target, step))

    def _lerp(self, c1, c2, t):
        r1,g1,b1 = int(c1[1:3],16),int(c1[3:5],16),int(c1[5:7],16)
        r2,g2,b2 = int(c2[1:3],16),int(c2[3:5],16),int(c2[5:7],16)
        r = int(r1+(r2-r1)*t); g = int(g1+(g2-g1)*t); b = int(b1+(b2-b1)*t)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _draw(self, e=None):
        self.delete("all")
        w = self.winfo_width(); h = self.winfo_height()
        if w < 10 or h < 10:
            return
        t = self._glow_alpha

        # card background
        bg = self._lerp(BG_CARD, BG_CARD_HOVER, t)
        border = self._lerp(BORDER_DARK, self.accent, t * 0.8)
        self._rrect(3, 3, w-3, h-3, 12, fill=bg, outline=border, width=2)

        # left accent stripe (glows on hover)
        stripe_color = self._lerp(self.accent+"44"[:7], self.accent, t)
        stripe_h = int(h * 0.55)
        sy = (h - stripe_h) // 2
        self._rrect(6, sy, 11, sy+stripe_h, 3, fill=self.accent, outline="")

        # icon background circle
        ix, iy, ir = 52, h//2, 24
        icon_bg = self._lerp("#0f172a", self.accent, 0.18 + t * 0.14)
        self.create_oval(ix-ir, iy-ir, ix+ir, iy+ir,
                         fill=icon_bg, outline=self.accent, width=1+(t>0.4))
        self.create_text(ix, iy, text=self.icon_char,
                         font=("Segoe UI Emoji", 17), fill=self.accent)

        # title
        title_col = self._lerp(TEXT_PRIMARY, "#ffffff", t*0.4)
        self.create_text(90, h//2 - 13, text=self.title_text, anchor="w",
                         font=("Segoe UI", 12, "bold"), fill=title_col)

        # subtitle
        self.create_text(90, h//2 + 10, text=self.subtitle_text, anchor="w",
                         font=("Segoe UI", 8), fill=TEXT_SECONDARY)

        # badge
        if self.badge_text:
            bx = w - 85
            by = h//2
            bw, bh = 68, 18
            badge_bg = self._lerp(BORDER_DARK, self.accent, t*0.3)
            self._rrect(bx, by-bh//2, bx+bw, by+bh//2, 9,
                        fill=badge_bg, outline=self.accent, width=1)
            self.create_text(bx+bw//2, by, text=self.badge_text,
                             font=("Segoe UI", 7, "bold"), fill=self.accent)

        # arrow
        ax = w - 22 if not self.badge_text else w - 105
        arrow_col = self._lerp(TEXT_DIM, self.accent, t)
        self.create_text(ax, h//2, text="›", font=("Segoe UI", 18), fill=arrow_col)

    def _rrect(self, x1,y1,x2,y2,r, **kw):
        pts = [x1+r,y1, x2-r,y1, x2,y1, x2,y1+r,
               x2,y2-r, x2,y2, x2-r,y2, x1+r,y2,
               x1,y2, x1,y2-r, x1,y1+r, x1,y1]
        self.create_polygon(pts, smooth=True, **kw)


# ─── Status dot widget ────────────────────────────────────────────
class StatusDot(tk.Canvas):
    """Pulsing dot that signals "Ready"."""
    def __init__(self, master, color, **kw):
        super().__init__(master, width=12, height=12, bg=BG_DARK,
                         highlightthickness=0, **kw)
        self._color = color
        self._t = 0
        self._pulse()

    def _pulse(self):
        self._t += 0.08
        scale = 0.5 + 0.5 * math.sin(self._t)
        r = 3 + 2 * scale
        cx, cy = 6, 6
        self.delete("all")
        # outer glow
        self.create_oval(cx-r-2, cy-r-2, cx+r+2, cy+r+2,
                         fill="", outline=self._color,
                         width=1 if scale > 0.5 else 0)
        self.create_oval(cx-r, cy-r, cx+r, cy+r,
                         fill=self._color, outline="")
        self.after(40, self._pulse)


# ─── Home App ─────────────────────────────────────────────────────
class HomeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Digital Logic Design & Simulation Toolkit")
        self.geometry("740x660")
        self.configure(bg=BG_DARK)
        self.resizable(False, False)

        # ── Particle background (full window) ──
        self._bg_canvas = ParticleBG(self)
        self._bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # ── Foreground container (transparent-ish) ──
        # All UI is packed directly on the window
        self._build_ui()

    def _build_ui(self):
        # ── Top gradient bar ──
        bar = tk.Canvas(self, height=3, bg=BG_DARK, highlightthickness=0)
        bar.pack(fill="x")
        bar.bind("<Configure>", lambda e: self._gradient_bar(bar))

        # ── Header section ──
        header = tk.Frame(self, bg=BG_DARK)
        header.pack(fill="x", pady=(28, 0))

        # Icon + pulse dot row
        icon_row = tk.Frame(header, bg=BG_DARK)
        icon_row.pack()
        self._icon_label = tk.Label(icon_row, text="⚡", font=("Segoe UI Emoji", 32),
                                    bg=BG_DARK, fg=ACCENT_CYAN)
        self._icon_label.pack(side="left")
        StatusDot(icon_row, ACCENT_GREEN).pack(side="left", padx=(6,0), pady=(18,0))

        # Title
        tk.Label(header, text="Digital Logic Design",
                 font=("Segoe UI", 26, "bold"), bg=BG_DARK,
                 fg=TEXT_PRIMARY).pack(pady=(8, 0))
        tk.Label(header, text="& Simulation Toolkit",
                 font=("Segoe UI", 19), bg=BG_DARK,
                 fg=ACCENT_CYAN).pack()

        # Subtitle
        tk.Label(header,
                 text="Interactive simulators for K-Maps • Combinational & Sequential Circuits • ASMs & PLDs",
                 font=("Segoe UI", 9), bg=BG_DARK,
                 fg=TEXT_SECONDARY, wraplength=560).pack(pady=(8, 0))

        # Version / info chips
        chips_row = tk.Frame(header, bg=BG_DARK)
        chips_row.pack(pady=(10, 0))
        for text, color in [("  Python + Tkinter  ", ACCENT_BLUE),
                             ("  4 Modules  ", ACCENT_PURPLE),
                             ("  Gate-Level Simulation  ", ACCENT_GREEN)]:
            chip = tk.Label(chips_row, text=text, font=("Segoe UI", 8, "bold"),
                            bg=BG_DARK, fg=color,
                            relief="flat", bd=0,
                            highlightthickness=1, highlightbackground=color,
                            padx=5, pady=3)
            chip.pack(side="left", padx=4)

        # ── Separator ──
        sep = tk.Canvas(self, height=1, bg=BG_DARK, highlightthickness=0)
        sep.pack(fill="x", padx=70, pady=(18, 12))
        sep.bind("<Configure>", lambda e: self._draw_sep(sep))

        # ── Section label ──
        tk.Label(self, text="  SELECT A MODULE TO SIMULATE",
                 font=("Segoe UI", 8, "bold"), bg=BG_DARK,
                 fg=TEXT_DIM, anchor="w").pack(fill="x", padx=42, pady=(0, 6))

        # ── Module cards ──
        cards_frame = tk.Frame(self, bg=BG_DARK)
        cards_frame.pack(fill="both", expand=True, padx=40)

        modules = [
            ("K-Map & Quine-McCluskey Minimizer",
             "Boolean minimization  •  K-map grid  •  AND-OR gate schematic",
             "🗺", ACCENT_CYAN, "Unit 1 • Logic",
             lambda: (self.iconify(), module1_kmap.launch(self))),

            ("Combinational Circuit Simulator",
             "Adders / Subtractors  •  Code converters  •  Gate propagation",
             "🔌", ACCENT_GREEN, "Unit 2A • Comb.",
             lambda: (self.iconify(), module2_combinational.launch(self))),

            ("Sequential Circuit Simulator",
             "Flip-flops  •  Shift registers  •  Counters  •  Timing diagrams",
             "⏱", ACCENT_PURPLE, "Unit 2B • Seq.",
             lambda: (self.iconify(), module3_sequential.launch(self))),

            ("ASM/FSM & PLA-PAL Simulator",
             "State machines  •  ASM charts  •  PLA fuse programming",
             "🔀", ACCENT_AMBER, "Unit 3 • FSM",
             lambda: (self.iconify(), module4_asm_pld.launch(self))),
        ]

        for title, sub, icon, color, badge, cmd in modules:
            card = AnimatedCard(cards_frame, title, sub, icon, color,
                                badge_text=badge, command=cmd,
                                width=640, height=82)
            card.pack(pady=5)

        # ── Bottom info bar ──
        info_bar = tk.Frame(self, bg=BG_DEEP, height=36)
        info_bar.pack(fill="x", side="bottom")
        info_bar.pack_propagate(False)

        tk.Label(info_bar,
                 text="Digital Electronics  •  Units 1–3  •  Course Project",
                 font=("Segoe UI", 8), bg=BG_DEEP,
                 fg=TEXT_DIM).pack(side="left", padx=16, pady=8)

        # stat dots
        stat_row = tk.Frame(info_bar, bg=BG_DEEP)
        stat_row.pack(side="right", padx=16)
        for stat, color in [("4 Modules", ACCENT_CYAN),
                             ("Pure stdlib", ACCENT_GREEN)]:
            tk.Label(stat_row, text="● ", font=("Segoe UI", 7),
                     bg=BG_DEEP, fg=color).pack(side="left")
            tk.Label(stat_row, text=stat + "  ", font=("Segoe UI", 7),
                     bg=BG_DEEP, fg=TEXT_DIM).pack(side="left")

        # ── Pulse animation ──
        self._pulse_t = 0
        self._pulse()

    def _gradient_bar(self, c):
        c.delete("all")
        w = c.winfo_width()
        if w < 2:
            return
        cols = [ACCENT_CYAN, ACCENT_BLUE, ACCENT_PURPLE, ACCENT_PINK]
        seg = w // len(cols)
        for ci, col in enumerate(cols):
            nxt = cols[(ci+1) % len(cols)]
            for i in range(seg):
                t = i / seg
                r = int(int(col[1:3],16) + (int(nxt[1:3],16)-int(col[1:3],16))*t)
                g = int(int(col[3:5],16) + (int(nxt[3:5],16)-int(col[3:5],16))*t)
                b = int(int(col[5:7],16) + (int(nxt[5:7],16)-int(col[5:7],16))*t)
                x = ci*seg + i
                c.create_line(x, 0, x, 3, fill=f"#{r:02x}{g:02x}{b:02x}")

    def _draw_sep(self, canvas):
        canvas.delete("all")
        w = canvas.winfo_width()
        mid = w // 2
        for i in range(w):
            dist = abs(i - mid) / max(mid, 1)
            alpha = max(0, 1.0 - dist * 2.2)
            v = int(30 + 60 * alpha)
            canvas.create_line(i, 0, i, 1, fill=f"#{v:02x}{v+8:02x}{v+20:02x}")

    def _pulse(self):
        self._pulse_t += 1
        t = (math.sin(self._pulse_t * 0.07) + 1) / 2
        r = int(6  + (56  - 6)  * t)
        g = int(182 + (220 - 182) * t)
        b = int(212 + (255 - 212) * t)
        try:
            self._icon_label.configure(fg=f"#{r:02x}{g:02x}{b:02x}")
        except tk.TclError:
            return
        self.after(45, self._pulse)


if __name__ == "__main__":
    app = HomeApp()
    app.mainloop()
