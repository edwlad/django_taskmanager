from django.shortcuts import render  # noqa
from django.http.response import HttpResponseRedirect, HttpResponse  # noqa
from django.http.request import HttpRequest  # noqa
from django.db import models  # noqa
from django.urls import reverse, reverse_lazy  # noqa
from django.conf import settings
from django.contrib.auth.models import User

from django.views.generic import (
    TemplateView,
    ListView,
    # DetailView,
    UpdateView,
    CreateView,
    DeleteView,
)
from .models import Proj, Sprint, Task, TaskStep
from api_task.serializers import (
    ProjSerializer,
    SprintSerializer,
    TaskSerializer,
    TaskStepSerializer,
)

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
    url_name = model.META.url_name
    url_filt = model.META.url_filt

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
    if model_url == Sprint.META.url_name:
        qs = Sprint.objects.filter(id=pk).exclude(proj_id=None).first()
        pk = qs.proj_id if qs else 0
    elif model_url == Task.META.url_name:
        qs = Task.objects.filter(id=pk).exclude(proj_id=None).first()
        pk = qs.proj_id if qs else 0
    if pk <= 0 and proj_id > 0:
        qs = Proj.objects.filter(id=proj_id).first()
        pk = qs.id if qs else 0
    one_qs = model.objects.filter(id=pk)

    match oper:
        case "list":
            match par.get(url_filt, ""):
                case "on":
                    list_qs = list_qs.exclude(date_end=None)
                case "all":
                    pass
                case _:
                    par[url_filt] = "off"
                    list_qs = list_qs.filter(date_end=None)

            obj = ListView(
                queryset=list_qs,
                template_name="list_proj.html",
                ordering=("-date_beg", "-id"),
                paginate_by=PAGINATE_BY,
                paginate_orphans=PAGINATE_ORPHANS,
                page_kwarg=model.META.url_page,
            )
        case "add":
            obj = CreateView(
                fields=["author", "name", "desc", "date_end", "date_max"],
                success_url=reverse_lazy(
                    "list",
                    kwargs={
                        "model": model_url,
                    },
                ),
            )
        case "edit":
            obj = UpdateView(
                fields=["name", "desc", "date_end", "date_max"],
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
    obj.url_filt = url_filt
    obj.url_name = url_name
    obj.fld = {v.name: v for v in obj.model._meta.get_fields()}
    obj.get_par = "&".join(map("=".join, par.items()))
    obj.ser = ProjSerializer
    # obj.api = {v.data["id"]: v.data for v in map(ProjSerializer, obj.queryset)}
    return obj


def SprintTemplate(self: TemplateView, oper):
    model = Sprint
    par = self.request.GET.dict()
    model_url = self.kwargs.get("model")
    pk = self.kwargs.get("pk")
    url_name = model.META.url_name
    url_filt = model.META.url_filt

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
            match par.get(url_filt, ""):
                case "on":
                    list_qs = list_qs.exclude(date_end=None)
                case "all":
                    pass
                case _:
                    par[url_filt] = "off"
                    list_qs = list_qs.filter(date_end=None)

            obj = ListView(
                queryset=list_qs,
                template_name="list_sprint.html",
                ordering=("-date_beg", "-id"),
                paginate_by=PAGINATE_BY,
                paginate_orphans=PAGINATE_ORPHANS,
                page_kwarg=model.META.url_page,
            )
        case "add":
            obj = CreateView(
                fields=["author", "proj", "name", "desc", "date_end", "date_max"],
                success_url=reverse_lazy(
                    "list",
                    kwargs={
                        "model": model_url,
                    },
                ),
            )
        case "edit":
            obj = UpdateView(
                queryset=one_qs,
                fields=["name", "desc", "date_end", "date_max", "proj"],
                success_url=reverse_lazy(
                    "detail",
                    kwargs={
                        "model": model_url,
                        "pk": pk,
                    },
                ),
            )
        case "delete":
            obj = DeleteView(
                queryset=one_qs,
                success_url=reverse(
                    "list",
                    kwargs={
                        "model": model_url,
                    },
                ),
            )
        case _:
            obj = ListView(
                queryset=model.objects.filter(id=pk),
                template_name="detail_sprint.html",
            )

    obj.kwargs = self.kwargs
    obj.model = model
    obj.request = self.request
    obj.context_object_name = "data"
    obj.url_filt = url_filt
    obj.url_name = url_name
    obj.fld = {v.name: v for v in obj.model._meta.get_fields()}
    obj.task_id = task_id
    obj.sprint_id = sprint_id
    obj.proj_id = proj_id
    obj.projs = Proj.objects.filter(date_end=None)
    obj.get_par = "&".join(map("=".join, par.items()))
    obj.ser = SprintSerializer
    # obj.api = {v.data["id"]: v.data for v in map(SprintSerializer, obj.queryset)}
    return obj


def TaskTemplate(self: TemplateView, oper):
    model = Task
    par = self.request.GET.dict()
    model_url = self.kwargs.get("model")
    pk = self.kwargs.get("pk")
    url_name = model.META.url_name
    url_filt = model.META.url_filt

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
    if model_url == Sprint.META.url_name:
        list_qs = list_qs.filter(sprint_id=pk)
    elif model_url == Proj.META.url_name:
        list_qs = list_qs.filter(proj_id=pk)
    one_qs = model.objects.filter(id=pk)

    match oper:
        case "list":
            match par.get(url_filt, ""):
                case "on":
                    list_qs = list_qs.exclude(date_end=None)
                case "all":
                    pass
                case _:
                    par[url_filt] = "off"
                    list_qs = list_qs.filter(date_end=None)

            obj = ListView(
                queryset=list_qs,
                template_name="list_task.html",
                ordering=("-date_beg", "-id"),
                paginate_by=PAGINATE_BY,
                paginate_orphans=PAGINATE_ORPHANS,
                page_kwarg=model.META.url_page,
            )
        case "add":
            obj = CreateView(
                fields=[
                    "author",
                    "user",
                    "proj",
                    "sprint",
                    "name",
                    "desc",
                    "date_end",
                    "date_max",
                ],
                success_url=reverse_lazy(
                    "list",
                    kwargs={
                        "model": model_url,
                    },
                ),
            )
        case "edit":
            obj = UpdateView(
                queryset=one_qs,
                fields=[
                    "user",
                    "name",
                    "desc",
                    "date_end",
                    "date_max",
                    "proj",
                    "sprint",
                ],
                success_url=reverse_lazy(
                    "detail",
                    kwargs={
                        "model": model_url,
                        "pk": pk,
                    },
                ),
            )
        case "delete":
            obj = DeleteView(
                queryset=one_qs,
                success_url=reverse(
                    "list",
                    kwargs={
                        "model": model_url,
                    },
                ),
            )
        case _:
            obj = ListView(
                queryset=one_qs,
                template_name="detail_task.html",
            )

    obj.kwargs = self.kwargs
    obj.model = model
    obj.request = self.request
    obj.context_object_name = "data"
    obj.url_filt = url_filt
    obj.url_name = url_name
    obj.fld = {v.name: v for v in obj.model._meta.get_fields()}
    obj.task_id = task_id
    obj.sprint_id = sprint_id
    obj.proj_id = proj_id
    obj.projs = Proj.objects.filter(date_end=None)
    obj.sprints = Sprint.objects.filter(date_end=None)
    obj.users = User.objects.all()
    obj.par = par
    obj.get_par = "&".join(map("=".join, par.items()))
    obj.ser = TaskSerializer
    # obj.api = {v.data["id"]: v.data for v in map(TaskSerializer, obj.queryset)}
    return obj


def TaskStepTemplate(self: TemplateView, oper):
    model = TaskStep
    par = self.request.GET.dict()
    # model_url = self.kwargs.get("model")
    pk = self.kwargs.get("pk")
    url_name = model.META.url_name
    url_filt = model.META.url_filt

    match oper:
        case "list":
            list_qs = model.objects.filter(task_id=pk)

            obj = ListView(
                queryset=list_qs,
                template_name="list_task_step.html",
                ordering=("-date_end", "-id"),
                paginate_by=PAGINATE_BY,
                paginate_orphans=PAGINATE_ORPHANS,
                page_kwarg=model.META.url_page,
            )
        case _:
            pass

    obj.kwargs = self.kwargs
    obj.model = model
    obj.request = self.request
    obj.context_object_name = "data"
    obj.url_name = url_name
    obj.url_filt = url_filt
    obj.fields = {v.name: v for v in obj.model._meta.get_fields()}
    obj.get_par = "&".join(map("=".join, par.items()))
    obj.ser = TaskStepSerializer
    # obj.api = {v.data["id"]: v.data for v in map(TaskStepSerializer, obj.queryset)}
    return obj


class Index(TemplateView):
    template_name = "index.html"

    def post(self, request, *args, **kwargs):
        if not self.request.POST.get("author", None):
            self.request.POST._mutable = True
            self.request.POST["author"] = self.request.user.id
            self.request.POST._mutable = False

        match self.kwargs.get("model"):
            case Proj.META.url_name:
                obj = ProjTemplate(self, self.kwargs.get("oper"))
            case Sprint.META.url_name:
                obj = SprintTemplate(self, self.kwargs.get("oper"))
            case Task.META.url_name:
                obj = TaskTemplate(self, self.kwargs.get("oper"))
            case _:
                return HttpResponseRedirect(reverse("index"))

        return obj.post(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        objs = []

        match self.kwargs.get("model"), self.kwargs.get("pk"):
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
                objs.append(ProjTemplate(self, "detail"))
                objs.append(TaskTemplate(self, "list"))
            case Task.META.url_name, _:
                context["title"] = "Просмотр задачи"
                context["header"] = "Просмотр задачи"
                objs.append(TaskTemplate(self, "detail"))
                objs.append(SprintTemplate(self, "detail"))
                objs.append(ProjTemplate(self, "detail"))
                objs.append(TaskStepTemplate(self, "list"))
            case TaskStep.META.url_name, _:
                context["title"] = "Просмотр шага"
                context["header"] = "Просмотр шага"
            case _:
                pass

        try:
            context["details"] = [v.get(self.request) for v in objs]
        except Exception as err:
            text = f"ERROR: {type(err).__name__} - {err}"
            # print(text)
            context["details"] = [{"rendered_content": text}]

        return context
