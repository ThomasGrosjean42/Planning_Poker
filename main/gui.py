import os
import tkinter as tk
from tkinter import messagebox, filedialog
import json
import statistics 
from functions import init_db, login_or_create, create_session, vote, get_votes

conn, cur = init_db()
players_in_session = [] 
backlog = []
session_id = None
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class PlanningPokerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Planning Poker - M1 Informatique")
        self.root.geometry("850x750")
        
        # Style général
        self.bg_color = "#F5F5F5"  # Gris très clair
        self.root.configure(bg=self.bg_color)
        
        self.main_frame = tk.Frame(self.root, bg=self.bg_color, padx=20, pady=20)
        self.main_frame.pack(expand=True, fill="both")
        
        self.mode_vote = tk.StringVar(value="Strict")
        self.login_screen()

    def clear(self):
        for w in self.main_frame.winfo_children(): w.destroy()

    # --- Étape 1 : Enregistrement des joueurs ---
    def login_screen(self):
        self.clear()
        tk.Label(self.main_frame, text="Enregistrement des Participants", font=("Arial", 18, "bold"), bg=self.bg_color).pack(pady=20)
        
        box = tk.LabelFrame(self.main_frame, text=" Nouveau Joueur ", padx=15, pady=15, bg=self.bg_color)
        box.pack(fill="x", padx=50)

        tk.Label(box, text="Pseudo:", bg=self.bg_color).grid(row=0, column=0, pady=5, sticky="w")
        ent_name = tk.Entry(box, font=("Arial", 11))
        ent_name.grid(row=0, column=1, padx=10, sticky="ew")

        tk.Label(box, text="Rôle:", bg=self.bg_color).grid(row=1, column=0, pady=5, sticky="w")
        self.role_var = tk.StringVar(value="user")
        role_menu = tk.OptionMenu(box, self.role_var, "user", "scrum_master")
        role_menu.grid(row=1, column=1, sticky="w", padx=10)

        def add_player():
            name = ent_name.get().strip()
            role = self.role_var.get()
            if not name: return

            uid, role_final = login_or_create(cur, conn, name, role)
            players_in_session.append({"id": uid, "name": name, "role": role_final})
            
            # Affichage dans la liste avec distinction pour le Scrum Master
            label_text = f" {name} ({role_final})"
            self.listbox_players.insert(tk.END, label_text)
            if role_final == "scrum_master":
                self.listbox_players.itemconfig(tk.END, fg="#D35400") # Orange sombre
            
            ent_name.delete(0, tk.END)

        tk.Button(box, text="Ajouter", command=add_player, bg="#AED6F1", width=10).grid(row=2, column=1, pady=10, sticky="e")

        self.listbox_players = tk.Listbox(self.main_frame, width=50, height=8, font=("Arial", 10))
        self.listbox_players.pack(pady=20)

        tk.Button(self.main_frame, text="Suivant >>", command=self.session_creation_screen, bg="#ABEBC6", font=("Arial", 10, "bold"), padx=20).pack()

    # --- Étape 2 : Création de Session ---
    def session_creation_screen(self):
        self.clear()
        tk.Label(self.main_frame, text="Configuration de la Session", font=("Arial", 16, "bold"), bg=self.bg_color).pack(pady=20)
        
        tk.Label(self.main_frame, text="Nom du projet / session:", bg=self.bg_color).pack()
        ent_sname = tk.Entry(self.main_frame, width=40)
        ent_sname.pack(pady=5)

        mode_box = tk.LabelFrame(self.main_frame, text=" Règle de calcul ", padx=10, pady=10, bg=self.bg_color)
        mode_box.pack(pady=15)
        for m in ["Strict", "Moyenne", "Médiane"]:
            tk.Radiobutton(mode_box, text=m, variable=self.mode_vote, value=m, bg=self.bg_color).pack(side="left", padx=10)

        def load_json():
            global backlog
            path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
            if path:
                with open(path, 'r', encoding='utf-8') as f:
                    backlog = json.load(f).get("issues", [])
                messagebox.showinfo("Succès", f"{len(backlog)} tâches importées.")

        tk.Button(self.main_frame, text="Charger le Backlog JSON", command=load_json, bg="#D5DBDB").pack(pady=10)

        def start():
            global session_id
            sm = next((p for p in players_in_session if p['role'] == 'scrum_master'), None)
            if not sm or not ent_sname.get() or not backlog:
                messagebox.showwarning("Erreur", "Vérifiez : Scrum Master présent, Nom session rempli et Backlog chargé.")
                return
            session_id = create_session(cur, conn, ent_sname.get(), self.mode_vote.get(), sm['id'])
            self.turn_by_turn_vote(0, 0)

        tk.Button(self.main_frame, text="Lancer le Vote", command=start, bg="#2E86C1", fg="white", font=("Arial", 11, "bold"), padx=30, pady=5).pack(pady=20)

    # --- Étape 3 : Vote Tour par Tour ---
    def turn_by_turn_vote(self, p_idx, t_idx):
        self.clear()
        if t_idx >= len(backlog):
            messagebox.showinfo("Terminé", "Fin du backlog.")
            return self.login_screen()

        current_player = players_in_session[p_idx]
        current_task = backlog[t_idx]

        # Bandeau de la tâche
        banner = tk.Frame(self.main_frame, bg="#34495E", pady=10)
        banner.pack(fill="x", pady=(0, 20))
        tk.Label(banner, text=f"Tâche : {current_task['title']}", fg="white", bg="#34495E", font=("Arial", 12, "bold")).pack()

        tk.Label(self.main_frame, text=f"Au tour de : {current_player['name']}", font=("Arial", 14), bg=self.bg_color, fg="#1A5276").pack(pady=10)

        card_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        card_frame.pack(pady=10)

        values = [0, 1, 2, 3, 5, 8, 13, 20, 40, 100, "?", "Cafe"]
        self.card_imgs = {} # Pour garder les images en mémoire

        for i, v in enumerate(values):
            path = os.path.join(BASE_DIR, "cartes", f"cartes_{v}.png")
            if os.path.exists(path):
                img = tk.PhotoImage(file=path).subsample(6, 6)
                self.card_imgs[v] = img
                btn = tk.Button(card_frame, image=img, command=lambda val=v: self.next_vote(p_idx, t_idx, val), borderwidth=1)
            else:
                btn = tk.Button(card_frame, text=str(v), width=8, height=4, font=("Arial", 10, "bold"), command=lambda val=v: self.next_vote(p_idx, t_idx, val))
            
            btn.grid(row=i//4, column=i%4, padx=8, pady=8)

    def next_vote(self, p_idx, t_idx, val):
        vote(cur, conn, session_id, players_in_session[p_idx]['id'], str(val))
        if p_idx + 1 >= len(players_in_session):
            self.show_results(t_idx)
        else:
            self.turn_by_turn_vote(p_idx + 1, t_idx)

    # --- Étape 4 : Résultats ---
    def show_results(self, t_idx):
        self.clear()
        tk.Label(self.main_frame, text="Résultats du tour", font=("Arial", 16, "bold"), bg=self.bg_color).pack(pady=20)
        
        votes = get_votes(cur, session_id)
        numeric_votes = []
        
        # Zone d'affichage des votes
        res_list = tk.Frame(self.main_frame, bg="white", padx=20, pady=20, relief="sunken", borderwidth=1)
        res_list.pack(pady=10)

        for u, v in votes:
            tk.Label(res_list, text=f"{u} a voté : {v}", font=("Arial", 11), bg="white").pack(anchor="w")
            try: numeric_votes.append(int(v))
            except: continue

        # Logique de calcul selon le mode
        mode = self.mode_vote.get()
        final_val = "Inconnu"
        if numeric_votes:
            if mode == "Moyenne": final_val = f"{sum(numeric_votes)/len(numeric_votes):.2f}"
            elif mode == "Médiane": final_val = statistics.median(numeric_votes)
            else: final_val = numeric_votes[0] if len(set(numeric_votes)) == 1 else "Débat requis (non unanime)"

        # Affichage du résultat final mis en évidence
        score_box = tk.Frame(self.main_frame, bg="#D4E6F1", padx=20, pady=10)
        score_box.pack(pady=20)
        tk.Label(score_box, text=f"Résultat Final ({mode}) : {final_val}", font=("Arial", 13, "bold"), bg="#D4E6F1", fg="#1B4F72").pack()

        def go_next():
            # Reset des votes pour la prochaine tâche
            cur.execute("DELETE FROM votes WHERE session_id=?", (session_id,))
            conn.commit()
            self.turn_by_turn_vote(0, t_idx + 1)

        tk.Button(self.main_frame, text="Tâche Suivante >>", command=go_next, bg="#2E86C1", fg="white", font=("Arial", 10, "bold"), padx=20).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = PlanningPokerApp(root)
    root.mainloop()