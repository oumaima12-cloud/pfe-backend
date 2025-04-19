from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth import get_user_model



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
    date_join=models.DateField(null=True, blank=True) 
    formations = models.ManyToManyField('Formation', blank=True, related_name='employes')
    evenements = models.ManyToManyField('Evenement', blank=True, related_name='employes')

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} {self.equipe} {self.poste} {self.date_join} "
 


class Formation(models.Model):
    titre = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    duree = models.IntegerField()
    participants = models.ManyToManyField('Employe', related_name='formations_participees', blank=True)

    def __str__(self):
        return self.titre

class Evenement(models.Model):
    titre = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    lieu = models.CharField(max_length=255)

class Competence(models.Model):
    nom = models.CharField(max_length=255,unique=True)
   
    

class formulaire(models.Model):
   
    utilisateur = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='formulaires')
    competences = models.JSONField(
        default=list,
        blank=True,
    )
    
    date_acquisition = models.DateField()
   


User = get_user_model()
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification pour {self.user.email}"