from django import template
from django.template.defaultfilters import stringfilter
import re

register = template.Library()


@register.simple_tag(takes_context=True)
def my_get(context, get_par: str, *args, **kwargs):
    inp = get_par.replace("?", "").replace(" ", "")

    if not (inp and "=" in inp):
        return ""
    out = dict(v.split("=") for v in inp.split("&"))
    gen = iter(args)

    for v in gen:
        out[str(v)] = str(next(gen, ""))
    for k, v in kwargs.items():
        out[str(k)] = str(v)

    if out:
        return "?" + "&".join(map("=".join, out.items()))
    return ""


@register.simple_tag(takes_context=True)
def my_get_del(context, get_par: str, *args):
    inp = get_par.replace("?", "").replace(" ", "")
    args = tuple(map(str, args))

    if not (inp and "=" in inp):
        return ""
    out = [v for v in inp.split("&") if not v.split("=")[0] in args]

    if out:
        return "?" + "&".join(out)
    return ""


@register.simple_tag(takes_context=True)
def my_get_filt(context, get_par: str, *args):
    inp = get_par.replace("?", "").replace(" ", "")
    args = tuple(map(str, args))

    if not (inp and "=" in inp):
        return ""
    out = [v for v in inp.split("&") if v.split("=")[0] in args]

    if out:
        return "?" + "&".join(out)
    return ""


@register.filter
@stringfilter
def my_in_get(value, get_par):
    return value + "=" in get_par


@register.filter
@stringfilter
def my_get_find(value, get_par):
    out = re.search(rf"(?<={value}=).+?(?=&)", get_par + "&")
    if out:
        return out[0]
    return out


@register.filter
def my_in_dict(value, par: dict):
    return value in par


@register.filter
def my_dict_find(value, par: dict):
    return par.get(value, None)
