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
    ResetForgetPasswordSerializer,
    ProfileSerializer,
    AddFollowRequestSerializer,
    GetFollowRequestSerializer,
    LogOutSerializer,
    UnfollowSerializer,
    DeleteFollowRequest,
    OTPVerificationSerializer,
    ResendOTPSerializer,
)
from .permissions import IsProfileOwner
from accounts.models import Profile, FollowRequest
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _
import jwt
from jwt import exceptions
from django.conf import settings
from .tasks import send_email, forget_password, send_follow_request_email
from .utils import decode_follow_request_token
from drf_spectacular.utils import extend_schema


User = get_user_model()


@extend_schema(tags=["Authentication"], description="User registration endpoint.")
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


@extend_schema(tags=["Authentication"], description="User login endpoint.")
class LoginApiView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            data = {
                "id": serializer.validated_data["id"],
                "otp": serializer.validated_data["otp"],
            }
            return Response(data=data, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Authentication"], description="OTP verification for login.")
class OTPVerificationView(generics.GenericAPIView):
    serializer_class = OTPVerificationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            data = {
                "is_staff": serializer.validated_data["is_staff"],
                "access": serializer.validated_data["access"],
                "refresh": serializer.validated_data["refresh"],
            }
            return Response(data=data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Authentication"], description="Resend OTP for login.")
class ResendOTPView(generics.GenericAPIView):
    serializer_class = ResendOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return Response(result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Authentication"], description="Logout endpoint.")
class LogoutApiView(generics.GenericAPIView):

    serializer_class = LogOutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        serializer = LogOutSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            data = {"details": "successfully logout  "}
            return Response(data=data, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Authentication"], description="User Activation endpoint.")
class ActivationApiview(views.APIView):
    @extend_schema(description="activation for new user")
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


@extend_schema(tags=["Authentication"], description="Resend User Activation endpoint.")
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


@extend_schema(tags=["Authentication"], description="User Reset Password endpoint.")
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


@extend_schema(tags=["Authentication"], description="User Forget Password endpoint.")
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


@extend_schema(tags=["Authentication"], description="User Reset Password endpoint.")
class ResetForgetpasswordApiView(generics.GenericAPIView):
    serializer_class = ResetForgetPasswordSerializer

    def post(self, request, *args, **kwargs):
        token = kwargs["token"]
        serializer = ResetForgetPasswordSerializer(
            data=request.data, context={"request": request, "token": token}
        )
        if serializer.is_valid():
            serializer.save()
            data = {"details": "password change successfully"}
            return Response(data=data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Profile"], description="Retrieve or update a user profile.")
class ProfileApiView(generics.GenericAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH"]:
            return [IsAuthenticated(), IsProfileOwner()]
        return super().get_permissions()

    def get_queryset(self):
        queryset = Profile.objects.all()
        return queryset

    def get_object(self):
        profile_id = self.kwargs.get("id")
        if profile_id is not None:
            obj = get_object_or_404(self.get_queryset(), id=profile_id)
            return obj
        else:
            obj = get_object_or_404(self.get_queryset(), user=self.request.user)
            return obj

    @extend_schema(
        operation_id="get_profile",
        description="Retrieve the profile of the authenticated user or a specific profile by ID.",
    )
    def get(self, request, *args, **kwargs):
        id = kwargs.get("id")
        obj = self.get_object()
        serializer = ProfileSerializer(
            instance=obj, context={"request": request, "id": id}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="update_profile",
        description="Fully update the profile of the authenticated user or a specific profile by ID.",
    )
    def put(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = ProfileSerializer(
            data=request.data, instance=obj, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        operation_id="partial_update_profile",
        description="Partially update the profile of the authenticated user or a specific profile by ID.",
    )
    def patch(self, request, *args, **kwargs):

        obj = self.get_object()
        serializer = ProfileSerializer(
            instance=obj, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Follow Requests"], description="Send a follow request to a user.")
class FollowRequestApiView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddFollowRequestSerializer

    @extend_schema(
        description="send follow request for user,if user was public directly follow,if it was private send follow request"
    )
    def post(self, request, *args, **kwargs):
        username = kwargs["slug"]
        serializer = AddFollowRequestSerializer(
            data=request.data, context={"request": request, "username": username}
        )
        if serializer.is_valid():
            instance = serializer.save()
            if hasattr(instance, "is_direct_follow") and instance.is_direct_follow:
                data = {
                    "status": "success",
                    "detail": f"You are now following {instance.to_user.email}",
                    "follow_status": "accepted",
                }
                return Response(data=data, status=status.HTTP_201_CREATED)

            else:
                from_user_id = request.user.id
                to_user_id = instance.to_user.id
                send_follow_request_email.delay(from_user_id, to_user_id)
                data = {
                    "status": "success",
                    "detail": f"Follow request sent to {instance.to_user.email}",
                    "follow_status": "pending",
                }
                return Response(data=data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Follow Requests"], description="Delete a pending follow request.")
class DeleteFollowRequestApiView(generics.GenericAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = DeleteFollowRequest

    @extend_schema(description="delete follow request that didnt accepted yet")
    def delete(self, request, *args, **kwargs):
        username = kwargs.get("slug")
        serializer = DeleteFollowRequest(
            data=request.data, context={"request": request, "username": username}
        )
        serializer.is_valid(raise_exception=True)
        serializer.delete()
        data = {"detils": "follow request successfully deleted"}
        return Response(data=data, status=status.HTTP_200_OK)


@extend_schema(tags=["Follow Requests"], description="Accept or Reject follow request.")
class AcceptOrRejectFollowRequestApiView(generics.GenericAPIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        sign = kwargs["sign"]
        id, action = decode_follow_request_token(sign)
        follow_request = FollowRequest.objects.get(
            to_user=request.user, from_user=User.objects.get(id=id)
        )
        to_user_profile = Profile.objects.get(user=request.user)
        from_user_profile = Profile.objects.get(user=follow_request.from_user)
        if action == "accept":
            follow_request.status = "accepted"
            to_user_profile.add_follower(from_user_profile)
            follow_request.save()
            return Response(
                {"details": f"{from_user_profile.user.username} following you "},
                status=status.HTTP_200_OK,
            )
        elif action == "reject":
            follow_request.status = "rejected"
            follow_request.save()
            return Response(
                {
                    "details": f"rejected follow request from {from_user_profile.user.username} "
                }
            )

        return Response(
            {"detail": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(tags=["Follow Requests"], description="Get follow request.")
class GetFollowRequestApiView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsProfileOwner]
    serializer_class = GetFollowRequestSerializer

    def get_queryset(self):
        queryset = FollowRequest.objects.filter(
            to_user=self.request.user, status="pending"
        )
        return queryset

    def get(self, request, *args, **kwargs):

        serializer = GetFollowRequestSerializer(
            instance=self.get_queryset(), many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=["Follow Requests"], description="Remove follow request.")
class RemoveFollowerApiView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer = UnfollowSerializer

    def delete(self, request, *args, **kwargs):
        username = self.kwargs.get("slug")
        serializer = UnfollowSerializer(
            data=request.data, context={"request": request, "username": username}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = {"details": "unfollow  successfully"}
        return Response(data=data, status=status.HTTP_200_OK)
