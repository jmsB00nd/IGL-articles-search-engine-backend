from rest_framework import serializers


class ArticleIndexSerializer(serializers.Serializer):
    titre = serializers.CharField()
    auteurs = serializers.CharField()
    institutions = serializers.CharField()
    resume = serializers.CharField()
    contenu = serializers.CharField()
    references = serializers.CharField()
    motsCles = serializers.CharField()
    urlPDF = serializers.CharField()
    pathPDF = serializers.CharField()