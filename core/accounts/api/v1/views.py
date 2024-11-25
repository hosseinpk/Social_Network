from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import RegistrationSerializer,LoginSerializer
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class RegistrationApiView(generics.GenericAPIView):
    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            email = serializer.validated_data["email"]
            user = get_object_or_404(User, email=email)
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            data = {
                "email": email,
                "is_staff": user.is_staff,
                "access": str(access),
                "refresh": str(refresh),
            }

            return Response(data=data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginApiView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    def post(self,request,*args,**kwargs):
        username = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request,username=username,password=password)
        if user is None:
            data = {
                "details" : "email or password is wrong"
            }
            return Response(data = data ,status=status.HTTP_400_BAD_REQUEST)
        id = user.id 
        email = user.email
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        data = {
            "id" : id,
            "email": email,
            "is_staff": user.is_staff,
            "access": str(access),
            "refresh": str(refresh),
        }

        return Response(data = data ,status=status.HTTP_200_OK)
        