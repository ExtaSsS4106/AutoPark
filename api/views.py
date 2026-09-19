from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, UserSerializer
from .models import *
from django.shortcuts import get_object_or_404
from django.db.models import Q


# ---------- 404 ----------
class ErrorResponse(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        return Response({"error": "Not found"}, status=404)


# ---------- Регистрация ----------
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer


# ---------- Суперюзер? ----------
class AmIsuperUser(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        return Response({"status_admin": request.user.is_superuser})


# ---------- Мой профиль ----------
class ProfileView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------- Профиль по user_id ----------
class ProfileInfo(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, user_id):
        profile = get_object_or_404(Profile, user__id=user_id)
        return Response({
            "user_id":     profile.user.id,
            "profile_id":  profile.id,
            "username":    profile.user.username,
            "email":       profile.user.email,
            "date_joined": profile.user.date_joined,
        })


# ---------- Логаут ----------
class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# ---------- Все пользователи ----------
class AllUsers(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        return Response([
            {
                "profile_id": p.id,
                "username":   p.user.username,
                "user_id":    p.user.id,
            }
            for p in Profile.objects.all().order_by('-id')
        ])

    def post(self, request):
        query = request.data.get('query')
        if not query:
            return Response({"error": "Not found"}, status=404)

        profiles_ = Profile.objects.filter(
            user__username__icontains=query
        ).order_by('-id')

        return Response([
            {
                "profile_id": p.id,
                "username":   p.user.username,
                "user_id":    p.user.id,
            }
            for p in profiles_
        ])


# ---------- ПРИЁМКА ----------
class AcceptCar(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        vin   = request.data.get('vin')
        model = request.data.get('model')
        year  = request.data.get('year')
        color = request.data.get('color')
        price = request.data.get('price')

        if not all([vin, model, price]):
            return Response({"error": "Missing required fields"}, status=400)

        if Car.objects.filter(vin=vin).exists():
            return Response({"error": "Car with this VIN already exists"}, status=400)

        # year и color необязательны в модели — передаём как есть, может быть None
        car = Car.objects.create(
            vin=vin,
            model=model,
            year=year or None,
            color=color or '',
            price=price,
            status='in_stock',
        )

        Log.objects.create(
            car=car,
            action='accept',
            user=request.user,
        )

        return Response({"message": "Car accepted successfully"}, status=201)


# ---------- ПРОДАЖА ----------
class SellCar(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        car_id = request.data.get('car_id')

        if not car_id:
            return Response({"error": "Missing car_id"}, status=400)

        try:
            car = Car.objects.get(id=car_id)
        except Car.DoesNotExist:
            return Response({"error": "Car not found"}, status=404)

        if car.status == 'sold':
            return Response({"error": "Car is already sold"}, status=400)

        car.status = 'sold'
        car.save()

        Log.objects.create(
            car=car,
            action='sale',
            user=request.user,
        )

        return Response({"message": "Car sold successfully"}, status=200)


# ---------- СПИСОК АВТО ----------
class GetCars(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def _serialize(self, cars_):
        return [
            {
                "car_id": c.id,
                "vin":    c.vin,
                "model":  c.model,
                "year":   c.year,
                "color":  c.color,
                "price":  str(c.price),
                "status": c.status,
            }
            for c in cars_
        ]

    def get(self, request):
        return Response(self._serialize(Car.objects.all().order_by('-id')))

    def post(self, request):
        query = request.data.get('query')
        if not query:
            return Response({"error": "Not found"}, status=404)

        cars_ = Car.objects.filter(
            Q(vin__icontains=query)   |
            Q(model__icontains=query) |
            Q(year__icontains=query)  |
            Q(color__icontains=query) |
            Q(price__icontains=query)
        ).order_by('-id')

        return Response(self._serialize(cars_))