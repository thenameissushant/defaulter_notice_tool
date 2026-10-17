"""
Defaulter Notice Generator - desktop UI.

Run with:  python app.py
"""
import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from engine.pipeline import run
from engine.loader import DumpError


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Defaulter Notice Generator")
        self.geometry("720x520")
        self.minsize(620, 460)

        self.excel_path = tk.StringVar()
        self.out_dir = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "defaulter_output"))
        self.last_run_dir = None

        self._build()

    # ---------- layout ----------
    def _build(self):
        pad = {"padx": 16, "pady": 6}

        ttk.Label(self, text="Monthly Defaulter Notice Generator",
                  font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=16, pady=(16, 0))
        ttk.Label(self, text="Pick the loan data dump, and the tool will split defaulters by EMI "
                             "bucket and prepare their notices.",
                  foreground="#555").pack(anchor="w", padx=16, pady=(0, 10))

        box = ttk.Frame(self)
        box.pack(fill="x", **pad)
        box.columnconfigure(1, weight=1)

        ttk.Label(box, text="Excel dump").grid(row=0, column=0, sticky="w")
        ttk.Entry(box, textvariable=self.excel_path).grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Button(box, text="Browse...", command=self.pick_file).grid(row=0, column=2)

        ttk.Label(box, text="Save output in").grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(box, textvariable=self.out_dir).grid(row=1, column=1, sticky="ew", padx=8, pady=(8, 0))
        ttk.Button(box, text="Change...", command=self.pick_folder).grid(row=1, column=2, pady=(8, 0))

        btns = ttk.Frame(self)
        btns.pack(fill="x", **pad)
        self.run_btn = ttk.Button(btns, text="Generate notices", command=self.start)
        self.run_btn.pack(side="left")
        self.open_btn = ttk.Button(btns, text="Open output folder", command=self.open_output, state="disabled")
        self.open_btn.pack(side="left", padx=8)

        self.bar = ttk.Progressbar(self, mode="determinate")
        self.bar.pack(fill="x", **pad)

        # little result cards
        cards = ttk.Frame(self)
        cards.pack(fill="x", **pad)
        self.card_vars = {}
        for i, (key, label) in enumerate([("early", "1st / 2nd EMI"), ("severe", "3rd EMI"), ("skipped", "Skipped")]):
            f = ttk.LabelFrame(cards, text=label)
            f.grid(row=0, column=i, sticky="ew", padx=(0, 8))
            cards.columnconfigure(i, weight=1)
            v = tk.StringVar(value="-")
            ttk.Label(f, textvariable=v, font=("Segoe UI", 18, "bold")).pack(padx=20, pady=6)
            self.card_vars[key] = v

        ttk.Label(self, text="Activity log").pack(anchor="w", padx=16)
        self.log_box = tk.Text(self, height=8, state="disabled", wrap="word", bg="#fafafa", relief="solid", bd=1)
        self.log_box.pack(fill="both", expand=True, padx=16, pady=(2, 16))

    # ---------- small helpers ----------
    def pick_file(self):
        path = filedialog.askopenfilename(
            title="Select the loan dump",
            filetypes=[("Excel files", "*.xlsx *.xlsm *.xls"), ("All files", "*.*")])
        if path:
            self.excel_path.set(path)

    def pick_folder(self):
        folder = filedialog.askdirectory(title="Where should the notices be saved?")
        if folder:
            self.out_dir.set(folder)

    def write_log(self, msg):
        # called from the worker thread too, so go through after()
        def _do():
            self.log_box.configure(state="normal")
            self.log_box.insert("end", msg + "\n")
            self.log_box.see("end")
            self.log_box.configure(state="disabled")
        self.after(0, _do)

    def set_progress(self, done, total):
        def _do():
            self.bar["maximum"] = max(total, 1)
            self.bar["value"] = done
        self.after(0, _do)

    def open_output(self):
        if self.last_run_dir and os.path.isdir(self.last_run_dir):
            if os.name == "nt":
                os.startfile(self.last_run_dir)
            else:
                import subprocess, sys
                subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", self.last_run_dir])

    # ---------- run ----------
    def start(self):
        path = self.excel_path.get().strip().strip('"')   # people paste paths with quotes from Explorer
        if not path:
            messagebox.showwarning("File needed", "Please choose the Excel dump first.")
            return
        if not os.path.isfile(path):
            messagebox.showerror("File not found", f"I can't find:\n{path}")
            return

        self.run_btn.configure(state="disabled")
        self.open_btn.configure(state="disabled")
        self.bar["value"] = 0
        for v in self.card_vars.values():
            v.set("-")
        threading.Thread(target=self._worker, args=(path,), daemon=True).start()

    def _worker(self, path):
        try:
            result = run(path, self.out_dir.get(), progress=self.set_progress, log=self.write_log)
            self.last_run_dir = result["run_dir"]
            self.after(0, lambda: self._finish(result))
        except DumpError as e:
            self.after(0, lambda: self._fail(str(e)))
        except Exception as e:
            self.write_log(f"Unexpected error: {e!r}")
            self.after(0, lambda: self._fail(f"Something went wrong:\n{e}"))

    def _finish(self, result):
        for k in ("early", "severe", "skipped"):
            self.card_vars[k].set(str(result[k]))
        self.run_btn.configure(state="normal")
        self.open_btn.configure(state="normal")
        messagebox.showinfo("Done", f"Notices generated for {result['early'] + result['severe']} customers.")

    def _fail(self, msg):
        self.run_btn.configure(state="normal")
        messagebox.showerror("Could not finish", msg)


if __name__ == "__main__":
    App().mainloop()
