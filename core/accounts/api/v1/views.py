from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import RegistrationSerializer


class RegistrationApiView(generics.GenericAPIView):
    serializer_class = RegistrationSerializer

    def post(self,request,*args,**kwargs):
        serializer = RegistrationSerializer(data = request.data,context = {"request":request})
        if serializer.is_valid():
            serializer.save()
            email = serializer.validated_data["email"]
            data = {
                "email" : email,
                "details" : "user create successfully"
            }

            return Response(data=data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
