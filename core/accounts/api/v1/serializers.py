from .validators import numeric_validator, special_character_validator, letter_validator
from django.core.validators import MinLengthValidator
from rest_framework import serializers
from django.contrib.auth import get_user_model
from accounts.models import Profile
from django.core import exceptions
from django.utils.translation import gettext_lazy as _ 
from django.contrib.auth.password_validation import validate_password


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
        fields = ["email","password","password1"]

    def validate(self, attrs):

        email = attrs["email"]
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"details":"the email already used"})
        if attrs["password"] != attrs["password1"]:
            raise serializers.ValidationError({"details":"password doesn't match"})
        
        if not attrs["password"] or not attrs["password1"]:
            raise serializers.ValidationError({"details":"fill password and confirm password"})
        
        try:
            validate_password(attrs["password"])
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"password" : [e.messages]})
        return super().validate(attrs)
    
    def create(self, validated_data):
        validated_data.pop("password1")
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user)
        return user