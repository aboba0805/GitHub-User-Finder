import json
import os
import random
import webbrowser

import requests
import tkinter as tk
from tkinter import messagebox


FAVORITES_FILE = "favorites.json"


class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("700x500")
        self.root.resizable(False, False)

        self.search_var = tk.StringVar()
        self.search_results = []

        self.create_widgets()
        self.load_favorites()

    def create_widgets(self):
        title = tk.Label(
            self.root,
            text="GitHub User Finder",
            font=("Arial", 18, "bold")
        )
        title.pack(pady=10)

        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=10)

        tk.Label(search_frame, text="Имя пользователя на GitHub:").pack(side=tk.LEFT, padx=5)

        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=35
        )
        self.search_entry.pack(side=tk.LEFT, padx=5)

        search_button = tk.Button(
            search_frame,
            text="Поиск",
            command=self.search_users,
            width=12
        )
        search_button.pack(side=tk.LEFT, padx=5)

        clear_button = tk.Button(
            search_frame,
            text="Очистить",
            command=self.clear_search,
            width=12
        )
        clear_button.pack(side=tk.LEFT, padx=5)

        results_label = tk.Label(
            self.root,
            text="Результаты поиска",
            font=("Arial", 12, "bold")
        )
        results_label.pack(pady=(10, 5))

        self.results_listbox = tk.Listbox(self.root, width=70, height=10)
        self.results_listbox.pack(pady=5)

        buttons_frame = tk.Frame(self.root)
        buttons_frame.pack(pady=10)

        add_button = tk.Button(
            buttons_frame,
            text="Добавить в Избранное",
            command=self.add_to_favorites,
            width=20
        )
        add_button.pack(side=tk.LEFT, padx=5)

        open_button = tk.Button(
            buttons_frame,
            text="Открыть профиль на GitHub",
            command=self.open_profile,
            width=20
        )
        open_button.pack(side=tk.LEFT, padx=5)

        favorites_label = tk.Label(
            self.root,
            text="Избранное",
            font=("Arial", 12, "bold")
        )
        favorites_label.pack(pady=(10, 5))

        self.favorites_listbox = tk.Listbox(self.root, width=70, height=8)
        self.favorites_listbox.pack(pady=5)

    def validate_input(self, value):
        return bool(value.strip())

    def search_users(self):
        query = self.search_var.get()

        if not self.validate_input(query):
            messagebox.showerror(
                "Ошибка ввода",
                "Поле поиска не может быть пустым."
            )
            return

        try:
            url = f"https://api.github.com/search/users?q={query}"
            response = requests.get(url, timeout=10)

            if response.status_code != 200:
                messagebox.showerror(
                    "Ошибка API",
                    "Не удалось получить данные из API GitHub."
                )
                return

            data = response.json()
            self.search_results = data.get("items", [])

            self.results_listbox.delete(0, tk.END)

            if not self.search_results:
                self.results_listbox.insert(tk.END, "Пользователи не найдены")
                return

            for user in self.search_results:
                text = f"{user['login']} | ID: {user['id']}"
                self.results_listbox.insert(tk.END, text)

        except requests.exceptions.RequestException:
            messagebox.showerror(
                "Ошибка подключения",
                "Не удалось подключиться к API GitHub."
            )

    def add_to_favorites(self):
        selection = self.results_listbox.curselection()

        if not selection:
            messagebox.showwarning(
                "Ошибка выбора",
                "Сначала выберите пользователя."
            )
            return

        index = selection[0]

        if index >= len(self.search_results):
            return

        user = self.search_results[index]

        existing_users = self.get_favorites_data()

        for existing_user in existing_users:
            if existing_user["login"] == user["login"]:
                messagebox.showinfo(
                    "Дубликат",
                    "Пользователь уже есть в избранном."
                )
                return

        favorite_user = {
            "local_id": random.randint(1000, 9999),
            "login": user["login"],
            "github_id": user["id"],
            "profile_url": user["html_url"]
        }

        existing_users.append(favorite_user)

        with open(FAVORITES_FILE, "w", encoding="utf-8") as file:
            json.dump(existing_users, file, indent=4)

        self.load_favorites()

        messagebox.showinfo(
            "Успех",
            "Пользователь добавлен в избранное"
        )

    def load_favorites(self):
        self.favorites_listbox.delete(0, tk.END)

        favorites = self.get_favorites_data()

        for user in favorites:
            text = (
                f"{user['login']} | "
                f"Local ID: {user['local_id']}"
            )
            self.favorites_listbox.insert(tk.END, text)

    def get_favorites_data(self):
        if not os.path.exists(FAVORITES_FILE):
            return []

        try:
            with open(FAVORITES_FILE, "r", encoding="utf-8") as file:
                return json.load(file)

        except json.JSONDecodeError:
            return []

    def open_profile(self):
        selection = self.results_listbox.curselection()

        if not selection:
            messagebox.showwarning(
                "Ошибка выбора",
                "Сначала выберите пользователя."
            )
            return

        index = selection[0]

        if index >= len(self.search_results):
            return

        user = self.search_results[index]
        webbrowser.open(user["html_url"])

    def clear_search(self):
        self.search_var.set("")
        self.results_listbox.delete(0, tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()
