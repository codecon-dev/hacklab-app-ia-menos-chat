from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from sentimental_analysis_api.settings import GEMINI_KEY
from google import genai
from rest_framework.permissions import IsAuthenticated
from analysis.serializers.text_message_serializer import TextMessageSerializer

class TextMessageAPIView(APIView):
    client = genai.Client(api_key=GEMINI_KEY)
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=TextMessageSerializer,
        responses={200: "OK", 400: "Text not fieled"}
    )
    def post(self, request):
        serializer = TextMessageSerializer(data=request.data)

        if (serializer.is_valid()):
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"""
Com base no texto abaixo, quero que o analise e retorne o sentimento do escritor expressado no texto:

{serializer.validated_data.get("message")}

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