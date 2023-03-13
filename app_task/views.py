from django.shortcuts import render  # noqa
from django.http.response import HttpResponseRedirect, HttpResponse  # noqa
from django.http.request import HttpRequest  # noqa
from django.db import models  # noqa
from django.urls import reverse, reverse_lazy  # noqa
from django.conf import settings
from django.contrib.auth import get_user_model
import logging
from django.contrib import messages

# from django.contrib.messages.views import SuccessMessageMixin

from django.views.generic import (
    View,
    TemplateView,
    ListView,
    # DetailView,
    UpdateView,
    CreateView,
    DeleteView,
)
from .models import Proj, Sprint, Task, TaskStep
import app_task.functions as functions

PAGINATE_BY = settings.PAGINATE_BY
PAGINATE_ORPHANS = settings.PAGINATE_ORPHANS
MY_OPER = settings.MY_OPER
LOG = logging.getLogger(__name__)


def error(req: HttpRequest, *args, **kwargs) -> HttpResponse:
    status = int(kwargs.get("status", 400))
    title = kwargs.get("title", "Ошибка")
    content = kwargs.get("content", f"<p>Код ошибки: {status}</p>")
    LOG.info(f"{title} {status} {content}")
    return render(
        req,
        "error.html",
        status=status,
        context={
            "title": title,
            "content": content,
            "buttons": ("back", "index"),
            "is_error": True,
        },
    )


def ProjTemplate(self: TemplateView, oper: str) -> View:
    """Создание объекта с шаблоном для модели Proj.
    Вариант шаблона зависит от аргумета oper.

    Args:
        self (TemplateView): Родительский объект шаблона
        oper (str): Название текущей операции


    Returns:
        View: Объект шаблона в зависимости от аргумента oper.

    oper = 'list' -> ListView
    oper = 'detail' -> ListView
    oper = 'add' -> CreateView
    oper = 'delete' -> DeleteView
    oper = 'edit' -> UpdateView
    """

    model = Proj
    par = self.request.GET.dict()
    model_url = self.kwargs.get("model")
    pk = self.kwargs.get("pk")
    user = self.request.user
    url_name = model.META.url_name  # url имя модели
    url_filt = model.META.url_filt  # GET имя фильтра по статусу проекта
    url_user = model.META.url_user  # GET имя фильтра по авторству

    LOG.debug(
        "VIEW Создание вью для модели {!r}, операция {!r}".format(model.__name__, oper)
    )

    # если есть данные в GET о модели и ключе, то собираем их
    task_id = 0
    if par.get("model", "") == Task.META.url_name:
        task_id = int(par.get("pk", 0))

    sprint_id = 0
    if task_id > 0:
        qs = Task.objects.filter(pk=task_id).exclude(sprint_id=None)
        sprint_id = qs.first().sprint_id if qs.exists() else 0
    if sprint_id <= 0 and par.get("model", "") == Sprint.META.url_name:
        sprint_id = int(par.get("pk", 0))

    proj_id = 0
    if task_id > 0:
        qs = Task.objects.filter(pk=task_id).exclude(proj_id=None)
        proj_id = qs.first().proj_id if qs.exists() else 0
    if proj_id <= 0 and sprint_id > 0:
        qs = Sprint.objects.filter(pk=sprint_id).exclude(proj_id=None)
        proj_id = qs.first().proj_id if qs.exists() else 0
    if proj_id <= 0 and par.get("model", "") == Proj.META.url_name:
        proj_id = int(par.get("pk", 0))

    # смотрим с какой страницы обращение
    list_qs = model.objects.all()
    if model_url == Sprint.META.url_name:
        qs = Sprint.objects.filter(id=pk).exclude(proj_id=None)
        pk = qs.first().proj_id if qs.exists() else 0
    elif model_url == Task.META.url_name:
        qs = Task.objects.filter(id=pk).exclude(proj_id=None)
        pk = qs.first().proj_id if qs.exists() else 0
    if pk <= 0 and proj_id > 0:
        qs = Proj.objects.filter(id=proj_id)
        pk = qs.first().id if qs.exists() else 0
    one_qs = model.objects.filter(id=pk)

    match oper:
        case "list":
            # фильтры
            # фильтр поиска в названии
            if fnd := par.get("name_f", ""):
                list_qs = list_qs.filter(name_upper__contains=fnd.upper())
                # list_qs = list_qs.filter(name__iregex=rf"{fnd}")

            # фильтр поиска по состоянию (выполнено, не выполнено, всё)
            match par.get(url_filt, ""):
                case "on":
                    list_qs = list_qs.exclude(date_end=None)
                case "all":
                    pass
                case _:
                    par[url_filt] = "off"
                    list_qs = list_qs.filter(date_end=None)

            # фильтр поиска по автору (автор или всё)
            if user.is_authenticated and par.get(url_user, "") == "aut":
                list_qs = list_qs.filter(author_id=user.id)
            else:
                par[url_user] = "all"

            # создание объекта
            obj = ListView(
                queryset=list_qs,
                template_name="list_proj.html",
                ordering=("-date_beg", "-id"),
                paginate_by=PAGINATE_BY,
                paginate_orphans=PAGINATE_ORPHANS,
                page_kwarg=model.META.url_page,
            )
        case "add":
            # присвоение своих значений
            self.request.POST._mutable = True
            self.request.POST["author"] = user.id
            self.request.POST["uweb"] = user.id
            self.request.POST._mutable = False
            # создание объекта
            obj = CreateView(
                template_name="redirect.html",
                fields=["uweb", "author", "name", "desc", "date_max"],
                success_url=reverse_lazy(
                    "list",
                    kwargs={
                        "model": model_url,
                    },
                ),
            )
        case "edit":
            # присвоение своих значений
            self.request.POST._mutable = True
            self.request.POST["uweb"] = user.id
            self.request.POST._mutable = False
            # создание объекта
            obj = UpdateView(
                template_name="redirect.html",
                fields=["uweb", "name", "desc", "date_end", "date_max"],
                queryset=one_qs,
                success_url=reverse(
                    "detail",
                    kwargs={
                        "model": model_url,
                        "pk": pk,
                    },
                ),
            )
        case "delete":
            # создание объекта
            obj = DeleteView(
                template_name="redirect.html",
                queryset=one_qs,
                success_url=reverse(
                    "list",
                    kwargs={
                        "model": model_url,
                    },
                ),
            )
        case "detail" | _:
            # создание объекта - список из одного значения
            obj = ListView(
                queryset=one_qs,
                template_name="detail_proj.html",
            )

    # создание дополнительных атрибутов
    obj.kwargs = self.kwargs
    obj.model = model
    obj.request = self.request
    obj.context_object_name = "data"
    obj.is_no_end = (  # запрещено ли закрыть проект
        self.kwargs["oper"] == "edit"
        and one_qs.exists()
        and (
            one_qs[0].proj_sprints.filter(date_end=None).exists()
            or one_qs[0].proj_tasks.filter(date_end=None).exists()
        )
    )
    obj.url_filt = url_filt
    obj.url_name = url_name
    obj.url_user = url_user
    obj.fld = {v.name: v for v in obj.model._meta.get_fields()}
    obj.get_par = "&".join(map("=".join, par.items()))

    return obj


def SprintTemplate(self: TemplateView, oper: str) -> View:
    """Создание объекта с шаблоном для модели Sprint.
    Вариант шаблона зависит от аргумета oper.

    Args:
        self (TemplateView): Родительский объект шаблона
        oper (str): Название текущей операции


    Returns:
        View: Объект шаблона в зависимости от аргумента oper.

    oper = 'list' -> ListView
    oper = 'detail' -> ListView
    oper = 'add' -> CreateView
    oper = 'delete' -> DeleteView
    oper = 'edit' -> UpdateView
    """

    model = Sprint
    par = self.request.GET.dict()
    oper_url = self.kwargs.get("oper")
    model_url = self.kwargs.get("model")
    pk = self.kwargs.get("pk")
    user = self.request.user
    url_name = model.META.url_name  # url имя модели
    url_filt = model.META.url_filt  # GET имя фильтра по статусу спринта
    url_user = model.META.url_user  # GET имя фильтра по авторству

    LOG.debug(
        "VIEW Создание вью для модели {!r}, операция {!r}".format(model.__name__, oper)
    )

    # если есть данные в GET о модели и ключе, то собираем их
    task_id = 0
    if par.get("model", "") == Task.META.url_name:
        task_id = int(par.get("pk", 0))

    sprint_id = 0
    if task_id > 0:
        qs = Task.objects.filter(pk=task_id).exclude(sprint_id=None).first()
        sprint_id = qs.sprint_id if qs else 0
    if sprint_id <= 0 and par.get("model", "") == Sprint.META.url_name:
        sprint_id = int(par.get("pk", 0))

    proj_id = 0
    if task_id > 0:
        qs = Task.objects.filter(pk=task_id).exclude(proj_id=None).first()
        proj_id = qs.proj_id if qs else 0
    if proj_id <= 0 and sprint_id > 0:
        qs = Sprint.objects.filter(pk=sprint_id).exclude(proj_id=None).first()
        proj_id = qs.proj_id if qs else 0
    if proj_id <= 0 and par.get("model", "") == Proj.META.url_name:
        proj_id = int(par.get("pk", 0))

    # смотрим с какой страницы обращение
    list_qs = model.objects.all()
    if model_url == Proj.META.url_name:
        list_qs = list_qs.filter(proj_id=pk)
    elif model_url == Task.META.url_name:
        qs = Task.objects.filter(id=pk).exclude(sprint_id=None).first()
        pk = qs.sprint_id if qs else 0
    if pk <= 0 and sprint_id > 0:
        qs = Sprint.objects.filter(id=sprint_id).first()
        pk = qs.id if qs else 0
    one_qs = model.objects.filter(id=pk)

    match oper:
        case "list":
            # фильтры
            # фильтр поиска в названии
            if fnd := par.get("name_f", ""):
                list_qs = list_qs.filter(name_upper__contains=fnd.upper())

            # фильтр поиска по состоянию (выполнено, не выполнено, всё)
            match par.get(url_filt, ""):
                case "on":
                    list_qs = list_qs.exclude(date_end=None)
                case "all":
                    pass
                case _:
                    par[url_filt] = "off"
                    list_qs = list_qs.filter(date_end=None)

            # фильтр поиска по автору (автор или всё)
            if user.is_authenticated and par.get(url_user, "") == "aut":
                list_qs = list_qs.filter(author_id=user.id)
            else:
                par[url_user] = "all"

            # создание объекта
            obj = ListView(
                queryset=list_qs,
                template_name="list_sprint.html",
                ordering=("-date_beg", "-id"),
                paginate_by=PAGINATE_BY,
                paginate_orphans=PAGINATE_ORPHANS,
                page_kwarg=model.META.url_page,
            )
        case "add":
            # присвоение своих значений
            self.request.POST._mutable = True
            self.request.POST["author"] = user.id
            self.request.POST["uweb"] = user.id
            self.request.POST._mutable = False
            # создание объекта
            obj = CreateView(
                template_name="redirect.html",
                fields=["uweb", "author", "proj", "name", "desc", "date_max"],
                success_url=reverse_lazy(
                    "detail",
                    kwargs={
                        "model": Proj.META.url_name,
                        "pk": self.request.POST["proj"],
                    },
                ),
            )
        case "edit":
            # присвоение своих значений
            self.request.POST._mutable = True
            self.request.POST["uweb"] = user.id
            self.request.POST._mutable = False
            # создание объекта
            obj = UpdateView(
                template_name="redirect.html",
                queryset=one_qs,
                fields=["uweb", "name", "desc", "date_end", "date_max", "proj"],
                success_url=reverse_lazy(
                    "detail",
                    kwargs={
                        "model": model_url,
                        "pk": pk,
                    },
                ),
            )
        case "delete":
            proj_pk = one_qs.first().proj_id
            # создание объекта
            obj = DeleteView(
                template_name="redirect.html",
                queryset=one_qs,
                success_url=reverse_lazy(
                    "detail",
                    kwargs={
                        "model": Proj.META.url_name,
                        "pk": proj_pk,
                    },
                ),
            )
        case "detail" | _:
            # создание объекта - список из одного значения
            obj = ListView(
                queryset=one_qs,
                template_name="detail_sprint.html",
            )
            # список не закрытых проектов
            if oper_url == "edit" or oper_url == "add":
                obj.projs = Proj.objects.filter(date_end=None)

    # создание дополнительных атрибутов
    obj.kwargs = self.kwargs
    obj.model = model
    obj.request = self.request
    obj.context_object_name = "data"
    obj.url_filt = url_filt
    obj.url_name = url_name
    obj.url_user = url_user
    obj.fld = {v.name: v for v in obj.model._meta.get_fields()}
    obj.task_id = task_id
    obj.sprint_id = sprint_id
    obj.proj_id = proj_id
    obj.get_par = "&".join(map("=".join, par.items()))
    obj.is_no_end = (  # запрещено ли закрыть спринт
        self.kwargs["oper"] == "edit"
        and one_qs.exists()
        and one_qs[0].sprint_tasks.filter(date_end=None).exists()
    )

    return obj


def TaskTemplate(self: TemplateView, oper: str) -> View:
    """Создание объекта с шаблоном для модели Task.
    Вариант шаблона зависит от аргумета oper.

    Args:
        self (TemplateView): Родительский объект шаблона
        oper (str): Название текущей операции

    Returns:
        View: Объект шаблона в зависимости от аргумента oper.

    oper = 'list' -> ListView
    oper = 'detail' -> ListView
    oper = 'add' -> CreateView
    oper = 'delete' -> DeleteView
    oper = 'edit' -> UpdateView
    """

    model = Task
    par = self.request.GET.dict()
    oper_url = self.kwargs.get("oper")
    model_url = self.kwargs.get("model")
    pk = self.kwargs.get("pk")
    user = self.request.user
    url_name = model.META.url_name  # url имя модели
    url_filt = model.META.url_filt  # GET имя фильтра по статусу задачи
    url_user = model.META.url_user  # GET имя фильтра по авторству

    LOG.debug(
        "VIEW Создание вью для модели {!r}, операция {!r}".format(model.__name__, oper)
    )

    # если есть данные в GET о модели и ключе, то собираем их
    task_step_id = 0
    if par.get("model", "") == TaskStep.META.url_name:
        task_step_id = int(par.get("pk", 0))

    task_id = 0
    if task_step_id > 0:
        qs = TaskStep.objects.filter(id=task_step_id).first()
        task_id = qs.task_id if qs else 0
    if task_id <= 0 and par.get("model", "") == Task.META.url_name:
        task_id = int(par.get("pk", 0))

    sprint_id = 0
    if task_id > 0:
        qs = Task.objects.filter(pk=task_id).exclude(sprint_id=None).first()
        sprint_id = qs.sprint_id if qs else 0
    if sprint_id <= 0 and par.get("model", "") == Sprint.META.url_name:
        sprint_id = int(par.get("pk", 0))

    proj_id = 0
    if task_id > 0:
        qs = Task.objects.filter(pk=task_id).exclude(proj_id=None).first()
        proj_id = qs.proj_id if qs else 0
    if proj_id <= 0 and sprint_id > 0:
        qs = Sprint.objects.filter(pk=sprint_id).exclude(proj_id=None).first()
        proj_id = qs.proj_id if qs else 0
    if proj_id <= 0 and par.get("model", "") == Proj.META.url_name:
        proj_id = int(par.get("pk", 0))

    # смотрим с какой страницы обращение
    list_qs = model.objects.all()
    if model_url == TaskStep.META.url_name:
        pk = task_id
        list_qs = list_qs.filter(id=pk)
    elif model_url == Sprint.META.url_name:
        list_qs = list_qs.filter(sprint_id=pk)
    elif model_url == Proj.META.url_name:
        list_qs = list_qs.filter(proj_id=pk)
    if pk <= 0 and task_id > 0:
        qs = Task.objects.filter(id=task_id).first()
        pk = qs.id if qs else 0
    one_qs = model.objects.filter(id=pk)

    match oper:
        case "list":
            # фильтры
            # фильтр поиска в названии
            if fnd := par.get("name_f", ""):
                list_qs = list_qs.filter(name_upper__contains=fnd.upper())

            # фильтр поиска по состоянию (выполнено, не выполнено, всё)
            match par.get(url_filt, ""):
                case "on":
                    list_qs = list_qs.exclude(date_end=None)
                case "all":
                    pass
                case _:
                    par[url_filt] = "off"
                    list_qs = list_qs.filter(date_end=None)

            # фильтр поиска по автору (автор, исполнитель, всё)
            match user.is_authenticated, par.get(url_user, ""):
                case True, "usr":
                    list_qs = list_qs.filter(user_id=user.id)
                case True, "aut":
                    list_qs = list_qs.filter(author_id=user.id)
                case _:
                    par[url_user] = "all"

            # создание объекта
            obj = ListView(
                queryset=list_qs,
                template_name="list_task.html",
                ordering=("-date_beg", "-id"),
                paginate_by=PAGINATE_BY,
                paginate_orphans=PAGINATE_ORPHANS,
                page_kwarg=model.META.url_page,
            )
        case "add":
            # присвоение своих значений
            self.request.POST._mutable = True
            self.request.POST["author"] = user.id
            self.request.POST["uweb"] = user.id
            self.request.POST._mutable = False
            # вычисление данных для страницы при успешном выполнении
            if add_pk := self.request.POST["sprint"]:
                add_model = Sprint.META.url_name
            elif add_pk := self.request.POST["proj"]:
                add_model = Proj.META.url_name
            else:
                add_model = Task.META.url_name
                add_pk = 0

            # создание объекта
            obj = CreateView(
                template_name="redirect.html",
                fields=[
                    "uweb",
                    "author",
                    "user",
                    "proj",
                    "sprint",
                    "parent",
                    "name",
                    "desc",
                    "date_max",
                ],
                success_url=reverse_lazy(
                    "detail",
                    kwargs={
                        "model": add_model,
                        "pk": add_pk,
                    },
                ),
            )
        case "edit":
            # присвоение своих значений
            self.request.POST._mutable = True
            self.request.POST["uweb"] = user.id
            # если юзер исполнитель, то меняем некоторые поля на текущие
            curr = one_qs.first()
            if curr.author_id != user.id and curr.user_id == user.id:
                for v in ("user", "name", "desc", "proj", "sprint", "parent"):
                    self.request.POST[v] = getattr(curr, v, None)
            self.request.POST._mutable = False

            # создание объекта
            obj = UpdateView(
                template_name="redirect.html",
                queryset=one_qs,
                fields=(
                    "uweb",
                    "user",
                    "date_end",
                    "date_max",
                    "name",
                    "desc",
                    "proj",
                    "sprint",
                    "parent",
                ),
                success_url=reverse_lazy(
                    "detail",
                    kwargs={
                        "model": model_url,
                        "pk": pk,
                    },
                ),
            )
        case "delete":
            # вычисление данных для страницы при успешном выполнении
            one_qs.first().proj_id
            if del_pk := one_qs.first().sprint_id:
                del_model = Sprint.META.url_name
            elif del_pk := one_qs.first().proj_id:
                del_model = Proj.META.url_name
            else:
                del_model = Task.META.url_name
                del_pk = 0

            # создание объекта
            obj = DeleteView(
                template_name="redirect.html",
                queryset=one_qs,
                success_url=reverse(
                    "detail",
                    kwargs={
                        "model": del_model,
                        "pk": del_pk,
                    },
                ),
            )
        case "detail" | _:
            # создание объекта
            obj = ListView(
                queryset=one_qs,
                template_name="detail_task.html",
            )
            # Первоначальные списки: список не закрытых проектов,
            # список не закрытых спринтов для текущего проекта
            # и список задач для текущего спринта.
            # При изменении данных на странице при редактировании
            # эти списки изменятся с помощью API и AJAX на самой странице.
            if oper_url == "edit" or oper_url == "add":
                obj.projs = Proj.objects.filter(date_end=None)
                obj.sprints = Sprint.objects.filter(date_end=None)
                one_task = one_qs.first()
                if one_task:
                    obj.sprints = obj.sprints.filter(proj=one_task.proj_id)
                    obj.parent = Task.objects.filter(
                        # date_end=None,
                        parent=None,
                        sprint_id=one_task.sprint_id,
                    )
                    if oper_url == "edit":
                        obj.parent = obj.parent.exclude(id=one_task.id)
                else:
                    obj.sprints = obj.sprints.filter(proj=proj_id)
                    obj.parent = Task.objects.filter(
                        # date_end=None,
                        parent=None,
                        sprint_id=sprint_id,
                    )

    # создание дополнительных атрибутов
    obj.kwargs = self.kwargs
    obj.model = model
    obj.request = self.request
    obj.context_object_name = "data"
    obj.url_filt = url_filt
    obj.url_user = url_user
    obj.url_name = url_name
    obj.fld = {v.name: v for v in obj.model._meta.get_fields()}
    obj.task_id = task_id
    obj.sprint_id = sprint_id
    obj.proj_id = proj_id
    obj.users = get_user_model().objects.all()
    obj.par = par
    obj.get_par = "&".join(map("=".join, par.items()))
    obj.is_no_end = False

    return obj


def TaskStepTemplate(self: TemplateView, oper: str) -> View:
    """Создание объекта с шаблоном для модели TaskStep.
    Вариант шаблона зависит от аргумета oper.

    Args:
        self (TemplateView): Родительский объект шаблона
        oper (str): Название текущей операции

    Returns:
        View: Объект шаблона в зависимости от аргумента oper.

    oper = (любое) -> ListView
    oper = 'add' -> CreateView
    """

    model = TaskStep
    par = self.request.GET.dict()
    model_url = self.kwargs.get("model")
    pk = self.kwargs.get("pk")
    user = self.request.user
    url_name = model.META.url_name
    url_filt = model.META.url_filt

    LOG.debug(
        "VIEW Создание вью для модели {!r}, операция {!r}".format(model.__name__, oper)
    )

    # если есть данные в GET о модели и ключе, то собираем их
    task_step_id = 0
    if par.get("model", "") == TaskStep.META.url_name:
        task_step_id = int(par.get("pk", 0))

    task_id = 0
    if task_step_id > 0:
        qs = TaskStep.objects.filter(id=task_step_id).first()
        task_id = qs.task_id if qs else 0
    if task_id <= 0 and par.get("model", "") == Task.META.url_name:
        task_id = int(par.get("pk", 0))

    # смотрим с какой страницы обращение
    if task_id <= 0 and model_url == Task.META.url_name:
        task_id = pk
    if task_id <= 0 and model_url == TaskStep.META.url_name:
        qs = TaskStep.objects.filter(id=pk).first()
        task_id = qs.task_id if qs else 0
    # one_qs = model.objects.filter(id=pk)
    list_qs = model.objects.filter(task_id=task_id)
    task = Task.objects.filter(id=task_id).first()

    match oper, bool(task):
        case "add", True:
            # присвоение своих значений
            self.request.POST._mutable = True
            self.request.POST["author"] = user.id
            self.request.POST["task"] = task_id
            self.request.POST._mutable = False
            # создание объекта
            obj = CreateView(
                fields=[
                    "desc",
                    "author",
                    "task",
                ],
                success_url=reverse_lazy(
                    "detail",
                    kwargs={
                        "model": Task.META.url_name,
                        "pk": task_id,
                    },
                ),
            )
        case _, _:
            # создание объекта
            obj = ListView(
                queryset=list_qs,
                template_name="list_task_step.html",
                ordering="-date_end",
                paginate_by=PAGINATE_BY,
                paginate_orphans=PAGINATE_ORPHANS,
                page_kwarg=model.META.url_page,
            )

    # создание дополнительных атрибутов
    obj.kwargs = self.kwargs
    obj.model = model
    obj.request = self.request
    obj.context_object_name = "data"
    obj.url_name = url_name
    obj.url_filt = url_filt
    obj.task = task
    obj.fld = {v.name: v for v in obj.model._meta.get_fields()}
    obj.get_par = "&".join(map("=".join, par.items()))

    return obj


class Index(TemplateView):
    template_name = "index.html"

    def get(self, request: HttpRequest, *args, **kwargs):
        oper = self.kwargs.get("oper", "")
        pk = self.kwargs.get("pk", 0)
        model = self.kwargs.get("model", "")
        perms = functions.get_perms(request)

        LOG.info("GET {}".format(self.kwargs))
        LOG.debug("PERMS Права доступа к модели {}={}".format(request.user, perms))

        if not perms.get(oper, False):
            text = "Нет прав для выполнения операции {}.".format(MY_OPER.get(oper, ""))
            LOG.warning(text)
            messages.warning(request, text)
            return HttpResponseRedirect("detail", kwargs={"model": model, "pk": pk})
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs):
        oper = self.kwargs.get("oper", "")
        pk = self.kwargs.get("pk", 0)
        model = self.kwargs.get("model", "")
        if oper not in ("add", "edit", "delete"):
            LOG.info("REDIRECT POST -> GET {}".format(self.kwargs))
            return HttpResponseRedirect(
                reverse("detail", kwargs={"model": model, "pk": pk})
            )

        perms = functions.get_perms(request)

        LOG.info("POST {}".format(self.kwargs))
        LOG.debug("PERMS Права доступа к модели {}={}".format(request.user, perms))

        if not perms.get(oper, False):
            text = "Нет прав для выполнения операции {}.".format(MY_OPER.get(oper, ""))
            LOG.warning(text)
            messages.warning(request, text)
            return HttpResponseRedirect(
                reverse("detail", kwargs={"model": model, "pk": pk})
            )

        match model:
            case Proj.META.url_name:
                obj = ProjTemplate(self, oper)
            case Sprint.META.url_name:
                obj = SprintTemplate(self, oper)
            case Task.META.url_name:
                obj = TaskTemplate(self, oper)
            case TaskStep.META.url_name:
                obj = TaskStepTemplate(self, oper)
            case _:
                text = f"Не найдена модель {model}"
                messages.warning(request, text)
                LOG.warning("POST {}".format(text))
                return HttpResponseRedirect(reverse("index"))
        out = obj.post(self, request, *args, **kwargs)
        messages.info(request, f"Операция {MY_OPER.get(oper, '')}.")
        return out

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.kwargs.get("model", "")
        pk = self.kwargs.get("pk", 0)
        objs = []

        match model, pk:
            case "finds", _:
                context["title"] = "Поиск"
                context["header"] = "Поиск в названиях проектов, спринтов и задач"
                objs.append(ProjTemplate(self, "list"))
                objs.append(SprintTemplate(self, "list"))
                objs.append(TaskTemplate(self, "list"))
            case Proj.META.url_name, 0:
                context["title"] = "Все проекты"
                context["header"] = "Все проекты"
                objs.append(ProjTemplate(self, "list"))
            case Sprint.META.url_name, 0:
                context["title"] = "Все спринты"
                context["header"] = "Все спринты"
                objs.append(SprintTemplate(self, "list"))
            case Task.META.url_name, 0:
                context["title"] = "Все задачи"
                context["header"] = "Все задачи"
                objs.append(TaskTemplate(self, "list"))
            case Proj.META.url_name, _:
                context["title"] = "Просмотр проекта"
                context["header"] = "Просмотр проекта"
                objs.append(ProjTemplate(self, "detail"))
                objs.append(SprintTemplate(self, "list"))
                objs.append(TaskTemplate(self, "list"))
            case Sprint.META.url_name, _:
                context["title"] = "Просмотр спринта"
                context["header"] = "Просмотр спринта"
                objs.append(SprintTemplate(self, "detail"))
                # objs.append(ProjTemplate(self, "detail"))
                objs.append(TaskTemplate(self, "list"))
            case Task.META.url_name, _:
                context["title"] = "Просмотр задачи"
                context["header"] = "Просмотр задачи"
                objs.append(TaskTemplate(self, "detail"))
                # objs.append(SprintTemplate(self, "detail"))
                # objs.append(ProjTemplate(self, "detail"))
                objs.append(TaskStepTemplate(self, "list"))
            case TaskStep.META.url_name, _:
                context["title"] = "Просмотр задачи"
                context["header"] = "Просмотр задачи"
                objs.append(TaskTemplate(self, "detail"))
                objs.append(TaskStepTemplate(self, "list"))
            case _:
                text = f"Не найдена модель {model}"
                messages.warning(self.request, text)
                LOG.warning("GET {}".format(text))

        try:
            context["details"] = [v.get(self.request) for v in objs]
        except Exception as err:
            text = f"ERROR: {type(err).__name__} - {err}"
            LOG.error("Ошибка рендеринга {}".format(text))
            context["details"] = [{"rendered_content": text}]

        return context
