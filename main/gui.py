import os
import tkinter as tk
from tkinter import messagebox, filedialog
import json
from functions import init_db, login_or_create, create_session, vote, get_votes

conn, cur = init_db()
players_in_session = [] # Liste des IDs des joueurs qui vont participer
backlog = []
current_task_idx = 0
session_id = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class PlanningPokerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Planning Poker M1")
        self.root.geometry("800x700")
        self.main_frame = tk.Frame(self.root, padx=20, pady=20)
        self.main_frame.pack(expand=True, fill="both")
        self.login_screen()

    def clear(self):
        for w in self.main_frame.winfo_children(): w.destroy()

# --- Étape 1 : Connexion des joueurs ---
    def login_screen(self):
        self.clear()
        
        # Titre avec un peu plus d'espace
        tk.Label(self.main_frame, text="👥 Gestion des Participants", 
                 font=("Helvetica", 20, "bold"), fg="#2c3e50").pack(pady=20)
        
        # Frame pour le formulaire
        form_frame = tk.LabelFrame(self.main_frame, text=" Nouveau Joueur ", padx=15, pady=15)
        form_frame.pack(fill="x", padx=20)

        tk.Label(form_frame, text="Pseudo :", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        ent_name = tk.Entry(form_frame, font=("Arial", 11))
        ent_name.grid(row=0, column=1, sticky="ew", padx=10)

        tk.Label(form_frame, text="Rôle :", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        ent_role = tk.Entry(form_frame, font=("Arial", 11))
        ent_role.insert(0, "user") # Valeur par défaut pour gagner du temps
        ent_role.grid(row=1, column=1, sticky="ew", padx=10)
        
        form_frame.columnconfigure(1, weight=1)

        def add_player():
            name = ent_name.get().strip()
            role = ent_role.get().strip().lower()
            
            if not name or not role:
                messagebox.showwarning("Champs vides", "Veuillez remplir toutes les informations.")
                return

            uid, role_final = login_or_create(cur, conn, name, role)
            players_in_session.append({"id": uid, "name": name, "role": role_final})
            
            # Affichage élégant : Nom à gauche, Rôle à droite
            # On utilise des espaces pour aligner proprement
            display_text = f"  {name.ljust(25)} |   {role_final.upper()}"
            self.listbox_players.insert(tk.END, display_text)
            
            # Couleurs alternées pour la lisibilité
            if role_final == "scrum_master":
                self.listbox_players.itemconfig(tk.END, fg="#e67e22") # Orange pour le SM
            else:
                self.listbox_players.itemconfig(tk.END, fg="#34495e") # Bleu nuit pour les users

            ent_name.delete(0, tk.END)
            ent_name.focus()

        tk.Button(form_frame, text="Ajouter au groupe", command=add_player, 
                  bg="#3498db", fg="white", font=("Arial", 10, "bold"), cursor="hand2").grid(row=2, column=0, columnspan=2, pady=15)

        # Zone de liste
        tk.Label(self.main_frame, text="Joueurs inscrits :", font=("Arial", 11, "bold")).pack(pady=(20, 5), anchor="w", padx=20)
        
        self.listbox_players = tk.Listbox(self.main_frame, width=60, height=10, 
                                          font=("Consolas", 11), borderwidth=0, 
                                          highlightthickness=1, highlightbackground="#bdc3c7")
        self.listbox_players.pack(padx=20, pady=5)

        # Bouton de validation final
        tk.Button(self.main_frame, text="Lancer la configuration de session →", 
                  command=self.session_creation_screen, bg="#27ae60", fg="white", 
                  font=("Arial", 11, "bold"), padx=20, pady=10, cursor="hand2").pack(pady=30)

    # --- Étape 2 : Création de session & JSON ---
    def session_creation_screen(self):
        self.clear()
        sm = next((p for p in players_in_session if p['role'] == 'scrum_master'), None)
        if not sm:
            messagebox.showerror("Erreur", "Il faut au moins un scrum_master !")
            return self.login_screen()

        tk.Label(self.main_frame, text="Configuration de la session", font=("Arial", 16)).pack(pady=10)
        
        tk.Label(self.main_frame, text="Nom de la session :").pack()
        ent_sname = tk.Entry(self.main_frame)
        ent_sname.pack()

        def load_json():
            global backlog
            path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
            if path:
                with open(path, 'r') as f:
                    backlog = json.load(f).get("issues", [])
                messagebox.showinfo("JSON", f"{len(backlog)} tâches chargées.")

        tk.Button(self.main_frame, text="Charger Backlog JSON", command=load_json).pack(pady=10)

        def start():
            global session_id
            session_id = create_session(cur, conn, ent_sname.get(), "Strict", sm['id'])
            self.turn_by_turn_vote(0, 0) # Premier joueur, première tâche

        tk.Button(self.main_frame, text="Lancer la session", command=start, bg="#2196F3", fg="white").pack(pady=10)

    # --- Étape 3 : Vote tour par tour ---
    def turn_by_turn_vote(self, p_idx, t_idx):
        self.clear()
        if t_idx >= len(backlog):
            messagebox.showinfo("Fin", "Toutes les tâches ont été votées !")
            return self.login_screen()

        current_player = players_in_session[p_idx]
        current_task = backlog[t_idx]

        tk.Label(self.main_frame, text=f"Tâche : {current_task['title']}", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(self.main_frame, text=f"C'est au tour de : {current_player['name']}", fg="blue", font=("Arial", 12)).pack(pady=10)

        card_frame = tk.Frame(self.main_frame)
        card_frame.pack()

        values = [0, 1, 2, 3, 5, 8, 13, 20, 40, 100, "?", "Cafe"]
        self.imgs = {} # Prevent garbage collection
        
        for i, v in enumerate(values):
            path = os.path.join(BASE_DIR, "cartes", f"cartes_{v}.png")
            if os.path.exists(path):
                img = tk.PhotoImage(file=path).subsample(6, 6)
                self.imgs[v] = img
                btn = tk.Button(card_frame, image=img, command=lambda val=v: self.next_vote(p_idx, t_idx, val))
            else:
                btn = tk.Button(card_frame, text=str(v), width=5, height=2, command=lambda val=v: self.next_vote(p_idx, t_idx, val))
            btn.grid(row=i//4, column=i%4, padx=5, pady=5)

    def next_vote(self, p_idx, t_idx, val):
        vote(cur, conn, session_id, players_in_session[p_idx]['id'], str(val))
        
        # Si c'est le dernier joueur à voter pour cette tâche
        if p_idx + 1 >= len(players_in_session):
            self.show_results(t_idx)
        else:
            self.turn_by_turn_vote(p_idx + 1, t_idx)

    def show_results(self, t_idx):
        self.clear()
        tk.Label(self.main_frame, text=f"Résultats pour : {backlog[t_idx]['title']}", font=("Arial", 14)).pack(pady=10)
        
        votes = get_votes(cur, session_id)
        for u, v in votes:
            tk.Label(self.main_frame, text=f"{u} : {v}", font=("Arial", 12)).pack()

        def next_t():
            # Nettoyer les votes en DB pour la tâche suivante
            cur.execute("DELETE FROM votes WHERE session_id=?", (session_id,))
            conn.commit()
            self.turn_by_turn_vote(0, t_idx + 1)

        tk.Button(self.main_frame, text="Tâche suivante", command=next_t, bg="#4CAF50", fg="white").pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = PlanningPokerApp(root)
    root.mainloop()