from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.utils.translation import gettext_lazy as _
from django.core.validators import EmailValidator, RegexValidator
from django.core.exceptions import ValidationError
from accounts.api.v1.validators import personal_code_validator
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_("the Email must"))
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
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    objects = UserManager()

    def __str__(self):
        return self.email


phone_number_validator = RegexValidator(
    regex=r"^(\+98|0)?9\d{9}$",  # Example regex for phone numbers
    message="Phone number must be entered in the format: '+989*****' or '09*******'. Up to 13 digits allowed.",
)



class Profile(models.Model):
    user = models.OneToOneField("User", on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="media/profile", blank=True, null=True)
    bio = models.CharField(max_length=50, blank=True, null=True)
    personal_code = models.CharField(max_length=10,unique=True,blank=True,null=True,validators=[personal_code_validator,])
    phone_number = models.CharField( max_length=13, unique=True,blank=True,null=True,validators=[phone_number_validator])
    follower = models.ManyToManyField("self",symmetrical=False,related_name='following',blank=True)
    private = models.BooleanField(default=False)
    #posts = models.ForeignKey()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def add_follower(self, profile):
        if profile == self:
            raise ValueError(" cannot follow yourself.")
        self.follower.add(profile)

    def __str__(self):
        return self.user.email
    
    # @receiver(post_save, sender=User)
    # def save_profile(sender, instance, created, **kwargs):
    #     """
    #     Signal for post creating a user which activates when a user being created ONLY
    #     """
    #     if created:
    #         Profile.objects.create(user=instance)