"""
Единый файл: API-клиент + GUI автосалона с авторизацией.
Запуск: python app.py
"""

import customtkinter as ctk
from tkinter import messagebox
import requests

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ============================================================
#                    API КЛИЕНТ
# ============================================================
class APIError(Exception):
    def __init__(self, status_code: int, data):
        self.status_code = status_code
        self.data = data
        super().__init__(f"HTTP {status_code}: {data}")


class AutoParkAPI:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip("/")
        self.access_token = None
        self.refresh_token = None
        self.session = requests.Session()

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def _headers(self, auth: bool = True) -> dict:
        h = {"Content-Type": "application/json"}
        if auth and self.access_token:
            h["Authorization"] = f"Bearer {self.access_token}"
        return h

    def _handle(self, response: requests.Response):
        try:
            data = response.json()
        except ValueError:
            data = {"raw": response.text}
        if response.status_code >= 400:
            raise APIError(response.status_code, data)
        return data

    # ---------- AUTH ----------
    def login(self, username: str, password: str):
        data = self._handle(self.session.post(
            self._url("/api/login/"),
            json={"username": username, "password": password},
        ))
        self.access_token  = data.get("access")
        self.refresh_token = data.get("refresh")
        return data

    def refresh_access(self):
        data = self._handle(self.session.post(
            self._url("/api/token/refresh/"),
            json={"refresh": self.refresh_token},
        ))
        self.access_token = data.get("access")
        return data

    def logout(self, refresh_token: str = None):
        token = refresh_token or self.refresh_token
        try:
            result = self._handle(self.session.post(
                self._url("/api/logout/"),
                headers=self._headers(),
                json={"refresh_token": token},
            ))
        finally:
            self.access_token = None
            self.refresh_token = None
        return result

    def set_token(self, access_token: str, refresh_token: str = None):
        self.access_token = access_token
        self.refresh_token = refresh_token

    # ---------- REGISTER ----------
    def register(self, username, password, password2=None, email="",
                 first_name="", last_name=""):
        return self._handle(self.session.post(
            self._url("/api/register/"),
            json={
                "username":   username,
                "password":   password,
                "password2":  password2 or password,
                "email":      email,
                "first_name": first_name,
                "last_name":  last_name,
            },
        ))

    # ---------- PROFILE ----------
    def get_profile(self):
        return self._handle(self.session.get(
            self._url("/api/profile/"),
            headers=self._headers(),
        ))

    def update_profile(self, **fields):
        return self._handle(self.session.put(
            self._url("/api/profile/"),
            headers=self._headers(),
            json=fields,
        ))

    def am_i_superuser(self) -> bool:
        data = self._handle(self.session.get(
            self._url("/api/amisuperuser/"),
            headers=self._headers(),
        ))
        return data.get("status_admin", False)

    # ---------- USERS ----------
    def get_users(self):
        return self._handle(self.session.get(
            self._url("/api/all-users/"),
            headers=self._headers(),
        ))

    def search_users(self, query: str):
        return self._handle(self.session.post(
            self._url("/api/all-users/"),
            headers=self._headers(),
            json={"query": query},
        ))

    # ---------- CARS ----------
    def get_cars(self):
        return self._handle(self.session.get(
            self._url("/api/GetCars/"),
            headers=self._headers(),
        ))

    def search_cars(self, query: str):
        return self._handle(self.session.post(
            self._url("/api/GetCars/"),
            headers=self._headers(),
            json={"query": query},
        ))

    def accept_car(self, vin, model, year, color, price):
        """POST /api/AcceptCar/ — без make"""
        return self._handle(self.session.post(
            self._url("/api/AcceptCar/"),
            headers=self._headers(),
            json={
                "vin":   vin,
                "model": model,
                "year":  year,
                "color": color,
                "price": str(price),
            },
        ))

    def sell_car(self, car_id: int):
        """POST /api/SellCar/"""
        return self._handle(self.session.post(
            self._url("/api/SellCar/"),
            headers=self._headers(),
            json={"car_id": car_id},
        ))


# ============================================================
#                       GUI
# ============================================================
class App(ctk.CTk):
    def __init__(self, server_url: str = "http://127.0.0.1:8000"):
        super().__init__()

        self.title("Автосалон")
        self.geometry("1280x800")
        self.minsize(1050, 680)

        self.api = AutoParkAPI(server_url)
        self.server_url = server_url
        self.current_user = None
        self.active_page = "home"
        self.nav = {}

        self.accept_entries = {}
        self.selected_car_id = None
        self.selected_car = None

        self.show_login()

    # ---------------------------------------------------------
    #                    LOGIN
    # ---------------------------------------------------------
    def show_login(self):
        for w in self.winfo_children():
            w.destroy()
        self.configure(fg_color=("#f2f2f2", "#1a1a1a"))

        card = ctk.CTkFrame(self, corner_radius=14, width=400, height=470)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        ctk.CTkLabel(
            card, text="Автосалон",
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack(pady=(36, 4))

        ctk.CTkLabel(
            card, text="Вход в систему",
            text_color="gray60"
        ).pack(pady=(0, 28))

        self.login_username = ctk.CTkEntry(
            card, height=40, placeholder_text="Имя пользователя"
        )
        self.login_username.pack(fill="x", padx=32, pady=6)

        self.login_password = ctk.CTkEntry(
            card, height=40, placeholder_text="Пароль", show="•"
        )
        self.login_password.pack(fill="x", padx=32, pady=6)
        self.login_password.bind("<Return>", lambda e: self.do_login())

        self.login_error = ctk.CTkLabel(
            card, text="", text_color="#e74c3c", wraplength=340
        )
        self.login_error.pack(pady=(8, 0))

        self.login_btn = ctk.CTkButton(
            card, text="Войти", height=42, command=self.do_login
        )
        self.login_btn.pack(fill="x", padx=32, pady=(14, 8))

        ctk.CTkLabel(
            card, text=f"Сервер: {self.server_url}",
            text_color="gray50", font=ctk.CTkFont(size=11)
        ).pack(pady=(20, 20))

        self.login_username.focus()

    def do_login(self):
        username = self.login_username.get().strip()
        password = self.login_password.get()

        if not username or not password:
            self.login_error.configure(text="Введите логин и пароль")
            return

        self.login_btn.configure(state="disabled", text="Вход...")
        self.login_error.configure(text="")
        self.update_idletasks()

        try:
            self.api.login(username, password)
        except APIError as e:
            if e.status_code == 404:
                msg = "Эндпоинт /api/login/ не найден.\nДобавьте TokenObtainPairView в urls.py."
            elif e.status_code == 401:
                msg = "Неверный логин или пароль"
            else:
                msg = f"Ошибка {e.status_code}: {e.data}"
            self.login_error.configure(text=msg)
            self.login_btn.configure(state="normal", text="Войти")
            return
        except requests.exceptions.ConnectionError:
            self.login_error.configure(text="Сервер недоступен")
            self.login_btn.configure(state="normal", text="Войти")
            return

        self.current_user = {"username": username, "is_admin": False, "profile": {}}
        try:
            self.current_user["is_admin"] = self.api.am_i_superuser()
        except Exception:
            pass
        try:
            self.current_user["profile"] = self.api.get_profile()
        except Exception:
            pass

        self.show_main()

    # ---------------------------------------------------------
    #                    MAIN
    # ---------------------------------------------------------
    def show_main(self):
        for w in self.winfo_children():
            w.destroy()
        self.configure(fg_color=("#ebebeb", "#242424"))

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_content()
        self.show_home()

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        ctk.CTkLabel(
            self.sidebar, text="Автосалон",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(anchor="w", padx=24, pady=(30, 4))

        name = self.current_user.get("username", "—")
        role = "Администратор" if self.current_user.get("is_admin") else "Менеджер"
        ctk.CTkLabel(
            self.sidebar,
            text=f"{name}\n{role}",
            justify="left",
            text_color="gray60",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=24, pady=(0, 20))

        self.nav = {}
        for key, title in (
            ("home",   "Главная"),
            ("accept", "Приёмка авто"),
            ("sale",   "Продажа авто"),
        ):
            button = ctk.CTkButton(
                self.sidebar, text=title, anchor="w", height=42, corner_radius=8,
                fg_color="transparent", hover_color=("gray75", "gray25"),
                command=lambda page=key: self.navigate(page)
            )
            button.pack(fill="x", padx=14, pady=4)
            self.nav[key] = button

        ctk.CTkFrame(
            self.sidebar, height=1, fg_color=("gray80", "gray25")
        ).pack(fill="x", padx=20, pady=20)

        ctk.CTkButton(
            self.sidebar, text="Выйти", anchor="w", height=38,
            fg_color="transparent",
            hover_color=("#c0392b", "#922b21"),
            text_color=("#c0392b", "#e74c3c"),
            command=self.do_logout
        ).pack(side="bottom", fill="x", padx=14, pady=(0, 20))

    def do_logout(self):
        try:
            self.api.logout()
        except Exception:
            pass
        self.current_user = None
        self.show_login()

    def _build_content(self):
        self.content = ctk.CTkFrame(
            self, corner_radius=0, fg_color=("gray95", "#202020")
        )
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(1, weight=1)

    def navigate(self, page):
        self.active_page = page
        if page == "home":
            self.show_home()
        elif page == "accept":
            self.show_accept()
        elif page == "sale":
            self.show_sale()

    def clear(self):
        for widget in self.content.winfo_children():
            widget.destroy()
        for key, button in self.nav.items():
            button.configure(
                fg_color="#1f6aa5" if key == self.active_page else "transparent"
            )

    # ---------------------------------------------------------
    #                    HELPERS
    # ---------------------------------------------------------
    def page_header(self, title, subtitle):
        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(26, 14))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header, text=title,
            font=ctk.CTkFont(size=27, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header, text=subtitle, text_color="gray60"
        ).grid(row=1, column=0, sticky="w", pady=(3, 0))

    def section(self, parent, title):
        frame = ctk.CTkFrame(parent, corner_radius=10)
        ctk.CTkLabel(
            frame, text=title,
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=18, pady=(16, 12))
        return frame

    def input_field(self, parent, label, placeholder="", key=None, store=None):
        block = ctk.CTkFrame(parent, fg_color="transparent")
        ctk.CTkLabel(block, text=label, text_color="gray60").pack(anchor="w", pady=(0, 5))
        entry = ctk.CTkEntry(block, height=38, placeholder_text=placeholder)
        entry.pack(fill="x")
        if store is not None and key:
            store[key] = entry
        return block

    # ---------------------------------------------------------
    #                    HOME
    # ---------------------------------------------------------
    def show_home(self):
        self.active_page = "home"
        self.clear()
        self.page_header("Главная", "Автомобили и сотрудники салона")

        body = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=25, pady=(0, 20))
        body.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.stat_values = {}
        for i, (key, title) in enumerate((
            ("in_stock", "В наличии"),
            ("total",    "Всего в базе"),
            ("sold",     "Продано"),
            ("users",    "Сотрудников"),
        )):
            card = ctk.CTkFrame(body, corner_radius=10)
            card.grid(row=0, column=i, sticky="ew", padx=5, pady=5)

            ctk.CTkLabel(card, text=title, text_color="gray60").pack(
                anchor="w", padx=18, pady=(16, 4)
            )
            value = ctk.CTkLabel(
                card, text="—", font=ctk.CTkFont(size=28, weight="bold")
            )
            value.pack(anchor="w", padx=18, pady=(0, 16))
            self.stat_values[key] = value

        tabs = ctk.CTkTabview(body)
        tabs.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=5, pady=(20, 5))

        tab_cars = tabs.add("Автомобили")
        tab_users = tabs.add("Сотрудники")

        self.build_cars_tab(tab_cars)
        self.build_users_tab(tab_users)

        self.refresh_home_data()

    def refresh_home_data(self):
        try:
            cars = self.api.get_cars()
        except Exception as e:
            print("cars error:", e)
            cars = []
            self._show_table_message("Не удалось загрузить автомобили")
        else:
            self.render_cars(cars)

        total = len(cars)
        sold = sum(1 for c in cars if c.get("status") == "sold")
        in_stock = total - sold

        self.stat_values["total"].configure(text=str(total))
        self.stat_values["sold"].configure(text=str(sold))
        self.stat_values["in_stock"].configure(text=str(in_stock))

        try:
            users = self.api.get_users()
        except Exception:
            users = []
        self.render_users(users)
        self.stat_values["users"].configure(text=str(len(users)))

    def _show_table_message(self, text, color="gray55"):
        for w in self.cars_table.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self.cars_table, text=text, text_color=color
        ).grid(row=0, column=0, columnspan=7, pady=60)

    def build_cars_tab(self, parent):
        toolbar = ctk.CTkFrame(parent, fg_color="transparent")
        toolbar.pack(fill="x", padx=10, pady=10)

        self.cars_search_entry = ctk.CTkEntry(
            toolbar, height=38, placeholder_text="Поиск по VIN, модели, цвету"
        )
        self.cars_search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.cars_search_entry.bind("<Return>", lambda e: self.do_search_cars())

        ctk.CTkButton(
            toolbar, text="Найти", width=100, height=38,
            command=self.do_search_cars
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            toolbar, text="Сбросить", width=110, height=38,
            fg_color="transparent", border_width=1,
            command=self.refresh_home_data
        ).pack(side="left")

        self.cars_table = ctk.CTkFrame(parent, corner_radius=8)
        self.cars_table.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def do_search_cars(self):
        query = self.cars_search_entry.get().strip()
        if not query:
            self.refresh_home_data()
            return
        try:
            cars = self.api.search_cars(query)
        except APIError as e:
            if e.status_code == 404:
                cars = []
            else:
                messagebox.showerror("Ошибка", str(e))
                return
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            return
        self.render_cars(cars)

    def render_cars(self, cars):
        for w in self.cars_table.winfo_children():
            w.destroy()

        # Без колонки «Марка»
        columns = ["ID", "VIN", "Модель", "Год", "Цвет", "Цена", "Статус"]
        for i in range(len(columns)):
            self.cars_table.grid_columnconfigure(i, weight=1)

        for i, title in enumerate(columns):
            ctk.CTkLabel(
                self.cars_table, text=title, text_color="gray60",
                font=ctk.CTkFont(size=12, weight="bold")
            ).grid(row=0, column=i, sticky="w", padx=10, pady=12)

        if not cars:
            ctk.CTkLabel(
                self.cars_table, text="Нет данных", text_color="gray55"
            ).grid(row=1, column=0, columnspan=len(columns), pady=60)
            return

        for r, car in enumerate(cars, start=1):
            status = car.get("status", "in_stock")
            status_ru = {"in_stock": "В наличии", "sold": "Продан"}.get(status, status)

            values = [
                car.get("car_id", ""),
                car.get("vin", ""),
                car.get("model", ""),
                car.get("year", ""),
                car.get("color", ""),
                car.get("price", ""),
                status_ru,
            ]
            for c, v in enumerate(values):
                text_color = ("gray90", "gray80")
                if c == len(values) - 1:
                    text_color = "#27ae60" if status == "in_stock" else "#e74c3c"
                ctk.CTkLabel(
                    self.cars_table, text=str(v), text_color=text_color
                ).grid(row=r, column=c, sticky="w", padx=10, pady=6)

    def build_users_tab(self, parent):
        self.users_scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        self.users_scroll.pack(fill="both", expand=True, padx=10, pady=10)

    def render_users(self, users):
        for w in self.users_scroll.winfo_children():
            w.destroy()

        self.users_scroll.grid_columnconfigure((0, 1, 2), weight=1)

        if not users:
            ctk.CTkLabel(
                self.users_scroll, text="Нет данных", text_color="gray55"
            ).grid(row=0, column=0, columnspan=3, pady=60)
            return

        for i, u in enumerate(users):
            card = ctk.CTkFrame(self.users_scroll, corner_radius=10)
            card.grid(row=i // 3, column=i % 3, sticky="nsew", padx=5, pady=5)

            name = u.get("username", "—")
            ctk.CTkLabel(
                card, text=name[0].upper() if name else "—",
                width=50, height=50, corner_radius=25,
                fg_color=("gray80", "#343434"),
                font=ctk.CTkFont(size=18, weight="bold")
            ).pack(anchor="w", padx=15, pady=(15, 8))

            ctk.CTkLabel(
                card, text=name, font=ctk.CTkFont(weight="bold")
            ).pack(anchor="w", padx=15)

            ctk.CTkLabel(
                card, text=f"user_id: {u.get('user_id', '—')}",
                text_color="gray60"
            ).pack(anchor="w", padx=15, pady=(3, 0))

            ctk.CTkLabel(
                card, text=f"profile_id: {u.get('profile_id', '—')}"
            ).pack(anchor="w", padx=15, pady=(8, 15))

    # ---------------------------------------------------------
    #                    ACCEPT
    # ---------------------------------------------------------
    def show_accept(self):
        self.active_page = "accept"
        self.clear()
        self.page_header("Приёмка авто", "Внесите данные автомобиля")

        self.accept_entries = {}

        body = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=25, pady=(0, 20))
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=1)

        car = self.section(body, "Автомобиль")
        car.grid(row=0, column=0, sticky="ew", padx=6, pady=6)

        car_grid = ctk.CTkFrame(car, fg_color="transparent")
        car_grid.pack(fill="x", padx=10, pady=(0, 12))
        car_grid.grid_columnconfigure((0, 1, 2), weight=1)

        fields = [
            ("vin",   "VIN",         "VIN автомобиля"),
            ("model", "Модель",      "Модель"),
            ("year",  "Год выпуска", "Год"),
            ("color", "Цвет",        "Цвет"),
            ("price", "Цена, ₽",     "0"),
        ]
        for i, (key, label, ph) in enumerate(fields):
            block = self.input_field(car_grid, label, ph, key=key, store=self.accept_entries)
            block.grid(row=i // 3, column=i % 3, sticky="ew", padx=6, pady=7)

        form = self.section(body, "Оформление")
        form.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=6, pady=6)

        ctk.CTkLabel(
            form,
            text="Поля VIN, модель и цена\nобязательны.",
            justify="left", text_color="gray60"
        ).pack(anchor="w", padx=15, pady=(0, 12))

        ctk.CTkButton(
            form, text="Принять авто", height=42,
            command=self.do_accept_car
        ).pack(fill="x", padx=15, pady=(10, 7))

        ctk.CTkButton(
            form, text="Очистить форму", height=38,
            fg_color="transparent", border_width=1,
            command=self.show_accept
        ).pack(fill="x", padx=15, pady=7)

    def do_accept_car(self):
        vin   = self.accept_entries["vin"].get().strip()
        model = self.accept_entries["model"].get().strip()
        year  = self.accept_entries["year"].get().strip()
        color = self.accept_entries["color"].get().strip()
        price = self.accept_entries["price"].get().strip()

        if not (vin and model and price):
            messagebox.showwarning(
                "Проверьте форму",
                "VIN, модель и цена обязательны"
            )
            return

        try:
            self.api.accept_car(
                vin=vin, model=model,
                year=year, color=color, price=price,
            )
        except APIError as e:
            if e.status_code == 400 and "already exists" in str(e.data):
                messagebox.showerror("Ошибка", "Авто с таким VIN уже есть в базе")
            else:
                messagebox.showerror("Ошибка", f"{e.status_code}: {e.data}")
            return
        except Exception as e:
            messagebox.showerror("Ошибка сети", str(e))
            return

        messagebox.showinfo("Успех", f"Авто {model} принято")
        self.navigate("home")

    # ---------------------------------------------------------
    #                    SALE
    # ---------------------------------------------------------
    def show_sale(self):
        self.active_page = "sale"
        self.clear()
        self.page_header("Продажа авто", "Выберите автомобиль и оформите продажу")

        self.selected_car_id = None
        self.selected_car = None

        body = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=25, pady=(0, 20))
        body.grid_columnconfigure(0, weight=2)
        body.grid_columnconfigure(1, weight=1)

        cars = self.section(body, "Автомобиль")
        cars.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        toolbar = ctk.CTkFrame(cars, fg_color="transparent")
        toolbar.pack(fill="x", padx=15, pady=(0, 10))

        self.sale_search_entry = ctk.CTkEntry(
            toolbar, placeholder_text="Поиск автомобиля или VIN", height=38
        )
        self.sale_search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.sale_search_entry.bind("<Return>", lambda e: self.do_search_sale_cars())

        ctk.CTkButton(
            toolbar, text="Найти", width=90, height=38,
            command=self.do_search_sale_cars
        ).pack(side="left")

        self.sale_list = ctk.CTkScrollableFrame(cars, corner_radius=8, height=380)
        self.sale_list.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        deal = self.section(body, "Оформление сделки")
        deal.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)

        ctk.CTkLabel(
            deal, text="Выбранный автомобиль", text_color="gray60"
        ).pack(anchor="w", padx=15, pady=(5, 3))

        self.selected_label = ctk.CTkLabel(
            deal, text="Автомобиль не выбран",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.selected_label.pack(anchor="w", padx=15)

        self.selected_price_label = ctk.CTkLabel(deal, text="", text_color="gray60")
        self.selected_price_label.pack(anchor="w", padx=15, pady=(3, 0))

        ctk.CTkFrame(
            deal, height=1, fg_color=("gray80", "gray35")
        ).pack(fill="x", padx=15, pady=18)

        ctk.CTkButton(
            deal, text="Оформить продажу", height=44,
            command=self.do_sell_car
        ).pack(fill="x", padx=15, pady=(10, 8))

        ctk.CTkButton(
            deal, text="Обновить список", height=38,
            fg_color="transparent", border_width=1,
            command=self.load_sale_cars
        ).pack(fill="x", padx=15, pady=7)

        self.load_sale_cars()

    def load_sale_cars(self):
        try:
            cars = self.api.get_cars()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            return
        cars = [c for c in cars if c.get("status", "in_stock") != "sold"]
        self.render_sale_cars(cars)

    def do_search_sale_cars(self):
        q = self.sale_search_entry.get().strip()
        if not q:
            self.load_sale_cars()
            return
        try:
            cars = self.api.search_cars(q)
        except APIError as e:
            if e.status_code == 404:
                cars = []
            else:
                messagebox.showerror("Ошибка", str(e))
                return
        cars = [c for c in cars if c.get("status", "in_stock") != "sold"]
        self.render_sale_cars(cars)

    def render_sale_cars(self, cars):
        for w in self.sale_list.winfo_children():
            w.destroy()

        self.sale_list.grid_columnconfigure(0, weight=1)

        if not cars:
            ctk.CTkLabel(
                self.sale_list, text="Нет доступных автомобилей",
                text_color="gray55"
            ).grid(row=0, column=0, pady=40)
            return

        for i, car in enumerate(cars):
            row = ctk.CTkFrame(self.sale_list, corner_radius=8)
            row.grid(row=i, column=0, sticky="ew", padx=5, pady=4)
            row.grid_columnconfigure(0, weight=1)

            model = car.get("model", "—")
            year = car.get("year", "")
            vin = car.get("vin", "")

            title = model
            subtitle = f"{year} · VIN {vin}" if year else f"VIN {vin}"

            ctk.CTkLabel(row, text=title, anchor="w").grid(
                row=0, column=0, sticky="w", padx=12, pady=(8, 2)
            )
            ctk.CTkLabel(
                row, text=subtitle, text_color="gray60",
                font=ctk.CTkFont(size=11)
            ).grid(row=1, column=0, sticky="w", padx=12, pady=(0, 0))

            ctk.CTkLabel(
                row, text=f'{car.get("price", "")} ₽',
                text_color="gray60"
            ).grid(row=2, column=0, sticky="w", padx=12, pady=(0, 8))

            ctk.CTkButton(
                row, text="Выбрать", width=90, height=30,
                command=lambda c=car: self.select_car(c)
            ).grid(row=0, column=1, rowspan=3, padx=12, pady=8)

    def select_car(self, car):
        self.selected_car = car
        self.selected_car_id = car.get("car_id")
        model = car.get("model", "—")
        year = car.get("year", "")
        self.selected_label.configure(text=f"{model} · {year}".strip(" ·"))
        self.selected_price_label.configure(
            text=f'VIN: {car.get("vin", "")}\nЦена: {car.get("price", "")} ₽'
        )

    def do_sell_car(self):
        if not self.selected_car_id:
            messagebox.showwarning("Внимание", "Сначала выберите автомобиль")
            return

        name = ""
        if self.selected_car:
            name = self.selected_car.get("model", "")

        if not messagebox.askyesno(
            "Подтверждение",
            f"Оформить продажу?\n\n{name}"
        ):
            return

        try:
            self.api.sell_car(self.selected_car_id)
        except APIError as e:
            messagebox.showerror("Ошибка", f"{e.status_code}: {e.data}")
            return
        except Exception as e:
            messagebox.showerror("Ошибка сети", str(e))
            return

        messagebox.showinfo("Успех", "Автомобиль продан")
        self.navigate("home")


if __name__ == "__main__":
    app = App("http://127.0.0.1:8000")
    app.mainloop()