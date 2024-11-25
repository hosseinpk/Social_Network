from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import User, Profile
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ("email",)


class CustomUserAdmin(UserAdmin):
    model = User
    add_form = CustomUserCreationForm
    list_display = ("email", "is_active", "is_superuser", "is_staff", "is_verified")
    list_filter = (
        "email",
        "is_active",
        "is_superuser",
        "is_staff",
    )
    search_fields = ("email",)
    ordering = ("email",)
    fieldsets = (
        (
            "user",
            {
                "fields": ("email", "password"),
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


# Register your models here.
admin.site.register(User, CustomUserAdmin)

admin.site.register(Profile)
