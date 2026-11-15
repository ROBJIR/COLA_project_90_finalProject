from django import template
register = template.Library()

@register.filter
def milliseconds(value):
    if value is None:
        return None
    return value.total_seconds() * 1000