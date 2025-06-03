from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth import get_user_model
from django.conf import settings



class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None):
        user = self.create_user(email, password=password, first_name=first_name, last_name=last_name)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    def user_profile_picture_path(instance, filename):
        return f'profile_pictures/user_{instance.id}/{filename}'

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    profile_picture = models.ImageField(upload_to=user_profile_picture_path, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email


class Admin(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    # You can still add other admin-specific fields if needed.


class Employe(models.Model):
    NIVEAUX = ['Débutant', 'Intermédiaire', 'Avancé', 'Expert']
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)  # Lien avec CustomUser
    poste = models.CharField(max_length=255, blank=True, null=True)
    equipe = models.CharField(max_length=255, blank=True, null=True)
    competences = models.JSONField(
        default=dict,
        blank=True,
    )
    formulaire = models.JSONField(
        default=dict,
        blank=True,
    )
    date_join = models.DateField(null=True, blank=True)
    formations = models.ManyToManyField('Formation', blank=True, related_name='employes')
    evenements = models.ManyToManyField('Evenement', blank=True, related_name='employes')


    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} {self.equipe} {self.poste} {self.date_join}"


class Formation(models.Model):
    titre = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    duree = models.IntegerField()
    participants = models.ManyToManyField('CustomUser', related_name='formations_participees', blank=True) 

    def __str__(self):
        return self.titre


class Evenement(models.Model):
    titre = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    lieu = models.CharField(max_length=255)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='evenements_participes', blank=True)

    def __str__(self):
        return self.titre


class Competence(models.Model):
    nom = models.CharField(max_length=255, unique=True)
    categorie = models.CharField(max_length=100, default="Technique")

    def __str__(self):
        return self.nom


class formulaire(models.Model):
    utilisateur = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='formulaires')
    competences = models.JSONField(default=list, blank=True)
    certifications = models.JSONField(default=list, blank=True)
    date_acquisition = models.DateField()

    niveaux_etude = models.CharField(
        max_length=100,
        choices=[
            ('bac', 'Bac'),
            ('licence', 'Licence'),
            ('master', 'Master'),
            ('ingenieur', 'Ingénieur'),
            ('doctorat', 'Doctorat')
        ],
        blank=True
    )

    soft_skills_dominante = models.CharField(max_length=100, blank=True)

    a_visa = models.BooleanField(default=False)
    date_debut_visa = models.DateField(null=True, blank=True)
    date_fin_visa = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Formulaire de {self.utilisateur}"



class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    employe = models.ForeignKey('Employe', on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
    


class Certification(models.Model):
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='certifications')
    titre = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.titre} ({self.employe.user.username})"
    


class CyberEvent(models.Model):
 #   evenement = models.OneToOneField(Evenement, on_delete=models.CASCADE, related_name='cyber_event')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)  
    date = models.DateField(blank=True, null=True)         
    lieu = models.CharField(max_length=255, blank=True, null=True)  

    url = models.URLField(blank=True, null=True)  


from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class ParticipationRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', _('En attente')),
        ('approved', _('Approuvée')),
        ('rejected', _('Rejetée')),
    ]
    
    TYPE_CHOICES = [
        ('event', _('Événement')),
    ]
    
    employee = models.ForeignKey('Employe', on_delete=models.CASCADE, related_name='participation_requests')
    event_title = models.CharField(max_length=255)
    event_date = models.DateField()
    event_url = models.URLField(blank=True, null=True)
    event_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    cyber_event = models.ForeignKey('CyberEvent', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    admin_comment = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Demande de participation')
        verbose_name_plural = _('Demandes de participation')
    
    def __str__(self):
        return f"{self.employee.user.get_full_name()} - {self.event_title} ({self.get_status_display()})"
    


class FormationRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', _('En attente')),
        ('approved', _('Approuvée')),
        ('rejected', _('Rejetée')),
    ]
    
    TYPE_CHOICES = [
        ('formation', _('Formation')),
    ]
    
    employee = models.ForeignKey('Employe', on_delete=models.CASCADE, related_name='formation_requests')
    formation_title = models.CharField(max_length=255)
    formation_date = models.DateField()
    formation_url = models.URLField(blank=True, null=True)
    formation_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    formation_budget = models.DecimalField(max_digits=10, decimal_places=2, help_text=_('Budget demandé pour la formation'))
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    admin_comment = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Demande de formation')
        verbose_name_plural = _('Demandes de formation')

    
    def __str__(self):
        return f"{self.employee.user.get_full_name()} - {self.formation_title} ({self.get_status_display()})"




class HistoriqueParticipation(models.Model):
    TYPE_CHOICES = [
        ('formation', 'Formation'),
        ('evenement', 'Événement'),
    ]

    employe = models.ForeignKey('Employe', on_delete=models.CASCADE, related_name='historique')
    type_participation = models.CharField(max_length=10, choices=TYPE_CHOICES)
    titre = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    lieu = models.CharField(max_length=255, blank=True, null=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    statut = models.CharField(max_length=50, default="Affecté")
    source = models.CharField(max_length=100, default="Affectation Admin") 
    date_enregistrement = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employe.user.get_full_name()} - {self.titre} ({self.type_participation})"
    

    from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Ouvrier(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField()
    date_naissance = models.DateField(null=True, blank=True)
    
    performance = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Note de performance entre 1 et 5"
    )

    def __str__(self):
        return f"{self.nom} {self.prenom}"
