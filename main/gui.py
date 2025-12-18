import os
import tkinter as tk
from tkinter import messagebox
from tkinter import PhotoImage
from functions import (
    init_db, create_user, login,
    create_session, list_sessions,
    join_session, vote, show_votes
)

conn, cur = init_db()
current_user = {"id": None, "role": None}
current_session = {"id": None}


# ======================
# Fenêtre principale
# ======================
root = tk.Tk()
root.title("Planning Poker")
root.geometry("800x700")


# ======================
# Utils
# ======================
def clear_window():
    for widget in root.winfo_children():
        widget.destroy()


# ======================
# LOGIN
# ======================
def login_screen():
    clear_window()

    tk.Label(root, text="Planning Poker", font=("Arial", 18)).pack(pady=10)
    tk.Label(root, text="Pseudo").pack()

    username_entry = tk.Entry(root)
    username_entry.pack()

    tk.Label(root, text="Rôle (user / scrum_master)").pack()
    role_entry = tk.Entry(root)
    role_entry.pack()

    def do_login():
        username = username_entry.get()
        role = role_entry.get()

        user = login(cur, username)
        if user is None:
            if role not in ["user", "scrum_master"]:
                messagebox.showerror("Erreur", "Rôle invalide")
                return
            user_id = create_user(cur, conn, username, role)
            current_user["id"] = user_id
            current_user["role"] = role
        else:
            current_user["id"], current_user["role"] = user

        menu_screen()

    tk.Button(root, text="Connexion", command=do_login).pack(pady=10)


# ======================
# MENU
# ======================
def menu_screen():
    clear_window()

    tk.Label(root, text="Menu principal", font=("Arial", 16)).pack(pady=10)

    if current_user["role"] == "scrum_master":
        tk.Button(root, text="Créer une session", command=create_session_screen).pack(pady=5)

    tk.Button(root, text="Rejoindre une session", command=join_session_screen).pack(pady=5)
    tk.Button(root, text="Quitter", command=root.quit).pack(pady=20)


# ======================
# CREATE SESSION
# ======================
def create_session_screen():
    clear_window()

    tk.Label(root, text="Créer une session", font=("Arial", 14)).pack(pady=10)

    name_entry = tk.Entry(root)
    theme_entry = tk.Entry(root)
    max_entry = tk.Entry(root)

    tk.Label(root, text="Nom").pack()
    name_entry.pack()
    tk.Label(root, text="Thème").pack()
    theme_entry.pack()
    tk.Label(root, text="Max utilisateurs").pack()
    max_entry.pack()

    public_var = tk.IntVar()
    tk.Checkbutton(root, text="Session publique", variable=public_var).pack()

    def create():
        sid = create_session(
            cur, conn,
            name_entry.get(),
            theme_entry.get(),
            int(max_entry.get()),
            public_var.get(),
            current_user["id"]
        )
        messagebox.showinfo("OK", f"Session créée (ID {sid})")
        menu_screen()

    tk.Button(root, text="Créer", command=create).pack(pady=10)
    tk.Button(root, text="Retour", command=menu_screen).pack()


# ======================
# JOIN SESSION
# ======================
def join_session_screen():
    clear_window()

    tk.Label(root, text="Sessions actives", font=("Arial", 14)).pack(pady=10)

    sessions = list_sessions(cur)
    listbox = tk.Listbox(root)
    listbox.pack(fill=tk.BOTH, expand=True)

    for s in sessions:
        listbox.insert(
            tk.END,
            f"ID {s[0]} | {s[1]} | max {s[3]}"
        )

    def join():
        selection = listbox.curselection()
        if not selection:
            return
        session_id = sessions[selection[0]][0]
        if not join_session(cur, session_id, current_user["id"]):
            messagebox.showerror("Erreur", "Session pleine")
            return
        current_session["id"] = session_id
        vote_screen()

    tk.Button(root, text="Rejoindre", command=join).pack(pady=5)
    tk.Button(root, text="Retour", command=menu_screen).pack()


# ======================
# VOTE
# ======================
def vote_screen():
    clear_window()

    tk.Label(root, text="Vote Planning Poker", font=("Arial", 14)).pack(pady=10)

    frame = tk.Frame(root)
    frame.pack(pady=20)

    root.card_images = {}

    values = [0, 1, 2, 3, 5, 8, 13, 20, 40, 100]

    def select_card(value):
        vote(cur, conn, current_session["id"], current_user["id"], value)
        results_screen()

    max_per_row = len(values) // 2 

    for index, v in enumerate(values):
        path = f"cartes/cartes_{v}.png"

        if not os.path.exists(path):
            print(f"❌ Image introuvable : {path}")
            continue

        img = tk.PhotoImage(file=path)
        img = img.subsample(5, 5)

        root.card_images[v] = img

        btn = tk.Button(
            frame,
            image=img,
            command=lambda val=v: select_card(val),
            borderwidth=0
        )

        row = index // max_per_row
        col = index % max_per_row
        btn.grid(row=row, column=col, padx=10, pady=8)





# ======================
# RESULTS
# ======================
def results_screen():
    clear_window()

    tk.Label(root, text="Résultats", font=("Arial", 14)).pack(pady=10)

    cur.execute("""
        SELECT users.username, votes.value
        FROM votes
        JOIN users ON users.id = votes.user_id
        WHERE votes.session_id=?
    """, (current_session["id"],))

    for u, v in cur.fetchall():
        tk.Label(root, text=f"{u} → {v}").pack()

    tk.Button(root, text="Menu", command=menu_screen).pack(pady=10)


# ======================
# START
# ======================
login_screen()
root.mainloop()
