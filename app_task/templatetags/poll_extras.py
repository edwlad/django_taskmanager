from django import template
from django.template.defaultfilters import stringfilter
import re

register = template.Library()


@register.simple_tag(name="my_g", takes_context=True)
def my_g(context, get_par: str, *args, **kwargs):
    """Пересборка и добавление GET параметров
    get_par - исходная строка GET параметров типа ?par1=val1&par2=val2
        может быть пустой
    args - список, перебор парами:
        первый элемент - имя параметра
        второй - значение
    kwargs - словарь {имя_параметра: значение}
    -> Ответ - строка GET параметров
    """
    inp = get_par.replace("?", "").replace(" ", "")

    gen = iter(args)
    if "=" in inp:
        out = dict(v.split("=") for v in inp.split("&"))
    else:
        out = {}

    for v in gen:
        out[str(v)] = str(next(gen, ""))
    for k, v in kwargs.items():
        out[str(k)] = str(v)

    if out:
        return "?" + "&".join(map("=".join, out.items()))
    return ""


@register.simple_tag(takes_context=True)
def my_gd(context, get_par: str, *args):
    """Удаление параметров из GET строки
    get_par - исходная строка GET
    args - список имён параметров для удаления
    -> Ответ - строка GET параметров
    """
    inp = get_par.replace("?", "").replace(" ", "")
    args = tuple(map(str, args))

    if not inp or "=" not in inp:
        return ""
    out = [v for v in inp.split("&") if not v.split("=")[0] in args]

    if out:
        return "?" + "&".join(out)
    return ""


@register.simple_tag(takes_context=True)
def my_gf(context, get_par: str, *args):
    """Отбор определённых параметров из строки
    get_par - исходная строка GET
    args - список имён параметров для отбора
    -> Ответ - строка GET параметров
    """
    inp = get_par.replace("?", "").replace(" ", "")
    args = tuple(map(str, args))

    if not (inp and "=" in inp):
        return ""
    out = [v for v in inp.split("&") if v.split("=")[0] in args]

    if out:
        return "?" + "&".join(out)
    return ""


@register.simple_tag(takes_context=True)
def my_e(context, *args):
    """Создание переменной из строки"""
    inp = "".join(map(str, args))
    return eval(inp)


@register.filter
@stringfilter
def my_gi(value, get_par):
    """Проверка наличия параметра в GET строке"""
    return value + "=" in get_par


@register.filter
@stringfilter
def my_gg(value, get_par):
    """Получение значения парамера из GET строки"""
    out = re.search(rf"(?<={value}=).+?(?=&)", get_par + "&")
    if out:
        return out[0]
    return out


@register.filter
def my_in_dict(value, par: dict):
    """Проверка наличия ключа в словаре"""
    return value in par


@register.filter
def my_dict_find(value, par: dict):
    """Получение значения по ключу из словаря"""
    return par.get(value, None)
