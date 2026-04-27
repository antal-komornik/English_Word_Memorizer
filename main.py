import tkinter as tk
from tkinter import messagebox
import plotly.graph_objects as go
from dictionary_management import szotar_kezelese


class SzotanuloApp:
    def __init__(self, root):
        self.szotar = szotar_kezelese()
        self.helyes_valaszok = 0
        self.helytelen_valaszok = 0
        self.eletek = 3

        self.root = root
        self.root.title("Szótanuló App")
        self.root.geometry("400x350")

        self.root.title("Szótanuló App")
        self.root.geometry("600x400")
        self.root.configure(bg="#1e1e2f")  # sötét háttér

        # --- Középső keret ---
        self.frame = tk.Frame(root, bg="#2b2b3c", padx=30, pady=30)
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        # --- Életek ---
        self.elet_label = tk.Label(self.frame, text="", font=("Arial", 14), bg="#2b2b3c", fg="white")
        self.elet_label.pack(pady=5)

        # --- Kérdés ---
        self.kerdes_cimke = tk.Label(
            self.frame,
            text="",
            font=("Arial", 16, "bold"),
            bg="#2b2b3c",
            fg="white",
            wraplength=400
        )
        self.kerdes_cimke.pack(pady=15)

        # --- Input ---
        self.valasz_entry = tk.Entry(self.frame, font=("Arial", 12), justify="center")
        self.valasz_entry.pack(pady=10, ipadx=10, ipady=5)

        # --- Gombok ---
        self.ellenoriz_gomb = tk.Button(
            self.frame,
            text="Ellenőrzés",
            bg="#4CAF50",
            fg="white",
            width=20,
            command=self.ellenoriz
        )
        self.ellenoriz_gomb.pack(pady=5)

        self.kovetkezo_gomb = tk.Button(
            self.frame,
            text="Következő kérdés",
            bg="#2196F3",
            fg="white",
            width=20,
            state="disabled",
            command=self.kov_kerdes
        )
        self.kovetkezo_gomb.pack(pady=5)

        self.veglegesit_gomb = tk.Button(
            self.frame,
            text="Eredmény",
            bg="#9C27B0",
            fg="white",
            width=20,
            command=self.eredmeny
        )
        self.veglegesit_gomb.pack(pady=5)

        # --- Eredmény ---
        self.eredmeny_label = tk.Label(self.frame, text="", font=("Arial", 12), bg="#2b2b3c")
        self.eredmeny_label.pack(pady=10)

        # --- Pont ---
        self.pont_label = tk.Label(self.frame, text="", font=("Arial", 12), bg="#2b2b3c", fg="white")
        self.pont_label.pack()

        self.update_eletek()
        self.update_pont()
        self.kov_kerdes()

    # --- UI frissítések ---
    def update_eletek(self):
        hearts = "❤️" * self.eletek
        self.elet_label.config(text=f"Életek: {hearts}")

    def update_pont(self):
        self.pont_label.config(
            text=f"Helyes: {self.helyes_valaszok} | Hibás: {self.helytelen_valaszok}"
        )

    # --- Új kérdés ---
    def kov_kerdes(self):
        result = self.szotar.valasztas()
        if result:
            self.angol, self.magyar = result
            self.kerdes_cimke.config(text=f"Mi a(z) '{self.angol}' szó jelentése?")
            self.valasz_entry.delete(0, tk.END)
            self.eredmeny_label.config(text="")
            self.kovetkezo_gomb.config(state="disabled")
        else:
            self.kerdes_cimke.config(text="Nincsenek szavak az adatbázisban.")
            self.valasz_entry.config(state="disabled")
            self.ellenoriz_gomb.config(state="disabled")

    # --- Ellenőrzés ---
    def ellenoriz(self):
        user_answer = self.valasz_entry.get()

        jo = self.szotar.ellenoriz(user_answer, self.magyar)

        if jo:
            self.eredmeny_label.config(text="✅ Helyes!", fg="green")
            self.helyes_valaszok += 1
        else:
            self.eredmeny_label.config(
                text=f"❌ Helytelen! Helyes: {self.magyar}",
                fg="red"
            )

            self.helytelen_valaszok += 1
            self.eletek -= 1
            self.update_eletek()

            if self.eletek == 0:
                messagebox.showinfo("Game Over", "Elfogytak az életeid!")
                self.eredmeny()
                self.root.quit()

        self.update_pont()
        self.kovetkezo_gomb.config(state="normal")

    # --- Diagram ---
    def eredmeny(self):
        felirat = ['Helyes', 'Helytelen']
        ertekek = [self.helyes_valaszok, self.helytelen_valaszok]

        fig = go.Figure(data=[go.Pie(labels=felirat, values=ertekek, hole=0.3)])
        fig.update_traces(textinfo='percent+label', pull=[0.1, 0])
        fig.update_layout(title_text="Eredmények")

        fig.show()


if __name__ == "__main__":
    root = tk.Tk()
    app = SzotanuloApp(root)
    root.mainloop()