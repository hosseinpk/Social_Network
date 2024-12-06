from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import User, Profile, FollowRequest
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ("email", "username")


class CustomUserAdmin(UserAdmin):
    model = User
    add_form = CustomUserCreationForm
    list_display = (
        "email",
        "username",
        "is_active",
        "is_superuser",
        "is_staff",
        "is_verified",
    )
    list_filter = (
        "email",
        "is_active",
        "is_superuser",
        "is_staff",
    )
    readonly_fields = ("username", "email")
    search_fields = ("email",)
    ordering = ("email",)
    fieldsets = (
        (
            "user",
            {
                "fields": ("email", "username", "password"),
            },
        ),
        (
            "permissions",
            {
                "fields": ("is_staff", "is_active", "is_superuser", "is_verified"),
            },
        ),
        (
            "group_permissions",
            {
                "fields": ("groups", "user_permissions"),
            },
        ),
        (
            "important_date",
            {
                "fields": ("last_login",),
            },
        ),
    )
    add_fieldsets = (
        (
            "Add User",
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_superuser",
                    "is_active",
                    "is_verified",
                ),
            },
        ),
    )


class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "first_name", "last_name", "phone_number", "private", "created_date")
    search_fields = ("user__username", "first_name", "last_name", "phone_number")
    list_filter = ("private", "created_date", "updated_date")

# Register your models here.
admin.site.register(User, CustomUserAdmin)
admin.site.register(FollowRequest)
admin.site.register(Profile,ProfileAdmin)
