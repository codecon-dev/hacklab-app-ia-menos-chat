from rest_framework import serializers

class TextMessageSerializer(serializers.Serializer):
    message = serializers.CharField()