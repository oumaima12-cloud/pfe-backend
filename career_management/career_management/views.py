from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import viewsets
from management.models import Employe
from management.models import Employe
from management.serializers import EmployeSerializer
from django.http import JsonResponse

def home(request):
    return JsonResponse({"message": "Bienvenue sur l'API Career Management!"})



class EmployeViewSet(viewsets.ModelViewSet):
    queryset = Employe.objects.all()
    serializer_class = EmployeSerializer
