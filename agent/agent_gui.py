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
import user_settings
import local_provider
try:
    from connector_registry import catalog, add_custom
except ImportError:
    from agent.connector_registry import catalog, add_custom

PROVIDER_LABELS = {
    "auto": "Auto (online, gdy jest klucz)",
    "local": "Lokalny (Ollama)",
    "hosted": "Online (klucz w .env)",
}
MODES = ["asystent", "badacz", "inzynier", "krytyk", "opiekun"]


class SettingsWindow(ctk.CTkToplevel):
    """Model settings: source (auto/local/online), Ollama model and online model name."""

    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.title("Ustawienia Jarvisa")
        self.geometry("580x560")
        self.minsize(520, 520)
        self.configure(fg_color="#0d1420")
        self.transient(app)
        prefs = user_settings.load()
        self.grid_columnconfigure(0, weight=1)
        label = lambda text: ctk.CTkLabel(self, text=text, text_color="#77e6ff", anchor="w", font=ctk.CTkFont(size=13, weight="bold"))

        label("Źródło modelu").grid(row=0, column=0, padx=22, pady=(20, 4), sticky="ew")
        self.provider_var = tk.StringVar(value=PROVIDER_LABELS.get(prefs["provider"], PROVIDER_LABELS["auto"]))
        ctk.CTkOptionMenu(self, values=list(PROVIDER_LABELS.values()), variable=self.provider_var, command=lambda _: self.update_hint()).grid(row=1, column=0, padx=22, sticky="ew")

        label("Model lokalny (Ollama)").grid(row=2, column=0, padx=22, pady=(16, 4), sticky="ew")
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.grid(row=3, column=0, padx=22, sticky="ew")
        row.grid_columnconfigure(0, weight=1)
        self.local_box = ctk.CTkComboBox(row, values=[prefs["local_model"] or "(wybierz lub wpisz nazwę)"], command=lambda _: self.update_hint())
        self.local_box.set(prefs["local_model"])
        self.local_box.grid(row=0, column=0, sticky="ew")
        self.local_box.bind("<KeyRelease>", lambda _: self.update_hint())
        ctk.CTkButton(row, text="Odśwież listę", width=120, command=self.refresh_models).grid(row=0, column=1, padx=(10, 0))

        label("Model online (Groq lub inny)").grid(row=4, column=0, padx=22, pady=(16, 4), sticky="ew")
        self.hosted_entry = ctk.CTkEntry(self, placeholder_text="puste = JARVIS_MODEL z pliku .env")
        self.hosted_entry.grid(row=5, column=0, padx=22, sticky="ew")
        if prefs["hosted_model"]:
            self.hosted_entry.insert(0, prefs["hosted_model"])

        self.hint = ctk.CTkLabel(self, text="", wraplength=500, justify="left", anchor="w", text_color="#90a8ba")
        self.hint.grid(row=6, column=0, padx=22, pady=(16, 4), sticky="ew")
        self.current = ctk.CTkLabel(self, text="", wraplength=500, justify="left", anchor="w", text_color="#71f6b5")
        self.current.grid(row=7, column=0, padx=22, pady=4, sticky="ew")
        ctk.CTkLabel(self, text="Klucze API i hasła ustawiasz tylko w pliku agent\\.env. Ta strona ich nie zapisuje.", wraplength=500, justify="left", anchor="w", text_color="#698394").grid(row=8, column=0, padx=22, pady=4, sticky="ew")

        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.grid(row=9, column=0, padx=22, pady=(14, 20), sticky="e")
        ctk.CTkButton(buttons, text="ZASTOSUJ", width=120, command=self.apply).grid(row=0, column=0, padx=(0, 10))
        ctk.CTkButton(buttons, text="ZAMKNIJ", width=100, fg_color="#2a3445", command=self.destroy).grid(row=0, column=1)

        self.update_hint()
        self.show_current(self.app.jarvis.model_router.describe())
        self.refresh_models()
        self.after(250, self._front)


    def selected_provider(self):
        return next((key for key, text in PROVIDER_LABELS.items() if text == self.provider_var.get()), "auto")

    def update_hint(self):
        name = self.local_box.get().strip()
        notes = []
        if self.selected_provider() == "hosted":
            notes.append("Online wymaga klucza API w pliku .env.")
        elif name.endswith("-cloud"):
            notes.append("Model z końcówką -cloud działa na serwerach Ollamy: Twoje rozmowy opuszczają komputer. Wymaga ollama signin i ollama pull.")
        elif self.selected_provider() == "local":
            notes.append("Model lokalny działa tylko na tym komputerze. Jarvis sam nie pobiera modeli.")
        else:
            notes.append("Auto: jeśli w .env jest klucz API, użyty będzie model online, w przeciwnym razie lokalny.")
        self.hint.configure(text=" ".join(notes))

    def show_current(self, info, ok_prefix="Aktualnie"):
        if info.get("client_ready", info.get("provider") != "unavailable"):
            self.current.configure(text=f"{ok_prefix}: {info.get('provider')} • {info.get('model')}", text_color="#71f6b5")
        else:
            self.current.configure(text=info.get("warning") or "Brak dostępnego modelu.", text_color="#ffb454")

    def refresh_models(self):
        def work():
            try:
                found = local_provider.models(user_settings.load()["ollama_url"] or None)
            except Exception:
                found = []
            self.app.after(0, self._models_ready, found)
        threading.Thread(target=work, daemon=True).start()

    def _models_ready(self, found):
        try:
            current = self.local_box.get()
            self.local_box.configure(values=found or ["(Ollama nie odpowiada lub brak modeli)"])
            self.local_box.set(current)
            self.update_hint()
        except tk.TclError:
            pass

    def apply(self):
        if self.app.busy:
            self.current.configure(text="Jarvis pracuje. Poczekaj na koniec zadania i spróbuj ponownie.", text_color="#ffb454")
            return
        local = self.local_box.get().strip()
        if local.startswith("("):
            local = ""
        user_settings.save(provider=self.selected_provider(), local_model=local, hosted_model=self.hosted_entry.get().strip())
        self.current.configure(text="Stosuję ustawienia...", text_color="#90a8ba")
        threading.Thread(target=self._reload, daemon=True).start()

    def _reload(self):
        try:
            info = self.app.jarvis.reload_model()
        except Exception as exc:
            info = {"provider": "unavailable", "model": "", "warning": f"Nie udało się zastosować ustawień ({type(exc).__name__})."}
        self.app.after(0, self._reloaded, info)

    def _reloaded(self, info):
        self.app.refresh_status(info)
        try:
            self.show_current(info, ok_prefix="Zastosowano")
        except tk.TclError:
            pass


class ConnectorWindow(ctk.CTkToplevel):
    """Safe connector picker. Discovery is metadata-only until explicitly registered."""
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.title("Konektory Jarvisa")
        self.geometry("760x560")
        self.configure(fg_color="#0d1420")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        ctk.CTkLabel(self, text="KONEKTORY", text_color="#77e6ff", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=18, pady=(18, 6), sticky="w")
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=1, column=0, padx=18, pady=6, sticky="ew")
        bar.grid_columnconfigure(0, weight=1)
        self.query = ctk.CTkEntry(bar, placeholder_text="Szukaj: YouTube, GitHub, OAuth...")
        self.query.grid(row=0, column=0, sticky="ew")
        self.query.bind("<KeyRelease>", lambda _: self.refresh())
        ctk.CTkButton(bar, text="ODŚWIEŻ", width=100, command=self.refresh).grid(row=0, column=1, padx=(8, 0))
        self.listbox = tk.Listbox(self, bg="#111c2b", fg="#d6e4ee", selectbackground="#27405c", relief="flat", height=18)
        self.listbox.grid(row=2, column=0, padx=18, pady=8, sticky="nsew")
        self.info = ctk.CTkLabel(self, text="", text_color="#90a8ba", anchor="w", justify="left", wraplength=700)
        self.info.grid(row=3, column=0, padx=18, pady=6, sticky="ew")
        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.grid(row=4, column=0, padx=18, pady=(4, 16), sticky="e")
        ctk.CTkButton(buttons, text="DODAJ WYBRANY", command=self.register_selected).grid(row=0, column=0, padx=5)
        ctk.CTkButton(buttons, text="STWÓRZ WŁASNY", fg_color="#1b2a3d", command=self.create_custom).grid(row=0, column=1, padx=5)
        self.items = []
        self.refresh()

    def refresh(self):
        self.items = catalog(self.query.get())
        self.listbox.delete(0, "end")
        for item in self.items:
            state = "zarejestrowany" if item["registered"] else "katalog"
            self.listbox.insert("end", f"{item['service']}  |  {item['kind']}  |  {state}")
        self.info.configure(text="Katalog nie przechowuje sekretów. Dodanie oznacza tylko przygotowanie konektora; dostęp wymaga osobnego OAuth/API i testu połączenia.")

    def register_selected(self):
        selection = self.listbox.curselection()
        if not selection:
            self.info.configure(text="Wybierz konektor.")
            return
        item = self.items[selection[0]]
        add_custom(item["service"], item["kind"], item["scopes"], item["endpoint"])
        self.refresh()
        self.info.configure(text=f"Dodano {item['service']}. Otwórz oficjalną stronę dokumentacji i skonfiguruj dostęp przez bezpieczny vault.")

    def create_custom(self):
        self.info.configure(text="Tworzenie własnego konektora: użyj w czacie Jarvisa skillu connector_manager z akcją create, podając oficjalny endpoint i zakresy. Sekrety dodaj wyłącznie przez vault.")


class JarvisGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Jarvis")
        self.geometry("1380x860")
        self.minsize(1050, 680)
        self.configure(fg_color="#212121")
        self.grid_columnconfigure(0, weight=0, minsize=245)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.busy = False
        self.state_text = tk.StringVar(value="GOTOWY")
        self.task_text = tk.StringVar(value="Brak aktywnego zadania")
        self.footer_text = tk.StringVar(value="")
        self.settings_window = None
        self.jarvis = JarvisCore(confirm=self.confirm_action, progress_callback=self.on_progress)
        self.build()
        self.refresh_status()
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
        # The worker thread may legitimately wait for the user.  300 ms made
        # every confirmation look like a silent denial while the task kept
        # running in the background.
        finished.wait()
        return answer[0]

    def build(self):
        bar = ctk.CTkFrame(self, fg_color="#0d1420", corner_radius=0)
        bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        bar.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(bar, text="Jarvis", font=ctk.CTkFont(size=22, weight="bold"), text_color="#f2f2f2").grid(row=0, column=0, padx=22, pady=15)
        ctk.CTkLabel(bar, textvariable=self.state_text, font=ctk.CTkFont(size=12, weight="bold"), text_color="#a8a8a8").grid(row=0, column=1, sticky="w")
        self.menu_button = ctk.CTkButton(bar, text="☰  Menu", width=110, fg_color="#3a3a3a", hover_color="#4a4a4a", command=self.open_menu)
        self.menu_button.grid(row=0, column=2, padx=(0, 10))
        ctk.CTkButton(bar, text="Zatrzymaj", width=110, fg_color="#7f3030", hover_color="#9b3b3b", command=self.stop).grid(row=0, column=3, padx=(0, 18))
        self.build_menu()

        face = ctk.CTkFrame(self, fg_color="#171717", corner_radius=0)
        face.grid(row=1, column=0, padx=(16, 8), pady=16, sticky="nsew")
        face.grid_rowconfigure(0, weight=1)
        face.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(face, text="＋  Nowa rozmowa", height=42, fg_color="#3b82f6", hover_color="#2563eb", command=self.clear_chat).grid(row=0, column=0, padx=16, pady=(20, 24), sticky="ew")
        ctk.CTkLabel(face, text="JARVIS", text_color="#f2f2f2", font=ctk.CTkFont(size=13, weight="bold"), anchor="w").grid(row=1, column=0, padx=18, pady=(0, 8), sticky="ew")
        ctk.CTkLabel(face, text="Twój lokalny asystent", text_color="#a3a3a3", anchor="w").grid(row=2, column=0, padx=18, sticky="ew")
        ctk.CTkLabel(face, text="\nNarzędzia\n• pliki i projekty\n• przeglądarka\n• konektory\n• pamięć i zadania", justify="left", anchor="nw", text_color="#b5b5b5").grid(row=3, column=0, padx=18, pady=22, sticky="new")
        ctk.CTkLabel(face, textvariable=self.task_text, wraplength=205, justify="left", anchor="sw", text_color="#8f8f8f").grid(row=4, column=0, padx=18, pady=18, sticky="sew")

        panel = ctk.CTkFrame(self, fg_color="#212121", corner_radius=0)
        panel.grid(row=1, column=1, padx=(8, 16), pady=16, sticky="nsew")
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(0, weight=3)
        panel.grid_rowconfigure(1, weight=1)
        self.chat = ctk.CTkTextbox(panel, state="disabled", font=ctk.CTkFont(size=14), fg_color="#212121", border_width=0, wrap="word")
        self.chat.grid(row=0, column=0, padx=14, pady=(14, 8), sticky="nsew")
        self.progress_view = ctk.CTkTextbox(panel, state="disabled", height=130, font=ctk.CTkFont(size=12), text_color="#a3a3a3", fg_color="#181818", border_width=0)
        self.progress_view.grid(row=1, column=0, padx=14, pady=8, sticky="nsew")
        bottom = ctk.CTkFrame(panel, fg_color="transparent")
        bottom.grid(row=2, column=0, padx=14, pady=(0, 14), sticky="ew")
        bottom.grid_columnconfigure(0, weight=1)
        self.input = ctk.CTkEntry(bottom, placeholder_text="Napisz wiadomość do Jarvisa…", height=46, fg_color="#303030", border_color="#4a4a4a")
        self.input.grid(row=0, column=0, sticky="ew")
        self.input.bind("<Return>", lambda _: self.send())
        self.send_button = ctk.CTkButton(bottom, text="Wyślij", width=100, height=44, fg_color="#3b82f6", hover_color="#2563eb", command=self.send)
        self.send_button.grid(row=0, column=1, padx=(10, 0))

        ctk.CTkLabel(self, textvariable=self.footer_text, text_color="#8f8f8f").grid(row=2, column=0, columnspan=2, padx=18, pady=8, sticky="w")

    def build_menu(self):
        style = {"tearoff": 0, "bg": "#0d1420", "fg": "#d6e4ee", "activebackground": "#27405c", "activeforeground": "#ffffff", "bd": 0}
        self.menu = tk.Menu(self, **style)
        self.mode_menu = tk.Menu(self.menu, **style)
        self.mode_var = tk.StringVar(value=getattr(self.jarvis, "mode", "asystent"))
        for mode in MODES:
            self.mode_menu.add_radiobutton(label=mode.capitalize(), value=mode, variable=self.mode_var, command=lambda m=mode: self.change_mode(m))
        self.menu.add_command(label="Ustawienia modelu...", command=self.open_settings)
        self.menu.add_command(label="Konektory...", command=self.open_connectors)
        self.menu.add_cascade(label="Tryb Jarvisa", menu=self.mode_menu)
        self.menu.add_separator()
        self.menu.add_command(label="Wyczyść okno rozmowy", command=self.clear_chat)
        self.menu.add_command(label="Zakończ", command=self.destroy)

    def open_menu(self):
        try:
            self.menu.tk_popup(self.menu_button.winfo_rootx(), self.menu_button.winfo_rooty() + self.menu_button.winfo_height())
        finally:
            self.menu.grab_release()

    def open_settings(self):
        if self.settings_window is not None and self.settings_window.winfo_exists():
            self.settings_window.lift()
            self.settings_window.focus_force()
            return
        self.settings_window = SettingsWindow(self)

    def open_connectors(self):
        ConnectorWindow(self)

    def change_mode(self, mode):
        self.write("SYSTEM", self.jarvis.set_mode(mode))

    def clear_chat(self):
        self.chat.configure(state="normal")
        self.chat.delete("1.0", "end")
        self.chat.configure(state="disabled")

    def refresh_status(self, info=None):
        try:
            info = info or self.jarvis.model_router.describe()
        except Exception:
            info = {"provider": "unavailable", "model": "", "warning": "Brak informacji o modelu."}
        if info.get("provider") == "unavailable":
            where = "BRAK MODELU: " + (info.get("warning") or "sprawdź ustawienia")
        else:
            where = f"MODEL: {info['provider']} • {info['model']}"
        self.footer_text.set(f"{where}  •  ZAPIS POSTĘPU LOKALNIE")

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
                self.write("SYSTEM", f"Mam zapisany plan zadania: {pending['goal']}. Możesz napisać „zatwierdzam plan”, aby wznowić.")
            handoff = task_runtime.latest_waiting_user()
            if handoff:
                self.task_text.set("Jarvis czeka na krok po Twojej stronie")
                self.state_text.set("CZEKA NA CIEBIE")
                self.write("SYSTEM", f"Zadanie czeka na Twój krok: {handoff['goal']}. Gdy skończysz, napisz „gotowe”.")
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

