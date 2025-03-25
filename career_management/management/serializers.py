from rest_framework import serializers
from management.models import Employe
from .models import Admin, Employe, Formation, Evenement, Competence, formulaire

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = '__all__'

class EmployeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employe
        fields = ['id', 'nom', 'email', 'poste', 'equipe', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = Employe.objects.create_user(**validated_data)
        return user

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
   class Meta :
    model = formulaire
    fields = '__all__'
