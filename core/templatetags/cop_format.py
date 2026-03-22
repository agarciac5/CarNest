from django import template

register = template.Library()


@register.filter
def cop_enteros(value):
    """Formatea entero con separador de miles estilo Colombia (punto)."""
    try:
        n = int(float(value))
    except (TypeError, ValueError):
        return value
    return f'{n:,}'.replace(',', '.')
