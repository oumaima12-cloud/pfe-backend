from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from management.views import (
    AdminViewSet, EmployeViewSet, FormationViewSet, EvenementViewSet,
    CompetenceViewSet, LoginView, SignupView, formulaireViewSet,
    UserViewSet, PasswordResetRequestView, PasswordResetConfirmView,
    participer, home, submit_formulaire, NotificationListView,
    ParticipationRequestAPIView,EvenementCreateView
)
from management.views import (
    ParticipationRequestViewSet, 
    ParticipationRequestAPIView, get_cyber_events
)
from django.conf import settings
from django.conf.urls.static import static
from management.views import affecter_formation_ou_evenement_par_admin,CertificationViewSet,test_log
from management.views import ParticipantView, FormationNotificationView, EvenementNotificationView,FormationRequestViewSet,FormationRequestAPIView

# Initialiser le routeur
router = DefaultRouter()
router.register(r'admins', AdminViewSet)
router.register(r'users', UserViewSet)
router.register(r'employes', EmployeViewSet)
router.register(r'formations', FormationViewSet)
router.register(r'evenements', EvenementViewSet)
router.register(r'competences', CompetenceViewSet)
router.register(r'formulaire', formulaireViewSet)
router.register(r'certifications', CertificationViewSet)
router.register(r'participation-requests', ParticipationRequestViewSet, basename='participation-request')
router.register(r'formation-requests',FormationRequestViewSet, basename='formation-request')


# Définir les patterns d'URL
urlpatterns = [
    path('admin/', admin.site.urls),
    path('test-log/', test_log),
    path('api/notifications/<str:employe_email>/', NotificationListView.as_view(), name='notification-list'),
    path('admin/affecter/<int:employe_id>/', affecter_formation_ou_evenement_par_admin, name='affecter_formation_evenement'),
    path('api/formation-notification/', FormationNotificationView.as_view(), name='formation-notification'),
    path('api/participants/', ParticipantView.as_view(), name='participants-list'),
    path('api/', include(router.urls)),
    path('api/cyber-events/', get_cyber_events, name='cyber-events'),
    path('api/my-participation-requests/', ParticipationRequestAPIView.as_view(), name='my-participation-requests'),
    path('api/formation-request/', FormationRequestAPIView.as_view(), name='formation-request-create'),
    # Ajouter cette nouvelle route pour l'endpoint manquant
    path('api/my-participation-status/', ParticipationRequestViewSet.as_view({'get': 'my_participation_status'}), name='my-participation-status'),
    # Renommer cette route pour correspondre à votre code React
    path('api/request-participation/', ParticipationRequestAPIView.as_view(), name='request-participation'),
    path('api/employes/<int:pk>/', EmployeViewSet.as_view({'put': 'update'}), name='update_employe_by_id'),
    path('api/password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('api/evenementsss/', EvenementCreateView.as_view(), name='evenement-create'),
    path('api/evenement-notification/', EvenementNotificationView.as_view(), name='evenement-notification'),
    path('api/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('api/password-reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('api/signup', SignupView.as_view(), name='signup'),
    path('api/login', LoginView.as_view(), name='login'),
    path('api/formulaire/submit', submit_formulaire, name='submit_formulaire'),
    path('api/participer/', participer),
    path('api/notifications/', NotificationListView.as_view(), name='notification-list'),
    path('', home, name='home'),
]

# Ajouter les fichiers médias et statiques en mode debug
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)