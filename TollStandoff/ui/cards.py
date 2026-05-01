import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import multiprocessing as mp

class ProductCardGrid:
    """Класс карточки товара с изображением для сетки"""

    def __init__(
        self,
        parent,
        name,
        id_skin,
        min_buy,
        max_buy,
        current_buy,
        price_sell,
        price_global_sell,
        time_out,
        image_path,
        row,
        col,
        bg_color="#ffffff",
        app=None
    ):
        self.app = app
        self.parent = parent
        self.name = name
        self.min_buy = min_buy
        self.max_buy = max_buy
        self.current_buy = current_buy
        self.price_sell = price_sell
        self.price_global_sell = price_global_sell
        self.time_out = time_out
        self.id_skin = id_skin
        self.search_frame = None

        self.card_frame = tk.Frame(
            parent,
            bg=bg_color,
            relief=tk.RAISED,
            borderwidth=2,
            width=300,
            height=400
        )
        self.card_frame.grid(row=row, column=col, padx=10, pady=10, sticky="n")
        self.card_frame.grid_propagate(False)

        top_frame = tk.Frame(self.card_frame, bg=bg_color)
        top_frame.pack(fill=tk.X, padx=10, pady=10)

        try:
            img = Image.open(image_path)
            img = img.resize((150, 150), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)
            self.image_label = tk.Label(top_frame, image=self.photo, bg=bg_color)
            self.image_label.pack(pady=10)
        except Exception as e:
            self.image_label = tk.Label(top_frame, text="[Нет фото]", bg=bg_color, font=("Arial", 10))
            self.image_label.pack(pady=10)
            print(f"Ошибка загрузки изображения: {e}")

        info_frame = tk.Frame(self.card_frame, bg=bg_color)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        self.name_label = tk.Label(
            info_frame,
            text=name,
            font=("Arial", 12, "bold"),
            bg=bg_color,
            wraplength=250
        )
        self.name_label.pack(anchor=tk.CENTER, pady=(0, 5))

        self.price_buy_label = tk.Label(
            info_frame,
            text=f"Мин Покупка: {min_buy}",
            font=("Arial", 11),
            bg=bg_color,
            fg="#e74c3c"
        )
        self.price_buy_label.pack(anchor=tk.W)

        self.price_sell_label = tk.Label(
            info_frame,
            text=f"Продажа: {price_sell}",
            font=("Arial", 11),
            bg=bg_color,
            fg="#2ecc71"
        )
        self.price_sell_label.pack(anchor=tk.W)

        self.price_global_sell_label = tk.Label(
            info_frame,
            text=f"Глобал: {price_global_sell}",
            font=("Arial", 11),
            bg=bg_color,
            fg="#3498db"
        )
        self.price_global_sell_label.pack(anchor=tk.W)

        self.time_skin = tk.Label(
            info_frame,
            text=f"Ожидание: {time_out} мин",
            font=("Arial", 11),
            bg=bg_color,
            fg="#37388f"
        )
        self.time_skin.pack(anchor=tk.W)

        buttons_frame = tk.Frame(self.card_frame, bg=bg_color)
        buttons_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.change_button = tk.Button(
            buttons_frame,
            text="Изменить",
            command=self.change_skin,
            bg="#3498db",
            fg="white",
            cursor="hand2",
            width=10
        )
        self.change_button.pack()

    def change_skin(self):
        """Действие при нажатии на кнопку изменения"""
        edit_window = tk.Toplevel()
        edit_window.title(f"Редактирование - {self.name}")
        edit_window.geometry("400x550")
        edit_window.configure(bg="#f0f0f0")
        edit_window.transient(self.card_frame.winfo_toplevel())
        edit_window.grab_set()

        tk.Label(
            edit_window,
            text=f"Редактирование: {self.name}",
            font=("Arial", 14, "bold"),
            bg="#f0f0f0"
        ).pack(pady=20)

        buy_min_frame = tk.Frame(edit_window, bg="#f0f0f0")
        buy_min_frame.pack(fill=tk.X, padx=50, pady=10)
        tk.Label(buy_min_frame, text="Цена мин. покупки:", font=("Arial", 12), width=15, anchor=tk.W).pack(side=tk.LEFT)
        buy_min_entry = tk.Entry(buy_min_frame, font=("Arial", 12), width=15)
        buy_min_entry.insert(0, str(self.min_buy))
        buy_min_entry.pack(side=tk.LEFT, padx=(10, 0))

        buy_max_frame = tk.Frame(edit_window, bg="#f0f0f0")
        buy_max_frame.pack(fill=tk.X, padx=50, pady=10)
        tk.Label(buy_max_frame, text="Цена макс. покупки:", font=("Arial", 12), width=15, anchor=tk.W).pack(side=tk.LEFT)
        buy_max_entry = tk.Entry(buy_max_frame, font=("Arial", 12), width=15)
        buy_max_entry.insert(0, str(self.max_buy))
        buy_max_entry.pack(side=tk.LEFT, padx=(10, 0))

        buy_current_frame = tk.Frame(edit_window, bg="#f0f0f0")
        buy_current_frame.pack(fill=tk.X, padx=50, pady=10)
        tk.Label(buy_current_frame, text="Текущая цена покупки:", font=("Arial", 12), width=15, anchor=tk.W).pack(side=tk.LEFT)
        buy_current_entry = tk.Entry(buy_current_frame, font=("Arial", 12), width=15)
        buy_current_entry.insert(0, str(self.current_buy))
        buy_current_entry.pack(side=tk.LEFT, padx=(10, 0))

        sell_frame = tk.Frame(edit_window, bg="#f0f0f0")
        sell_frame.pack(fill=tk.X, padx=50, pady=10)
        tk.Label(sell_frame, text="Цена продажи:", font=("Arial", 12), width=15, anchor=tk.W).pack(side=tk.LEFT)
        sell_entry = tk.Entry(sell_frame, font=("Arial", 12), width=15)
        sell_entry.insert(0, str(self.price_sell))
        sell_entry.pack(side=tk.LEFT, padx=(10, 0))

        global_frame = tk.Frame(edit_window, bg="#f0f0f0")
        global_frame.pack(fill=tk.X, padx=50, pady=10)
        tk.Label(global_frame, text="Глобальная цена:", font=("Arial", 12), width=15, anchor=tk.W).pack(side=tk.LEFT)
        global_entry = tk.Entry(global_frame, font=("Arial", 12), width=15)
        global_entry.insert(0, str(self.price_global_sell))
        global_entry.pack(side=tk.LEFT, padx=(10, 0))

        wait_skin_frame = tk.Frame(edit_window, bg="#f0f0f0")
        wait_skin_frame.pack(fill=tk.X, padx=50, pady=10)
        tk.Label(wait_skin_frame, text="Время ожидания:", font=("Arial", 12), width=15, anchor=tk.W).pack(side=tk.LEFT)
        wait_skin_entry = tk.Entry(wait_skin_frame, font=("Arial", 12), width=15)
        wait_skin_entry.insert(0, str(self.time_out))
        wait_skin_entry.pack(side=tk.LEFT, padx=(10, 0))

        def save_changes():
            try:
                min_buy = float(buy_min_entry.get())
                max_buy = float(buy_max_entry.get())
                new_sell = float(sell_entry.get())
                current_buy = float(buy_current_entry.get())
                new_global = float(global_entry.get())
                time_out = float(wait_skin_entry.get())

                messagebox.showinfo(
                    "Сохранение",
                    f"Данные для {self.name}:\n"
                    f"Мин: Цена покупки: {min_buy}$\n"
                    f"Макс: Цена покупки: {max_buy}$\n"
                    f"Текущая цена покупки: {current_buy}$\n\n"
                    f"Цена продажи: {new_sell}$\n"
                    f"Глобальная цена: {new_global}$\n\n"
                    f"Время ожидания: {time_out}$\n\n"
                    f"Здесь будет обновление базы данных для {self.id_skin}"
                )

                if self.app is not None:
                    self.app.db.execute_query(
                        """UPDATE skins SET min_buy = %s , max_buy = %s , sell_price = %s ,buy_price = %s , sell_global_price = %s , interval_minutes = %s
                               WHERE id = %s""",
                        params=(min_buy, max_buy,  new_sell, current_buy, new_global, time_out, self.id_skin)
                    )
                    self.app.refresh_cards()

                print('сохранил')
                edit_window.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Пожалуйста, введите корректные числа")

        button_frame = tk.Frame(edit_window, bg="#f0f0f0")
        button_frame.pack(pady=30)

        tk.Button(
            button_frame,
            text="Сохранить",
            command=save_changes,
            bg="#2ecc71",
            fg="white",
            font=("Arial", 11),
            width=12,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            button_frame,
            text="Отмена",
            command=edit_window.destroy,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 11),
            width=12,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=10)


class AccountSkinCard:
    """Класс карточки скина, привязанного к аккаунту"""

    def __init__( self, parent, app, account_id, skin_id, name, url, buy_count,sell_count, row, col, bg_color="#ffffff"):
        self.app = app
        self.account_id = account_id
        self.skin_id = skin_id
        self.name = name
        self.buy_count = buy_count
        self.sell_count = sell_count

        self.card_frame = tk.Frame(
            parent,
            bg=bg_color,
            relief=tk.RAISED,
            borderwidth=2,
            width=260,
            height=340
        )
        self.card_frame.grid(row=row, column=col, padx=10, pady=10, sticky="n")
        self.card_frame.grid_propagate(False)

        top_frame = tk.Frame(self.card_frame, bg=bg_color)
        top_frame.pack(fill=tk.X, padx=10, pady=10)

        image_path = rf".\img\skins\{url}.png"
        try:
            img = Image.open(image_path)
            img = img.resize((160, 160), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)
            self.image_label = tk.Label(top_frame, image=self.photo, bg=bg_color)
            self.image_label.pack(pady=5)
        except Exception as e:
            self.image_label = tk.Label(top_frame, text="[Нет фото]", bg=bg_color, font=("Arial", 10))
            self.image_label.pack(pady=5)
            print(f"Ошибка загрузки изображения: {e}")

        info_frame = tk.Frame(self.card_frame, bg=bg_color)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        tk.Label(
            info_frame,
            text=name,
            font=("Arial", 12, "bold"),
            bg=bg_color,
            wraplength=240
        ).pack(anchor=tk.CENTER, pady=(0, 8))

        tk.Label(
            info_frame,
            text=f"Куплено: {buy_count}",
            font=("Arial", 11),
            bg=bg_color,
            fg="#2ecc71"
        ).pack(anchor=tk.CENTER, pady=(0, 8))

        tk.Label(
            info_frame,
            text=f"Продано: {sell_count}",
            font=("Arial", 11),
            bg=bg_color,
            fg="#e74c3c"
        ).pack(anchor=tk.CENTER, pady=(0, 8))

        buttons_frame = tk.Frame(self.card_frame, bg=bg_color)
        buttons_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        tk.Button(
            buttons_frame,
            text="Удалить",
            command=self.delete_skin,
            bg="#e74c3c",
            fg="white",
            cursor="hand2",
            width=12
        ).pack()

    def delete_skin(self):
        """Удаление скина из аккаунта"""
        if self.app is not None:
            self.app.delete_account_skin(self.account_id, self.skin_id)


class AccountCard:
    """Класс карточки аккаунта с улучшенным интерфейсом"""
    
    def __init__(self, parent, app, id_account, name, email, gold, avatar_path, row, col, bg_color="#ffffff"):
        self.app = app
        self.parent = parent
        self.id_account = id_account
        self.name = name
        self.email = email
        self.gold = gold

        # Основная рамка карточки
        self.card_frame = tk.Frame(
            parent,
            bg=bg_color,
            relief=tk.RAISED,
            borderwidth=2,
            width=360,
            height=160
        )
        self.card_frame.grid(row=row, column=col, padx=12, pady=12, sticky="nsew")
        self.card_frame.grid_propagate(False)

        # === Основная горизонтальная структура ===
        main_frame = tk.Frame(self.card_frame, bg=bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Левая часть — аватар
        left_frame = tk.Frame(main_frame, bg=bg_color, width=90 , height=90)
        left_frame.pack(side=tk.LEFT, padx=(0, 15))
        left_frame.pack_propagate(False)


        try:
            img = Image.open(avatar_path)
            img = img.resize((80, 80), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)
            self.avatar_label = tk.Label(left_frame, image=self.photo, bg=bg_color)
            self.avatar_label.pack()
        except Exception as e:
            self.avatar_label = tk.Label(left_frame, text="[Нет фото]", bg=bg_color, font=("Arial", 10))
            self.avatar_label.pack()


        # Правая часть — информация + кнопки
        right_frame = tk.Frame(main_frame, bg=bg_color)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Информация об аккаунте
        tk.Label(right_frame, text=name, font=("Arial", 13, "bold"), bg=bg_color, anchor="w").pack(anchor="w")
        tk.Label(right_frame, text=email, font=("Arial", 10), bg=bg_color, fg="#555", anchor="w").pack(anchor="w")
        tk.Label(right_frame, text=f"Gold: {gold}", font=("Arial", 12, "bold"), 
                 bg=bg_color, fg="#f1c40f", anchor="w").pack(anchor="w", pady=(8, 12))

        # === Блок действий (кнопки) — улучшенная структура ===
        actions_frame = tk.Frame(right_frame, bg=bg_color)
        actions_frame.pack(fill=tk.X, pady=(5, 0))

        # Кнопки "Выбрать" и "История"
        buttons_frame = tk.Frame(actions_frame, bg=bg_color)
        buttons_frame.pack(fill=tk.X, pady=(0, 8))

        self.select_button = tk.Button(
            buttons_frame,
            text="Выбрать",
            command=self.select_account,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            width=12,
            height=1
        )
        self.select_button.pack(side=tk.LEFT, padx=(0, 8))

        self.history_button = tk.Button(
            buttons_frame,
            text="История",
            command=self.show_history,
            bg="#9b59b6",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            width=12,
            height=1
        )
        self.history_button.pack(side=tk.LEFT)

        # Нижняя строка: Выбор действия + кнопка "Запустить"
        bottom_action_frame = tk.Frame(actions_frame, bg=bg_color)
        bottom_action_frame.pack(fill=tk.X)

        # OptionMenu (выбор действия)
        self.action_var = tk.StringVar(value="Действие")
        self.action_menu = tk.OptionMenu(
            bottom_action_frame,
            self.action_var,
            "Продажа по Глобальной цене",
            "Продажа по обычной цене",
            "Рандомная продажа",
            "Тест функций"
        )
        self.action_menu.config(width=25, font=("Arial", 9))
        self.action_menu.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        # Кнопка "Запустить"
        self.action_button = tk.Button(
            bottom_action_frame,
            text="Запустить",
            command=self.run_action,
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            width=12,
            height=1
        )
        self.action_button.pack(side=tk.RIGHT)

    def run_action(self):
        import main
        
        action = self.action_var.get()
        if action == "Тест функций":          # пример
            # Для теста можно запускать в том же потоке
            main.test(self.id_account)
        else:
            
            # Запускаем в отдельном процессе
            process = mp.Process(
                target=main.buy_action,
                args=(self.id_account, action),   # передаём reader
                name=f"Account_{self.id_account}"
            )
            process.daemon = True
            process.start()
            print(f"🚀 Процесс для аккаунта {self.id_account} запущен (PID: {process.pid})")
            print(f"Запущено действие для аккаунта {self.id_account}: {action}")

    def select_account(self):
        print(f"Выбран аккаунт: {self.id_account}")
        if self.app is not None:
            self.app.show_account_skins(self.id_account, self.name)

    def show_history(self):
        print(f"Показана история для аккаунта: {self.id_account}")
        if self.app is not None:
            self.app.show_account_history(self.id_account)