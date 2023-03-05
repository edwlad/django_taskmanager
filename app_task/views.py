from django.shortcuts import render  # noqa
from django.http.response import HttpResponseRedirect, HttpResponse  # noqa
from django.http.request import HttpRequest  # noqa
from django.db import models  # noqa
from django.urls import reverse, reverse_lazy  # noqa
from django.conf import settings
from django.contrib.auth import get_user_model

from django.contrib import messages

# from django.contrib.messages.views import SuccessMessageMixin

from django.views.generic import (
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


def error(req: HttpRequest, *args, **kwargs) -> HttpResponse:
    status = int(kwargs.get("status", 400))
    title = kwargs.get("title", "Ошибка")
    content = kwargs.get("content", f"<p>Код ошибки: {status}</p>")
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


def ProjTemplate(self: TemplateView, oper):
    model = Proj
    par = self.request.GET.dict()
    model_url = self.kwargs.get("model")
    pk = self.kwargs.get("pk")
    user = self.request.user
    url_name = model.META.url_name
    url_filt = model.META.url_filt
    url_user = model.META.url_user

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
    list_qs = model.objects
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
            if fnd := par.get("name_f", ""):
                list_qs = list_qs.filter(name__icontains=fnd)

            match par.get(url_filt, ""):
                case "on":
                    list_qs = list_qs.exclude(date_end=None)
                case "all":
                    pass
                case _:
                    par[url_filt] = "off"
                    list_qs = list_qs.filter(date_end=None)

            match user.is_authenticated, par.get(url_user, ""):
                case (False, _) | (_, "all"):
                    pass
                case _:
                    par[url_user] = "aut"
                    list_qs = list_qs.filter(author_id=user.id)

            obj = ListView(
                queryset=list_qs,
                template_name="list_proj.html",
                ordering=("-date_beg", "-id"),
                paginate_by=PAGINATE_BY,
                paginate_orphans=PAGINATE_ORPHANS,
                page_kwarg=model.META.url_page,
            )
        case "add":
            self.request.POST._mutable = True
            self.request.POST["author"] = user.id
            self.request.POST["uweb"] = user.id
            self.request.POST._mutable = False
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
            self.request.POST._mutable = True
            self.request.POST["uweb"] = user.id
            self.request.POST._mutable = False
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
            obj = ListView(
                queryset=one_qs,
                template_name="detail_proj.html",
            )

    obj.kwargs = self.kwargs
    obj.model = model
    obj.request = self.request
    obj.context_object_name = "data"
    obj.is_no_end = (
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


def SprintTemplate(self: TemplateView, oper):
    model = Sprint
    par = self.request.GET.dict()
    oper_url = self.kwargs.get("oper")
    model_url = self.kwargs.get("model")
    pk = self.kwargs.get("pk")
    user = self.request.user
    url_name = model.META.url_name
    url_filt = model.META.url_filt
    url_user = model.META.url_user

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
    list_qs = model.objects
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
            if fnd := par.get("name_f", ""):
                list_qs = list_qs.filter(name__icontains=fnd)

            match par.get(url_filt, ""):
                case "on":
                    list_qs = list_qs.exclude(date_end=None)
                case "all":
                    pass
                case _:
                    par[url_filt] = "off"
                    list_qs = list_qs.filter(date_end=None)

            match user.is_authenticated, par.get(url_user, ""):
                case (False, _) | (_, "all"):
                    pass
                case _:
                    par[url_user] = "aut"
                    list_qs = list_qs.filter(author_id=user.id)

            obj = ListView(
                queryset=list_qs,
                template_name="list_sprint.html",
                ordering=("-date_beg", "-id"),
                paginate_by=PAGINATE_BY,
                paginate_orphans=PAGINATE_ORPHANS,
                page_kwarg=model.META.url_page,
            )
        case "add":
            self.request.POST._mutable = True
            self.request.POST["author"] = user.id
            self.request.POST["uweb"] = user.id
            self.request.POST._mutable = False
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
            self.request.POST._mutable = True
            self.request.POST["uweb"] = user.id
            self.request.POST._mutable = False
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
            obj = ListView(
                queryset=one_qs,
                template_name="detail_sprint.html",
            )
            if oper_url == "edit" or oper_url == "add":
                obj.projs = Proj.objects.filter(date_end=None)

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
    obj.is_no_end = (
        self.kwargs["oper"] == "edit"
        and one_qs.exists()
        and one_qs[0].sprint_tasks.filter(date_end=None).exists()
    )
    return obj


def TaskTemplate(self: TemplateView, oper):
    model = Task
    par = self.request.GET.dict()
    oper_url = self.kwargs.get("oper")
    model_url = self.kwargs.get("model")
    pk = self.kwargs.get("pk")
    user = self.request.user
    url_name = model.META.url_name
    url_filt = model.META.url_filt
    url_user = model.META.url_user

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
            if fnd := par.get("name_f", ""):
                list_qs = list_qs.filter(name__icontains=fnd)

            match par.get(url_filt, ""):
                case "on":
                    list_qs = list_qs.exclude(date_end=None)
                case "all":
                    pass
                case _:
                    par[url_filt] = "off"
                    list_qs = list_qs.filter(date_end=None)

            match user.is_authenticated, par.get(url_user, ""):
                case (False, _) | (_, "all"):
                    pass
                case _, "aut":
                    list_qs = list_qs.filter(author_id=user.id)
                case _:
                    par[url_user] = "usr"
                    list_qs = list_qs.filter(user_id=user.id)

            obj = ListView(
                queryset=list_qs,
                template_name="list_task.html",
                ordering=("-date_beg", "-id"),
                paginate_by=PAGINATE_BY,
                paginate_orphans=PAGINATE_ORPHANS,
                page_kwarg=model.META.url_page,
            )
        case "add":
            self.request.POST._mutable = True
            self.request.POST["author"] = user.id
            self.request.POST["uweb"] = user.id
            self.request.POST._mutable = False

            if add_pk := self.request.POST["sprint"]:
                add_model = Sprint.META.url_name
            elif add_pk := self.request.POST["proj"]:
                add_model = Proj.META.url_name
            else:
                add_model = Task.META.url_name
                add_pk = 0

            obj = CreateView(
                template_name="redirect.html",
                fields=[
                    "uweb",
                    "author",
                    "user",
                    "proj",
                    "sprint",
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
            self.request.POST._mutable = True
            self.request.POST["uweb"] = user.id
            # если юзер исполнитель, то меняем некоторые поля на текущие
            curr = one_qs.first()
            if curr.author_id != user.id and curr.user_id == user.id:
                for v in ("user", "name", "desc", "proj", "sprint"):
                    self.request.POST[v] = getattr(curr, v, None)
            self.request.POST._mutable = False
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
            one_qs.first().proj_id
            if del_pk := one_qs.first().sprint_id:
                del_model = Sprint.META.url_name
            elif del_pk := one_qs.first().proj_id:
                del_model = Proj.META.url_name
            else:
                del_model = Task.META.url_name
                del_pk = 0

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
            obj = ListView(
                queryset=one_qs,
                template_name="detail_task.html",
            )
            if oper_url == "edit" or oper_url == "add":
                obj.projs = Proj.objects.filter(date_end=None)
                obj.sprints = Sprint.objects.filter(date_end=None)
                if temp := one_qs.first():
                    obj.sprints = obj.sprints.filter(proj=temp.proj_id)
                else:
                    obj.sprints = obj.sprints.filter(proj=proj_id)

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


def TaskStepTemplate(self: TemplateView, oper):
    model = TaskStep
    par = self.request.GET.dict()
    model_url = self.kwargs.get("model")
    pk = self.kwargs.get("pk")
    user = self.request.user
    url_name = model.META.url_name
    url_filt = model.META.url_filt

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
            self.request.POST._mutable = True
            self.request.POST["author"] = user.id
            self.request.POST["task"] = task_id
            self.request.POST._mutable = False
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
            obj = ListView(
                queryset=list_qs,
                template_name="list_task_step.html",
                ordering="-date_end",
                paginate_by=PAGINATE_BY,
                paginate_orphans=PAGINATE_ORPHANS,
                page_kwarg=model.META.url_page,
            )

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
        perms = functions.get_perms(request)
        if not perms.get(self.kwargs["oper"], False):
            messages.warning(
                request, f"Нет прав для выполнения операции {self.kwargs['oper']}"
            )
            return HttpResponseRedirect(reverse("index"))
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs):
        perms = functions.get_perms(request)
        if not perms.get(self.kwargs["oper"], False):
            messages.warning(
                request,
                f"Нет прав для выполнения операции {self.kwargs.get('oper', '')}",
            )
            return HttpResponseRedirect(reverse("index"))

        match self.kwargs.get("model"):
            case Proj.META.url_name:
                obj = ProjTemplate(self, self.kwargs.get("oper"))
            case Sprint.META.url_name:
                obj = SprintTemplate(self, self.kwargs.get("oper"))
            case Task.META.url_name:
                obj = TaskTemplate(self, self.kwargs.get("oper"))
            case TaskStep.META.url_name:
                obj = TaskStepTemplate(self, self.kwargs.get("oper"))
            case _:
                messages.warning(
                    request, f"Не найдена модель {self.kwargs.get('model', '')}"
                )
                return HttpResponseRedirect(reverse("index"))
        out = obj.post(self, request, *args, **kwargs)
        messages.info(request, f"Операция {self.kwargs.get('oper', '')} выполнена.")
        return out

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        objs = []

        match self.kwargs.get("model"), self.kwargs.get("pk"):
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
                messages.warning(
                    self.request, f"Не найдена модель {self.kwargs.get('model', '')}"
                )

        try:
            context["details"] = [v.get(self.request) for v in objs]
        except Exception as err:
            text = f"ERROR: {type(err).__name__} - {err}"
            # print(text)
            context["details"] = [{"rendered_content": text}]

        return context
