import openpyxl
from .models import Ouvrier
from datetime import datetime
from django.db import IntegrityError

class ExcelImporter:
    def __init__(self, file):
        self.file = file
        self.errors = []

    def import_ouvriers(self):
        wb = openpyxl.load_workbook(self.file, read_only=True)
        sheet = wb.active

        ouvriers_to_create = []
        emails_existants = set(Ouvrier.objects.values_list('email', flat=True))
        ligne_num = 1

        for row in sheet.iter_rows(min_row=2, values_only=True):
            ligne_num += 1
            try:
                nom, prenom, email, date_naissance = row

                # Vérification des champs obligatoires
                if not all([nom, prenom, email]):
                    self.errors.append(f"Ligne {ligne_num}: Données manquantes")
                    continue

                # Vérifier les doublons
                if email in emails_existants:
                    self.errors.append(f"Ligne {ligne_num}: Email déjà existant ({email})")
                    continue

                # Convertir la date si nécessaire
                if isinstance(date_naissance, str):
                    try:
                        date_naissance = datetime.strptime(date_naissance, "%Y-%m-%d").date()
                    except ValueError:
                        self.errors.append(f"Ligne {ligne_num}: Date invalide")
                        continue

                ouvriers_to_create.append(Ouvrier(
                    nom=nom,
                    prenom=prenom,
                    email=email,
                    date_naissance=date_naissance
                ))
                emails_existants.add(email)

            except Exception as e:
                self.errors.append(f"Ligne {ligne_num}: Erreur {str(e)}")

        # Import en bloc
        try:
            Ouvrier.objects.bulk_create(ouvriers_to_create)
        except IntegrityError as e:
            self.errors.append(f"Erreur lors de la sauvegarde en base : {str(e)}")

        return len(ouvriers_to_create), self.errors
