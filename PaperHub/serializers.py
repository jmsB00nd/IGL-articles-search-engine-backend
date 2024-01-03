from rest_framework import serializers
from .models import PaperHubUser,Moderator

class UserSignupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class PaperHubUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaperHubUser
        fields = '__all__'

class ModeratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moderator
        fields = '__all__'

