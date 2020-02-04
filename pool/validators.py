from django.core.exceptions import ValidationError
import re

def pool_username_validator(value):

    regex = r'^[A-Za-z0-9 ]+$'

    if re.match(regex, value):
        return value
    else:
        raise ValidationError('VALIDATOR: You entered invalid characters in your Username')

    # if re.match(r'^[\w.@+\-]+$', value):
    #     print('an error is thrown')
    #     raise ValidationError('VALIDATOR: You entered invalid characters in your Username')
    # else:
    #     print('forwarding onto the next step: ')
    #     return value