from rest_framework import serializers
from management.models import Employe
from .models import Admin, Employe, Formation, Evenement, Competence, formulaire, CustomUser




class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'date_joined']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user
class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = '__all__'

class EmployeSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    competences = serializers.DictField(
        child=serializers.ChoiceField(choices=Employe.NIVEAUX),
        allow_empty=True
    )
    class Meta:
        model = Employe
        fields = ['user', 'poste', 'equipe','competences']
    



class FormationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Formation
        fields = '__all__'

class EvenementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evenement
        fields = '__all__'

class CompetenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competence
        fields = '__all__'
class formulaireSerializer(serializers.ModelSerializer):
    utilisateur=EmployeSerializer(read_only=True)
    competences = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=True
    )
    class Meta :
        model = formulaire
        fields = '__all__'
    def get_utilisateur(self, obj):
        return {
            "id": obj.utilisateur.id,
            "first_name": obj.utilisateur.user.first_name,
            "last_name": obj.utilisateur.user.last_name,
            "email": obj.utilisateur.user.email
        }
    