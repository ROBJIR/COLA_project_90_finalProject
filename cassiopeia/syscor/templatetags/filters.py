from django import template
register = template.Library()

# Converts a time interval to milliseconds for display.
# Převádí časový interval na milisekundy pro zobrazení.
@register.filter
def milliseconds(value):
    if value is None:
        return None
    return value.total_seconds() * 1000