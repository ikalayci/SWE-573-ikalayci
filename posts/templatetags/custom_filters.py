from django import template

register = template.Library()

@register.filter
def get_text_color(bg_color):
    """
    Returns an appropriate text color (black or white) for a given background color.
    """
    if not bg_color.startswith("#") or len(bg_color) != 7:
        return '#000'  # Default to black if the input is invalid
    try:
        r, g, b = int(bg_color[1:3], 16), int(bg_color[3:5], 16), int(bg_color[5:7], 16)
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        return '#000' if brightness > 125 else '#fff'
    except ValueError:
        return '#000'  # Default to black if parsing fails
