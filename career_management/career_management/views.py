from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from management.models import Employe
from management.serializers import EmployeSerializer
from django.shortcuts import render
from django.http import HttpResponse


# Page d'accueil
def home(request):
    return HttpResponse("Bienvenue sur l'application de gestion de carrière")

# Vue d'inscription
class SignupView(APIView):
    def post(self, request):
        data = request.data
        data["password"] = make_password(data["password"])  # Hasher le mot de passe
        serializer = EmployeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Utilisateur créé avec succès"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Vue de connexion
class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return Response({"message": "Connexion réussie"}, status=status.HTTP_200_OK)
        return Response({"error": "Email ou mot de passe incorrect"}, status=status.HTTP_401_UNAUTHORIZED)
