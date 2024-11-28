from rest_framework.response import Response
from rest_framework import generics, views
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import (
    RegistrationSerializer,
    LoginSerializer,
    ResendActivationSerializer,
    ResetPasswordSerializer,
    ForgetpassworSerializer,
    ResetForgetPasswordSerializer
    
)
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _
import jwt
from jwt import exceptions
from django.conf import settings
from .tasks import send_email, forget_password



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
            token = refresh.access_token
            data = {
                "email": email,
                "is_staff": user.is_staff,
                "access": str(token),
                "refresh": str(refresh),
            }
            send_email.delay(email, str(token))

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

    def get(self, request, *args, **kwargs):
        token = kwargs["token"]
        try:
            token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except exceptions.ExpiredSignatureError:
            return Response(
                {"details": "token has been expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except exceptions.InvalidTokenError:
            return Response(
                {"details": "token is not valid"}, status=status.HTTP_400_BAD_REQUEST
            )
        user_id = token["user_id"]
        user = get_object_or_404(User, pk=user_id)
        if user.is_verified:
            return Response({"details": "user has already been verified"})
        user.is_verified = True
        user.save()
        return Response({"details": "user has been verified"})


class ResendActivationApiview(generics.GenericAPIView):
    serializer_class = ResendActivationSerializer

    def post(self, request, *args, **kwargs):
        serializer = ResendActivationSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user = serializer.validated_data["user"]
        token = RefreshToken.for_user(user)
        token = str(token.access_token)
        send_email.delay(email, token)
        return Response(
            {"details": "activation email resend!!"}, status=status.HTTP_200_OK
        )


class ResetPasswordApiview(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *agrs, **kwargs):
        serializer = ResetPasswordSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            data = {"details": "password changed successfully"}
            return Response(data=data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgetpasswordApiView(generics.GenericAPIView):
    serializer_class = ForgetpassworSerializer

    def post(self, request, *args, **kwargs):
        serializer = ForgetpassworSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            user = get_object_or_404(User, email=email)
            token = RefreshToken.for_user(user)
            token = str(token.access_token)
            forget_password.delay(email, token)
            return Response(
                {"details": "check your email for reset password!!"},
                status=status.HTTP_200_OK,
            )


class ResetForgetpasswordApiView(generics.GenericAPIView):
    serializer_class = ResetForgetPasswordSerializer
    
    def post(self,request,*args,**kwargs):
        token = kwargs["token"]
        serializer = ResetForgetPasswordSerializer(data = request.data,context = {"request":request,"token":token})
        if serializer.is_valid():
            serializer.save()
            data = {
                "details" :"password change successfully"
            }
            return Response(data = data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
