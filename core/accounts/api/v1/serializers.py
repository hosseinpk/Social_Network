from .validators import numeric_validator, special_character_validator, letter_validator
from django.core.validators import MinLengthValidator
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from accounts.models import Profile
from django.core import exceptions
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
import jwt
from jwt import exceptions
from django.conf import settings

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(
        validators=[
            numeric_validator,
            special_character_validator,
            letter_validator,
            MinLengthValidator(limit_value=8),
        ],
    )
    password1 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "password1"]

    def validate(self, attrs):

        email = attrs["email"]
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"details": "the email already used"})
        if attrs["password"] != attrs["password1"]:
            raise serializers.ValidationError({"details": "password doesn't match"})

        if not attrs["password"] or not attrs["password1"]:
            raise serializers.ValidationError(
                {"details": "fill password and confirm password"}
            )

        try:
            validate_password(attrs["password"])
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"password": [e.messages]})
        return super().validate(attrs)

    def create(self, validated_data):
        validated_data.pop("password1")
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True)

    class Meta:
        fields = ["email", "password"]

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        username = validated_data["email"]
        password = validated_data["password"]
        request = self.context.get("request")
        user = authenticate(request=request, username=username, password=password)

        if not user.is_verified:
            raise serializers.ValidationError(
                {"details": "you should verified your account before login!!!"}
            )
        if user is None:
            raise serializers.ValidationError({"details": "wrong username or password"})
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        validated_data["is_staff"] = user.is_staff
        validated_data["access"] = str(access)
        validated_data["refresh"] = str(refresh)
        validated_data.pop("password")

        return validated_data


class ResendActivationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    class Meta:
        fields = ["email"]

    def validate(self, attrs):
        email = attrs.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"details": "user does not exist"})
        if user.is_verified:
            raise serializers.ValidationError(
                {"details": "user has been already verified"}
            )

        attrs["user"] = user

        return super().validate(attrs)


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        write_only=True,
        validators=[
            numeric_validator,
            special_character_validator,
            letter_validator,
            MinLengthValidator(limit_value=8),
        ],
    )
    confirm_password = serializers.CharField()
    old_password = serializers.CharField()

    class Meta:
        fields = [
            "old_password",
            "new_password",
            "confirm_password",
        ]

    def validate(self, attrs):
        data = super().validate(attrs)

        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError({"details": "password doesn't match"})

        try:
            validate_password(attrs["new_password"])
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"password": [e.messages]})

        attrs.pop("confirm_password")
        return attrs

    def save(self, **kwargs):
        request = self.context.get("request")
        user = User.objects.get(id=request.user.id)

        if not user.check_password(self.validated_data["old_password"]):
            raise serializers.ValidationError({"details": "wrong old password"})

        user.set_password(self.validated_data["new_password"])
        user.save()


class ForgetpassworSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    class Meta:
        
        fileds = ["email"]

    def validate(self, attrs):
        
        email = attrs["email"]

        if email is None:
            raise serializers.ValidationError({"details" : "wrong email "})
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"details":"you didnt sign up!!"})
        
        if not user.is_verified:
            raise serializers.ValidationError({
                "details" : "user is not verified!!"
            })

        attrs["email"] = email
        
        return super().validate(attrs)
    

class ResetForgetPasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(required=True,write_only=True,validators=[
        numeric_validator,
        special_character_validator,
        letter_validator,
        MinLengthValidator(limit_value=8),
    ],)
    
    confirm_password = serializers.CharField(required=True,write_only=True)

    class Meta:
        model = User
        fields = ["new_password","confirm_password"]

    def validate(self, attrs):
        token = self.context["token"]
        try:
            token = jwt.decode(token,settings.SECRET_KEY,algorithms=["HS256"])
        except exceptions.ExpiredSignatureError:
            raise serializers.ValidationError({"details": "token has been expired"})
        except exceptions.InvalidTokenError:
            raise serializers.ValidationError({"details": "token is not valid"})
        user_id = token["user_id"]
        user = User.objects.get(pk=user_id)
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "details" : "password doesn't match"
            })
        try:
            validate_password(attrs["new_password"])
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"password": [e.messages]})

        attrs.pop("confirm_password")
        attrs["token"] = token
        return super().validate(attrs)
    
    def save(self, **kwargs):
        token = self.validated_data["token"]
        user_id = token["user_id"]
        user = User.objects.get(pk=int(user_id))
        user.set_password(self.validated_data["new_password"])
        user.save()

        




