from rest_framework import serializers
from management.models import Employe
from .models import Admin, Employe, Formation, Evenement, Competence, formulaire, CustomUser, Notification
from django.contrib.auth.models import User
from .models import CustomUser,CyberEvent,Certification





class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'profile_picture', 'last_name', 'date_joined']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user
class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = '__all__'

class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = ['id', 'titre']

class EmployeSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    certifications = CertificationSerializer(many=True, read_only=True)
    competences = serializers.DictField(
        child=serializers.ChoiceField(choices=Employe.NIVEAUX),
        allow_empty=True
    )
    formulaire = serializers.DictField(
        allow_empty=True,
        required=False
    )
    date_join = serializers.DateField()
    class Meta:
        model = Employe
        fields = ['id', 'user', 'poste', 'equipe', 'competences', 'formulaire', 'date_join','certifications']



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email']  # Ajoute les champs que tu veux afficher

class FormationSerializer(serializers.ModelSerializer):
     participants = serializers.SlugRelatedField(slug_field='email', queryset=CustomUser.objects.all(), many=True)
     class Meta:
        model = Formation
        fields = ['id', 'titre', 'description', 'date', 'duree', 'participants']


class EvenementSerializer(serializers.ModelSerializer):
    participants = serializers.SlugRelatedField(slug_field='email', queryset=CustomUser.objects.all(), many=True)

    class Meta:
        model = Evenement
        fields = ['id', 'titre', 'description', 'date', 'lieu', 'participants']


class CompetenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competence
        fields = '__all__'



       

class formulaireSerializer(serializers.ModelSerializer):
    utilisateur=EmployeSerializer(read_only=True)
    competences = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=True
    )
    class Meta :
        model = formulaire
        fields = '__all__'
    def get_utilisateur(self, obj):
        return {
            "id": obj.utilisateur.id,
            "first_name": obj.utilisateur.user.first_name,
            "last_name": obj.utilisateur.user.last_name,
            "email": obj.utilisateur.user.email
        }
    
class NotificationSerializer(serializers.ModelSerializer):
       class Meta:
        model = Notification
        fields = '__all__'




class CyberEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CyberEvent
        fields = '__all__'


from rest_framework import serializers
from .models import ParticipationRequest

class ParticipationRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    employee_email = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = ParticipationRequest
        fields = ['id', 'employee', 'employee_name', 'employee_email', 'event_title', 
                  'event_date', 'event_url', 'event_type', 'status', 'status_display',
                  'created_at', 'updated_at', 'admin_comment', 'cyber_event']
        read_only_fields = ['created_at', 'updated_at', 'status_display']

    def get_employee_name(self, obj):
        return f"{obj.employee.user.first_name} {obj.employee.user.last_name}"

    def get_employee_email(self, obj):
        return obj.employee.user.email

    def get_status_display(self, obj):
        return obj.get_status_display()

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user

        # Récupérer l'employee lié à l'utilisateur connecté
        try:
            employee = user.employe
        except AttributeError:
            raise serializers.ValidationError("Employé introuvable pour cet utilisateur")

        cyber_event = validated_data.get('cyber_event')
        if not cyber_event:
            raise serializers.ValidationError("L'événement CyberEvent est obligatoire")

        # Créer l'objet ParticipationRequest avec toutes les informations nécessaires
        participation_request = ParticipationRequest(
            employee=employee,
            cyber_event=cyber_event,
            event_title=cyber_event.title,
            event_date=cyber_event.date,
            event_url=cyber_event.url,
            event_type='event',
            status='pending'
        )
        participation_request.save()
        
        return participation_request
    

from rest_framework import serializers
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import FormationRequest, Employe

class FormationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormationRequest
        fields = [
            'id', 
            'formation_title', 
            'formation_date', 
            'formation_url', 
            'formation_type', 
            'formation_budget',
            'status', 
            'created_at', 
            'updated_at', 
            'admin_comment'
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at', 'admin_comment']
    
    def validate_formation_date(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError(_("La date de formation doit être dans le futur."))
        return value
    
    def validate_formation_budget(self, value):
        if value <= 0:
            raise serializers.ValidationError(_("Le budget doit être supérieur à zéro."))
        return value
    
    def validate_formation_type(self, value):
        valid_types = [choice[0] for choice in FormationRequest.TYPE_CHOICES]
        if value not in valid_types:
            raise serializers.ValidationError(_("Type de formation invalide."))
        return value
    
    def create(self, validated_data):
        # Récupérer l'employé à partir du contexte de la requête
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            employee = Employe.objects.get(user=request.user)
            
            # Créer la demande de formation avec les données fournies par l'utilisateur
            formation_request = FormationRequest.objects.create(
                employee=employee,
                formation_title=validated_data.get('formation_title'),
                formation_date=validated_data.get('formation_date'),
                formation_url=validated_data.get('formation_url'),
                formation_type=validated_data.get('formation_type'),
                formation_budget=validated_data.get('formation_budget'),
                status='pending'  # Statut par défaut
            )
            
            return formation_request
        else:
            raise serializers.ValidationError(_("Utilisateur non authentifié."))
    
    def update(self, instance, validated_data):
        # Empêcher la modification du statut par l'employé
        if 'status' in validated_data and not self.context.get('is_admin', False):
            raise serializers.ValidationError(_("Vous n'êtes pas autorisé à modifier le statut."))
        
        # Mettre à jour les champs modifiables
        instance.formation_title = validated_data.get('formation_title', instance.formation_title)
        instance.formation_date = validated_data.get('formation_date', instance.formation_date)
        instance.formation_url = validated_data.get('formation_url', instance.formation_url)
        instance.formation_type = validated_data.get('formation_type', instance.formation_type)
        instance.formation_budget = validated_data.get('formation_budget', instance.formation_budget)
        
        if self.context.get('is_admin', False):
            instance.status = validated_data.get('status', instance.status)
            instance.admin_comment = validated_data.get('admin_comment', instance.admin_comment)
        
        instance.save()
        return instance