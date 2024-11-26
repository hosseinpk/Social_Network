from rest_framework.response import Response
from rest_framework import generics,views
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import RegistrationSerializer, LoginSerializer,ResendActivationSerializer
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
import jwt
from jwt import exceptions
from django.conf import settings
from mail_templated import EmailMessage

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
            mail =EmailMessage(
                "email/mail.tpl",
                {"token" : access},
                "from@example.com",
                to=[email]
            )
            mail.send()
            
            return Response(data=data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginApiView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            data = {

                "is_staff": serializer.validated_data["is_staff"],
                "access": serializer.validated_data["access"],
                "refresh": serializer.validated_data["refresh"],
            }
            return Response(data=data, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ActivationApiview(views.APIView):

    def get(self,request,*args,**kwargs):
        token = kwargs["token"]
        try:
            token = jwt.decode(token,settings.SECRET_KEY,algorithms=["HS256"])
        except exceptions.ExpiredSignatureError:
            return Response({"details" : "token has been expired"},status=status.HTTP_400_BAD_REQUEST)
        except exceptions.InvalidTokenError:
            return Response({"details" : "token is not valid"},status=status.HTTP_400_BAD_REQUEST)
        user_id = token["user_id"]
        user = get_object_or_404(User,pk=user_id)
        if user.is_verified:
            return Response({"details" : "user has already been verified"})
        user.is_verified = True
        user.save()
        return Response({"details" : "user has been verified"})
    

class ResendActivationApiview(generics.GenericAPIView):
    serializer_class = ResendActivationSerializer

    def post(self,request,*args,**kwargs):
        serializer = ResendActivationSerializer(data = request.data , context = {"request" : request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token = RefreshToken.for_user(user)
        token = str(token.access_token)
        email_obj = EmailMessage(
        "email/mail.tpl",
        {"token":token},
        "from@example.com",
        to=[user],
        )
        email_obj.send()
        return Response({
            "details" : "activation email resend!!"
        },status=status.HTTP_200_OK)