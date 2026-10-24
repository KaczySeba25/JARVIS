"""Local secure credential intake window; secret never passes through chat."""
from __future__ import annotations
import sys
import tkinter as tk
from tkinter import messagebox
from secret_store import save

def main(service: str):
    root = tk.Tk(); root.title(f"Jarvis — bezpieczne dane: {service}"); root.geometry("520x330"); root.resizable(False, False)
    fields = {}
    for row, (label, key, secret) in enumerate((("Usługa", "service", False), ("Adres usługi/API", "url", False), ("Login lub e-mail", "username", False), ("Hasło / token / klucz API", "secret", True))):
        tk.Label(root, text=label, anchor="w").grid(row=row, column=0, padx=18, pady=8, sticky="w")
        entry = tk.Entry(root, width=55, show="•" if secret else "")
        entry.grid(row=row, column=1, padx=18, pady=8)
        if key == "service": entry.insert(0, service)
        fields[key] = entry
    def submit():
        try:
            service_value = fields["service"].get().strip()
            secret = fields["secret"].get()
            if not service_value or not secret: raise ValueError("Usługa i sekret są wymagane")
            result = save(service_value, secret, fields["username"].get().strip(), {"url": fields["url"].get().strip(), "source": "secure_local_form"})
            fields["secret"].delete(0, "end")
            messagebox.showinfo("Jarvis", f"Zapisano dane dla: {result['service']}\nSekret nie został pokazany ani zapisany jawnie.")
            root.destroy()
        except Exception as exc:
            messagebox.showerror("Jarvis", f"Nie zapisano danych: {type(exc).__name__}")
    tk.Button(root, text="ZAPISZ W ZASZYFROWANYM VAULT", command=submit).grid(row=5, column=0, columnspan=2, pady=18)
    root.protocol("WM_DELETE_WINDOW", root.destroy); root.mainloop()

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "service")
