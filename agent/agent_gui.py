"""Jarvis desktop cockpit with a visible, persistent task timeline."""
from __future__ import annotations

import threading
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from pathlib import Path
from PIL import Image

from jarvis_core import JarvisCore
import task_runtime


class JarvisGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("JARVIS // NEURAL COCKPIT")
        self.geometry("1280x820")
        self.minsize(980, 650)
        self.configure(fg_color="#080b12")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.busy = False
        self.state_text = tk.StringVar(value="GOTOWY")
        self.task_text = tk.StringVar(value="Brak aktywnego zadania")
        self.jarvis = JarvisCore(confirm=self.confirm_action, progress_callback=self.on_progress)
        self.build()
        self._restore_task_timeline()
        self.after(120, self.pulse)

    def confirm_action(self, prompt):
        """Show any unavoidable safety confirmation on Tk's UI thread."""
        finished = threading.Event()
        answer = [False]

        def ask():
            try:
                answer[0] = messagebox.askyesno("Potwierdzenie Jarvisa", prompt, parent=self)
            finally:
                finished.set()

        self.after(0, ask)
        return finished.wait(300) and answer[0]

    def build(self):
        bar = ctk.CTkFrame(self, fg_color="#0d1420", corner_radius=0)
        bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        bar.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(bar, text="JARVIS", font=ctk.CTkFont(size=22, weight="bold"), text_color="#77e6ff").grid(row=0, column=0, padx=22, pady=15)
        ctk.CTkLabel(bar, textvariable=self.state_text, font=ctk.CTkFont(size=12, weight="bold"), text_color="#71f6b5").grid(row=0, column=1, sticky="w")
        ctk.CTkButton(bar, text="AWARYJNE STOP", width=130, fg_color="#8f2638", command=self.stop).grid(row=0, column=2, padx=18)

        face = ctk.CTkFrame(self, fg_color="#0a101a", corner_radius=0)
        face.grid(row=1, column=0, padx=(16, 8), pady=16, sticky="nsew")
        face.grid_rowconfigure(0, weight=1)
        face.grid_columnconfigure(0, weight=1)
        asset = Path(__file__).resolve().parent.parent / "assets" / "jarvis_face.webp"
        self.face_image = ctk.CTkImage(light_image=Image.open(asset), dark_image=Image.open(asset), size=(390, 440))
        ctk.CTkLabel(face, image=self.face_image, text="").grid(row=0, column=0, padx=18, pady=18)
        ctk.CTkLabel(face, textvariable=self.task_text, wraplength=360, text_color="#90a8ba").grid(row=1, column=0, padx=20, pady=(0, 18))

        panel = ctk.CTkFrame(self, fg_color="#0d1420", corner_radius=8)
        panel.grid(row=1, column=1, padx=(8, 16), pady=16, sticky="nsew")
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(0, weight=3)
        panel.grid_rowconfigure(1, weight=1)
        self.chat = ctk.CTkTextbox(panel, state="disabled", font=ctk.CTkFont(size=14))
        self.chat.grid(row=0, column=0, padx=14, pady=(14, 8), sticky="nsew")
        self.progress_view = ctk.CTkTextbox(panel, state="disabled", height=130, font=ctk.CTkFont(size=12), text_color="#9eb6c4")
        self.progress_view.grid(row=1, column=0, padx=14, pady=8, sticky="nsew")
        bottom = ctk.CTkFrame(panel, fg_color="transparent")
        bottom.grid(row=2, column=0, padx=14, pady=(0, 14), sticky="ew")
        bottom.grid_columnconfigure(0, weight=1)
        self.input = ctk.CTkEntry(bottom, placeholder_text="Wpisz polecenie dla Jarvisa...")
        self.input.grid(row=0, column=0, sticky="ew")
        self.input.bind("<Return>", lambda _: self.send())
        self.send_button = ctk.CTkButton(bottom, text="WYŚLIJ", width=100, command=self.send)
        self.send_button.grid(row=0, column=1, padx=(10, 0))

        ctk.CTkLabel(self, text="SYSTEM ONLINE  •  LOCAL-FIRST  •  ZAPIS POSTĘPU LOKALNIE", text_color="#698394").grid(row=2, column=0, columnspan=2, padx=18, pady=8, sticky="w")

    def _append(self, widget, text):
        widget.configure(state="normal")
        widget.insert("end", text + "\n")
        widget.see("end")
        widget.configure(state="disabled")

    def write(self, sender, text):
        self._append(self.chat, f"{sender}: {text}\n")

    def on_progress(self, event):
        """Core callback can run on a worker; marshal all UI work to Tk."""
        self.after(0, self._show_progress, event)

    def _show_progress(self, event):
        self.state_text.set(event.get("stage", "PRACUJE").replace("_", " ").upper())
        self.task_text.set(event.get("message", "Jarvis pracuje"))
        self._append(self.progress_view, f"• {event.get('stage', 'krok')}: {event.get('message', '')}")
        if event.get("result"):
            evidence = str(event["result"]).replace("\n", " ")[:360]
            self._append(self.progress_view, f"  Wynik: {evidence}")

    def _restore_task_timeline(self):
        try:
            for event in task_runtime.recent(30):
                self._append(self.progress_view, f"• {event['stage']}: {event['message']}")
                if event.get("details", {}).get("result"):
                    self._append(self.progress_view, f"  Wynik: {str(event['details']['result']).replace(chr(10), ' ')[:360]}")
            pending = task_runtime.latest_pending()
            if pending:
                self.task_text.set("Plan oczekuje na Twoją akceptację")
                self.state_text.set("OCZEKUJE NA AKCEPTACJĘ")
                self.write("SYSTEM", f"Mam zapisany plan zadania: {pending['goal']}. Możesz napisać ‘zatwierdzam plan’, aby wznowić.")
            handoff = task_runtime.latest_waiting_user()
            if handoff:
                self.task_text.set("Jarvis czeka na krok po Twojej stronie")
                self.state_text.set("CZEKA NA CIEBIE")
                self.write("SYSTEM", f"Zadanie czeka na Twój krok: {handoff['goal']}. Gdy skończysz, napisz ‘gotowe’.")
        except Exception:
            self._append(self.progress_view, "• Historia postępu jest chwilowo niedostępna.")

    def send(self):
        if self.busy:
            return
        message = self.input.get().strip()
        if not message:
            return
        self.input.delete(0, "end")
        self.write("TY", message)
        self.busy = True
        self.send_button.configure(state="disabled")
        self.state_text.set("PRACUJE")
        self.task_text.set(message[:180])
        threading.Thread(target=self.process, args=(message,), daemon=True).start()

    def process(self, message):
        try:
            answer = self.jarvis.ask(message)
        except Exception as exc:
            answer = f"Zadanie zatrzymane przez błąd programu ({type(exc).__name__})."
        self.after(0, self.done, answer)

    def done(self, answer):
        self.write("JARVIS", answer)
        self.busy = False
        self.send_button.configure(state="normal")
        pending = task_runtime.latest_pending()
        if pending:
            self.state_text.set("OCZEKUJE NA AKCEPTACJĘ")
            self.task_text.set("Plan czeka na Twoją decyzję")
        elif task_runtime.latest_waiting_user():
            self.state_text.set("CZEKA NA CIEBIE")
            self.task_text.set("Jarvis czeka na Twój krok")
        else:
            current = task_runtime.get(self.jarvis.active_task_id) if self.jarvis.active_task_id else None
            state = current.get("status") if current else "done"
            self.state_text.set("ZATRZYMANO / SPRAWDŹ" if state == "blocked" else "WYMAGA WERYFIKACJI" if state == "needs_review" else "ZAKOŃCZONE" if state == "done" else "GOTOWY")
            self.task_text.set(current.get("goal", "Ostatnie zadanie zakończone")[:180] if current else "Ostatnie zadanie zakończone")

    def stop(self):
        self.jarvis.run_skill("emergency_stop", "stop")
        self.state_text.set("ZATRZYMANY")
        self.write("SYSTEM", "Aktywowano awaryjne zatrzymanie. Bieżący krok zewnętrzny może już być w toku.")

    def pulse(self):
        self.after(420, self.pulse)


if __name__ == "__main__":
    JarvisGUI().mainloop()
