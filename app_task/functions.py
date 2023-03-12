from django.http.response import HttpResponseRedirect, HttpResponse  # noqa
from django.http.request import HttpRequest  # noqa
from rest_framework.request import Request
from django.db.models import Model  # noqa
from app_task.models import Proj, Sprint, Task, TaskStep
from datetime import date, timedelta
from random import randint, choice, sample
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Permission
import logging
from django.conf import settings

# from django.contrib.contenttypes.models import ContentType  # noqa

# DEBUG = settings.DEBUG
# TIME_ZONE = settings.TIME_ZONE


def get_perms(request: HttpRequest | Request, obj: Model = None) -> dict:
    """Вычисление прав доступа пользователя к объекту модели или к модели

    Args:
        request (HttpRequest | Request): Реквест
        obj (Model, optional): Объект модели. Defaults to None.

    Returns:
        dict: Словарь прав доступа.
        True - есть доступ
        False - нет доступа
    {
        "list": доступ на просмотр списка
        "detail": доступ к детальной информации
        "is_author": пользователь - автор объекта
        "is_user": пользователь - исполнитель
        "add": право добавить запись
        "delete": право удалить запись
        "edit": право редактировать запись
    }
    """

    log = logging.getLogger(__name__ + ".perms")

    # ищем данные о модели и ИД объекта и заносим в словарь
    kw = {}
    if isinstance(request, HttpRequest):
        kw = getattr(request.resolver_match, "kwargs", {})
    elif isinstance(request, Request):
        kw = request.parser_context.get("kwargs", {})
        kw["model"] = request.parser_context["view"].basename
    user = request.user

    # если объект инстанс модели, то поытка найти объект по данным из url
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

    # первоначально поиск прав доступа к модели
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
    # если объект зависит от проекта и проект закрыт
    if p_de:
        out.update({"edit": False, "delete": False})
    # если объект зависит от спринта и спринт закрыт
    elif s_de:
        out.update({"edit": False, "delete": False})
    # если пользователь суперпользователь
    elif user.is_superuser:
        pass
    # если пользователь автор
    elif a_id and user.id == a_id:
        out.update({"is_author": True})
    # если пользователь исполнитель
    elif u_id and user.id == u_id:
        out.update({"is_user": True, "delete": False})
    # если есть автор
    elif a_id:
        out.update({"edit": False, "delete": False})

    if log.isEnabledFor(logging.DEBUG):
        pass
        log.debug("PERMS: user={}, obj={}, perms={}".format(user, str(obj)[:50], out))

    return out


def gen_data(cnt=0, close=0, clear=False, parent=False, clear_user=False) -> None:
    """Генерация данных для базы. Даты выбираются случайно
    в промежуте +/- 3 месяца от текущей даты.

    Args:
        cnt (int, optional): Количество генерируемых проектов.
            Defaults to 0.
        close (int, optional): Процент закрытия проектов и спринтов.
            Defaults to 0.
        clear (bool, optional): Очищать базу перед генерацией.
            Defaults to False.
        parent (bool, optional): Создавать зависимые задачи.
            Defaults to False.
        clear_user (bool, optional): Удалить и создать заново спецпользователей для
            генерируемых данных.
            Defaults to False.

    Как работаает:
        Создётся указанное число проектов.
    Для проекта указывается случайные автор, дата создания и планируемая дата закрытия.
        Создётся удвоеное число спринтов.
    Для спринтов - случайные автор, проект, дата создания и планируемая дата закрытия.
        Создётся в десять раз увеличеное число задач.
    Для задач - случайные автор, исполнитель, проект, спринт, дата создания
    и планируемая дата закрытия.
        Если есть зависимые задачи, попытка в поекте создать их.
    Выбираются две случайные задачи проекта главная и зависимая.
        Попытка закрыть указанное число спринтов.
    Выбираются случайные даты закрытия задач (не всех) спринта и дата закрытия спринта.
        Попытка закрыть указанное число проектов.
    Выбирается случайные даты закрытия задач (не всех) проекта и дата закрытия проекта.

    При записи данных модели проверяют их корректность:
    - даты больше/меньше чем надо,
    - можно ли создать зависимости
    - можно ли закрыть проект/спринт/задачу
    - и пр.
    """

    old_email_backend = getattr(settings, "EMAIL_BACKEND", "")
    settings.EMAIL_BACKEND = "django.core.mail.backends.dummy.EmailBackend"
    log = logging.getLogger("more")

    objs_proj = Proj.objects
    objs_sprint = Sprint.objects
    objs_task = Task.objects
    user_model: User = get_user_model()
    beg = date.today() - timedelta(90)  # день начала назначения дат
    step = 180  # максимальный шаг в днях
    user_start = getattr(settings, "MY_TEST_USER", "user")
    user_pass = getattr(settings, "MY_TEST_PASS", "U-321rew")

    users = user_model.objects.filter(username__startswith=user_start)

    if clear or clear_user:
        log.info("Удаление старых данных")
        for user in users:
            objs_proj.filter(author=user).delete()

    if clear_user:
        log.info("Удаление пользователей")
        users.delete()
        users = user_model.objects.filter(username__startswith=user_start)

    if cnt and not users.exists():
        log.info("Создание 5 пользователей")
        qp = Permission.objects.filter(content_type__app_label="app_task")
        for i in range(5):
            username = f"{user_start}{i}"
            user = user_model.objects.create_user(username, "", user_pass)
            user.first_name = user_pass
            user.email = f"{username}@none.none"
            user.save()
            user.user_permissions.set([v.id for v in qp])
        users = user_model.objects.filter(username__startswith=user_start)

    cou = cnt
    log.info(f"Создание {cou} проектов")
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
    log.info(f"Создание {cou} спринтов")
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
    log.info(f"Создание {cou} задач")
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
        log.info(f"Создание в {cou}% проектов зависимых задач")
        qs_proj = objs_proj.all()
        for proj in sample(tuple(qs_proj), int(cou / 100 * len(qs_proj))):
            tasks_id = tuple(v.id for v in proj.proj_tasks.all())
            for id in sample(tasks_id, int(0.2 * len(tasks_id))):  # tasks_id:
                task = objs_task.filter(id=id).get()
                task.parent = objs_task.filter(id=choice(tasks_id)).get()
                task.save()

    if close:
        qs_sprint = objs_sprint.all()
        qs_task = objs_task.all()
        cou = close % 100
        log.info(f"Закрытие не более {cou}% спринтов")
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
        log.info(f"Закрытие не более {cou}% проектов")
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

    log.info("Генерация данных выполнена")

    settings.EMAIL_BACKEND = old_email_backend

    return
