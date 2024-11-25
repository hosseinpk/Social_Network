import re, string
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


def numeric_validator(password):
    regex = re.compile(r"[0-9]")
    if regex.search(password) == None:
        raise ValidationError(
            _("password must include number"), 
            code="password_must_include_number"
        )


def letter_validator(password):
    regex = re.compile(r"[a-zA-Z]")
    if regex.search(password) == None:
        raise ValidationError(
            _("password must include letter"),
            code="password_must_include_letter"
        )


def special_character_validator(password):
    regex = re.compile(r"[~!@#$/\%^&*()_+=;:|><]")
    if regex.search(password) == None:
        raise ValidationError(
            _("password must include specific character"),
            code="password_must_include_specific_character",
        )
