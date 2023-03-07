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


def gen_data(cnt=0, close=0, clear=False, parent=False):
    # if not DEBUG:
    #     return

    print()  # перевод строки
    objs_proj = Proj.objects
    objs_sprint = Sprint.objects
    objs_task = Task.objects
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
            objs_proj.filter(author=user).delete()

    cou = cnt
    print(f"Создание {cou} проектов")
    qs_proj = objs_proj.all()
    full = len(qs_proj)
    # генерация проектов
    for i in range(full + 1, int(cou) + full + 1):
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

    cou = cnt * 2
    print(f"Создание {cou} спринтов")
    qs_proj = objs_proj.all()
    qs_sprint = objs_sprint.all()
    full = len(qs_sprint)
    for i in range(full + 1, int(cou) + full + 1):
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

    cou = cnt * 10
    print(f"Создание {cou} задач")
    qs_proj = objs_proj.all()
    qs_sprint = objs_sprint.all()
    qs_task = objs_task.all()
    full = len(qs_task)
    for i in range(full + 1, int(cou) + full + 1):
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
        if randint(0, 5):
            obj.sprint = choice(qs_sprint)
        if randint(0, 2):
            obj.date_max = beg + timedelta(randint(0, step))
        obj.save()

    if parent:
        cou = close % 100
        print(f"Создание в не более {cou}% проектов зависимых задач")
        qs_proj = objs_proj.all()
        for proj in sample(tuple(qs_proj), int(cou / 100 * len(qs_proj))):
            tasks_id = tuple(v.id for v in proj.proj_tasks.all())
            for id in tasks_id:
                task = objs_task.filter(id=id).get()
                task.parent = objs_task.filter(id=choice(tasks_id)).get()
                task.save()

    if close:
        qs_sprint = objs_sprint.all()
        qs_task = objs_task.all()
        cou = close % 100
        print(f"Закрытие не более {cou}% спринтов")
        for sprint in sample(tuple(qs_sprint), int(cou / 100 * len(qs_sprint))):
            if randint(0, 3):
                # закрываем все задачи спринта
                for task in sprint.sprint_tasks.all():
                    task.date_end = beg + timedelta(randint(0, step))
                    task.save()
            # получить по новой спринт
            sprint = objs_sprint.filter(id=sprint.id).get()
            sprint.date_end = beg + timedelta(randint(0, step))
            sprint.save()

        qs_proj = objs_proj.all()
        qs_task = objs_task.all()
        cou = close % 100
        print(f"Закрытие не более {cou}% проектов")
        for proj in sample(tuple(qs_proj), int(cou / 100 * len(qs_proj))):
            if randint(0, 3):
                # закрываем все задачи проекта без спринта
                for task in proj.proj_tasks.filter(sprint_id=None).all():
                    task.date_end = beg + timedelta(randint(0, step))
                    task.save()
            # получить по новой проект
            proj = objs_proj.filter(id=proj.id).get()
            proj.date_end = beg + timedelta(randint(0, step))
            proj.save()

    print("Генерация данных выполнена")

    return
