from django.contrib import admin
from .models import CustomUser, Employe, Admin, Formation, Evenement, Competence, formulaire

admin.site.register(CustomUser)
admin.site.register(Employe)
admin.site.register(Admin)
admin.site.register(Formation)
admin.site.register(Evenement)
admin.site.register(Competence)
admin.site.register(formulaire)
