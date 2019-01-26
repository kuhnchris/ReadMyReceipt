'''
stolen from: https://stackoverflow.com/questions/36744109/how-to-generate-a-random-number-in-a-template-django-python
'''
import random
from django import template

register = template.Library()


@register.simple_tag(name='random_int')
def random_int(a, b=None):
    if b is None:
        a, b = 0, a
    return random.randint(a, b)


@register.simple_tag(name='random_hex')
def random_hex(a, b=None):
    return "%0.2X" % random_int(a, b)

