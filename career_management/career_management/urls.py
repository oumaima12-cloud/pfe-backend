
from django.contrib import admin  
from django.urls import path, include  
from rest_framework.routers import DefaultRouter  
from management.views import AdminViewSet, EmployeViewSet, FormationViewSet, EvenementViewSet, CompetenceViewSet, formulaireViewSet
from django.http import HttpResponse 
from .views import home, SignupView, LoginView

  

# Initialize the router  
router = DefaultRouter()  
router.register(r'admins', AdminViewSet)  
router.register(r'employes', EmployeViewSet)  
router.register(r'formations', FormationViewSet)  
router.register(r'evenements', EvenementViewSet)  
router.register(r'competences', CompetenceViewSet)  
router.register(r'formulaire', formulaireViewSet) 

# Define URL patterns  
urlpatterns = [  
    path('admin/', admin.site.urls),  
    path('api/signup/', SignupView.as_view(), name='signup'),  # Route Inscription
    path('api/login/', LoginView.as_view(), name='login'),  # Route Connexion
    path('api/', include(router.urls)),  # Routes des ViewSets
    path('', home, name='home'),  # <-- Ajouter cette ligne
]  

