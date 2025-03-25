from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.models import AbstractUser, Group, Permission
class Admin(models.Model):
    nom = models.CharField(max_length=255)
    email = models.EmailField()

    def __str__(self):
        return self.nom
class EmployeManager(BaseUserManager):
    def create_user(self, email, nom, password=None, poste="", equipe=""):
        if not email:
            raise ValueError("L'email est requis")
        email = self.normalize_email(email)
        user = self.model(email=email, nom=nom, poste=poste, equipe=equipe)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nom, password):
        user = self.create_user(email, nom, password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Employe(AbstractBaseUser, PermissionsMixin):
    nom = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255, default="changeme123")
    poste = models.CharField(max_length=255, blank=True, null=True)
    equipe = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = EmployeManager()

    groups = models.ManyToManyField(Group, related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions", blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom']

    def __str__(self):
        return self.nom

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