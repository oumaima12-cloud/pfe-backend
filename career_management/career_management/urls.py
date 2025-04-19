from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from management.views import (
    AdminViewSet, EmployeViewSet, FormationViewSet, EvenementViewSet,
    CompetenceViewSet, LoginView, SignupView, formulaireViewSet,
    UserViewSet, PasswordResetRequestView, PasswordResetConfirmView,
    participer, home, submit_formulaire,NotificationViewSet
)
from django.conf import settings
from django.conf.urls.static import static

# Initialiser le routeur
router = DefaultRouter()
router.register(r'admins', AdminViewSet)
router.register(r'users', UserViewSet)
router.register(r'employes', EmployeViewSet)
router.register(r'formations', FormationViewSet)
router.register(r'evenements', EvenementViewSet)
router.register(r'competences', CompetenceViewSet)
router.register(r'formulaire', formulaireViewSet)
router.register(r'notifications', NotificationViewSet, basename='notification')


# Définir les patterns d'URL
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/employes/by_email/<str:email>', EmployeViewSet.as_view({'put': 'update'})),
    path('api/password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('api/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('api/password-reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('api/signup', SignupView.as_view(), name='signup'),
    path('api/login', LoginView.as_view(), name='login'),
    path('api/formulaire/submit', submit_formulaire, name='submit_formulaire'),
    path('api/participer/', participer),
    path('', home, name='home'),
]

# Ajouter les fichiers médias et statiques en mode debug
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
