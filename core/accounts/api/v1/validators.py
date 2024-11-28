import re, string
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


def numeric_validator(password):
    regex = re.compile(r"[0-9]")
    if regex.search(password) == None:
        raise ValidationError(
            _("password must include number"), code="password_must_include_number"
        )


def letter_validator(password):
    regex = re.compile(r"[a-zA-Z]")
    if regex.search(password) == None:
        raise ValidationError(
            _("password must include letter"), code="password_must_include_letter"
        )


def special_character_validator(password):
    regex = re.compile(r"[~!@#$/\%^&*()_+=;:|><]")
    if regex.search(password) == None:
        raise ValidationError(
            _("password must include specific character"),
            code="password_must_include_specific_character",
        )


def personal_code_validator(value: str):
    if not len(value) == 10:
        raise ValidationError(_({"details": "personal code should be 10digits"}))

    res = 0
    for i, num in enumerate(value[:-1]):
        res = res + (int(num) * (10 - i))

    remain = res % 11
    if remain < 2:
        if not remain == int(value[-1]):
            raise ValidationError(_({"details": "wrong persoal code"}))
    else:
        if not (11 - remain) == int(value[-1]):
            raise ValidationError(_({"details": "wrong persoal code"}))
