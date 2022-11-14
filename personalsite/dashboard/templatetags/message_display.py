from django import template

register = template.Library()


@register.filter(name="get_tag")
def get_tag(message, index):
    tags = message.tags.split(" ")
    if index >= 0 and index < len(tags):
        return message.tags.split(" ")[index]
    else:
        return ""
