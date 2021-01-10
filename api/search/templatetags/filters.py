from django import template

register = template.Library()


@register.filter
def list_to_text(list):
    text = ""
    for idx, item in enumerate(list):
        text += item
        if idx < len(list) - 1:
            text += ", "
    return text

