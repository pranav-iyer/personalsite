from django import template
from django.template.defaultfilters import stringfilter
register = template.Library()

@register.filter
@stringfilter
def shorten_date(value):
    # takes the string that results from timesince filter, and shortens them so that they look a little nicer
    # number = ''
    # unit = ''
    # for i, c in enumerate(value):
    #     if c.isdecimal():
    #         number += c
    #     else:
    #         unit = value[i+1]
    #         break
        
    words = value.split()
    number = words[0]
    if words[1].startswith('minute'):
        unit = 'm'
    elif words[1].startswith('hour'):
        unit = 'h'
    elif words[1].startswith('day'):
        unit = 'd'
    elif words[1].startswith('month'):
        unit = 'mo'
    elif words[1].startswith('year'):
        unit = 'y'
    else:
        unit = ''

    return number+unit