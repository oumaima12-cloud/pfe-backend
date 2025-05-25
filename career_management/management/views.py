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
from .serializers import AdminSerializer, EmployeSerializer, FormationSerializer, EvenementSerializer, CompetenceSerializer,  formulaireSerializer,CustomUserSerializer,NotificationSerializer,CertificationSerializer

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
    

from rest_framework.decorators import action
from rest_framework.response import Response
from collections import defaultdict

class CompetenceViewSet(viewsets.ModelViewSet):
    queryset = Competence.objects.all()
    serializer_class = CompetenceSerializer

    @action(detail=False, methods=["get"], url_path="grouped")
    def grouped_by_categorie(self, request):
        competences = self.get_queryset()
        grouped = defaultdict(list)

        for comp in competences:
            grouped[comp.categorie].append({
                "id": comp.id,
                "nom": comp.nom
            })

        return Response(grouped)

class formulaireViewSet(viewsets.ModelViewSet):
    queryset = formulaire.objects.all()
    serializer_class = formulaireSerializer
 

from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import logging

logger = logging.getLogger(__name__)
User = get_user_model()  # ✅ Ceci récupère le bon modèle utilisateur

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

        subject = "🔐 Réinitialisation de votre mot de passe"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [user.email]

        html_content = f"""
        <html>
        <head>
          <style>
            body {{
              font-family: Arial, sans-serif;
              background-color: #f4f4f4;
              padding: 20px;
            }}
            .container {{
              background-color: #ffffff;
              padding: 20px;
              border-radius: 10px;
              box-shadow: 0 2px 5px rgba(0,0,0,0.1);
              max-width: 600px;
              margin: auto;
            }}
            .btn {{
              display: inline-block;
              margin-top: 20px;
              padding: 10px 20px;
              background-color: #007bff;
              color: #ffffff;
              text-decoration: none;
              border-radius: 5px;
              font-weight: bold;
            }}
            .footer {{
              margin-top: 30px;
              font-size: 12px;
              color: #777777;
            }}
          </style>
        </head>
        <body>
          <div class="container">
            <h2>Réinitialisation de votre mot de passe</h2>
            <p>Bonjour,</p>
            <p>Nous avons reçu une demande de réinitialisation de votre mot de passe. Cliquez sur le bouton ci-dessous pour définir un nouveau mot de passe :</p>
            <a href="{reset_url}" class="btn">Réinitialiser le mot de passe</a>
            <p>Si vous n'avez pas demandé cette action, vous pouvez ignorer cet e-mail. Votre mot de passe restera inchangé.</p>
            <div class="footer">
              <p>Merci,<br>L’équipe CareerFlow</p>
            </div>
          </div>
        </body>
        </html>
        """

        text_content = strip_tags(html_content)

        message = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        message.attach_alternative(html_content, "text/html")
        message.send()

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

@csrf_exempt
def submit_formulaire(request):
    if request.method == "POST":
        try:
            print("\n=== Nouvelle requête reçue ===")
            print("\nCorps brut:", request.body)

            try:
                data = json.loads(request.body)
                print(json.dumps(data, indent=2))
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON format"}, status=400)

            email = data.get('email')
            if not email:
                return JsonResponse({"error": "Email manquant dans les données"}, status=400)

            employe = Employe.objects.filter(user__email=email).first()
            if not employe:
                return JsonResponse({"error": "Employé non trouvé"}, status=404)

            # Mise à jour des compétences
            competences = data.get('competences')
            if not isinstance(competences, list):
                return JsonResponse({"error": "Le champ competences doit être une liste"}, status=400)

            for competence in competences:
                nom_competence = competence.get("nom_competence")
                niveau_competence = competence.get("niveau")
                if nom_competence and niveau_competence:
                    employe.competences[nom_competence] = niveau_competence

            # Mise à jour de la date d'embauche si fournie
            if data.get("date_join"):
                try:
                    employe.date_join = datetime.strptime(data["date_join"], "%Y-%m-%d").date()
                except ValueError:
                    return JsonResponse({"error": "Format de la date invalide. Utilisez 'YYYY-MM-DD'."}, status=400)

            # Récupération des données visa
            a_visa = data.get("a_visa", False)
            date_debut_visa = data.get("date_debut_visa")
            date_fin_visa = data.get("date_fin_visa")

            # Conversion des dates uniquement si a_visa est vrai
            debut = fin = None
            if a_visa:
                try:
                    debut = date_debut_visa if date_debut_visa else None
                    fin = date_fin_visa if date_fin_visa else None
                except ValueError:
                    return JsonResponse({"error": "Dates de visa invalides. Utilisez 'YYYY-MM-DD'."}, status=400)

            # Mise à jour du champ formulaire directement dans le modèle Employe
            employe.formulaire = {
                "competences": competences,
                "date_acquisition": data.get("date_debut_travail", datetime.today().strftime("%Y-%m-%d")),
                "niveaux_etude": data.get("niveaux_etude", ""),
                "soft_skills_dominante": data.get("soft_skills_dominante", ""),
                "a_visa": a_visa,
                "date_debut_visa": debut,
                "date_fin_visa": fin
            }

            # NOUVEAU : Traitement des certifications
            certifications_data = data.get('certifications', [])
            
            if certifications_data and isinstance(certifications_data, list):
                # Option 1: Supprimer les anciennes certifications et créer les nouvelles
                # Décommenter la ligne suivante si vous souhaitez supprimer les anciennes certifications
                # Certification.objects.filter(employe=employe).delete()
                
                # Créer les nouvelles certifications
                for cert_data in certifications_data:
                    if isinstance(cert_data, dict) and 'titre' in cert_data:
                        titre = cert_data['titre']
                    elif isinstance(cert_data, str):
                        titre = cert_data
                    else:
                        continue
                    
                    if titre and titre.strip():
                        # Vérifier si la certification existe déjà pour éviter les doublons
                        existing_cert = Certification.objects.filter(
                            employe=employe, 
                            titre=titre.strip()
                        ).first()
                        
                        if not existing_cert:
                            Certification.objects.create(
                                employe=employe,
                                titre=titre.strip()
                            )

            # Sauvegarde des modifications
            employe.save()

            return JsonResponse({"message": "Formulaire soumis avec succès"}, status=200)

        except Exception as e:
            print("\nErreur interne:", str(e))
            return JsonResponse({"error": "Internal server error"}, status=500)

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

            # Create notification for the employee
            notification_message = f"Vous avez été ajouté à la formation : {formation.name}."
            Notification.objects.create(user=employe.user, message=notification_message)

            return Response({"message": "Participation à la formation réussie."})

        elif evenement_id:
            evenement = Evenement.objects.get(id=evenement_id)
            evenement.participants.add(employe)

            # Create notification for the employee
            notification_message = f"Vous avez été ajouté à l'événement : {evenement.name}."
            Notification.objects.create(user=employe.user, message=notification_message)

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
from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework.exceptions import NotAuthenticated
from rest_framework.exceptions import PermissionDenied





class NotificationListView(ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Récupérer l'email de l'utilisateur depuis les paramètres de l'URL
        employe_email = self.kwargs.get('employe_email')

        if not employe_email:
            raise PermissionDenied("Email de l'utilisateur manquant dans la requête.")
        
        try:
            user = User.objects.get(email=employe_email)
        except User.DoesNotExist:
            raise PermissionDenied("Utilisateur avec cet email non trouvé.")

        # Vérifier si l'utilisateur authentifié est le même que l'utilisateur cible
        if self.request.user != user:
            raise PermissionDenied("Vous n'êtes pas autorisé à voir les notifications de cet utilisateur.")

        return Notification.objects.filter(user=user).order_by('-created_at')
    
def affecter_formation_ou_evenement(request, employe_id, formation_id=None, evenement_id=None):
    try:
        employe = Employe.objects.get(id=employe_id)

        if formation_id:
            formation = Formation.objects.get(id=formation_id)
            message = f"Vous avez été affecté à la formation '{formation.titre}'"
            # Créer la notification
            Notification.objects.create(employe=employe, message=message)
        elif evenement_id:
            evenement = Evenement.objects.get(id=evenement_id)
            message = f"Vous avez été affecté à l'événement '{evenement.titre}'"
            # Créer la notification
            Notification.objects.create(employe=employe, message=message)

        return Response({"message": "Formation/Événement affecté et notification envoyée."})
    except Employe.DoesNotExist:
        return Response({"error": "L'employé n'a pas été trouvé."}, status=404)
    except (Formation.DoesNotExist, Evenement.DoesNotExist):
        return Response({"error": "La formation ou l'événement n'a pas été trouvé."}, status=404)
    


@api_view(['POST'])
def marquer_notification_lue(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.is_read = True
        notification.save()

        return Response({"message": "Notification marquée comme lue."})
    except Notification.DoesNotExist:
        return Response({"error": "Notification introuvable."}, status=404)
@api_view(['GET'])
def unread_notifications_count(request):
    user = request.user
    if user.is_authenticated:
        count = Notification.objects.filter(user=user, is_read=False).count()
        return Response({'unread_count': count}, status=status.HTTP_200_OK)
    else:
        return Response({'unread_count': 0}, status=status.HTTP_200_OK)
    
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status


@api_view(['POST'])
@permission_classes([IsAdminUser])  # Limite l'accès à l'admin uniquement
def affecter_formation_ou_evenement_par_admin(request, employe_id):
    """
    Cette vue permet à un administrateur d'affecter un employé à une formation ou un événement.
    """
    formation_id = request.data.get('formation_id')
    evenement_id = request.data.get('evenement_id')

    if not formation_id and not evenement_id:
        return Response({"error": "Formation ou événement requis."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Récupérer l'employé par ID
        employe = Employe.objects.get(id=employe_id)
    except Employe.DoesNotExist:
        return Response({"error": "Employé non trouvé."}, status=status.HTTP_404_NOT_FOUND)

    # Affecter l'employé à une formation, si ID de formation est fourni
    if formation_id:
        try:
            formation = Formation.objects.get(id=formation_id)
            formation.participants.add(employe)
            
            # Créer une notification pour l'employé
            notification_message = f"Vous avez été ajouté à la formation : {formation.titre}."
            Notification.objects.create(user=employe.user, message=notification_message)
        except Formation.DoesNotExist:
            return Response({"error": "Formation non trouvée."}, status=status.HTTP_404_NOT_FOUND)

    # Affecter l'employé à un événement, si ID d'événement est fourni
    if evenement_id:
        try:
            evenement = Evenement.objects.get(id=evenement_id)
            evenement.participants.add(employe)

            # Créer une notification pour l'employé
            notification_message = f"Vous avez été ajouté à l'événement : {evenement.titre}."
            Notification.objects.create(user=employe.user, message=notification_message)
        except Evenement.DoesNotExist:
            return Response({"error": "Événement non trouvé."}, status=status.HTTP_404_NOT_FOUND)

    return Response({"message": "L'employé a été affecté avec succès à la formation ou à l'événement."}, status=status.HTTP_200_OK)

class ParticipantView(APIView):
    def post(self, request):
        # Logique pour ajouter un participant
        return Response({"message": "Participant ajouté!"}, status=status.HTTP_201_CREATED)
    



from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class FormationNotificationView(APIView):
    def post(self, request):
        # Récupérer les données
        titre = request.data.get("titre")
        description = request.data.get("description")
        date = request.data.get("date")
        duree = request.data.get("duree")
        participants_emails = request.data.get("participants", [])

        # Validation des données
        if not titre or not date or not duree:
            return Response({"error": "Données incomplètes"}, status=status.HTTP_400_BAD_REQUEST)
        if not participants_emails:
            return Response({"error": "Aucun participant spécifié"}, status=status.HTTP_400_BAD_REQUEST)

        for email in participants_emails:
            try:
                validate_email(email)
            except ValidationError:
                return Response({"error": f"Email invalide: {email}"}, status=status.HTTP_400_BAD_REQUEST)

        subject = f"Notification de formation: {titre}"

        # Contenu texte brut de l'email
        text_content = f"""
Détails de la formation :
- Titre : {titre}
- Description : {description or "Non spécifiée"}
- Date : {date}
- Durée : {duree} jours

Merci de confirmer votre présence.

Cordialement,
L'équipe des ressources humaines
"""

        # Contenu HTML de l'email
        html_content = f"""
<html>
<body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
    <div style="background-color: #ffffff; padding: 20px; border-radius: 8px;">
        <h2 style="color: #333;">📚 Notification de Formation</h2>
        <p>Bonjour,</p>
        <p>Vous êtes invité(e) à participer à la formation suivante :</p>

        <ul style="list-style: none; padding: 0; margin-bottom: 20px;">
            <li><strong>Titre :</strong> {titre}</li>
            <li><strong>Description :</strong> {description or "Non spécifiée"}</li>
            <li><strong>Date :</strong> {date}</li>
            <li><strong>Durée :</strong> {duree} jours</li>
        </ul>

        <div style="text-align: center; margin: 30px 0;">
            <a href="mailto:{settings.DEFAULT_FROM_EMAIL}?subject=Confirmation de présence à la formation {titre}" style="
                background-color: #4CAF50;
                color: white;
                padding: 12px 24px;
                text-decoration: none;
                border-radius: 5px;
                font-size: 16px;">
                Confirmer votre présence
            </a>
        </div>

        <p style="margin-top: 30px;">Merci et à bientôt !</p>
        <p><strong>L'équipe des ressources humaines</strong></p>
    </div>
</body>
</html>
"""

        try:
            # Création de l'email avec texte brut et HTML
            email = EmailMultiAlternatives(
                subject,
                text_content.strip(),
                settings.DEFAULT_FROM_EMAIL,
                participants_emails
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

            logger.info(f"Email de formation envoyé à {len(participants_emails)} participants")
            return Response({"message": "Notifications envoyées avec succès"}, status=200)

        except Exception as e:
            logger.error(f"Erreur SMTP: {str(e)}")
            return Response({"error": f"Échec de l'envoi: {str(e)}"}, status=500)




from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class EvenementNotificationView(APIView):
    authentication_classes = []  # IMPORTANT : Pas d'authentification
    permission_classes = [permissions.AllowAny]  # Accessible à tout le monde

    def post(self, request):
        titre = request.data.get("titre")
        description = request.data.get("description")
        date = request.data.get("date")
        lieu = request.data.get("lieu")
        participants_emails = request.data.get("participants", []) or request.data.get("participants_emails", [])

        if not titre or not date or not lieu:
            return Response({"error": "Données incomplètes"}, status=status.HTTP_400_BAD_REQUEST)
        if not participants_emails:
            return Response({"error": "Aucun participant spécifié"}, status=status.HTTP_400_BAD_REQUEST)

        for email in participants_emails:
            try:
                validate_email(email)
            except ValidationError:
                return Response({"error": f"Email invalide: {email}"}, status=status.HTTP_400_BAD_REQUEST)

        subject = f"Notification d'événement: {titre}"
        message = f"""
Détails de l'événement:
- Titre: {titre}
- Description: {description}
- Date: {date}
- Lieu: {lieu}

Nous espérons vous y voir !

Cordialement,
L'équipe d'organisation
"""

        try:
            send_mail(
                subject,
                message.strip(),
                settings.DEFAULT_FROM_EMAIL,
                participants_emails,
                fail_silently=False,
            )
            return Response({"message": "Notifications envoyées avec succès"}, status=200)
        except Exception as e:
            logger.error(f"Erreur SMTP: {str(e)}")
            return Response({"error": f"Échec de l'envoi: {str(e)}"}, status=500)
        


import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def get_cyber_events(request):
    print("🚀 Scraping des événements lancé...")

    url = "https://infosec-conferences.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "fr-FR,fr;q=0.9"
    }

    try:
        response = requests.get(url, headers=headers)
        print("✅ Requête envoyée, statut:", response.status_code)
    except Exception as e:
        print("❌ Erreur lors de la requête:", str(e))
        return JsonResponse({'error': 'Erreur de connexion au site'}, status=500)

    if response.status_code != 200:
        return JsonResponse({'error': 'Erreur de requête vers le site'}, status=500)

    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.select("table tbody tr")
        print(f"📄 {len(rows)} lignes trouvées")

        events = []
        count = 0

        for row in rows:
            if count >= 1000:
                break

            cols = row.find_all("td")
            if len(cols) < 6:
                continue

            link = cols[0].find("a")
            date_text = cols[1].get_text(strip=True)
            description = cols[2].get_text(strip=True)
            lieu_parts = [cols[3].get_text(strip=True), cols[4].get_text(strip=True), cols[5].get_text(strip=True), cols[6].get_text(strip=True)]
            lieu = ', '.join(part for part in lieu_parts if part)

            if link:
                title = link.get_text(strip=True)
                href = link.get("href")

                events.append({
                    'title': title,
                    'url': href,
                    'date': date_text,
                    'description': description or "Description non disponible",
                    'lieu': lieu or "Lieu non précisé"
                })
                count += 1

        return JsonResponse(events, safe=False)

    except Exception as e:
        print("❌ Erreur lors du parsing:", str(e))
        return JsonResponse({'error': str(e)}, status=500)
    

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from .models import ParticipationRequest, Employe, Notification
from .serializers import ParticipationRequestSerializer


class ParticipationRequestViewSet(viewsets.ModelViewSet):
    queryset = ParticipationRequest.objects.all()
    serializer_class = ParticipationRequestSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return ParticipationRequest.objects.all()

    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        requests = ParticipationRequest.objects.all()
        serializer = self.get_serializer(requests, many=True)
        return Response(serializer.data)

    def send_participation_email(self, user, titre, status):
        subject = {
            "approved": "🎉 Votre demande a été approuvée",
            "rejected": "❌ Votre demande a été refusée",
        }[status]

        from_email = settings.DEFAULT_FROM_EMAIL
        to = [user.email]

        text_content = (
            f"Bonjour {user.first_name},\n\n"
            f"Votre demande de participation à l'événement \"{titre}\" a été {status}.\n\n"
            f"Cordialement,\nL'équipe RH"
        )

        couleur = "#4CAF50" if status == "approved" else "#e53935"
        statut_libelle = "approuvée" if status == "approved" else "refusée"
        emoji = "✅" if status == "approved" else "❌"

        html_content = f"""
        <html>
          <body style="margin: 0; padding: 0; background-color: #f4f4f4;">
            <table width="100%" cellspacing="0" cellpadding="0" style="font-family: Arial, sans-serif;">
              <tr>
                <td align="center" style="padding: 20px;">
                  <table width="600" style="background-color: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                    <tr>
                      <td style="background-color: {couleur}; padding: 20px; text-align: center;">
                        <h2 style="margin: 0; color: white;">{emoji} Demande {statut_libelle}</h2>
                      </td>
                    </tr>
                    <tr>
                      <td style="padding: 30px;">
                        <p>Bonjour <strong>{user.first_name}</strong>,</p>
                        <p>
                          Votre demande de participation à l'événement
                          <strong>« {titre} »</strong> a été
                          <span style="color: {couleur}; font-weight: bold;">{statut_libelle}</span>.
                        </p>
                        {"<p>Merci pour votre engagement. Nous vous souhaitons une excellente participation !</p>" if status == "approved" else
                         "<p>Cette décision peut résulter de contraintes internes. Merci pour votre intérêt et n'hésitez pas à renouveler votre demande.</p>"}
                        <p style="margin-top: 30px;">Cordialement,<br><strong>L'équipe Ressources Humaines</strong></p>
                      </td>
                    </tr>
                    <tr>
                      <td style="background-color: #eeeeee; text-align: center; padding: 10px; font-size: 12px; color: #666;">
                        Ceci est un message automatique. Merci de ne pas y répondre.
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
          </body>
        </html>
        """

        email = EmailMultiAlternatives(subject, text_content, from_email, to)
        email.attach_alternative(html_content, "text/html")
        email.send()

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        participation_request = self.get_object()

        if participation_request.status != 'pending':
            return Response({"error": "Cette demande a déjà été traitée."}, status=400)

        participation_request.status = 'approved'
        participation_request.admin_comment = request.data.get('comment', '')
        participation_request.save()

        employe_user = participation_request.employee.user

        HistoriqueParticipation.objects.create(
            employe=participation_request.employee,
            type_participation='evenement',  
            titre=participation_request.event_title,
            description=f"Validé par l'admin ",
            date=participation_request.event_date,
            lieu='',
            budget=None,
            statut='Approuvé',
            source='Validation demande'
        )

        Notification.objects.create(
            user=employe_user,
            message=f"✅ Votre demande de participation à l'événement '{participation_request.event_title}' a été approuvée."
        )

        self.send_participation_email(employe_user, participation_request.event_title, "approved")
        return Response({"status": "approved"})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        participation_request = self.get_object()

        if participation_request.status != 'pending':
            return Response({"error": "Cette demande a déjà été traitée."}, status=400)

        participation_request.status = 'rejected'
        participation_request.admin_comment = request.data.get('comment', '')
        participation_request.save()

        employe_user = participation_request.employee.user

        Notification.objects.create(
            user=employe_user,
            message=f"❌ Votre demande de participation à l'événement '{participation_request.event_title}' a été refusée."
        )

        self.send_participation_email(employe_user, participation_request.event_title, "rejected")
        return Response({"status": "rejected"})





from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Employe, CyberEvent, ParticipationRequest, Notification
from .serializers import ParticipationRequestSerializer

class ParticipationRequestAPIView(APIView):
    permission_classes = [permissions.AllowAny]  # Ou adapte selon ton besoin

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Le champ 'email' est requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_employe = Employe.objects.get(user__email=email)
        except Employe.DoesNotExist:
            return Response({"error": "Aucun profil employé trouvé pour cet email."}, status=status.HTTP_404_NOT_FOUND)

        title = request.data.get('title')
        date = request.data.get('date')
        url = request.data.get('url')
        lieu = request.data.get('lieu', '')

        if not all([title, date, url]):
            return Response({"error": "Les champs 'title', 'date' et 'url' sont requis."}, status=status.HTTP_400_BAD_REQUEST)

        # Création ou récupération de l'événement cyber
        cyber_event, created = CyberEvent.objects.get_or_create(
            url=url,
            defaults={'title': title, 'date': date, 'lieu': lieu}
        )

        if not created and lieu and not cyber_event.lieu:
            cyber_event.lieu = lieu
            cyber_event.save()

        # Vérifie si une demande existe déjà pour cet employee ET titre d'événement
        if ParticipationRequest.objects.filter(employee=user_employe, event_title=title).exists():
            return Response({"error": "Une demande de participation pour cet événement existe déjà."}, status=status.HTTP_400_BAD_REQUEST)

        participation_request = ParticipationRequest.objects.create(
            employee=user_employe,
            event_title=title,
            event_date=date,
            event_url=url,
            event_type='event',
            cyber_event=cyber_event,
            status='pending'
        )

        # Notifications aux admins
        admin_users = Employe.objects.filter(user__is_staff=True)
        for admin in admin_users:
            Notification.objects.create(
                user=admin.user,
                message=f"{user_employe.user.get_full_name()} a demandé à participer à l'événement « {title} »."
            )

        serializer = ParticipationRequestSerializer(participation_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


from rest_framework import generics
from .models import Evenement
from .serializers import EvenementSerializer
from rest_framework.permissions import IsAuthenticated

class EvenementCreateView(generics.CreateAPIView):
    queryset = Evenement.objects.all()
    serializer_class = EvenementSerializer
    permission_classes = [permissions.AllowAny]

    

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions, status
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from .models import FormationRequest, Employe, Notification
from .serializers import FormationRequestSerializer
from .models import HistoriqueParticipation


class FormationRequestViewSet(viewsets.ModelViewSet):
    queryset = FormationRequest.objects.all()
    serializer_class = FormationRequestSerializer
    permission_classes = [permissions.AllowAny]  # À adapter selon vos besoins de sécurité

    def get_queryset(self):
        user = self.request.user
        
        # Check if user is authenticated first
        if not user.is_authenticated:
            # For anonymous users, return all requests (admin view)
            return FormationRequest.objects.all()
            
        if user.is_staff:
            return FormationRequest.objects.all()
        try:
            employe = Employe.objects.get(user=user)
            return FormationRequest.objects.filter(employee=employe)
        except Employe.DoesNotExist:
            return FormationRequest.objects.none()

    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        user = request.user
        
        # Check authentication for this specific action
        if not user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
            
        try:
            employe = Employe.objects.get(user=user)
            requests = FormationRequest.objects.filter(employee=employe)
            serializer = self.get_serializer(requests, many=True)
            return Response(serializer.data)
        except Employe.DoesNotExist:
            return Response({"error": "Profil employé non trouvé"}, status=status.HTTP_404_NOT_FOUND)

    def send_formation_email(self, user, titre, status):
        subject = {
            "approved": "🎉 Votre demande de formation a été approuvée",
            "rejected": "❌ Votre demande de formation a été refusée",
        }[status]

        from_email = settings.DEFAULT_FROM_EMAIL
        to = [user.email]

        text_content = (
            f"Bonjour {user.first_name},\n\n"
            f"Votre demande de formation \"{titre}\" a été {status}.\n\n"
            f"Cordialement,\nL'équipe RH"
        )

        couleur = "#4CAF50" if status == "approved" else "#e53935"
        statut_libelle = "approuvée" if status == "approved" else "refusée"
        emoji = "✅" if status == "approved" else "❌"

        html_content = f"""
        <html>
          <body style="margin: 0; padding: 0; background-color: #f4f4f4;">
            <table width="100%" cellspacing="0" cellpadding="0" style="font-family: Arial, sans-serif;">
              <tr>
                <td align="center" style="padding: 20px;">
                  <table width="600" style="background-color: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                    <tr>
                      <td style="background-color: {couleur}; padding: 20px; text-align: center;">
                        <h2 style="margin: 0; color: white;">{emoji} Demande de formation {statut_libelle}</h2>
                      </td>
                    </tr>
                    <tr>
                      <td style="padding: 30px;">
                        <p>Bonjour <strong>{user.first_name}</strong>,</p>
                        <p>
                          Votre demande de formation
                          <strong>« {titre} »</strong> a été
                          <span style="color: {couleur}; font-weight: bold;">{statut_libelle}</span>.
                        </p>
                        {"<p>Félicitations ! Merci pour votre investissement dans votre développement professionnel.</p>" if status == "approved" else
                         "<p>Cette décision peut résulter de contraintes budgétaires ou organisationnelles. N'hésitez pas à soumettre d'autres demandes.</p>"}
                        <p style="margin-top: 30px;">Cordialement,<br><strong>L'équipe Ressources Humaines</strong></p>
                      </td>
                    </tr>
                    <tr>
                      <td style="background-color: #eeeeee; text-align: center; padding: 10px; font-size: 12px; color: #666;">
                        Ceci est un message automatique. Merci de ne pas y répondre.
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
          </body>
        </html>
        """

        email = EmailMultiAlternatives(subject, text_content, from_email, to)
        email.attach_alternative(html_content, "text/html")
        email.send()

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        formation_request = self.get_object()

        if formation_request.status != 'pending':
            return Response({"error": "Cette demande a déjà été traitée."}, status=400)

        formation_request.status = 'approved'
        formation_request.admin_comment = request.data.get('comment', '')
        formation_request.save()

        employe_user = formation_request.employee.user

        Notification.objects.create(
            user=employe_user,
            message=f"✅ Votre demande de formation '{formation_request.formation_title}' a été approuvée."
        )

        self.send_formation_email(employe_user, formation_request.formation_title, "approved")
        return Response({"status": "approved"})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        formation_request = self.get_object()

        if formation_request.status != 'pending':
            return Response({"error": "Cette demande a déjà été traitée."}, status=400)

        formation_request.status = 'rejected'
        formation_request.admin_comment = request.data.get('comment', '')
        formation_request.save()

        employe_user = formation_request.employee.user

        Notification.objects.create(
            user=employe_user,
            message=f"❌ Votre demande de formation '{formation_request.formation_title}' a été refusée."
        )

        self.send_formation_email(employe_user, formation_request.formation_title, "rejected")
        return Response({"status": "rejected"})

    def create(self, request, *args, **kwargs):
        # Check authentication for creating requests
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required to create formation requests"}, 
                          status=status.HTTP_401_UNAUTHORIZED)
            
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        formation_request = serializer.save()
        
        # Notification aux administrateurs
        admin_users = Employe.objects.filter(user__is_staff=True)
        for admin in admin_users:
            Notification.objects.create(
                user=admin.user,
                message=f"{formation_request.employee.user.get_full_name()} a fait une demande de formation « {formation_request.formation_title} »."
            )
            
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Employe, FormationRequest, Notification
from .serializers import FormationRequestSerializer

class FormationRequestAPIView(APIView):
    permission_classes = [permissions.AllowAny]  # À adapter selon vos besoins de sécurité

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Le champ 'email' est requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_employe = Employe.objects.get(user__email=email)
        except Employe.DoesNotExist:
            return Response({"error": "Aucun profil employé trouvé pour cet email."}, status=status.HTTP_404_NOT_FOUND)

        title = request.data.get('title')
        date = request.data.get('date')
        url = request.data.get('url', '')
        formation_type = request.data.get('type', 'formation')
        budget = request.data.get('budget')

        if not all([title, date, budget]):
            return Response({"error": "Les champs 'title', 'date' et 'budget' sont requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            budget = float(budget)
        except (ValueError, TypeError):
            return Response({"error": "Le budget doit être un nombre valide."}, status=status.HTTP_400_BAD_REQUEST)

        # Vérifie si une demande existe déjà pour cet employé ET titre de formation
        if FormationRequest.objects.filter(employee=user_employe, formation_title=title).exists():
            return Response({"error": "Une demande pour cette formation existe déjà."}, status=status.HTTP_400_BAD_REQUEST)

        formation_request = FormationRequest.objects.create(
            employee=user_employe,
            formation_title=title,
            formation_date=date,
            formation_url=url,
            formation_type=formation_type,
            formation_budget=budget,
            status='pending'
        )

        # Notifications aux admins
        admin_users = Employe.objects.filter(user__is_staff=True)
        for admin in admin_users:
            Notification.objects.create(
                user=admin.user,
                message=f"{user_employe.user.get_full_name()} a demandé une formation « {title} » pour un budget de {budget}€."
            )

        serializer = FormationRequestSerializer(formation_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

from .models import Certification

class CertificationViewSet(viewsets.ModelViewSet):
    queryset = Certification.objects.all()
    serializer_class = CertificationSerializer

import logging
from django.http import HttpResponse

logger = logging.getLogger('security')

def test_log(request):
    logger.info("🔐 Quelqu’un a accédé à /test-log/")

    ip = request.META.get('REMOTE_ADDR', '')
    logger.info(f"Adresse IP: {ip}")

    return HttpResponse("Log de sécurité enregistré.")


from rest_framework import generics
from .models import HistoriqueParticipation
from .serializers import HistoriqueDemandeSerializer

class HistoriqueDemandeListAPIView(generics.ListAPIView):
    queryset = HistoriqueParticipation.objects.all()
    serializer_class = HistoriqueDemandeSerializer





