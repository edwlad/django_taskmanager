from django import template
from django.template.defaultfilters import stringfilter
from django.contrib.auth.models import User
from django.db.models import Model

import re

# from django.contrib.auth import get_user_model

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
def my_hp(context, user: User, obj: Model) -> bool:
    """Права на работу с записью
    user - объект текущего пользователя
    obj - объект текущей записи
    выход словарь разрешений
    """
    if not isinstance(obj, Model):
        obj = context.dicts[3]["view"].model
    temp: str = f"{obj._meta.app_label}.{{}}_{obj._meta.verbose_name}"
    out = {
        "detail": user.has_perm(temp.format("view")),
        "add": user.has_perm(temp.format("add")),
        "delete": user.has_perm(temp.format("delete")),
        "edit": user.has_perm(temp.format("change")),
        "edit_user": user.has_perm(temp.format("change")),
    }
    a_id = hasattr(obj, "author_id") and obj.author_id
    u_id = hasattr(obj, "user_id") and obj.user_id
    p_de = hasattr(obj, "proj") and hasattr(obj.proj, "date_end")
    s_de = hasattr(obj, "sprint") and hasattr(obj.sprint, "date_end")
    if p_de and obj.proj.date_end:
        out.update({"edit": False, "delete": False})
    elif s_de and obj.sprint.date_end:
        out.update({"edit": False, "delete": False})
    elif user.is_superuser or a_id and user.id == a_id:
        pass
    elif u_id and user.id == u_id:
        out.update({"delete": False, "edit_user": False})
    elif a_id and user.id != a_id:
        out.update({"edit": False, "delete": False})
    return out


@register.simple_tag(takes_context=True)
def my_e(context, *args):
    """Создание переменной из строки"""
    inp = "".join(map(str, args))
    return eval(inp)


@register.simple_tag(takes_context=True)
def my_s(context, *args):
    """Создание строки"""
    return "".join(map(str, args))


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
def my_ds(value: int, par):
    """Склонение чисел
    value - целое число
    par - строка вида "рубль,рубля,рублей"
    """
    lst = str(par).split(",") + ["", ""]

    if isinstance(value, str) and value.isdigit():
        value = int(value)
    elif not isinstance(value, int):
        value = 0
    value = abs(value)

    out = lst[2]
    if 11 <= value <= 14:
        pass
    elif value % 10 == 1:
        out = lst[0]
    elif 2 <= value % 10 <= 4:
        out = lst[1]
    return out


@register.filter
def my_in_dict(value, par: dict):
    """Проверка наличия ключа в словаре"""
    return value in par


@register.filter
def my_dict_find(value, par: dict):
    """Получение значения по ключу из словаря"""
    return par.get(value, None)
