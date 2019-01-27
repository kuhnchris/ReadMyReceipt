from django import template

register = template.Library()


@register.filter(name='calcTransformScale')
def calcTransformScale(value, arg):
    aspectRatio = value.height / value.width
    if value.width > arg:
        return 1 / (value.width / (arg * aspectRatio))
    else:
        return 1 / (value.width / aspectRatio)
