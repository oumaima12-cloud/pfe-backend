from django.shortcuts import render
from rest_framework import viewsets
from management.models import Employe
from management.serializers import EmployeSerializer
from django.http import HttpResponse
from .models import Admin, Employe, Formation, Evenement, Competence, formulaire
from .serializers import AdminSerializer, EmployeSerializer, FormationSerializer, EvenementSerializer, CompetenceSerializer,  formulaireSerializer


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

