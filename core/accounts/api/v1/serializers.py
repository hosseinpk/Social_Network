from .validators import numeric_validator, special_character_validator, letter_validator , email_validator
from django.core.validators import MinLengthValidator
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from accounts.models import Profile,FollowRequest
from django.core import exceptions as e
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
import jwt
from jwt import exceptions
from django.conf import settings

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    username = serializers.CharField()
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
        fields = ["email","username", "password", "password1"]

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
    email_or_username = serializers.CharField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True)

    class Meta:
        fields = ["email_or_username", "password"]


    def validate(self, attrs):
        validated_data = super().validate(attrs)
        username = validated_data["email_or_username"]
        password = validated_data["password"]
        request = self.context.get("request")
        
        if email_validator(username) is None:
            try:
                username = User.objects.get(username = username)
                user = authenticate(request=request,username=username,password=password)

            except User.DoesNotExist:
                raise serializers.ValidationError({"details": "user does not exist"})

        else:
            try:
                username = User.objects.get(email = username)
                user = authenticate(request=request,username=username,password=password)

            except User.DoesNotExist:
                raise serializers.ValidationError({"details": "user does not exist"})
        if user is None:
            raise serializers.ValidationError({"details": "wrong username or password"})
        
        if not user.is_verified:
            raise serializers.ValidationError(
                {"details": "you should verified your account before login!!!"}
            )

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

        

class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.CharField(read_only = True)
    username = serializers.CharField(source="user.username", read_only = True)
    
    class Meta:
        model = Profile
        fields = ("user","username","first_name","last_name","image","bio","personal_code","phone_number","follower","following","private",)
        

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["follower"] = [
            {"id":follower.id , "username": follower.user.username}
            for follower in instance.follower.all()
        ]

        data["following"] = [
            {"id":follower.id , "username": follower.user.username}
            for follower in instance.following.all()
        ]

        return data
    


class AddFollowRequestSerializer(serializers.ModelSerializer):

    
    class Meta:
        model =FollowRequest
        fields = ["id", "from_user", "to_user", "status", "created_at"]
        read_only_fields = ["id","from_user" ,"status", "created_at"]

    def create(self, validated_data):
        request = self.context["request"]
        from_user = request.user
        to_user = validated_data["to_user"]
        
        try:
            to_user = Profile.objects.get(user__email = to_user.email)
            from_user = Profile.objects.get(user__email = from_user.email)
        except Profile.DoesNotExist:
            raise serializers.ValidationError({
                "details" : "profile not found"
            })

        if not to_user.private:
            try:
                
                follow_request = FollowRequest.objects.create(
                        from_user=from_user.user,
                        to_user=to_user.user,
                        status="accepted"
                )
                from_user.add_follower(to_user)
                follow_request.is_direct_follow = True
                return follow_request
            except e.ValidationError:
                raise serializers.ValidationError({"details" : "this user already follow you"})
        follow_request,created=FollowRequest.objects.get_or_create(from_user=from_user.user,to_user=to_user.user)
        if not created:
            raise serializers.ValidationError({"detils" : "request already sent!!"})
        follow_request.is_direct_follow = False
        return follow_request
        
        


