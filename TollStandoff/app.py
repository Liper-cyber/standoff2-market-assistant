from decimal import Decimal
import tkinter as tk
from tkinter import messagebox
import os
import io
from PIL import Image

from services.database_service import data
from .ui.cards import ProductCardGrid, AccountCard, AccountSkinCard


#РАЗРЕШЕНГИЕ ДЛЯ ОКНА ПРОГРАММЫ
WINDOWSCALE = (1400, 1240)

#ДЛЯ ФОТОК
SKIN_FULL = [238, 58 , 172 , 112]
SKIN_NACKLE = [230 , 240 , 160 , 60]
AVATARS_REGION = [288, 178 , 36 , 284]


# Путь к скриншоту с аватарками
AVATARS_PATH = './img/screenshots/avatars.png' 

class MenuApp:
    """Главное приложение с меню"""

    def __init__(self, root):
        self.root = root
        self.root.geometry(f"{WINDOWSCALE[0]}x{WINDOWSCALE[1]}")
        self.root.configure(bg="#f0f0f0")

        self.db = data
        self.cards_container = None
        self.canvas = None
        self.search_entry = None
        self.search_frame = None
        self.cards_in_row = 0
        self.accounts = []

        # Для аватарок
        self.avatar_nox_id = tk.StringVar(value="1")
        self.avatar_output_dir = tk.StringVar(value="./img/screenshots")
        self.avatar_driver = None
        self.avatar_driver_manager = None
        self.avatar_status_var = tk.StringVar(value="Готов. Нажмите 'Подключиться к устройству'")
        self.avatar_images_frame = None

        self.create_menu()
        self.main_container = tk.Frame(root, bg="#f0f0f0")
        self.main_container.pack(fill=tk.BOTH, expand=True)

    def refresh_cards(self):
        """Обновление карточек после изменения в БД"""
        if self.cards_container is not None:
            for widget in self.cards_container.winfo_children():
                widget.destroy()
            self.cards_in_row = 0
            self.create_interfaces_skin()

    def create_menu(self):
        """Создание верхнего меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        skin_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Скины", menu=skin_menu)
        skin_menu.add_command(label="Список скинов", command=self.create_interfaces_skin)

        account_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Аккаунты", menu=account_menu)
        account_menu.add_command(label="Список скинов", command=self.create_interfaces_account)

        photo_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Скриншот Tool", menu=photo_menu)
        photo_menu.add_command(label="Скриншот Tool", command=self.create_interfaces_photo)


    def create_interfaces_photo(self):
        """Интерфейс для сохранения скриншотов"""
        # Очистить основной контейнер
        for widget in self.main_container.winfo_children():
            widget.destroy()

        # Переменные для хранения значений
        self.id_devices = tk.StringVar(value="1")
        self.photo_x_var = tk.StringVar(value="0")
        self.photo_y_var = tk.StringVar(value="0")
        self.photo_w_var = tk.StringVar(value="960")
        self.photo_h_var = tk.StringVar(value="540")
        self.photo_path_var = tk.StringVar(value="./img/screenshots/region.png")
        self.photo_driver = None
        self.photo_driver_manager = None
        self.photo_status_var = tk.StringVar(value="Готов. Нажмите 'Подключиться к устройству'")

        # Основной фрейм
        main_frame = tk.Frame(self.main_container, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Заголовок
        title_label = tk.Label(main_frame, text="Сохранение скриншотов", font=('Arial', 14, 'bold'), bg="#f0f0f0")
        title_label.pack(pady=(0, 15))

        # Рамка для параметров области
        region_frame = tk.LabelFrame(main_frame, text="Параметры области", bg="#f0f0f0", padx=10, pady=10)
        region_frame.pack(fill=tk.X, pady=(0, 10))

        # Поле X
        x_frame = tk.Frame(region_frame, bg="#f0f0f0")
        x_frame.pack(fill=tk.X, pady=2)
        tk.Label(x_frame, text="X:", width=10, bg="#f0f0f0").pack(side=tk.LEFT)
        tk.Entry(x_frame, textvariable=self.photo_x_var, width=20).pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(x_frame, text="(левая граница)", fg="gray", bg="#f0f0f0").pack(side=tk.LEFT)

        # Поле Y
        y_frame = tk.Frame(region_frame, bg="#f0f0f0")
        y_frame.pack(fill=tk.X, pady=2)
        tk.Label(y_frame, text="Y:", width=10, bg="#f0f0f0").pack(side=tk.LEFT)
        tk.Entry(y_frame, textvariable=self.photo_y_var, width=20).pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(y_frame, text="(верхняя граница)", fg="gray", bg="#f0f0f0").pack(side=tk.LEFT)

        # Поле Width
        w_frame = tk.Frame(region_frame, bg="#f0f0f0")
        w_frame.pack(fill=tk.X, pady=2)
        tk.Label(w_frame, text="Width:", width=10, bg="#f0f0f0").pack(side=tk.LEFT)
        tk.Entry(w_frame, textvariable=self.photo_w_var, width=20).pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(w_frame, text="(ширина области)", fg="gray", bg="#f0f0f0").pack(side=tk.LEFT)

        # Поле Height
        h_frame = tk.Frame(region_frame, bg="#f0f0f0")
        h_frame.pack(fill=tk.X, pady=2)
        tk.Label(h_frame, text="Height:", width=10, bg="#f0f0f0").pack(side=tk.LEFT)
        tk.Entry(h_frame, textvariable=self.photo_h_var, width=20).pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(h_frame, text="(высота области)", fg="gray", bg="#f0f0f0").pack(side=tk.LEFT)

        #ID NOX 
        id_devices = tk.Frame(region_frame, bg="#f0f0f0")
        id_devices.pack(fill=tk.X, pady=2)
        tk.Label(id_devices, text="ID NOX:", width=10, bg="#f0f0f0").pack(side=tk.LEFT)
        tk.Entry(id_devices, textvariable=self.id_devices, width=20).pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(id_devices, text="(Айди NOX)", fg="gray", bg="#f0f0f0").pack(side=tk.LEFT)

        # Рамка для пути сохранения
        path_frame = tk.LabelFrame(main_frame, text="Путь для сохранения", bg="#f0f0f0", padx=10, pady=10)
        path_frame.pack(fill=tk.X, pady=(0, 10))

        path_entry_frame = tk.Frame(path_frame, bg="#f0f0f0")
        path_entry_frame.pack(fill=tk.X, pady=2)
        tk.Label(path_entry_frame, text="Путь:", width=10, bg="#f0f0f0").pack(side=tk.LEFT)
        tk.Entry(path_entry_frame, textvariable=self.photo_path_var, width=35).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(path_entry_frame, text="Обзор...", command=self.photo_choose_path, bg="#3498db", fg="white").pack(side=tk.LEFT)

        # Кнопки предустановок
        presets_frame = tk.Frame(main_frame, bg="#f0f0f0")
        presets_frame.pack(pady=(0, 10))

        tk.Button(presets_frame, text="Полный скин", command=lambda: self.set_preset("skin"), bg="#2ecc71", fg="white").pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(presets_frame, text="Наклейки", command=lambda: self.set_preset("sticker"), bg="#2ecc71", fg="white").pack(side=tk.LEFT , padx=(0, 10))
        # Кнопки действий
        buttons_frame = tk.Frame(main_frame, bg="#f0f0f0")
        buttons_frame.pack(pady=15)

        tk.Button(buttons_frame, text="📸 Сделать скриншот", command=self.photo_save_region, bg="#3498db", fg="white", width=20).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(buttons_frame, text="🔌 Подключиться к устройству", command=self.photo_connect_device, bg="#e74c3c", fg="white", width=25).pack(side=tk.LEFT)

        # Статусная строка
        status_label = tk.Label(main_frame, textvariable=self.photo_status_var, relief=tk.SUNKEN, anchor=tk.W, padx=5, pady=2, bg="#f0f0f0")
        status_label.pack(fill=tk.X, pady=(10, 0))

    def photo_choose_path(self):
        """Диалог выбора пути для сохранения"""
        
        from tkinter import filedialog
        initial_dir = os.path.dirname(self.photo_path_var.get())
        if not initial_dir:
            initial_dir = "./img/screenshots"
        
        file_path = filedialog.asksaveasfilename(
            title="Сохранить скриншот как...",
            initialdir=initial_dir,
            defaultextension=".png",
            filetypes=[("PNG файлы", "*.png"), ("Все файлы", "*.*")]
        )
        if file_path:
            self.photo_path_var.set(file_path)

    def photo_connect_device(self):
        from dotenv import load_dotenv
        load_dotenv()
        """Подключение к устройству через Appium"""
        try:
            self.photo_status_var.set("Подключение к устройству...")
            self.root.update()
            from config.appium_config import capability_me , appium_config
            capability_me = appium_config.get_capabilities(self.id_devices.get())
            from core.driver_manager import driver_manager
            self.photo_driver_manager = driver_manager
            
            self.photo_driver = self.photo_driver_manager.start_driver()
            
            self.photo_status_var.set("✅ Подключено успешно!")
            messagebox.showinfo("Успех", "Подключение к устройству выполнено!")
            
        except Exception as e:
            self.photo_status_var.set(f"❌ Ошибка подключения: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось подключиться:\n{str(e)}")

    def photo_save_region(self):
        """Сохраняет область экрана"""
        if not self.photo_driver:
            messagebox.showwarning("Нет подключения", "Сначала подключитесь к устройству!")
            return
        
        try:
            x = int(self.photo_x_var.get())
            y = int(self.photo_y_var.get())
            w = int(self.photo_w_var.get())
            h = int(self.photo_h_var.get())
            path = self.photo_path_var.get()
            
            if w <= 0 or h <= 0:
                messagebox.showerror("Ошибка", "Ширина и высота должны быть больше 0!")
                return
            
            self.photo_status_var.set("Сохранение области...")
            self.root.update()
            
            screenshot = self.photo_driver.get_screenshot_as_png()
            screenshot_img = Image.open(io.BytesIO(screenshot))
            region = screenshot_img.crop((x, y, x + w, y + h))
            
            output_dir = os.path.dirname(path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            region.save(path, format='PNG')
            
            self.photo_status_var.set(f"✅ Область сохранена: {path}")
            messagebox.showinfo("Успех", f"Область сохранена в:\n{path}")
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверный формат числа:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении:\n{str(e)}")
            self.photo_status_var.set(f"❌ Ошибка: {str(e)}")

    def set_preset(self, preset):
        """Установка предустановленных значений для координат"""
        if preset == "skin":
            self.photo_x_var.set(SKIN_FULL[0])
            self.photo_y_var.set(SKIN_FULL[1])
            self.photo_w_var.set(SKIN_FULL[2])
            self.photo_h_var.set(SKIN_FULL[3])
        elif preset == "sticker":
            self.photo_x_var.set(SKIN_NACKLE[0])
            self.photo_y_var.set(SKIN_NACKLE[1])
            self.photo_w_var.set(SKIN_NACKLE[2])
            self.photo_h_var.set(SKIN_NACKLE[3])

    def create_interfaces_account(self):
        """Создание двух колонок: аккаунты и скины"""
        for widget in self.main_container.winfo_children():
            widget.destroy()

        left_panel = tk.Frame(self.main_container, bg="#f0f0f0", width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        tk.Label(
            left_panel,
            text="Аккаунты",
            font=("Arial", 16, "bold"),
            bg="#2c3e50",
            fg="white",
            height=2
        ).pack(fill=tk.X)

        search_frame = tk.Frame(left_panel, bg="#f0f0f0", height=50)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        search_frame.pack_propagate(False)

        tk.Label(search_frame, text="Поиск:", font=("Arial", 10), bg="#f0f0f0").pack(side=tk.LEFT, padx=(0, 5))

        self.account_search_entry = tk.Entry(search_frame, font=("Arial", 10), width=25)
        self.account_search_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.account_search_entry.bind("<Return>", self.on_account_search)

        show_all_accounts_button = tk.Button(
            search_frame,
            text="Показать все",
            command=self.show_all_accounts,
            bg="#34c2db",
            fg="white",
            font=("Arial", 10),
            cursor="hand2"
        )
        show_all_accounts_button.pack(side=tk.LEFT, padx=(10, 0))

        left_canvas = tk.Canvas(left_panel, bg="#f0f0f0", highlightthickness=0)
        left_scrollbar = tk.Scrollbar(left_panel, orient="vertical", command=left_canvas.yview)
        self.left_cards_container = tk.Frame(left_canvas, bg="#f0f0f0")

        self.left_cards_container.bind(
            "<Configure>",
            lambda e: left_canvas.configure(scrollregion=left_canvas.bbox("all"))
        )

        left_canvas.create_window((0, 0), window=self.left_cards_container, anchor="nw")
        left_canvas.configure(yscrollcommand=left_scrollbar.set)

        left_canvas.pack(side="left", fill="both", expand=True)
        left_scrollbar.pack(side="right", fill="y")
        left_canvas.bind("<MouseWheel>", lambda e: left_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        self._populate_account_cards("")

        right_panel = tk.Frame(self.main_container, bg="#f0f0f0", width=800)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.right_title = tk.Label(
            right_panel,
            text="Скины (выберите аккаунт)",
            font=("Arial", 16, "bold"),
            bg="#2c3e50",
            fg="white",
            height=2
        )
        self.right_title.pack(fill=tk.X)

        add_skin_button = tk.Button(
            right_panel,
            text="Добавить скин",
            command=self.open_add_skin_window,
            bg="#2ecc71",
            fg="white",
            font=("Arial", 11),
            cursor="hand2"
        )
        add_skin_button.pack(pady=10)

        self.right_canvas = tk.Canvas(right_panel, bg="#f0f0f0", highlightthickness=0)
        right_scrollbar = tk.Scrollbar(right_panel, orient="vertical", command=self.right_canvas.yview)
        self.right_cards_container = tk.Frame(self.right_canvas, bg="#f0f0f0")

        self.right_cards_container.bind(
            "<Configure>",
            lambda e: self.right_canvas.configure(scrollregion=self.right_canvas.bbox("all"))
        )

        self.right_canvas.create_window((0, 0), window=self.right_cards_container, anchor="nw")
        self.right_canvas.configure(yscrollcommand=right_scrollbar.set)

        self.right_canvas.pack(side="left", fill="both", expand=True)
        right_scrollbar.pack(side="right", fill="y")
        self.right_canvas.bind("<MouseWheel>", lambda e: self.right_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))


    def show_account_skins(self, account_id, account_name):
        """Показать скины выбранного аккаунта в правой панели"""
        if not hasattr(self, 'right_cards_container') or self.right_cards_container is None:
            return

        self.selected_account_id = account_id
        self.selected_account_name = account_name
        self.right_title.config(text=f"Скины аккаунта: {account_name}")

        for widget in self.right_cards_container.winfo_children():
            widget.destroy()

        skins = self.db.execute_query(
            """SELECT s.id, s.name, s.url, ask.count, ask.sell_count FROM account_skins ask
                JOIN skins s ON s.id = ask.skin_id
                WHERE ask.account_id = %s""",
            params=(account_id,),
            fetch_all=True
        )

        if not skins:
            tk.Label(
                self.right_cards_container,
                text="У этого аккаунта нет скинов",
                font=("Arial", 14),
                bg="#f0f0f0",
                fg="#333"
            ).pack(pady=20)
            return

        cards_in_row = 0
        for skin in skins:
            row = cards_in_row // 3
            col = cards_in_row % 3
            AccountSkinCard(
                parent=self.right_cards_container,
                app=self,
                account_id=account_id,
                skin_id=skin['id'],
                name=skin['name'],
                url=skin['url'],
                buy_count=skin['count'],
                sell_count=skin['sell_count'],
                row=row,
                col=col
            )
            cards_in_row += 1

    def delete_account_skin(self, account_id, skin_id):
        """Удалить скин из аккаунта и обновить правую панель"""
        self.db.execute_query(
            "DELETE FROM account_skins WHERE account_id = %s AND skin_id = %s",
            params=(account_id, skin_id)
        )
        if hasattr(self, 'selected_account_id') and self.selected_account_id == account_id:
            self.show_account_skins(account_id, self.selected_account_name)

    def open_add_skin_window(self):
        """Открыть окно добавления скина к аккаунту"""
        if not hasattr(self, 'selected_account_id') or self.selected_account_id is None:
            messagebox.showwarning("Выберите аккаунт", "Сначала выберите аккаунт, чтобы добавить скин.")
            return

        add_window = tk.Toplevel(self.root)
        add_window.title(f"Добавить скин аккаунту {self.selected_account_name}")
        add_window.geometry("480x640")
        add_window.configure(bg="#f0f0f0")
        add_window.transient(self.root)
        add_window.grab_set()

        tk.Label(
            add_window,
            text="Поиск",
            font=("Arial", 14, "bold"),
            bg="#f0f0f0"
        ).pack(pady=(15, 5))

        search_frame = tk.Frame(add_window, bg="#f0f0f0")
        search_frame.pack(fill=tk.X, padx=15, pady=(0, 10))

        search_entry = tk.Entry(search_frame, font=("Arial", 12), width=28)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        def update_skin_list():
            for widget in skins_container.winfo_children():
                widget.destroy()

            search_text = search_entry.get().strip()
            if search_text:
                query = "SELECT id, name FROM skins WHERE name LIKE %s LIMIT 30"
                skins = self.db.execute_query(query, params=(f"%{search_text}%",), fetch_all=True)
            else:
                skins = self.db.execute_query("SELECT id, name FROM skins LIMIT 30", fetch_all=True)

            for skin in skins:
                btn = tk.Button(
                    skins_container,
                    text=skin['name'],
                    command=lambda skin_id=skin['id']: add_skin_to_account(skin_id),
                    bg="#3498db",
                    fg="white",
                    font=("Arial", 11),
                    cursor="hand2",
                    relief=tk.RAISED
                )
                btn.pack(fill=tk.X, pady=4)

        def add_skin_to_account(skin_id):
            exists = self.db.execute_query(
                "SELECT 1 FROM account_skins WHERE account_id = %s AND skin_id = %s LIMIT 1",
                params=(self.selected_account_id, skin_id),
                fetch_all=True
            )
            if exists:
                messagebox.showinfo("Скин уже добавлен", "Этот скин уже привязан к аккаунту.")
                return

            self.db.execute_query(
                "INSERT INTO account_skins (account_id, skin_id) VALUES (%s, %s)",
                params=(self.selected_account_id, skin_id)
            )
            messagebox.showinfo("Готово", "Скин добавлен аккаунту.")
            self.show_account_skins(self.selected_account_id, self.selected_account_name)
            update_skin_list()

        search_button = tk.Button(
            search_frame,
            text="Найти",
            command=update_skin_list,
            bg="#3498db",
            fg="white",
            font=("Arial", 11),
            cursor="hand2"
        )
        search_button.pack(side=tk.LEFT, padx=(10, 0))

        container_frame = tk.Frame(add_window, bg="#f0f0f0")
        container_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        canvas = tk.Canvas(container_frame, bg="#f0f0f0", highlightthickness=0)
        scrollbar = tk.Scrollbar(container_frame, orient="vertical", command=canvas.yview)
        skins_container = tk.Frame(canvas, bg="#f0f0f0")

        skins_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=skins_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        update_skin_list()

    def on_account_search(self, event=None):
        """Поиск аккаунтов по Enter"""
        search_text = self.account_search_entry.get().strip()
        self._populate_account_cards(search_text)

    def show_all_accounts(self):
        """Показать все аккаунты, как при старте"""
        self.account_search_entry.delete(0, tk.END)
        self._populate_account_cards("")

    def _populate_account_cards(self, search_text=""):
        for widget in self.left_cards_container.winfo_children():
            widget.destroy()

        if search_text:
            query = "SELECT id, name, gmail, gold FROM account WHERE name LIKE %s OR gmail LIKE %s LIMIT 30"
            accounts = self.db.execute_query(query, params=(f"%{search_text}%", f"%{search_text}%"), fetch_all=True)
        else:
            accounts = self.db.execute_query("SELECT id, name, gmail, gold FROM account LIMIT 30", fetch_all=True)

        row = 0
        for account in accounts:
            avatar_path = rf".\img\avatars\{account['name']}.jpg"
            AccountCard(
                parent=self.left_cards_container,
                app=self,
                id_account=account['id'],
                name=account['name'],
                email=account['gmail'],
                gold=account['gold'],
                avatar_path=avatar_path,
                row=row,
                col=0
            )
            row += 1

    def create_interfaces_skin(self, search_text=""):
        """Создание карточек скинов с фильтрацией по поиску"""
        # Очищаем весь основной контейнер
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Сбрасываем переменные
        self.cards_container = None
        self.canvas = None
        
        # Создаём холст и контейнер заново
        self.canvas = tk.Canvas(self.main_container, bg="#f0f0f0", highlightthickness=0)
        scrollbar = tk.Scrollbar(self.main_container, orient="vertical", command=self.canvas.yview)
        self.cards_container = tk.Frame(self.canvas, bg="#f0f0f0")        
        self.cards_container.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.cards_container, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)

        for widget in self.cards_container.winfo_children():
            widget.destroy()


        self.cards_in_row = 0

        self.search_frame = tk.Frame(self.cards_container, bg="#f0f0f0")
        self.search_frame.grid(row=0, column=0, columnspan=5, pady=20, sticky="ew")
        self.search_frame.grid_columnconfigure(1, weight=1)

        tk.Label(
            self.search_frame,
            text="Поиск скина:",
            font=("Arial", 12),
            bg="#f0f0f0"
        ).grid(row=0, column=0, padx=(0, 10))

        self.search_entry = tk.Entry(
            self.search_frame,
            font=("Arial", 12),
            width=40
        )
        self.search_entry.grid(row=0, column=1, padx=(0, 10), sticky="ew")
        self.search_entry.insert(0, search_text)
        self.search_entry.bind("<Return>", self.on_search_enter)

        search_button = tk.Button(
            self.search_frame,
            text="Найти",
            command=self.on_search_button,
            bg="#3498db",
            fg="white",
            font=("Arial", 10),
            cursor="hand2"
        )
        search_button.grid(row=0, column=2, padx=(10, 0))

        all_skins = tk.Button(
            self.search_frame,
            text="Все скины",
            command=self.show_all_skins,
            bg="#34c2db",
            fg="white",
            font=("Arial", 10),
            cursor="hand2"
        )
        all_skins.grid(row=0, column=3, padx=(10, 0))

        self.add_skin_button_frame = tk.Frame(self.cards_container, bg="#f0f0f0")
        self.add_skin_button_frame.grid(row=1, column=0, columnspan=5, pady=(10, 20), sticky="w")

        add_skin_button = tk.Button(
            self.add_skin_button_frame,
            text="Добавить скин",
            command=self.open_add_skin_dialog,
            bg="#2ecc71",
            fg="white",
            font=("Arial", 11),
            cursor="hand2",
            width=20
        )
        add_skin_button.pack(anchor="w")

        self.cards_in_row = 10

        if search_text:
            query = "SELECT id, name, url, min_buy, max_buy, buy_price, sell_price, sell_global_price, interval_minutes FROM skins WHERE name LIKE %s LIMIT 30"
            skins = self.db.execute_query(query, params=(f"%{search_text}%",), fetch_all=True)
            print(f"Найдено скинов: {len(skins)}")
        else:
            skins = self.db.execute_query("SELECT id, name, url, min_buy, max_buy, buy_price , sell_price, sell_global_price, interval_minutes FROM skins LIMIT 30", fetch_all=True)

        for skin in skins:
            row = self.cards_in_row // 5
            col = self.cards_in_row % 5
            image_path = rf".\img\skins\{skin['url']}.png"

            ProductCardGrid(
                parent=self.cards_container,
                app=self,
                id_skin=skin['id'],
                name=skin['name'],
                min_buy=skin['min_buy'],
                max_buy=skin['max_buy'],
                current_buy=skin['buy_price'],
                price_sell=skin['sell_price'],
                price_global_sell=skin['sell_global_price'],
                time_out=skin['interval_minutes'],
                image_path=image_path,
                row=row,
                col=col
            )
            self.cards_in_row += 1

        if len(skins) == 0 and search_text:
            no_result_label = tk.Label(
                self.cards_container,
                text=f"По запросу '{search_text}' ничего не найдено",
                font=("Arial", 14),
                bg="#f0f0f0",
                fg="red"
            )
            no_result_label.grid(row=self.cards_in_row // 5, column=0, columnspan=5, pady=50)

    def open_add_skin_dialog(self):
        """Открыть окно для добавления нового скина"""
        add_window = tk.Toplevel(self.root)
        add_window.title("Добавить скин")
        add_window.geometry("520x520")
        add_window.configure(bg="#f0f0f0")
        add_window.transient(self.root)
        add_window.grab_set()

        form_frame = tk.Frame(add_window, bg="#f0f0f0")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        form_frame.grid_columnconfigure(1, weight=1)

        def create_field(label_text, row, width=40):
            tk.Label(
                form_frame,
                text=label_text,
                font=("Arial", 12),
                bg="#f0f0f0",
                anchor="w"
            ).grid(row=row, column=0, sticky="w", pady=8)
            entry = tk.Entry(form_frame, font=("Arial", 12), width=width)
            entry.grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=8)
            return entry

        name_entry = create_field("Имя:", 0)

        tk.Label(
            form_frame,
            text="Редкость:",
            font=("Arial", 12),
            bg="#f0f0f0",
            anchor="w"
        ).grid(row=1, column=0, sticky="w", pady=8)
        rarity_var = tk.StringVar(value="common")
        rarity_menu = tk.OptionMenu(
            form_frame,
            rarity_var,
            "common",
            "uncommon",
            "rare",
            "epic",
            "Legendary",
            "arcane"
        )
        rarity_menu.config(font=("Arial", 12), width=35)
        rarity_menu.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=8)

        url_entry = create_field("Ссылка на фотку:", 2)
        min_buy_price_entry = create_field("Мин. цена покупки:", 3)
        max_buy_price_entry = create_field("Макс. цена покупки:", 4)
        sell_price_entry = create_field("Цена продажи:", 5)
        wait_entry = create_field("Ожидание скупки:", 6)
        global_price_entry = create_field("Глобальная продажа:", 7)

        def save_new_skin():
            name = name_entry.get().strip()
            rarity = rarity_var.get().strip()
            url = url_entry.get().strip()
            min_buy_price = min_buy_price_entry.get().strip()
            max_buy_price = max_buy_price_entry.get().strip()
            sell_price = sell_price_entry.get().strip()
            wait_time = wait_entry.get().strip()
            global_price = global_price_entry.get().strip()

            if not name:
                messagebox.showerror("Ошибка", "Введите имя скина")
                return

            try:
                min_buy_price_value = Decimal(min_buy_price)
                max_buy_price_value = Decimal(max_buy_price)
                sell_price_value = Decimal(sell_price)
                global_price_value = float(global_price)
                wait_value = float(wait_time)
            except ValueError:
                messagebox.showerror("Ошибка", "Цены и ожидание должны быть числами")
                return

            insert_with_rarity = self.db.execute_query(
                """INSERT INTO skins (name, url, buy_price , min_buy, max_buy, sell_price, sell_global_price, interval_minutes, rarity)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                params=(name, url, min_buy_price_value ,min_buy_price_value , max_buy_price_value , sell_price_value, global_price_value, wait_value, rarity)
            )

            messagebox.showinfo("Готово", "Скин добавлен")
            add_window.destroy()
            self.create_interfaces_skin()

        button_frame = tk.Frame(add_window, bg="#f0f0f0")
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="Сохранить",
            command=save_new_skin,
            bg="#2ecc71",
            fg="white",
            font=("Arial", 11),
            cursor="hand2",
            width=14
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            button_frame,
            text="Отмена",
            command=add_window.destroy,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 11),
            cursor="hand2",
            width=14
        ).pack(side=tk.LEFT, padx=10)

    def on_search_enter(self, event):
        """Обработчик нажатия Enter в поле поиска"""
        search_text = self.search_entry.get()
        print(f"Поиск: {search_text}")
        self.create_interfaces_skin(search_text)

    def on_search_button(self):
        """Обработчик нажатия на кнопку поиска"""
        search_text = self.search_entry.get()
        print(f"Поиск (кнопка): {search_text}")
        self.create_interfaces_skin(search_text)

    def show_all_skins(self):
        """Показать все скины"""
        print("Показываем все скины")

        for widget in self.cards_container.winfo_children():
            if widget not in (self.search_frame, getattr(self, 'add_skin_button_frame', None)):
                widget.destroy()

        self.search_entry.delete(0, tk.END)
        self.cards_in_row = 10

        skins = self.db.execute_query("SELECT id, name, url, min_buy, max_buy, buy_price, sell_price, sell_global_price, interval_minutes FROM skins LIMIT 30", fetch_all=True)

        for skin in skins:
            row = self.cards_in_row // 5
            col = self.cards_in_row % 5
            image_path = rf".\img\skins\{skin['url']}.png"

            ProductCardGrid(
                parent=self.cards_container,
                app=self,
                id_skin=skin['id'],
                name=skin['name'],
                min_buy=skin['min_buy'],
                max_buy=skin['max_buy'],
                current_buy=skin['buy_price'],
                price_sell=skin['sell_price'],
                price_global_sell=skin['sell_global_price'],
                time_out=skin['interval_minutes'],
                image_path=image_path,
                row=row,
                col=col
            )
            self.cards_in_row += 1

    def on_mousewheel(self, event):
        """Прокрутка колесиком мыши"""
        if self.canvas:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
