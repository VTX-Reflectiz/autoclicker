"""
AutoClicker - by Davide
Dipendenze: pip install pynput keyboard
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from pynput import mouse as pynput_mouse
from pynput.mouse import Button, Controller as MouseController
import keyboard

# ─── Costanti colori ──────────────────────────────────────────────────────────
BG        = "#1a1a2e"
SURFACE   = "#16213e"
CARD      = "#0f3460"
ACCENT    = "#e94560"
ACCENT2   = "#00b4d8"
FG        = "#eaeaea"
FG_DIM    = "#8a8aaa"
GREEN     = "#4caf50"
RED_STOP  = "#e94560"

FONT_TITLE  = ("Segoe UI", 13, "bold")
FONT_LABEL  = ("Segoe UI", 9)
FONT_SMALL  = ("Segoe UI", 8)
FONT_BIG    = ("Segoe UI", 22, "bold")
FONT_MONO   = ("Consolas", 9)

# ─── Controller globale mouse ─────────────────────────────────────────────────
mouse_ctrl = MouseController()

# ─── Mappa tasti modificatori supportati ─────────────────────────────────────
MOD_MAP = {
    "Nessuno":    [],
    "Shift":      ["shift"],
    "Ctrl":       ["ctrl"],
    "Alt":        ["alt"],
    "Ctrl+Shift": ["ctrl", "shift"],
    "Ctrl+Alt":   ["ctrl", "alt"],
    "Alt+Shift":  ["alt", "shift"],
}

BUTTON_MAP = {
    "Sinistro":  Button.left,
    "Destro":    Button.right,
    "Centrale":  Button.middle,
}

# ─── App principale ───────────────────────────────────────────────────────────
class AutoClickerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("AutoClicker")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        # Stato
        self.running       = False
        self.click_count   = 0
        self._thread: threading.Thread | None = None
        self._stop_event   = threading.Event()

        # Variabili tkinter
        self.interval_ms   = tk.IntVar(value=100)
        self.click_type    = tk.StringVar(value="Sinistro")
        self.double_click  = tk.BooleanVar(value=False)
        self.modifier_var  = tk.StringVar(value="Nessuno")
        self.custom_combo  = tk.StringVar(value="")
        self.use_custom    = tk.BooleanVar(value=False)
        self.limit_clicks  = tk.BooleanVar(value=False)
        self.max_clicks    = tk.IntVar(value=100)
        self.hotkey_var    = tk.StringVar(value="F6")

        self._build_ui()
        self._register_hotkey()

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        root = self.root

        # ── Header ──
        hdr = tk.Frame(root, bg=CARD, pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text="⚡ AutoClicker", font=FONT_TITLE,
                 bg=CARD, fg=ACCENT).pack(side="left", padx=18)
        self.status_dot = tk.Label(hdr, text="●", font=("Segoe UI", 16),
                                   bg=CARD, fg=FG_DIM)
        self.status_dot.pack(side="right", padx=8)
        self.status_lbl = tk.Label(hdr, text="INATTIVO", font=("Segoe UI", 9, "bold"),
                                   bg=CARD, fg=FG_DIM)
        self.status_lbl.pack(side="right")

        body = tk.Frame(root, bg=BG, padx=18, pady=14)
        body.pack(fill="both")

        # ── Contatore ──
        cnt_frame = tk.Frame(body, bg=SURFACE, pady=10)
        cnt_frame.pack(fill="x", pady=(0, 12))
        tk.Label(cnt_frame, text="Click totali", font=FONT_SMALL,
                 bg=SURFACE, fg=FG_DIM).pack()
        self.counter_lbl = tk.Label(cnt_frame, text="0", font=FONT_BIG,
                                    bg=SURFACE, fg=ACCENT2)
        self.counter_lbl.pack()

        # ── Intervallo ──
        self._section(body, "INTERVALLO")
        int_row = tk.Frame(body, bg=BG)
        int_row.pack(fill="x", pady=(2, 8))

        self.interval_entry = self._entry(int_row, self.interval_ms, width=7)
        self.interval_entry.pack(side="left")
        tk.Label(int_row, text="ms", font=FONT_LABEL, bg=BG, fg=FG_DIM).pack(side="left", padx=4)

        # Preset bottoni
        for label, val in [("50ms", 50), ("100ms", 100), ("250ms", 250),
                            ("500ms", 500), ("1s", 1000)]:
            tk.Button(int_row, text=label, font=FONT_SMALL,
                      bg=CARD, fg=FG, relief="flat", cursor="hand2",
                      activebackground=ACCENT, activeforeground="white",
                      command=lambda v=val: self.interval_ms.set(v)
                      ).pack(side="left", padx=2)

        # ── Tasto mouse ──
        self._section(body, "TASTO MOUSE")
        btn_row = tk.Frame(body, bg=BG)
        btn_row.pack(fill="x", pady=(2, 8))
        for opt in ["Sinistro", "Destro", "Centrale"]:
            tk.Radiobutton(btn_row, text=opt, variable=self.click_type, value=opt,
                           font=FONT_LABEL, bg=BG, fg=FG, selectcolor=CARD,
                           activebackground=BG, activeforeground=ACCENT,
                           indicatoron=0, relief="flat", padx=10, pady=4,
                           cursor="hand2").pack(side="left", padx=2)
        tk.Checkbutton(btn_row, text="Doppio click", variable=self.double_click,
                       font=FONT_LABEL, bg=BG, fg=FG, selectcolor=CARD,
                       activebackground=BG).pack(side="left", padx=10)

        # ── Modificatori ──
        self._section(body, "MODIFICATORI")
        mod_row = tk.Frame(body, bg=BG)
        mod_row.pack(fill="x", pady=(2, 4))

        tk.Label(mod_row, text="Preset:", font=FONT_LABEL,
                 bg=BG, fg=FG_DIM).pack(side="left")
        mod_menu = ttk.Combobox(mod_row, textvariable=self.modifier_var,
                                values=list(MOD_MAP.keys()), state="readonly",
                                width=14, font=FONT_LABEL)
        mod_menu.pack(side="left", padx=6)
        mod_menu.bind("<<ComboboxSelected>>",
                      lambda e: self.use_custom.set(False))

        custom_row = tk.Frame(body, bg=BG)
        custom_row.pack(fill="x", pady=(4, 8))
        tk.Checkbutton(custom_row, text="Combo manuale:", variable=self.use_custom,
                       font=FONT_LABEL, bg=BG, fg=FG, selectcolor=CARD,
                       activebackground=BG).pack(side="left")
        self._entry(custom_row, self.custom_combo, width=22,
                    placeholder="es. ctrl+shift+alt+left").pack(side="left", padx=6)
        tk.Label(custom_row, text="(nomi pynput/keyboard)", font=FONT_SMALL,
                 bg=BG, fg=FG_DIM).pack(side="left")

        # ── Limite click ──
        self._section(body, "LIMITE CLICK")
        lim_row = tk.Frame(body, bg=BG)
        lim_row.pack(fill="x", pady=(2, 8))
        tk.Checkbutton(lim_row, text="Ferma dopo", variable=self.limit_clicks,
                       font=FONT_LABEL, bg=BG, fg=FG, selectcolor=CARD,
                       activebackground=BG).pack(side="left")
        self._entry(lim_row, self.max_clicks, width=6).pack(side="left", padx=4)
        tk.Label(lim_row, text="click", font=FONT_LABEL,
                 bg=BG, fg=FG_DIM).pack(side="left")

        # ── Hotkey ──
        self._section(body, "HOTKEY START / STOP")
        hk_row = tk.Frame(body, bg=BG)
        hk_row.pack(fill="x", pady=(2, 12))
        tk.Label(hk_row, text="Tasto:", font=FONT_LABEL,
                 bg=BG, fg=FG_DIM).pack(side="left")
        hk_entry = self._entry(hk_row, self.hotkey_var, width=8)
        hk_entry.pack(side="left", padx=6)
        tk.Button(hk_row, text="Aggiorna", font=FONT_SMALL,
                  bg=CARD, fg=FG, relief="flat", cursor="hand2",
                  command=self._register_hotkey).pack(side="left")

        # ── Pulsanti Start / Stop / Reset ──
        btn_frame = tk.Frame(body, bg=BG)
        btn_frame.pack(fill="x", pady=(4, 0))

        self.start_btn = tk.Button(btn_frame, text="▶  START",
                                   font=("Segoe UI", 11, "bold"),
                                   bg=GREEN, fg="white", relief="flat",
                                   cursor="hand2", pady=8,
                                   command=self.start)
        self.start_btn.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.stop_btn = tk.Button(btn_frame, text="■  STOP",
                                  font=("Segoe UI", 11, "bold"),
                                  bg=SURFACE, fg=FG_DIM, relief="flat",
                                  cursor="hand2", pady=8, state="disabled",
                                  command=self.stop)
        self.stop_btn.pack(side="left", fill="x", expand=True, padx=(4, 0))

        tk.Button(body, text="Reset contatore",
                  font=FONT_SMALL, bg=BG, fg=FG_DIM,
                  relief="flat", cursor="hand2",
                  command=self._reset_counter).pack(pady=(6, 0))

        # Footer
        tk.Label(root, text=f"Hotkey globale: {self.hotkey_var.get()}  •  non serve tenere la finestra in primo piano",
                 font=FONT_SMALL, bg=BG, fg=FG_DIM).pack(pady=(0, 8))
        self.footer_lbl = root.winfo_children()[-1]

    def _section(self, parent, text):
        f = tk.Frame(parent, bg=BG)
        f.pack(fill="x", pady=(6, 0))
        tk.Label(f, text=text, font=("Segoe UI", 7, "bold"),
                 bg=BG, fg=ACCENT).pack(side="left")
        tk.Frame(f, bg=CARD, height=1).pack(side="left", fill="x",
                                             expand=True, padx=(6, 0))

    def _entry(self, parent, var, width=10, placeholder=""):
        e = tk.Entry(parent, textvariable=var, width=width,
                     font=FONT_MONO, bg=SURFACE, fg=FG,
                     insertbackground=FG, relief="flat",
                     highlightthickness=1, highlightcolor=ACCENT2,
                     highlightbackground=CARD)
        return e

    # ── Hotkey ───────────────────────────────────────────────────────────────
    def _register_hotkey(self):
        try:
            keyboard.unhook_all_hotkeys()
        except Exception:
            pass
        hk = self.hotkey_var.get().strip() or "F6"
        try:
            keyboard.add_hotkey(hk, self._toggle)
            try:
                self.footer_lbl.configure(
                    text=f"Hotkey globale: {hk}  •  non serve tenere la finestra in primo piano")
            except Exception:
                pass
        except Exception as ex:
            messagebox.showerror("Hotkey non valida", str(ex))

    def _toggle(self):
        if self.running:
            self.stop()
        else:
            self.start()

    # ── Click loop ────────────────────────────────────────────────────────────
    def start(self):
        if self.running:
            return
        try:
            interval = max(10, int(self.interval_ms.get())) / 1000
        except ValueError:
            messagebox.showerror("Errore", "Intervallo non valido.")
            return

        self.running = True
        self._stop_event.clear()
        self._set_ui_state(running=True)

        self._thread = threading.Thread(target=self._loop,
                                         args=(interval,), daemon=True)
        self._thread.start()

    def stop(self):
        if not self.running:
            return
        self.running = False
        self._stop_event.set()
        self._set_ui_state(running=False)

    def _loop(self, interval: float):
        btn      = BUTTON_MAP.get(self.click_type.get(), Button.left)
        double   = self.double_click.get()
        limit    = self.limit_clicks.get()
        max_n    = self.max_clicks.get() if limit else None
        use_cust = self.use_custom.get()
        mods     = []

        if use_cust:
            raw = self.custom_combo.get().strip()
            if raw:
                mods = [k.strip() for k in raw.split("+")]
                # rimuovi l'ultimo token se è il tasto mouse (non modificatore)
                # così l'utente può scrivere "ctrl+shift" o "ctrl+shift+left"
                # in ogni caso usiamo pynput per il click
        else:
            mods = MOD_MAP.get(self.modifier_var.get(), [])

        while not self._stop_event.is_set():
            # Premi modificatori
            for m in mods:
                keyboard.press(m)

            # Click
            if double:
                mouse_ctrl.click(btn, 2)
            else:
                mouse_ctrl.click(btn, 1)

            # Rilascia modificatori
            for m in reversed(mods):
                keyboard.release(m)

            self.click_count += 1
            self.root.after(0, self._update_counter)

            if max_n and self.click_count >= max_n:
                self.root.after(0, self.stop)
                break

            self._stop_event.wait(interval)

    # ── UI updates ────────────────────────────────────────────────────────────
    def _set_ui_state(self, running: bool):
        if running:
            self.start_btn.configure(bg=SURFACE, fg=FG_DIM, state="disabled")
            self.stop_btn.configure(bg=RED_STOP, fg="white", state="normal")
            self.status_dot.configure(fg=GREEN)
            self.status_lbl.configure(fg=GREEN, text="ATTIVO")
        else:
            self.start_btn.configure(bg=GREEN, fg="white", state="normal")
            self.stop_btn.configure(bg=SURFACE, fg=FG_DIM, state="disabled")
            self.status_dot.configure(fg=FG_DIM)
            self.status_lbl.configure(fg=FG_DIM, text="INATTIVO")

    def _update_counter(self):
        self.counter_lbl.configure(text=str(self.click_count))

    def _reset_counter(self):
        self.click_count = 0
        self.counter_lbl.configure(text="0")


# ─── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    root.iconbitmap(default="")          # evita errori su sistemi senza icona
    app = AutoClickerApp(root)
    root.mainloop()
