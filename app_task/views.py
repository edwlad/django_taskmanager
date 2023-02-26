from django.shortcuts import render  # noqa
from django.http.response import HttpResponseRedirect, HttpResponse  # noqa
from django.http.request import HttpRequest  # noqa
from django.db import models  # noqa
from django.urls import reverse, reverse_lazy  # noqa
from django.conf import settings
from django.contrib.auth import get_user_model

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
    list_qs = model.objects
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
            self.request.POST._mutable = True
            self.request.POST["author"] = self.request.user.id
            self.request.POST["uweb"] = self.request.user.id
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
            self.request.POST["uweb"] = self.request.user.id
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
            self.request.POST._mutable = True
            self.request.POST["author"] = self.request.user.id
            self.request.POST["uweb"] = self.request.user.id
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
            self.request.POST["uweb"] = self.request.user.id
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
    obj.is_no_end = (
        self.kwargs["oper"] == "edit"
        and one_qs.exists()
        and one_qs[0].sprint_tasks.filter(date_end=None).exists()
    )
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
    list_qs = model.objects
    if model_url == TaskStep.META.url_name:
        pk = task_id
        list_qs = list_qs.filter(id=pk)
    elif model_url == Sprint.META.url_name:
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
            self.request.POST._mutable = True
            self.request.POST["author"] = self.request.user.id
            self.request.POST["uweb"] = self.request.user.id
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
            edit_fld = (
                "uweb",
                "user",
                "name",
                "desc",
                "date_end",
                "date_max",
                "proj",
                "sprint",
            )
            self.request.POST._mutable = True
            self.request.POST["uweb"] = self.request.user.id
            # если не хватает данных добавляем из текущей записи
            curr = one_qs.first()
            for v in edit_fld:
                if v not in self.request.POST:
                    self.request.POST[v] = getattr(curr, v, None)
            self.request.POST._mutable = False
            obj = UpdateView(
                template_name="redirect.html",
                queryset=one_qs,
                fields=edit_fld,
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
    obj.users = get_user_model().objects.all()
    obj.par = par
    obj.get_par = "&".join(map("=".join, par.items()))
    obj.is_no_end = False
    obj.ser = TaskSerializer
    # obj.api = {v.data["id"]: v.data for v in map(TaskSerializer, obj.queryset)}
    return obj


def TaskStepTemplate(self: TemplateView, oper):
    model = TaskStep
    par = self.request.GET.dict()
    model_url = self.kwargs.get("model")
    pk = self.kwargs.get("pk")
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
            self.request.POST["author"] = self.request.user.id
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
    obj.ser = TaskStepSerializer
    # obj.api = {v.data["id"]: v.data for v in map(TaskStepSerializer, obj.queryset)}
    return obj


class Index(TemplateView):
    template_name = "index.html"

    def get_perms(self, request: HttpRequest, obj_in: models.Model = None):
        kw = request.resolver_match.kwargs
        user = request.user

        if isinstance(obj_in, models.Model):
            obj = obj_in
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
            has_obj = isinstance(obj, models.Model)
            if not has_obj:
                obj = model

        temp: str = (
            f"{obj._meta.app_label}.{{}}_{obj._meta.verbose_name.replace(' ', '')}"
        )
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
        p_de = (
            hasattr(obj, "proj") and hasattr(obj.proj, "date_end") and obj.proj.date_end
        )
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

    def get(self, request: HttpRequest, *args, **kwargs):
        perms = self.get_perms(request)
        if not perms.get(self.kwargs["oper"], False):
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs):
        perms = self.get_perms(request)
        if not perms.get(self.kwargs["oper"], False):
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))

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
                pass

        try:
            context["details"] = [v.get(self.request) for v in objs]
        except Exception as err:
            text = f"ERROR: {type(err).__name__} - {err}"
            # print(text)
            context["details"] = [{"rendered_content": text}]

        return context
