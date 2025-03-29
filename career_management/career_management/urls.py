from django.contrib import admin  
from django.urls import path, include  
from rest_framework.routers import DefaultRouter  
from management.views import AdminViewSet, EmployeViewSet, FormationViewSet, EvenementViewSet, CompetenceViewSet, LoginView, SignupView, formulaireViewSet,UserViewSet
from django.http import HttpResponse 
from management.views import home  
from management.views import PasswordResetRequestView, PasswordResetConfirmView, PasswordResetCompleteView,UserListView

# Initialize the router  
router = DefaultRouter()  
router.register(r'admins', AdminViewSet)  
router.register(r'users', UserViewSet)
router.register(r'employes', EmployeViewSet)  
router.register(r'formations', FormationViewSet)  
router.register(r'evenements', EvenementViewSet)  
router.register(r'competences', CompetenceViewSet)  
router.register(r'formulaire', formulaireViewSet) 

# Define URL patterns  
urlpatterns = [  
    path('admin/', admin.site.urls),  
    path('api/', include(router.urls)),
    path('api/password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('api/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('api/password-reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('api/signup', SignupView.as_view(), name='signup'),  # Route Inscription
    path('api/login', LoginView.as_view(), name='login'),  # Route Connexion  
    path('', home, name='home'),  # <-- Ajouter cette ligne
]
