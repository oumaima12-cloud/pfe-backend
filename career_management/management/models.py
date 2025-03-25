from django.db import models

class Admin(models.Model):
    nom = models.CharField(max_length=255)
    email = models.EmailField()

class Employe(models.Model):
    nom = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    poste = models.CharField(max_length=255)
    equipe = models.CharField(max_length=255)

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
