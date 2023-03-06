from django.http.response import HttpResponseRedirect, HttpResponse  # noqa
from django.http.request import HttpRequest  # noqa
from rest_framework.request import Request
from django.db.models import Model  # noqa
from app_task.models import Proj, Sprint, Task, TaskStep
from django.conf import settings
from datetime import date, timedelta
from random import randint, choice, sample
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Permission

# from django.contrib.contenttypes.models import ContentType  # noqa

DEBUG = settings.DEBUG
# TIME_ZONE = settings.TIME_ZONE


def get_perms(request: HttpRequest | Request, obj: Model = None):
    kw = {}
    if isinstance(request, HttpRequest):
        kw = getattr(request.resolver_match, "kwargs", {})
    elif isinstance(request, Request):
        kw = request.parser_context.get("kwargs", {})
        kw["model"] = request.parser_context["view"].basename
    user = request.user

    if isinstance(obj, Model):
        has_obj = True
    else:
        match kw["model"]:
            case Proj.META.url_name:
                model = Proj
            case Sprint.META.url_name:
                model = Sprint
            case Task.META.url_name:
                model = Task
            case TaskStep.META.url_name:
                model = TaskStep
            case _:
                return {
                    "list": True,
                    "detail": True,
                }
        obj = model.objects.filter(id=kw["pk"]).first()
        has_obj = isinstance(obj, Model)
        if not has_obj:
            obj = model

    temp: str = f"{obj._meta.app_label}.{{}}_{obj._meta.model_name}"
    out = {
        "list": True,
        "detail": True,
        "is_author": False,  # автор
        "is_user": False,  # исполнитель
        "add": user.has_perm(temp.format("add")),
        "delete": has_obj and user.has_perm(temp.format("delete")),
        "edit": has_obj and user.has_perm(temp.format("change")),
    }

    a_id = hasattr(obj, "author") and hasattr(obj.author, "id") and obj.author.id
    u_id = hasattr(obj, "user") and hasattr(obj.user, "id") and obj.user.id
    p_de = hasattr(obj, "proj") and hasattr(obj.proj, "date_end") and obj.proj.date_end
    s_de = (
        hasattr(obj, "sprint")
        and hasattr(obj.sprint, "date_end")
        and obj.sprint.date_end
    )
    if p_de:
        out.update({"edit": False, "delete": False})
    elif s_de:
        out.update({"edit": False, "delete": False})
    elif user.is_superuser:
        pass
    elif a_id and user.id == a_id:
        out.update({"is_author": True})
    elif u_id and user.id == u_id:
        out.update({"is_user": True, "delete": False})
    elif a_id:
        out.update({"edit": False, "delete": False})

    return out


def gen_data(cnt=0, clear=False, close=0):
    # if not DEBUG:
    #     return

    print()  # перевод строки
    qs_proj = Proj.objects.all()
    qs_sprint = Sprint.objects.all()
    qs_task = Task.objects.all()
    user_model: User = get_user_model()
    beg = date.today() - timedelta(90)  # день начала назначения дат
    step = 180  # максимальный шаг в днях

    users = user_model.objects.filter(username__startswith="user")
    if not users.exists():
        print("Создание 5 пользователей")
        qp = Permission.objects.filter(content_type__app_label="app_task")
        for i in range(5):
            p = "U-321rew"
            user = user_model.objects.create_user(f"user{i}", "", p)
            user.first_name = p
            user.save()
            user.user_permissions.set([v.id for v in qp])
        users = user_model.objects.filter(username__startswith="user")

    if clear:
        print("Удаление старых данных")
        for user in users:
            qs_proj.filter(author=user).delete()

    print(f"Создание {cnt} проектов")
    qs_proj = qs_proj.all()
    full = len(qs_proj)
    # генерация проектов
    for i in range(full + 1, int(cnt) + full + 1):
        author = choice(users)
        obj = Proj()
        obj.name = f"Проект №{i}"
        obj.desc = f"Описание проекта №{i}"
        obj.author = author
        obj.uweb = author
        obj.date_beg = beg + timedelta(randint(0, step))
        if randint(0, 2):
            obj.date_max = beg + timedelta(randint(0, step))
        obj.save()

    print(f"Создание {cnt * 2} спринтов")
    qs_proj = qs_proj.all()
    qs_sprint = qs_sprint.all()
    full = len(qs_sprint)
    for i in range(full + 1, int(cnt * 2) + full + 1):
        author = choice(users)
        obj = Sprint()
        obj.name = f"Спринт №{i}"
        obj.desc = f"Описание спринта №{i}"
        obj.author = author
        obj.uweb = author
        obj.proj = choice(qs_proj)
        obj.date_beg = beg + timedelta(randint(0, step))
        if randint(0, 2):
            obj.date_max = beg + timedelta(randint(0, step))
        obj.save()

    print(f"Создание {cnt * 5} задач")
    qs_proj = qs_proj.all()
    qs_sprint = qs_sprint.all()
    qs_task = qs_task.all()
    full = len(qs_task)
    for i in range(full + 1, int(cnt * 5) + full + 1):
        author = choice(users)
        user = choice(users)
        obj = Task()
        obj.name = f"Задача №{i}"
        obj.desc = f"Описание задачи №{i}"
        obj.author = author
        obj.uweb = author
        obj.user = user
        obj.date_beg = beg + timedelta(randint(0, step))
        obj.proj = choice(qs_proj)
        if randint(0, 2):
            obj.sprint = choice(qs_sprint)
        if randint(0, 2):
            obj.date_max = beg + timedelta(randint(0, step))
        obj.save()

    if close:
        qs_proj = qs_proj.all()
        qs_sprint = qs_sprint.all()
        qs_task = qs_task.all()

        print(f"Закрытие {close % 100}% спринтов")
        for sprint in sample(tuple(qs_sprint), int(close % 100 / 100 * len(qs_sprint))):
            # закрываем все задачи спринта
            for task in sprint.sprint_tasks.all():
                task.date_end = beg + timedelta(randint(0, step))
                task.save()
            # получить по новой спринт
            sprint = qs_sprint.filter(id=sprint.id).get()
            sprint.date_end = beg + timedelta(randint(0, step))
            sprint.save()

        print(f"Попытка закрыть {close % 100}% проектов")
        for proj in sample(tuple(qs_proj), int(close % 100 / 100 * len(qs_proj))):
            # закрываем все задачи проекта без спринта
            for task in proj.proj_tasks.filter(sprint_id=None).all():
                task.date_end = beg + timedelta(randint(0, step))
                task.save()
            # получить по новой проект
            proj = qs_proj.filter(id=proj.id).get()
            proj.date_end = beg + timedelta(randint(0, step))
            proj.save()

    print("Генерация данных выполнена")

    return
