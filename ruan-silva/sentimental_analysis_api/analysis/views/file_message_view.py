from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from sentimental_analysis_api.settings import GEMINI_KEY
from google import genai
from rest_framework.permissions import IsAuthenticated
from analysis.serializers.file_message_serializer import FileMessageSerializer
import os
from PyPDF2 import PdfReader

class FileMessageAPIView(APIView):
    client = genai.Client(api_key=GEMINI_KEY)
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'file': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_BINARY)
            },
        )
    )
    def post(self, request):
        serializer = FileMessageSerializer(data=request.data)
        text_content = ""

        if (serializer.is_valid()):
            file = serializer.validated_data['file']
            ext = os.path.splitext(file.name)[1].lower()

            if ext == ".txt":
                text_content = file.read().decode("utf-8")
            
            elif ext == ".pdf":
                reader = PdfReader(file)
                text_content = ""
                for page in reader.pages:
                    text_content += page.extract_text() or ""

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"""
Com base no texto abaixo, quero que o analise e retorne o sentimento do escritor expressado no texto:

{text_content}

Regras:
1. O formato do retorno deverá ser:

Sentimento do escritor:
Motivo:

2. Não adicione nenhum texto que não seja refernte a regra 1;

3. Caso a messagem não expresse nenhum sentimento, retone: Nenhum sentimento encontrado.
"""
            )
            
            return Response({'message': response.text}, status=status.HTTP_200_OK)
        
        return Response("Message are required!", status=status.HTTP_400_BAD_REQUEST)