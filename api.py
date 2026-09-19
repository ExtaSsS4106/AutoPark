import requests


class APIError(Exception):
    def __init__(self, status_code: int, data):
        self.status_code = status_code
        self.data = data
        super().__init__(f"HTTP {status_code}: {data}")


class AutoParkAPI:
    """
    Клиент для AutoPark.
    Маршруты соответствуют urls.py без изменений:

        ''                      ErrorResponse
        /api/profile-info/      ProfileInfo
        /api/amisuperuser/      AmIsuperUser
        /api/register/          RegisterView
        /api/profile/           ProfileView
        /api/logout/            LogoutView
        /api/all-users/         AllUsers
        /api/SellCar/           SellCar
        /api/AcceptCar/         AcceptCar
        /api/GetCars/           GetCars
    """

    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip("/")
        self.access_token = None
        self.refresh_token = None
        self.session = requests.Session()

    # ---------- internal ----------
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

    # ---------- token ----------
    def set_token(self, access_token: str, refresh_token: str = None):
        """Установить токен вручную (если логин делается вне этого клиента)."""
        self.access_token = access_token
        self.refresh_token = refresh_token

    # ---------- REGISTER ----------
    def register(self, username, password, password2=None, email="",
                 first_name="", last_name=""):
        """POST /api/register/"""
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
        """GET /api/profile/"""
        return self._handle(self.session.get(
            self._url("/api/profile/"),
            headers=self._headers(),
        ))

    def update_profile(self, **fields):
        """PUT /api/profile/"""
        return self._handle(self.session.put(
            self._url("/api/profile/"),
            headers=self._headers(),
            json=fields,
        ))

    # ---------- PROFILE INFO ----------
    def get_profile_info(self):
        """
        GET /api/profile-info/
        Внимание: во views.py сигнатура get(self, request, user_id),
        но в urls.py нет <user_id> — сервер вернёт 500.
        Метод оставлен для совместимости с маршрутом.
        """
        return self._handle(self.session.get(
            self._url("/api/profile-info/"),
            headers=self._headers(),
        ))

    # ---------- AM I SUPERUSER ----------
    def am_i_superuser(self) -> bool:
        """GET /api/amisuperuser/"""
        data = self._handle(self.session.get(
            self._url("/api/amisuperuser/"),
            headers=self._headers(),
        ))
        return data.get("status_admin", False)

    # ---------- LOGOUT ----------
    def logout(self, refresh_token: str = None):
        """POST /api/logout/"""
        token = refresh_token or self.refresh_token
        result = self._handle(self.session.post(
            self._url("/api/logout/"),
            headers=self._headers(),
            json={"refresh_token": token},
        ))
        self.access_token = None
        self.refresh_token = None
        return result

    # ---------- USERS ----------
    def get_users(self):
        """GET /api/all-users/"""
        return self._handle(self.session.get(
            self._url("/api/all-users/"),
            headers=self._headers(),
        ))

    def search_users(self, query: str):
        """POST /api/all-users/"""
        return self._handle(self.session.post(
            self._url("/api/all-users/"),
            headers=self._headers(),
            json={"query": query},
        ))

    # ---------- CARS ----------
    def get_cars(self):
        """GET /api/GetCars/"""
        return self._handle(self.session.get(
            self._url("/api/GetCars/"),
            headers=self._headers(),
        ))

    def search_cars(self, query: str):
        """POST /api/GetCars/"""
        return self._handle(self.session.post(
            self._url("/api/GetCars/"),
            headers=self._headers(),
            json={"query": query},
        ))

    def accept_car(self, vin, model, year, color, price):
        """POST /api/AcceptCar/"""
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