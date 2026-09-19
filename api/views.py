from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, UserSerializer
from .models import *
from django.shortcuts import render, redirect, get_object_or_404
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Q
import json
from django.urls import reverse
import os
# Регистрация пользователя
class ErrorResponse(APIView):
    permission_classes = (permissions.AllowAny,)
    def get(self, request):
        return Response({"error": "Not found"}, status=404)
    
class RegisterView(generics.CreateAPIView):
    """
    POST /api/register/
    Content-Type: application/json

    {
        "username": "john",
        "password": "StrongPass123!",
        "password2": "StrongPass123!",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe"
    }
    """
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,) 
    serializer_class = RegisterSerializer
class AmIsuperUser(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        if user.is_superuser:
            status = True
        else:
            status = False
        return Response({"status_admin": status})
# Получение профиля текущего пользователя
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

class ProfileInfo(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, user_id):
        profile = get_object_or_404(profiles, user__id=user_id)
        response = {
            "user_id": profile.user.id,
            "profile_id": profile.id,
            "username": profile.user.username,
            "email": profile.user.email,
            "date_joined": profile.user.date_joined,
        }
        return Response(response)

# Логаут (добавляем refresh-токен в чёрный список)
class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
class AllUsers(APIView):
    permission_classes = (permissions.AllowAny,)
    def get(self, request):
        profiles_ = profiles.objects.all().order_by('-id')
        response = []
        for p in profiles_:
            response.append({
                                "profile_id": p.id,
                                "username": p.user.username,
                                "user_id": p.user.id,
                            })
        return Response(response)
    
    def post(self, request):
        data = json.loads(request.body)
        query = data.get('query')
        
        if query:
            profiles_ = profiles.objects.filter(user__username__icontains=query).order_by('-id')
        else:
            return Response({"error": "Not found"}, status=404)
        response = []
        for p in profiles_:
            response.append({
                                "profile_id": p.id,
                                "username": p.user.username,
                                "user_id": p.user.id,
                            })
        return Response(response)
    

