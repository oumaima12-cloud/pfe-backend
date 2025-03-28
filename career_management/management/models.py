from django.db import models
# from django.contrib.auth.models import AbstractUser
# from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


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
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
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
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)  # Lien avec CustomUser
    poste = models.CharField(max_length=255, blank=True, null=True)
    equipe = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Formation(models.Model):
    titre = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    duree = models.IntegerField()

class Evenement(models.Model):
    titre = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    lieu = models.CharField(max_length=255)

class Competence(models.Model):
    nom = models.CharField(max_length=255)
    niveau = models.CharField(max_length=100)

class formulaire(models.Model):
    NIVEAUX = [
        ('Débutant', 'Débutant'),
        ('Intermédiaire', 'Intermédiaire'),
        ('Avancé', 'Avancé'),
        ('Expert', 'Expert'),
    ]

    utilisateur = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='competences')
    nom_competence = models.CharField(max_length=100)
    niveau = models.CharField(max_length=20, choices=NIVEAUX, default='Débutant')
    date_acquisition = models.DateField()

    def __str__(self):
        return f"{self.utilisateur.nom} - {self.nom_competence} ({self.niveau})"
