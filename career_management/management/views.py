from django.shortcuts import render
from rest_framework import viewsets, status
from django.contrib.auth import authenticate
import logging
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from management.models import Employe
from management.serializers import EmployeSerializer
from django.http import HttpResponse
from .models import Admin, Employe, Formation, Evenement, Competence, formulaire,CustomUser
from .serializers import AdminSerializer, EmployeSerializer, FormationSerializer, EvenementSerializer, CompetenceSerializer,  formulaireSerializer,CustomUserSerializer,NotificationSerializer
from django.http import HttpResponse
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from datetime import datetime


User = get_user_model()

logger = logging.getLogger(__name__)

def home(request):
    return JsonResponse({"message": "Bienvenue sur l'API Career Management!"})

class AdminViewSet(viewsets.ModelViewSet):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer







class EmployeViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]


    queryset = Employe.objects.all()
    serializer_class = EmployeSerializer
    def update(self, request, *args, **kwargs):
        # Récupérer l'employé par ID
        try:
            employe = Employe.objects.get(id=kwargs['pk'])  # Utilisation de kwargs['pk'] pour accéder à l'ID
        except Employe.DoesNotExist:
            return Response({"error": "Employé non trouvé"}, status=status.HTTP_404_NOT_FOUND)

        # Sérialiser les données envoyées dans la requête
        serializer = self.get_serializer(employe, data=request.data, partial=True)  # partial=True pour la mise à jour partielle
        if serializer.is_valid():
            serializer.save()

            # Si des informations utilisateur sont envoyées dans la requête
            if 'user' in request.data:
                user_data = request.data['user']
                if 'first_name' in user_data:
                    employe.user.first_name = user_data['first_name']
                if 'last_name' in user_data:
                    employe.user.last_name = user_data['last_name']
                if 'email' in user_data:
                    employe.user.email = user_data['email']
                employe.user.save()  # Sauvegarder les informations de l'utilisateur

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @action(detail=False, methods=['get'], url_path='by_email/(?P<email>[^/]+)')
    def get_by_email(self, request, email=None):
        if not email:
            return Response({'error': 'Email manquant'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            employe = Employe.objects.get(user__email=email)
            serializer = self.get_serializer(employe)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Employe.DoesNotExist:
            return Response({'error': 'Employé non trouvé'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, *args, **kwargs):
        user = self.user
        super().delete(*args, **kwargs)
        user.delete()  # Supprime le CustomUser associé

class UserViewSet(viewsets.ModelViewSet):
    queryset=CustomUser.objects.all()
    serializer_class=CustomUserSerializer
class FormationViewSet(viewsets.ModelViewSet):
    queryset = Formation.objects.all()
    serializer_class = FormationSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        print(f"Formation créée avec succès : {instance}")



class EvenementViewSet(viewsets.ModelViewSet):
    queryset = Evenement.objects.all()
    serializer_class = EvenementSerializer
    

class CompetenceViewSet(viewsets.ModelViewSet):
    queryset = Competence.objects.all()
    serializer_class = CompetenceSerializer

class formulaireViewSet(viewsets.ModelViewSet):
    queryset = formulaire.objects.all()
    serializer_class = formulaireSerializer
 

class PasswordResetRequestView(APIView):
    def post(self, request):
        email = request.data.get("email")
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Aucun utilisateur trouvé avec cet email."}, status=status.HTTP_400_BAD_REQUEST)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"

        send_mail(
            subject="Réinitialisation de votre mot de passe",
            message=f"Cliquez sur le lien suivant pour réinitialiser votre mot de passe : {reset_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        logger.info(f"Un email de réinitialisation a été envoyé à {email}")
        
        return Response({"message": "Un email de réinitialisation a été envoyé."}, status=status.HTTP_200_OK)

class PasswordResetConfirmView(APIView):
    def post(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Lien invalide ou expiré."}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Token invalide."}, status=status.HTTP_400_BAD_REQUEST)

        new_password = request.data.get("new_password")
        if not new_password:
            return Response({"error": "Un nouveau mot de passe doit être fourni."}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        
        logger.info(f"Mot de passe réinitialisé pour l'utilisateur {user.email}")
        
        return Response({"message": "Mot de passe réinitialisé avec succès."}, status=status.HTTP_200_OK)

class PasswordResetCompleteView(APIView):
    def get(self, request):
        return Response({"message": "Votre mot de passe a été réinitialisé avec succès."}, status=status.HTTP_200_OK)
    

# ✅ Fonction pour créer un token JWT
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class UserListView(APIView):
    def get(self, request):
        users = CustomUser.objects.all()  # Fetch all users from the database
        serializer = CustomUserSerializer(users, many=True)  # Serialize the queryset
        return Response(serializer.data, status=status.HTTP_200_OK)

class SignupView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        print("debug data from signup ",data)

        # Vérifier que les champs requis sont présents dans la requête
        required_fields = ['email', 'firstname', 'lastname', 'password', 'profile_picture', 'poste', 'equipe']
        if not all(field in data for field in required_fields):
            return Response(
                {'detail': 'Missing required fields.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Créer l'utilisateur
        try:
            user = CustomUser.objects.create_user(
                email=data['email'],
                first_name=data['firstname'],
                last_name=data['lastname'],
                password=data['password']
            )

            # Gérer l'upload de l'image de profil
            if 'profile_picture' in request.FILES:
                user.profile_picture = request.FILES['profile_picture']
                user.save()

            # Créer l'employé lié à l'utilisateur
            employe = Employe.objects.create(
                user=user,
                poste=data['poste'],
                equipe=data['equipe']
            )

            # Réponse de succès avec les détails de l'utilisateur créé
            return Response({'detail': 'User created successfully.'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
# ✅ API pour la connexion
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print("debug login")
        email = request.data.get('email')
        password = request.data.get('password')

        # Vérifier si l'utilisateur existe dans la base de données
        user = authenticate(username=email, password=password)

        if user:
            # 🔹 Déterminer le rôle
            if user.is_staff:  # Admin Django
                role = "admin"
            else:
                employe = Employe.objects.filter(user=user).first()
                role = "employe" if employe else "unknown"

            # 🔹 Générer le token JWT
            tokens = get_tokens_for_user(user)

            return Response({
                "user": CustomUserSerializer(user).data,
                "role": role,
                "tokens": tokens
            }, status=status.HTTP_200_OK)
        
        return Response({'error': 'Email ou mot de passe incorrect'}, status=status.HTTP_401_UNAUTHORIZED)
        


# @csrf_exempt  # Désactive temporairement la protection CSRF (pour les tests)
# def submit_formulaire(request):
#     if request.method == "POST":
#         try:
#             print("=========================submit form==============================================")
           
#             data = json.loads(request.body)  # Récupérer les données envoyées
#             print(data)
#             # email = data.get("email")  # Email de l'utilisateur
#             # competences=data.get("competences",[])
           

#             # # Vérifier si l'employé existe
#             # employe = Employe.objects.filter(user__email=email).first()
#             # if not employe:
#             #     return JsonResponse({"error": "Employé non trouvé"}, status=404)
            
#             # for competence in competences:
#             #     nom_competence=competence.get("nom_competence")
#             #     niveau_competence=competence.get("niveau")
#             #     if not nom_competence or not niveau_competence:
#             #         continue
#             #     employe.competences[nom_competence]=niveau_competence
#             # employe.save()


          
      

#             # # Créer et enregistrer le formulaire
#             # new_formulaire = formulaire.objects.create(
#             #     utilisateur=employe,
#             #     date_acquisition=datetime.datetime.today(),
#             # )

#             return JsonResponse({"message": "Formulaire soumis avec succès!"}, status=201)
#         except e:
#             print(e)
@csrf_exempt
def submit_formulaire(request):
    if request.method == "POST":
        try:
            print("\n=== Nouvelle requête reçue ===")
            print("\nCorps brut:", request.body)

            try:
                data = json.loads(request.body)
                print(json.dumps(data, indent=2))
            except json.JSONDecodeError as e:
                return JsonResponse({"error": "Invalid JSON format"}, status=400)

            # Simulation de traitement...
            if not data.get('email'):
                return JsonResponse({"error": "Email manquant dans les données"}, status=400)
            
            # Vérifier si l'employé existe
            employe = Employe.objects.filter(user__email=data.get('email')).first()
            if not employe:
                return JsonResponse({"error": "Employé non trouvé"}, status=404)

            competences = data.get('competences')
            if not competences:
                return JsonResponse({"error": "Competences non envoyées"}, status=400)

            # Mise à jour des compétences de l'employé
            for competence in competences:
                nom_competence = competence.get("nom_competence")
                niveau_competence = competence.get("niveau")
                if not nom_competence or not niveau_competence:
                    continue
                employe.competences[nom_competence] = niveau_competence

            # Mise à jour de la date d'embauche
            if data.get("date_join"):
                try:
                    employe.date_join = datetime.strptime(data["date_join"], "%Y-%m-%d").date()
                except ValueError:
                    return JsonResponse({"error": "Format de la date d'embauche invalide. Utilisez 'YYYY-MM-DD'."}, status=400)


            # Sauvegarde de l'employé avec la nouvelle date
            employe.save()

            # Créer un formulaire associé à l'employé
            formul = formulaire.objects.create(
                utilisateur=employe,
                competences=competences,
                date_acquisition=datetime.today()
            )

            return JsonResponse({"message": "Réponse envoyée"}, status=200)

        except Exception as e:
            print("\nErreur interne:", str(e))
            return JsonResponse({"error": "Internal server error"}, status=500)

    print("\nMéthode non autorisée:", request.method)
    return JsonResponse({"error": "Method not allowed"}, status=405)


@api_view(['POST'])
def participer(request):
    email = request.data.get('email')
    formation_id = request.data.get('formation_id')
    evenement_id = request.data.get('evenement_id')

    if not email:
        return Response({"error": "Email requis"}, status=400)

    try:
        employe = Employe.objects.get(user__email=email)

        if formation_id:
            formation = Formation.objects.get(id=formation_id)
            formation.participants.add(employe)
            return Response({"message": "Participation à la formation réussie."})

        elif evenement_id:
            evenement = Evenement.objects.get(id=evenement_id)
            evenement.participants.add(employe)
            return Response({"message": "Participation à l'événement réussie."})

        return Response({"error": "Aucun ID de formation ou d'événement fourni."}, status=400)

    except Employe.DoesNotExist:
        return Response({"error": "Employé non trouvé."}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

from rest_framework.views import APIView
from rest_framework.response import Response

class ProfilEmployeView(APIView):
    def get(self, request):
        employe = request.user.employe
        formations = employe.formations.all()
        evenements = employe.evenements.all()

        formation_serializer = FormationSerializer(formations, many=True)
        evenement_serializer = EvenementSerializer(evenements, many=True)

        return Response({
            "formations": formation_serializer.data,
            "evenements": evenement_serializer.data
        })
    
class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    parser_classes = (MultiPartParser, FormParser)


from .models import Notification
from .serializers import NotificationSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-created_at')