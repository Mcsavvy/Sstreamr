from django.core.exceptions import ValidationError
import re

class User:
    @staticmethod
    def username(value):
        errors = []
        # username should be 3 chars at least
        if len(value) < 3:
            errors.append('username too short, should be at least 3 characters')
        # username should be 25 chars at most
        elif len(value) > 25:
            errors.append('username too long, should be 25 characters or less')
        # only underscores, a-z and 0-9
        if re.match('[^a-z0-9_]', value, re.I):
            errors.append('username contains unwanted characters, use only a-z 0-9 and underscores(_)')
        # not only underscores
        elif re.match("^_+$", value, re.I):
            errors.append('username should not contain only underscores')
        # not only numbers
        elif re.match("^[0-9]+$", value, re.I):
            errors.append('username should not contain only numbers')
        elif re.match("^[0-9_]+$", value, re.I):
            errors.append('username should not contain only numbers and underscores')
        if errors:
            raise ValidationError(errors)

    @staticmethod
    def password(value):
        errors = []
        if len(value) < 8:
            raise ValidationError(
                'password should be at least eight(8) characters'
            )

