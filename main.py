import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Автосалон")
        self.geometry("1280x800")
        self.minsize(1050, 680)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.active_page = "home"
        self._build_sidebar()
        self._build_content()
        self.show_home()

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        ctk.CTkLabel(
            self.sidebar,
            text="Автосалон",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(anchor="w", padx=24, pady=(30, 36))

        self.nav = {}

        for key, title in (
            ("home", "Главная"),
            ("accept", "Приёмка авто"),
            ("sale", "Продажа авто"),
        ):
            button = ctk.CTkButton(
                self.sidebar,
                text=title,
                anchor="w",
                height=42,
                corner_radius=8,
                fg_color="transparent",
                hover_color=("gray75", "gray25"),
                command=lambda page=key: self.navigate(page)
            )
            button.pack(fill="x", padx=14, pady=4)
            self.nav[key] = button

        ctk.CTkFrame(
            self.sidebar,
            height=1,
            fg_color=("gray80", "gray25")
        ).pack(fill="x", padx=20, pady=24)

        ctk.CTkLabel(
            self.sidebar,
            text="Система управления\nавтосалоном",
            justify="left",
            text_color="gray60"
        ).pack(anchor="w", padx=24)

    def _build_content(self):
        self.content = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=("gray95", "#202020")
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

    def page_header(self, title, subtitle):
        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=30,
            pady=(26, 14)
        )
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text=title,
            font=ctk.CTkFont(size=27, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text=subtitle,
            text_color="gray60"
        ).grid(row=1, column=0, sticky="w", pady=(3, 0))

    def section(self, parent, title):
        frame = ctk.CTkFrame(parent, corner_radius=10)

        ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=18, pady=(16, 12))

        return frame

    def input_field(self, parent, label, placeholder=""):
        block = ctk.CTkFrame(parent, fg_color="transparent")

        ctk.CTkLabel(
            block,
            text=label,
            text_color="gray60"
        ).pack(anchor="w", pady=(0, 5))

        ctk.CTkEntry(
            block,
            height=38,
            placeholder_text=placeholder
        ).pack(fill="x")

        return block

    def show_home(self):
        self.active_page = "home"
        self.clear()
        self.page_header(
            "Главная",
            "Автомобили и сотрудники салона"
        )

        body = ctk.CTkScrollableFrame(
            self.content,
            fg_color="transparent"
        )
        body.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=25,
            pady=(0, 20)
        )
        body.grid_columnconfigure((0, 1, 2, 3), weight=1)

        for i, title in enumerate(
            ("В наличии", "На приёмке", "Продано", "Сотрудников на смене")
        ):
            card = ctk.CTkFrame(body, corner_radius=10)
            card.grid(
                row=0,
                column=i,
                sticky="ew",
                padx=5,
                pady=5
            )

            ctk.CTkLabel(
                card,
                text=title,
                text_color="gray60"
            ).pack(anchor="w", padx=18, pady=(16, 4))

            ctk.CTkLabel(
                card,
                text="—",
                font=ctk.CTkFont(size=28, weight="bold")
            ).pack(anchor="w", padx=18, pady=(0, 16))

        tabs = ctk.CTkTabview(body)
        tabs.grid(
            row=1,
            column=0,
            columnspan=4,
            sticky="nsew",
            padx=5,
            pady=(20, 5)
        )

        tabs.add("Автомобили")
        tabs.add("Сотрудники")

        self.build_empty_cars(tabs.tab("Автомобили"))
        self.build_empty_employees(tabs.tab("Сотрудники"))

    def build_empty_cars(self, parent):
        toolbar = ctk.CTkFrame(parent, fg_color="transparent")
        toolbar.pack(fill="x", padx=10, pady=10)

        ctk.CTkEntry(
            toolbar,
            height=38,
            placeholder_text="Поиск по марке, модели или VIN"
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkComboBox(
            toolbar,
            width=180,
            height=38,
            values=["Все статусы", "В наличии", "Забронирован", "На приёмке", "Продан"]
        ).pack(side="left")

        table = ctk.CTkFrame(parent, corner_radius=8)
        table.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        columns = [
            "Автомобиль",
            "Год",
            "Пробег",
            "Характеристики",
            "Цена",
            "Статус",
            ""
        ]

        for i, title in enumerate(columns):
            table.grid_columnconfigure(i, weight=1)

            ctk.CTkLabel(
                table,
                text=title,
                text_color="gray60",
                font=ctk.CTkFont(size=12, weight="bold")
            ).grid(
                row=0,
                column=i,
                sticky="w",
                padx=12,
                pady=14
            )

        ctk.CTkLabel(
            table,
            text="Нет данных",
            text_color="gray55"
        ).grid(
            row=1,
            column=0,
            columnspan=len(columns),
            pady=100
        )

    def build_empty_employees(self, parent):
        scroll = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent"
        )
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        scroll.grid_columnconfigure((0, 1, 2), weight=1)

        for i in range(6):
            card = ctk.CTkFrame(scroll, corner_radius=10)
            card.grid(
                row=i // 3,
                column=i % 3,
                sticky="nsew",
                padx=5,
                pady=5
            )

            ctk.CTkLabel(
                card,
                text="—",
                width=50,
                height=50,
                corner_radius=25,
                fg_color=("gray80", "#343434"),
                font=ctk.CTkFont(size=18, weight="bold")
            ).pack(anchor="w", padx=15, pady=(15, 8))

            ctk.CTkLabel(
                card,
                text="Имя сотрудника",
                font=ctk.CTkFont(weight="bold")
            ).pack(anchor="w", padx=15)

            ctk.CTkLabel(
                card,
                text="Должность",
                text_color="gray60"
            ).pack(anchor="w", padx=15, pady=(3, 0))

            ctk.CTkLabel(
                card,
                text="Телефон"
            ).pack(anchor="w", padx=15, pady=(8, 0))

            ctk.CTkLabel(
                card,
                text="● Статус",
                text_color="gray60"
            ).pack(anchor="w", padx=15, pady=(5, 15))

    def show_accept(self):
        self.active_page = "accept"
        self.clear()
        self.page_header(
            "Приёмка авто",
            "Внесите данные автомобиля и результаты осмотра"
        )

        body = ctk.CTkScrollableFrame(
            self.content,
            fg_color="transparent"
        )
        body.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=25,
            pady=(0, 20)
        )
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=1)

        car = self.section(body, "Автомобиль")
        car.grid(row=0, column=0, sticky="ew", padx=6, pady=6)
        car.grid_columnconfigure((0, 1, 2), weight=1)

        fields = [
            ("VIN", "VIN автомобиля"),
            ("Марка", "Марка"),
            ("Модель", "Модель"),
            ("Год выпуска", "Год"),
            ("Пробег, км", "Пробег"),
            ("Цвет", "Цвет"),
        ]

        for i, (label, placeholder) in enumerate(fields):
            block = self.input_field(car, label, placeholder)
            block.grid(
                row=1 + i // 3,
                column=i % 3,
                sticky="ew",
                padx=10,
                pady=7
            )

        for col, (label, values) in enumerate([
            ("Кузов", ["Седан", "Хэтчбек", "Лифтбек", "Универсал", "Кроссовер"]),
            ("Коробка передач", ["МКПП", "АКПП", "CVT", "Робот"]),
            ("Топливо", ["Бензин", "Дизель", "Гибрид", "Электро"]),
        ]):
            block = ctk.CTkFrame(car, fg_color="transparent")
            block.grid(row=3, column=col, sticky="ew", padx=10, pady=7)

            ctk.CTkLabel(
                block,
                text=label,
                text_color="gray60"
            ).pack(anchor="w", pady=(0, 5))

            ctk.CTkComboBox(
                block,
                values=values,
                height=38
            ).pack(fill="x")

        owner = self.section(body, "Прежний владелец")
        owner.grid(row=4, column=0, sticky="ew", padx=6, pady=6)
        owner.grid_columnconfigure((0, 1, 2), weight=1)

        for i, (label, placeholder) in enumerate([
            ("ФИО", "Фамилия Имя Отчество"),
            ("Телефон", "+7"),
        ]):
            block = self.input_field(owner, label, placeholder)
            block.grid(row=1, column=i, sticky="ew", padx=10, pady=7)

        source = ctk.CTkFrame(owner, fg_color="transparent")
        source.grid(row=1, column=2, sticky="ew", padx=10, pady=7)
        ctk.CTkLabel(source, text="Источник", text_color="gray60").pack(anchor="w", pady=(0, 5))
        ctk.CTkComboBox(
            source,
            values=["Выкуп у владельца", "Trade-in", "Комиссия"],
            height=38
        ).pack(fill="x")

        inspection = self.section(body, "Комплектность и осмотр")
        inspection.grid(row=5, column=0, sticky="ew", padx=6, pady=6)

        checks = [
            "ПТС / ЭПТС",
            "СТС",
            "Два комплекта ключей",
            "Сервисная книжка",
            "Запасное колесо",
            "Второй комплект резины",
        ]

        for i, text in enumerate(checks):
            ctk.CTkCheckBox(
                inspection,
                text=text
            ).grid(
                row=1 + i // 3,
                column=i % 3,
                sticky="w",
                padx=12,
                pady=8
            )

        ctk.CTkLabel(
            inspection,
            text="Замечания при осмотре",
            text_color="gray60"
        ).grid(
            row=3,
            column=0,
            columnspan=3,
            sticky="w",
            padx=12,
            pady=(14, 5)
        )

        ctk.CTkTextbox(
            inspection,
            height=100
        ).grid(
            row=4,
            column=0,
            columnspan=3,
            sticky="ew",
            padx=12,
            pady=(0, 12)
        )

        form = self.section(body, "Оформление")
        form.grid(
            row=0,
            column=1,
            rowspan=6,
            sticky="nsew",
            padx=6,
            pady=6
        )

        self.input_field(form, "Дата приёмки", "ДД.ММ.ГГГГ").pack(
            fill="x", padx=15, pady=7
        )

        employee = ctk.CTkFrame(form, fg_color="transparent")
        employee.pack(fill="x", padx=15, pady=7)
        ctk.CTkLabel(employee, text="Приёмщик", text_color="gray60").pack(anchor="w", pady=(0, 5))
        ctk.CTkComboBox(
            employee,
            values=["Выберите сотрудника"],
            height=38
        ).pack(fill="x")

        self.input_field(form, "Цена выкупа, ₽", "0").pack(
            fill="x", padx=15, pady=7
        )
        self.input_field(form, "Цена в продаже, ₽", "0").pack(
            fill="x", padx=15, pady=7
        )

        ctk.CTkLabel(
            form,
            text="Ожидаемая маржа\n—",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=18)

        ctk.CTkCheckBox(
            form,
            text="Сразу выставить в продажу"
        ).pack(anchor="w", padx=15, pady=8)

        ctk.CTkButton(
            form,
            text="Принять авто",
            height=42
        ).pack(fill="x", padx=15, pady=(28, 7))

        ctk.CTkButton(
            form,
            text="Очистить форму",
            height=38,
            fg_color="transparent",
            border_width=1
        ).pack(fill="x", padx=15, pady=7)

    def show_sale(self):
        self.active_page = "sale"
        self.clear()
        self.page_header(
            "Продажа авто",
            "Выберите автомобиль и оформите продажу"
        )

        body = ctk.CTkScrollableFrame(
            self.content,
            fg_color="transparent"
        )
        body.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=25,
            pady=(0, 20)
        )
        body.grid_columnconfigure(0, weight=2)
        body.grid_columnconfigure(1, weight=1)

        cars = self.section(body, "Автомобиль")
        cars.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        toolbar = ctk.CTkFrame(cars, fg_color="transparent")
        toolbar.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkEntry(
            toolbar,
            placeholder_text="Поиск автомобиля или VIN",
            height=38
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkComboBox(
            toolbar,
            values=["Все", "В наличии", "Забронированные"],
            width=170,
            height=38
        ).pack(side="left")

        list_frame = ctk.CTkFrame(cars, corner_radius=8)
        list_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        headers = ["Автомобиль", "Год", "Цена", "Статус", ""]
        for i, text in enumerate(headers):
            list_frame.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(
                list_frame,
                text=text,
                text_color="gray60",
                font=ctk.CTkFont(size=12, weight="bold")
            ).grid(row=0, column=i, sticky="w", padx=10, pady=12)

        ctk.CTkLabel(
            list_frame,
            text="Нет доступных автомобилей",
            text_color="gray55"
        ).grid(row=1, column=0, columnspan=5, pady=100)

        buyer = self.section(body, "Покупатель")
        buyer.grid(row=1, column=0, sticky="ew", padx=6, pady=6)
        buyer.grid_columnconfigure((0, 1), weight=1)

        for i, (label, placeholder) in enumerate([
            ("ФИО покупателя", "Фамилия Имя Отчество"),
            ("Телефон", "+7"),
            ("Паспорт", "Серия и номер"),
            ("Дата продажи", "ДД.ММ.ГГГГ"),
        ]):
            block = self.input_field(buyer, label, placeholder)
            block.grid(
                row=1 + i // 2,
                column=i % 2,
                sticky="ew",
                padx=10,
                pady=7
            )

        deal = self.section(body, "Оформление сделки")
        deal.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=6, pady=6)

        ctk.CTkLabel(
            deal,
            text="Выбранный автомобиль",
            text_color="gray60"
        ).pack(anchor="w", padx=15, pady=(5, 3))

        ctk.CTkLabel(
            deal,
            text="Автомобиль не выбран",
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(anchor="w", padx=15)

        ctk.CTkFrame(
            deal,
            height=1,
            fg_color=("gray80", "gray35")
        ).pack(fill="x", padx=15, pady=18)

        for title in ("Цена автомобиля", "Скидка", "Итого"):
            row = ctk.CTkFrame(deal, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=6)
            row.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(row, text=title).grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(
                row,
                text="—",
                font=ctk.CTkFont(weight="bold")
            ).grid(row=0, column=1, sticky="e")

        ctk.CTkButton(
            deal,
            text="Оформить продажу",
            height=44
        ).pack(fill="x", padx=15, pady=(35, 8))

        ctk.CTkButton(
            deal,
            text="Очистить",
            height=38,
            fg_color="transparent",
            border_width=1
        ).pack(fill="x", padx=15, pady=7)


if __name__ == "__main__":
    app = App()
    app.mainloop()