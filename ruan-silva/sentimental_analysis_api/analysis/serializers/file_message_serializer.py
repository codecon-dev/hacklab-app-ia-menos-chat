from rest_framework import serializers

class FileMessageSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        if value.content_type != 'application/pdf' or value.content_type != 'text/plain':
            raise serializers.ValidationError("O arquivo enviado não é um PDF ou TXT.")
        return value