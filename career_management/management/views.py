from django.contrib.auth import authenticate
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from management.models import Admin, Employe, Formation, Evenement, Competence, formulaire
from management.serializers import (
    AdminSerializer, EmployeSerializer, FormationSerializer, 
    EvenementSerializer, CompetenceSerializer, formulaireSerializer
)

# ✅ Fonction pour créer un token JWT
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# ✅ API pour l'inscription
class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmployeSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(request.data["password"])  # Hachage du mot de passe
            user.save()

            # Génération du token JWT
            tokens = get_tokens_for_user(user)

            return Response({
                'user': EmployeSerializer(user).data,
                'tokens': tokens
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ✅ API pour la connexion
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = Employe.objects.filter(email=email).first()
        if user and user.check_password(password):
            tokens = get_tokens_for_user(user)
            return Response({
                'user': EmployeSerializer(user).data,
                'tokens': tokens
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Email ou mot de passe incorrect'}, status=status.HTTP_401_UNAUTHORIZED)

# ✅ API CRUD pour les modèles
class AdminViewSet(viewsets.ModelViewSet):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer

class EmployeViewSet(viewsets.ModelViewSet):
    queryset = Employe.objects.all()
    serializer_class = EmployeSerializer

class FormationViewSet(viewsets.ModelViewSet):
    queryset = Formation.objects.all()
    serializer_class = FormationSerializer

class EvenementViewSet(viewsets.ModelViewSet):
    queryset = Evenement.objects.all()
    serializer_class = EvenementSerializer

class CompetenceViewSet(viewsets.ModelViewSet):
    queryset = Competence.objects.all()
    serializer_class = CompetenceSerializer

class formulaireViewSet(viewsets.ModelViewSet):
    queryset = formulaire.objects.all()
    serializer_class = formulaireSerializer
