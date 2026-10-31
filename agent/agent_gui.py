"""Jarvis desktop cockpit with a visible, persistent task timeline."""
from __future__ import annotations

import threading
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog
from pathlib import Path
from PIL import Image

from jarvis_core import JarvisCore
import task_runtime
import user_settings
import local_provider
import ollama_manager
import local_speech
import voice_input
import skill_lifecycle
from skill_registry import discover
from research_engine import search as research_search
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

        label("Adres Ollama (lokalny)").grid(row=6, column=0, padx=22, pady=(16, 4), sticky="ew")
        self.ollama_url_entry = ctk.CTkEntry(self, placeholder_text="http://127.0.0.1:11434")
        self.ollama_url_entry.grid(row=7, column=0, padx=22, sticky="ew")
        if prefs["ollama_url"]:
            self.ollama_url_entry.insert(0, prefs["ollama_url"])

        self.hint = ctk.CTkLabel(self, text="", wraplength=500, justify="left", anchor="w", text_color="#90a8ba")
        self.hint.grid(row=8, column=0, padx=22, pady=(16, 4), sticky="ew")
        self.current = ctk.CTkLabel(self, text="", wraplength=500, justify="left", anchor="w", text_color="#71f6b5")
        self.current.grid(row=9, column=0, padx=22, pady=4, sticky="ew")
        ctk.CTkLabel(self, text="Klucze API i hasła ustawiasz tylko w pliku agent\\.env. Ta strona ich nie zapisuje.", wraplength=500, justify="left", anchor="w", text_color="#698394").grid(row=10, column=0, padx=22, pady=4, sticky="ew")

        ctk.CTkButton(self, text="ZARZĄDZAJ MODELAMI OLLAMA", fg_color="#1b2a3d", hover_color="#27405c", command=self.open_model_manager).grid(row=11, column=0, padx=22, pady=(10, 4), sticky="ew")

        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.grid(row=12, column=0, padx=22, pady=(14, 20), sticky="e")
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
            notes.append("Model lokalny działa tylko na tym komputerze. Możesz pobrać go w oknie ‘Zarządzaj modelami Ollama’.")
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
        user_settings.save(provider=self.selected_provider(), local_model=local, hosted_model=self.hosted_entry.get().strip(), ollama_url=self.ollama_url_entry.get().strip())
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

    def open_model_manager(self):
        ModelManagerWindow(self.app, self)


class ModelManagerWindow(ctk.CTkToplevel):
    """Install and remove local Ollama models without exposing secrets."""

    def __init__(self, app, settings_window=None):
        super().__init__(app)
        self.app = app
        self.settings_window = settings_window
        self.title("Modele AI — Ollama lokalnie")
        self.geometry("720x620")
        self.minsize(620, 520)
        self.configure(fg_color="#0d1420")
        self.transient(app)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.cancel_event = threading.Event()
        self.busy = False

        ctk.CTkLabel(self, text="MODELE AI", text_color="#77e6ff", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=20, pady=(18, 4), sticky="w")
        ctk.CTkLabel(self, text="Modele są pobierane lokalnie przez Ollama. Nie tworzę konta ani płatnej usługi.", text_color="#90a8ba", anchor="w", justify="left", wraplength=650).grid(row=1, column=0, padx=20, pady=(0, 12), sticky="ew")

        install = ctk.CTkFrame(self, fg_color="#111c2b")
        install.grid(row=2, column=0, padx=20, pady=4, sticky="ew")
        install.grid_columnconfigure(0, weight=1)
        self.model_box = ctk.CTkComboBox(install, values=[name for name, _ in ollama_manager.RECOMMENDED_MODELS])
        self.model_box.set("qwen3.5:4b")
        self.model_box.grid(row=0, column=0, padx=12, pady=12, sticky="ew")
        ctk.CTkButton(install, text="POBIERZ / ZAINSTALUJ", width=170, command=self.install).grid(row=0, column=1, padx=(0, 12), pady=12)

        self.listbox = tk.Listbox(self, bg="#111c2b", fg="#d6e4ee", selectbackground="#27405c", relief="flat", height=10)
        self.listbox.grid(row=3, column=0, padx=20, pady=(14, 8), sticky="nsew")
        self.listbox.bind("<<ListboxSelect>>", lambda _: self._selection_changed())

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=4, column=0, padx=20, pady=4, sticky="ew")
        ctk.CTkButton(actions, text="ODŚWIEŻ", width=110, command=self.refresh).pack(side="left")
        self.delete_button = ctk.CTkButton(actions, text="USUŃ WYBRANY", width=140, fg_color="#7f3030", hover_color="#9b3b3b", state="disabled", command=self.delete_selected)
        self.delete_button.pack(side="left", padx=8)
        ctk.CTkButton(actions, text="ZAMKNIJ", width=100, fg_color="#2a3445", command=self.destroy).pack(side="right")

        self.status = ctk.CTkLabel(self, text="Sprawdzam Ollama…", text_color="#90a8ba", anchor="w", justify="left", wraplength=650)
        self.status.grid(row=5, column=0, padx=20, pady=(8, 4), sticky="ew")
        self.log = ctk.CTkTextbox(self, height=110, state="disabled", fg_color="#111c2b", text_color="#a9bac8")
        self.log.grid(row=6, column=0, padx=20, pady=(4, 18), sticky="ew")
        self.refresh()

    def _append_log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", str(text) + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def refresh(self):
        def work():
            info = ollama_manager.status(user_settings.load().get("ollama_url") or None)
            found = [str(item.get("name")) for item in info.get("models", []) if item.get("name")]
            self.after(0, lambda: self._refreshed(info.get("available", False), found))
        threading.Thread(target=work, daemon=True).start()

    def _refreshed(self, available, found):
        try:
            self.listbox.delete(0, "end")
            for name in found:
                self.listbox.insert("end", name)
            self.status.configure(text=(f"Ollama działa. Zainstalowane modele: {len(found)}." if available else "Ollama nie odpowiada. Uruchom Ollama i spróbuj ponownie."), text_color="#71f6b5" if available else "#ffb454")
            self._selection_changed()
            if self.settings_window is not None and self.settings_window.winfo_exists():
                self.settings_window.refresh_models()
        except tk.TclError:
            pass

    def _selection_changed(self):
        try:
            self.delete_button.configure(state="normal" if self.listbox.curselection() and not self.busy else "disabled")
        except tk.TclError:
            pass

    def install(self):
        if self.busy:
            return
        name = self.model_box.get().strip()
        try:
            ollama_manager.validate_model(name)
        except ValueError as exc:
            self.status.configure(text=str(exc), text_color="#ffb454")
            return
        self.busy = True
        self.cancel_event.clear()
        self.status.configure(text=f"Pobieram model {name}… To może potrwać.", text_color="#90a8ba")
        self._append_log(f"START: ollama pull {name}")
        threading.Thread(target=self._pull_worker, args=(name,), daemon=True).start()

    def _pull_worker(self, name):
        result = ollama_manager.pull(name, on_line=lambda line: self.after(0, self._append_log, line), cancel_event=self.cancel_event, url=user_settings.load().get("ollama_url") or None)
        self.after(0, self._pull_done, name, result)

    def _pull_done(self, name, result):
        self.busy = False
        self._append_log(result.get("message", "Zakończono."))
        self.status.configure(text=(f"Model {name} jest gotowy do użycia." if result.get("ok") else result.get("message", "Instalacja nie powiodła się.")), text_color="#71f6b5" if result.get("ok") else "#ffb454")
        self.refresh()

    def delete_selected(self):
        selection = self.listbox.curselection()
        if not selection or self.busy:
            return
        name = self.listbox.get(selection[0])
        if not messagebox.askyesno("Usuń model", f"Usunąć lokalny model {name}?", parent=self):
            return
        self.busy = True
        self.status.configure(text=f"Usuwam {name}…", text_color="#90a8ba")
        def work():
            try:
                ollama_manager.delete(name, user_settings.load().get("ollama_url") or None)
                result = {"ok": True, "message": f"Usunięto model {name}."}
            except Exception as exc:
                result = {"ok": False, "message": f"Nie udało się usunąć modelu ({type(exc).__name__})."}
            self.after(0, lambda: self._delete_done(result))
        threading.Thread(target=work, daemon=True).start()

    def _delete_done(self, result):
        self.busy = False
        self.status.configure(text=result["message"], text_color="#71f6b5" if result.get("ok") else "#ffb454")
        self.refresh()


class PersonalizationWindow(ctk.CTkToplevel):
    """User-facing preferences stored locally and applied without secrets."""

    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.title("Personalizacja JARVISA")
        self.geometry("620x620")
        self.configure(fg_color="#0d1420")
        self.transient(app)
        self.grid_columnconfigure(0, weight=1)
        prefs = user_settings.load()
        ctk.CTkLabel(self, text="PERSONALIZACJA", text_color="#77e6ff", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=22, pady=(20, 4), sticky="w")
        ctk.CTkLabel(self, text="Ustawienia są lokalne. Nie zawierają haseł, tokenów ani kluczy API.", text_color="#90a8ba", anchor="w", wraplength=560).grid(row=1, column=0, padx=22, pady=(0, 16), sticky="ew")
        form = ctk.CTkFrame(self, fg_color="#111c2b")
        form.grid(row=2, column=0, padx=22, pady=4, sticky="ew")
        form.grid_columnconfigure(1, weight=1)

        self.name = ctk.CTkEntry(form, placeholder_text="Imię")
        self.name.insert(0, prefs["user_name"])
        self._row(form, 0, "Jak ma mówić do Ciebie", self.name)
        self.language = self._menu(form, prefs["language"], {"pl": "Polski", "en": "English"})
        self._row(form, 1, "Język odpowiedzi", self.language)
        self.appearance = self._menu(form, prefs["appearance"], {"dark": "Ciemny", "light": "Jasny", "system": "Systemowy"})
        self._row(form, 2, "Wygląd", self.appearance)
        self.accent = self._menu(form, prefs["accent_color"], {"blue": "Niebieski", "cyan": "Cyjan", "purple": "Fioletowy", "green": "Zielony"})
        self._row(form, 3, "Kolor akcentu", self.accent)
        self.font_scale = self._menu(form, prefs["font_scale"], {"small": "Mały", "normal": "Normalny", "large": "Duży"})
        self._row(form, 4, "Rozmiar tekstu", self.font_scale)
        self.voice_input = self._menu(form, prefs["voice_input"], {"off": "Wyłączone", "on": "Włączone"})
        self._row(form, 5, "Rozpoznawanie mowy", self.voice_input)
        self.voice_output = self._menu(form, prefs["voice_output"], {"off": "Wyłączone", "on": "Włączone"})
        self._row(form, 6, "Głos JARVISA", self.voice_output)
        self.notifications = self._menu(form, prefs["notifications"], {"on": "Włączone", "off": "Wyłączone"})
        self._row(form, 7, "Powiadomienia lokalne", self.notifications)
        self.compact = self._menu(form, prefs["compact_mode"], {"off": "Standardowy", "on": "Kompaktowy"})
        self._row(form, 8, "Układ interfejsu", self.compact)

        self.status = ctk.CTkLabel(self, text="Zmiany zostaną zapisane lokalnie.", text_color="#90a8ba", anchor="w", wraplength=560)
        self.status.grid(row=3, column=0, padx=22, pady=14, sticky="ew")
        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.grid(row=4, column=0, padx=22, pady=(0, 20), sticky="e")
        ctk.CTkButton(buttons, text="ZAPISZ", width=120, command=self.save).pack(side="left", padx=5)
        ctk.CTkButton(buttons, text="ZAMKNIJ", width=100, fg_color="#2a3445", command=self.destroy).pack(side="left", padx=5)

    @staticmethod
    def _menu(parent, value, values):
        widget = ctk.CTkOptionMenu(parent, values=list(values.values()))
        widget._jarvis_values = values
        widget.set(values.get(value, next(iter(values.values()))))
        return widget

    @staticmethod
    def _row(parent, index, label, widget):
        ctk.CTkLabel(parent, text=label, text_color="#d6e4ee", anchor="w").grid(row=index, column=0, padx=14, pady=8, sticky="w")
        widget.grid(row=index, column=1, padx=14, pady=8, sticky="ew")

    @staticmethod
    def _value(widget):
        return next((key for key, label in widget._jarvis_values.items() if label == widget.get()), "")

    def save(self):
        user_settings.save(
            user_name=self.name.get().strip(), language=self._value(self.language),
            appearance=self._value(self.appearance), accent_color=self._value(self.accent),
            font_scale=self._value(self.font_scale), voice_input=self._value(self.voice_input),
            voice_output=self._value(self.voice_output), notifications=self._value(self.notifications),
            compact_mode=self._value(self.compact),
        )
        self.app.apply_personalization()
        self.status.configure(text="Zapisano. Nowe ustawienia wyglądu są aktywne.", text_color="#71f6b5")


class SkillsWindow(ctk.CTkToplevel):
    """Review and install a single skill through the existing validation lifecycle."""

    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.title("Umiejętności i wtyczki JARVISA")
        self.geometry("820x620")
        self.configure(fg_color="#0d1420")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        ctk.CTkLabel(self, text="UMIEJĘTNOŚCI I WTYCZKI", text_color="#77e6ff", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=20, pady=(18, 4), sticky="w")
        ctk.CTkLabel(self, text="JARVIS instaluje pojedyncze rozszerzenia dopiero po analizie składni i bezpiecznej kontroli kodu. Nie uruchamiaj nieznanych plików bez sprawdzenia źródła.", text_color="#90a8ba", anchor="w", justify="left", wraplength=760).grid(row=1, column=0, padx=20, pady=(0, 12), sticky="ew")
        self.listbox = tk.Listbox(self, bg="#111c2b", fg="#d6e4ee", selectbackground="#27405c", relief="flat")
        self.listbox.grid(row=2, column=0, padx=20, pady=8, sticky="nsew")
        self.info = ctk.CTkLabel(self, text="", text_color="#90a8ba", anchor="w", justify="left", wraplength=760)
        self.info.grid(row=3, column=0, padx=20, pady=6, sticky="ew")
        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.grid(row=4, column=0, padx=20, pady=(4, 18), sticky="e")
        ctk.CTkButton(buttons, text="ODŚWIEŻ", width=100, command=self.refresh).pack(side="left", padx=4)
        ctk.CTkButton(buttons, text="ZAINSTALUJ Z PLIKU", width=160, command=self.install_from_file).pack(side="left", padx=4)
        ctk.CTkButton(buttons, text="ZAMKNIJ", width=100, fg_color="#2a3445", command=self.destroy).pack(side="left", padx=4)
        self.refresh()

    def refresh(self):
        self.listbox.delete(0, "end")
        items = discover(Path(__file__).resolve().parent.parent / "skills")
        for item in items:
            state = "gotowe" if item.has_run and item.has_module_doc else "wymaga przeglądu"
            self.listbox.insert("end", f"{item.name} | ryzyko: {item.risk} | {state}")
        self.info.configure(text=f"Znaleziono {len(items)} umiejętności. Instalacja z pliku trafia najpierw do wersji roboczej i przechodzi walidację.")

    def install_from_file(self):
        path = filedialog.askopenfilename(parent=self, title="Wybierz plik umiejętności Python", filetypes=[("Python", "*.py"), ("Wszystkie pliki", "*.*")])
        if not path:
            return
        try:
            source = Path(path)
            code = source.read_text(encoding="utf-8")
            draft = skill_lifecycle.create_draft(source.stem, code)
            report = skill_lifecycle.validate(source.stem)
            if not (report.get("syntax") and report.get("execution")):
                self.info.configure(text="Odrzucono rozszerzenie. Walidacja: " + "; ".join(report.get("errors", [])[:3]), text_color="#ffb454")
                return
            if messagebox.askyesno("Aktywować umiejętność?", f"Walidacja przeszła. Aktywować {source.stem} jako nową umiejętność wysokiego ryzyka?", parent=self):
                result = skill_lifecycle.promote(source.stem, confirm=True, metadata={"source": "user_file", "path": str(source)})
                self.info.configure(text=result, text_color="#71f6b5")
                self.refresh()
            else:
                self.info.configure(text=f"Zweryfikowany draft pozostawiono lokalnie: {draft}")
        except Exception as exc:
            self.info.configure(text=f"Nie udało się zainstalować umiejętności ({type(exc).__name__}).", text_color="#ffb454")


class APIDiscoveryWindow(ctk.CTkToplevel):
    """Read-only public API discovery with optional metadata-only connector preparation."""

    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.title("Znajdź darmowe i publiczne API")
        self.geometry("900x680")
        self.configure(fg_color="#0d1420")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        ctk.CTkLabel(self, text="RESEARCH PUBLICZNYCH API", text_color="#77e6ff", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=20, pady=(18, 4), sticky="w")
        ctk.CTkLabel(self, text="Wyniki są tylko materiałem do oceny. JARVIS nie podłącza losowego API, nie wysyła sekretów i nie tworzy kont bez Twojej decyzji.", text_color="#90a8ba", anchor="w", wraplength=850).grid(row=1, column=0, padx=20, pady=(0, 12), sticky="ew")
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=2, column=0, padx=20, pady=4, sticky="new")
        bar.grid_columnconfigure(0, weight=1)
        self.query = ctk.CTkEntry(bar, placeholder_text="np. pogoda, produkty, kursy walut, generowanie obrazów")
        self.query.grid(row=0, column=0, sticky="ew")
        self.search_button = ctk.CTkButton(bar, text="SZUKAJ", width=110, command=self.search)
        self.search_button.grid(row=0, column=1, padx=(8, 0))
        self.results = tk.Listbox(self, bg="#111c2b", fg="#d6e4ee", selectbackground="#27405c", relief="flat")
        self.results.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        self.info = ctk.CTkLabel(self, text="Wpisz temat i rozpocznij research.", text_color="#90a8ba", anchor="w", justify="left", wraplength=850)
        self.info.grid(row=4, column=0, padx=20, pady=6, sticky="ew")
        ctk.CTkButton(self, text="PRZYGOTUJ KONEKTOR (TYLKO METADANE)", fg_color="#1b2a3d", command=self.prepare_connector).grid(row=5, column=0, padx=20, pady=(4, 18), sticky="e")
        self.items = []

    def search(self):
        query = self.query.get().strip()
        if not query:
            self.info.configure(text="Podaj temat researchu.")
            return
        self.search_button.configure(state="disabled")
        self.info.configure(text="Szukam oficjalnych i publicznych źródeł…")
        threading.Thread(target=self._search_worker, args=(query,), daemon=True).start()

    def _search_worker(self, query):
        try:
            items = research_search(query + " free public API official documentation", 8)
            self.after(0, self._show_results, items)
        except Exception as exc:
            self.after(0, lambda: self.info.configure(text=f"Research nie powiódł się ({type(exc).__name__}).", text_color="#ffb454"))
            self.after(0, lambda: self.search_button.configure(state="normal"))

    def _show_results(self, items):
        self.items = items or []
        self.results.delete(0, "end")
        for item in self.items:
            self.results.insert("end", f"{item.get('title', 'Źródło')} | {item.get('url', '')}")
        self.info.configure(text=f"Znaleziono {len(self.items)} źródeł. Wybierz wynik, aby obejrzeć opis.", text_color="#71f6b5" if self.items else "#ffb454")
        self.search_button.configure(state="normal")

    def prepare_connector(self):
        selection = self.results.curselection()
        if not selection:
            self.info.configure(text="Najpierw wybierz wynik.")
            return
        item = self.items[selection[0]]
        from connector_registry import add_custom
        service = "api_" + "".join(ch if ch.isalnum() else "_" for ch in item.get("title", "public").lower())[:48].strip("_")
        add_custom(service, "api", ["public-documentation-review"], item.get("url", ""))
        self.info.configure(text=f"Przygotowano metadane konektora {service}. Nie jest połączony i nie ma dostępu do sekretów.", text_color="#71f6b5")


class TaskCenterWindow(ctk.CTkToplevel):
    """Inspect durable local task records without changing their state."""

    def __init__(self, app):
        super().__init__(app)
        self.title("Centrum zadań JARVISA")
        self.geometry("860x620")
        self.configure(fg_color="#0d1420")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(self, text="CENTRUM ZADAŃ", text_color="#77e6ff", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=20, pady=(18, 8), sticky="w")
        self.listbox = tk.Listbox(self, bg="#111c2b", fg="#d6e4ee", selectbackground="#27405c", relief="flat")
        self.listbox.grid(row=1, column=0, padx=20, pady=8, sticky="nsew")
        self.info = ctk.CTkLabel(self, text="", text_color="#90a8ba", anchor="w", justify="left", wraplength=800)
        self.info.grid(row=2, column=0, padx=20, pady=6, sticky="ew")
        ctk.CTkButton(self, text="ODŚWIEŻ", width=110, command=self.refresh).grid(row=3, column=0, padx=20, pady=(4, 18), sticky="e")
        self.refresh()

    def refresh(self):
        self.listbox.delete(0, "end")
        events = task_runtime.recent(100)
        latest = {}
        for event in events:
            latest[event["task_id"]] = event
        for task_id, event in latest.items():
            self.listbox.insert("end", f"{event['stage'].upper():18} | {task_id[:10]} | {event['message']}")
        pending = task_runtime.latest_pending()
        waiting = task_runtime.latest_waiting_user()
        flags = []
        if pending:
            flags.append("oczekuje plan do akceptacji")
        if waiting:
            flags.append("oczekuje na krok użytkownika")
        self.info.configure(text=f"Pokazano {len(latest)} ostatnich zadań. " + ("; ".join(flags) + "." if flags else "Brak oczekujących blokad."))


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
        self.title("JARVIS — Cyfrowy asystent")
        self.geometry("1480x940")
        self.minsize(1120, 760)
        self.configure(fg_color="#070b14")
        self.grid_columnconfigure(0, weight=0, minsize=252)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.busy = False
        self.speaking = False
        self.listening = False
        self.avatar_phase = 0
        self.state_text = tk.StringVar(value="GOTOWY")
        self.task_text = tk.StringVar(value="Brak aktywnego zadania")
        self.footer_text = tk.StringVar(value="")
        self.settings_window = None
        self.jarvis = JarvisCore(confirm=self.confirm_action, progress_callback=self.on_progress)
        self.build()
        self.apply_personalization()
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
        self.build_menu()
        sidebar = ctk.CTkFrame(self, fg_color="#0b1220", corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(8, weight=1)
        ctk.CTkLabel(sidebar, text="JARVIS", text_color="#e9fbff", font=ctk.CTkFont(size=25, weight="bold")).grid(row=0, column=0, padx=24, pady=(28, 0), sticky="w")
        ctk.CTkLabel(sidebar, text="LOKALNY KOKPIT AI", text_color="#4edcf8", font=ctk.CTkFont(size=10, weight="bold")).grid(row=1, column=0, padx=25, pady=(0, 24), sticky="w")
        ctk.CTkButton(sidebar, text="＋  Nowa rozmowa", height=44, fg_color="#176bdb", hover_color="#2588ff", command=self.clear_chat).grid(row=2, column=0, padx=16, pady=(0, 20), sticky="ew")
        ctk.CTkLabel(sidebar, text="NAWIGACJA", text_color="#5d7892", font=ctk.CTkFont(size=10, weight="bold"), anchor="w").grid(row=3, column=0, padx=22, pady=(0, 8), sticky="ew")
        self._nav_button(sidebar, 4, "⌂  Rozmowa", self.focus_chat)
        self._nav_button(sidebar, 5, "◈  Centrum zadań", self.open_task_center)
        self._nav_button(sidebar, 6, "◉  Konektory", self.open_connectors)
        self._nav_button(sidebar, 7, "✦  Umiejętności", self.open_skills)
        self._nav_button(sidebar, 8, "⌁  Research API", self.open_api_discovery)
        self._nav_button(sidebar, 9, "⚙  Ustawienia", self.open_settings)
        account = ctk.CTkFrame(sidebar, fg_color="#111d30", corner_radius=12)
        account.grid(row=10, column=0, padx=16, pady=(16, 22), sticky="ew")
        ctk.CTkLabel(account, text="●  SYSTEM DZIAŁA", text_color="#55e6b0", font=ctk.CTkFont(size=10, weight="bold")).pack(anchor="w", padx=14, pady=(12, 2))
        ctk.CTkLabel(account, text="Tryb: lokalny / nadzorowany", text_color="#8da4b7", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=14, pady=(0, 12))
        self.menu_button = ctk.CTkButton(sidebar, text="☰  Więcej opcji", height=36, fg_color="transparent", border_width=1, border_color="#263d56", hover_color="#14263b", command=self.open_menu)
        self.menu_button.grid(row=11, column=0, padx=16, pady=(0, 18), sticky="ew")

        main = ctk.CTkFrame(self, fg_color="#070b14", corner_radius=0)
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=4)
        main.grid_rowconfigure(2, weight=2)
        top = ctk.CTkFrame(main, fg_color="transparent", height=68)
        top.grid(row=0, column=0, padx=30, pady=(18, 0), sticky="ew")
        top.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(top, text="Panel główny", text_color="#eef9ff", font=ctk.CTkFont(size=24, weight="bold"), anchor="w").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(top, text="Twój cyfrowy partner do pracy, researchu i wykonywania zadań", text_color="#7994a9", anchor="w").grid(row=1, column=0, sticky="w")
        self.status_chip = ctk.CTkLabel(top, textvariable=self.state_text, text_color="#65e8ff", fg_color="#102b3d", corner_radius=14, padx=14, pady=7, font=ctk.CTkFont(size=11, weight="bold"))
        self.status_chip.grid(row=0, column=1, rowspan=2, padx=(12, 0), sticky="e")

        avatar_card = ctk.CTkFrame(main, fg_color="#0c1625", corner_radius=24, border_width=1, border_color="#173954")
        avatar_card.grid(row=1, column=0, padx=30, pady=(10, 14), sticky="nsew")
        avatar_card.grid_columnconfigure(0, weight=1)
        avatar_card.grid_rowconfigure(0, weight=1)
        stage = ctk.CTkFrame(avatar_card, fg_color="#08111e", corner_radius=20)
        stage.grid(row=0, column=0, padx=18, pady=18, sticky="nsew")
        stage.grid_columnconfigure(0, weight=1)
        stage.grid_rowconfigure(0, weight=1)
        asset = Path(__file__).resolve().parent.parent / "assets" / "jarvis_hologram_reference.webp"
        try:
            image = Image.open(asset).convert("RGBA")
            width, height = image.size
            image = image.crop((int(width * 0.25), int(height * 0.01), width, int(height * 0.99)))
            self.avatar_image = ctk.CTkImage(light_image=image, dark_image=image, size=(380, 280))
            self.avatar_label = ctk.CTkLabel(stage, text="", image=self.avatar_image)
        except Exception:
            self.avatar_label = ctk.CTkLabel(stage, text="JARVIS", text_color="#5de9ff", font=ctk.CTkFont(size=46, weight="bold"))
        self.avatar_label.grid(row=0, column=0, padx=20, pady=12)
        self.mouth_label = ctk.CTkLabel(stage, text="◡", text_color="#c4fbff", fg_color="#102a3f", corner_radius=14, width=52, height=28, font=ctk.CTkFont(size=20, weight="bold"))
        self.mouth_label.place(relx=0.51, rely=0.77, anchor="center")
        self.avatar_state = ctk.CTkLabel(avatar_card, text="JARVIS  •  GOTOWY", text_color="#68e9ff", font=ctk.CTkFont(size=12, weight="bold"))
        self.avatar_state.grid(row=1, column=0, pady=(0, 4))
        ctk.CTkLabel(avatar_card, textvariable=self.task_text, text_color="#7f9aae", anchor="center", wraplength=900).grid(row=2, column=0, padx=20, pady=(0, 14), sticky="ew")

        chat_card = ctk.CTkFrame(main, fg_color="#0c1625", corner_radius=20, border_width=1, border_color="#173954")
        chat_card.grid(row=2, column=0, padx=30, pady=(0, 12), sticky="nsew")
        chat_card.grid_columnconfigure(0, weight=1)
        chat_card.grid_rowconfigure(0, weight=1)
        self.chat = ctk.CTkTextbox(chat_card, state="disabled", font=ctk.CTkFont(size=14), fg_color="#0c1625", border_width=0, wrap="word", text_color="#d8edf5")
        self.chat.grid(row=0, column=0, padx=22, pady=(14, 8), sticky="nsew")
        self.progress_view = ctk.CTkTextbox(chat_card, state="disabled", height=64, font=ctk.CTkFont(size=11), text_color="#7190a5", fg_color="#08111e", border_width=0)
        self.progress_view.grid(row=1, column=0, padx=22, pady=(0, 8), sticky="ew")
        bottom = ctk.CTkFrame(main, fg_color="transparent")
        bottom.grid(row=3, column=0, padx=30, pady=(0, 6), sticky="ew")
        bottom.grid_columnconfigure(0, weight=1)
        self.input = ctk.CTkEntry(bottom, placeholder_text="Napisz, co mam zrobić…", height=52, fg_color="#101f32", border_color="#26516f", corner_radius=16)
        self.input.grid(row=0, column=0, sticky="ew")
        self.input.bind("<Return>", lambda _: self.send())
        self.mic_button = ctk.CTkButton(bottom, text="MIKROFON", width=120, height=50, corner_radius=15, fg_color="#102a3f", hover_color="#194865", command=self.toggle_microphone)
        self.mic_button.grid(row=0, column=1, padx=(10, 0))
        self.send_button = ctk.CTkButton(bottom, text="WYŚLIJ  ➤", width=126, height=50, corner_radius=15, fg_color="#176bdb", hover_color="#2588ff", command=self.send)
        self.send_button.grid(row=0, column=2, padx=(10, 0))
        ctk.CTkLabel(main, textvariable=self.footer_text, text_color="#5d7892", font=ctk.CTkFont(size=10), anchor="w").grid(row=4, column=0, padx=30, pady=(0, 12), sticky="w")

    def _nav_button(self, parent, row, text, command):
        ctk.CTkButton(parent, text=text, height=38, anchor="w", fg_color="transparent", hover_color="#14263b", text_color="#b7cfdd", command=command).grid(row=row, column=0, padx=12, pady=2, sticky="ew")

    def focus_chat(self):
        self.input.focus_set()

    def toggle_microphone(self):
        if self.busy or self.listening:
            return
        if not voice_input.available():
            self.write("SYSTEM", "Mikrofon nie jest dostępny. Zainstaluj lokalne biblioteki audio w środowisku JARVISA.")
            return
        self.listening = True
        self.mic_button.configure(text="SŁUCHAM…", state="disabled", fg_color="#a34d35")
        self.state_text.set("SŁUCHAM")
        self.set_avatar_state("SŁUCHAM", "słucham")
        self.task_text.set("Mów do mikrofonu po sygnale…")
        threading.Thread(target=self._listen_worker, daemon=True).start()

    def _listen_worker(self):
        result = voice_input.listen(language="pl-PL")
        self.after(0, self._voice_result, result)

    def _voice_result(self, result):
        self.listening = False
        self.mic_button.configure(text="MIKROFON", state="normal", fg_color="#102a3f")
        if result.get("ok"):
            self.input.delete(0, "end")
            self.input.insert(0, result["text"])
            self.write("TY (GŁOS)", result["text"])
            self.input.delete(0, "end")
            self.busy = True
            self.send_button.configure(state="disabled")
            self.state_text.set("PRACUJE")
            self.set_avatar_state("MYŚLĘ", "myślę")
            self.task_text.set(result["text"][:180])
            threading.Thread(target=self.process, args=(result["text"],), daemon=True).start()
        else:
            self.state_text.set("GOTOWY")
            self.set_avatar_state("GOTOWY", "gotowy")
            self.write("SYSTEM", result.get("message", "Nie udało się rozpoznać mowy."))

    def build_menu(self):
        style = {"tearoff": 0, "bg": "#0d1420", "fg": "#d6e4ee", "activebackground": "#27405c", "activeforeground": "#ffffff", "bd": 0}
        self.menu = tk.Menu(self, **style)
        self.mode_menu = tk.Menu(self.menu, **style)
        self.mode_var = tk.StringVar(value=getattr(self.jarvis, "mode", "asystent"))
        for mode in MODES:
            self.mode_menu.add_radiobutton(label=mode.capitalize(), value=mode, variable=self.mode_var, command=lambda m=mode: self.change_mode(m))
        self.menu.add_command(label="Ustawienia modelu...", command=self.open_settings)
        self.menu.add_command(label="Konektory...", command=self.open_connectors)
        self.menu.add_command(label="Umiejętności i wtyczki...", command=self.open_skills)
        self.menu.add_command(label="Znajdź darmowe API...", command=self.open_api_discovery)
        self.menu.add_command(label="Personalizacja...", command=self.open_personalization)
        self.menu.add_command(label="Centrum zadań...", command=self.open_task_center)
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

    def open_skills(self):
        SkillsWindow(self)

    def open_api_discovery(self):
        APIDiscoveryWindow(self)

    def open_personalization(self):
        PersonalizationWindow(self)

    def open_task_center(self):
        TaskCenterWindow(self)

    def apply_personalization(self):
        prefs = user_settings.load()
        accents = {"blue": "#3b82f6", "cyan": "#06b6d4", "purple": "#8b5cf6", "green": "#10b981"}
        accent = accents.get(prefs["accent_color"], accents["blue"])
        dark = prefs["appearance"] != "light"
        base = "#212121" if dark else "#f2f5f8"
        panel = "#171717" if dark else "#ffffff"
        try:
            self.configure(fg_color=base)
            self.chat.configure(fg_color=base, text_color="#f2f2f2" if dark else "#1f2937")
            self.progress_view.configure(fg_color=panel)
            self.send_button.configure(fg_color=accent, hover_color=accent)
            self.menu_button.configure(fg_color="#3a3a3a" if dark else "#dbe4ee")
            self.footer_text.set(self.footer_text.get() + f"  •  AKCENT: {prefs['accent_color'].upper()}")
        except (AttributeError, tk.TclError):
            pass

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
        normalized = message.lower().replace("ł", "l").strip()
        if normalized in {"wlacz mikrofon", "uruchom mikrofon", "włącz mikrofon", "zacznij sluchac", "zacznij słuchać"}:
            self.write("JARVIS", "Włączam mikrofon. Mów po polsku po zmianie statusu na SŁUCHAM.")
            self.toggle_microphone()
            return
        self.busy = True
        self.send_button.configure(state="disabled")
        self.state_text.set("PRACUJE")
        self.set_avatar_state("MYŚLĘ", "myślę")
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
        prefs = user_settings.load()
        if prefs.get("voice_output") == "on" and local_speech.available():
            self.set_avatar_state("MÓWIĘ", "mówię")
            self.speaking = True
            threading.Thread(target=self._speak_answer, args=(answer,), daemon=True).start()
        else:
            self.set_avatar_state("GOTOWY", "gotowy")
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

    def _speak_answer(self, answer):
        try:
            local_speech.speak(str(answer)[:5000])
        finally:
            self.after(0, self._speech_finished)

    def _speech_finished(self):
        self.speaking = False
        if not self.busy:
            self.set_avatar_state("GOTOWY", "gotowy")

    def set_avatar_state(self, label, mode):
        try:
            self.avatar_state.configure(text=f"JARVIS  •  {label}", text_color="#65e8ff" if mode != "gotowy" else "#68e9ff")
        except (AttributeError, tk.TclError):
            pass

    def stop(self):
        self.jarvis.run_skill("emergency_stop", "stop")
        self.state_text.set("ZATRZYMANY")
        self.write("SYSTEM", "Aktywowano awaryjne zatrzymanie. Bieżący krok zewnętrzny może już być w toku.")

    def pulse(self):
        self.avatar_phase = (self.avatar_phase + 1) % 4
        active_avatar = getattr(self, "speaking", False) or getattr(self, "listening", False)
        if active_avatar:
            try:
                self.avatar_label.grid_configure(pady=(10 + (self.avatar_phase % 2) * 3, 10))
            except (AttributeError, tk.TclError):
                pass
        if getattr(self, "speaking", False):
            mouths = ("—", "◡", "○", "◠")
            try:
                self.mouth_label.configure(text=mouths[self.avatar_phase], text_color="#c4fbff")
            except (AttributeError, tk.TclError):
                pass
        elif getattr(self, "mouth_label", None) is not None:
            try:
                self.mouth_label.configure(text="◡", text_color="#8af3ff")
            except (AttributeError, tk.TclError):
                pass
        self.after(420, self.pulse)


if __name__ == "__main__":
    JarvisGUI().mainloop()

