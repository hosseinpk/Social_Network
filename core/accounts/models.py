from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.utils.translation import gettext_lazy as _
from django.core.validators import EmailValidator, RegexValidator
from accounts.api.v1.validators import personal_code_validator, phone_number_validator
from django.utils.text import slugify
from django.core.exceptions import ValidationError


# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_("the Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("superuser must have is_staff=True "))

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("superuser must have is_superuser=True"))

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(max_length=100, unique=True, validators=[EmailValidator])
    username = models.CharField(max_length=20, unique=True, blank=True, null=True)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    objects = UserManager()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if self.pk:
            user = User.objects.get(pk=self.pk)
            if user.email != self.email:
                raise ValidationError("Email cannot be changed.")
            if user.username != self.username:
                raise ValidationError("Username cannot be changed.")
        return super().save(*args, **kwargs)


class Profile(models.Model):

    user = models.OneToOneField("User", on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="media/profile", blank=True, null=True)
    bio = models.CharField(max_length=50, blank=True, null=True)
    personal_code = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        null=True,
        validators=[
            personal_code_validator,
        ],
    )
    phone_number = models.CharField(
        max_length=13,
        unique=True,
        blank=True,
        null=True,
        validators=[phone_number_validator],
    )
    follower = models.ManyToManyField(
        "self", symmetrical=False, related_name="following", blank=True
    )
    private = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.user.username)
        super().save(*args, **kwargs)

    def add_follower(self, profile):
        if profile == self:
            raise ValueError("You cannot follow yourself.")
        if not self.private:
            raise PermissionError(_("Follow request required for private profiles."))
        if profile in self.follower.all():
            raise ValidationError(_("This user is already following you."))
        self.follower.add(profile)
        return f"{profile} is now following {self}."

    def remove_follower(self, profile):

        self.follower.remove(profile)
        return f"{profile} unfollow by {self}."

    def follower_count(self):

        return len(self.follower.all())

    def following_count(self):

        return len(self.following.all())

    def __str__(self):
        return self.user.email


status_name = [
    ("pending", "Pending"),
    ("accepted", "Accepted"),
    ("rejected", "Rejected"),
    ("deleted", "Deleted"),
]


class FollowRequest(models.Model):

    from_user = models.ForeignKey(
        User, related_name="sent_follow_requests", on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        User, related_name="received_follow_requests", on_delete=models.CASCADE
    )
    status = models.CharField(max_length=10, choices=status_name, default="pending")
    deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["from_user", "to_user"]

    def __str__(self):
        return f"{self.from_user} => {self.to_user} ({self.status})"


# @receiver(post_save, sender=User)
# def save_profile(sender, instance, created, **kwargs):
#     """
#     Signal for post creating a user which activates when a user being created ONLY
#     """
#     if created:
#         Profile.objects.create(user=instance)
