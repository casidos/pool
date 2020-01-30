from django.core.exceptions import ValidationError
import re

def pool_username_validator(value):

    if re.match(r'^[\w.@+\-]+$', value):
        raise ValidationError('You entered invalid characters in your Username')
    else:
        return value