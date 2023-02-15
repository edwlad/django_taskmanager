from django.shortcuts import render  # noqa
from django.http.response import HttpResponseRedirect, HttpResponse  # noqa
from django.http.request import HttpRequest  # noqa
from django.db import models  # noqa
from django.urls import reverse, reverse_lazy  # noqa

from django.views.generic import (
    TemplateView,
    ListView,
    # DetailView,
    UpdateView,
    CreateView,
    DeleteView,
)
from .models import Proj, Sprint, Task, TaskStep
from django.conf import settings
from api_task.serializers import (
    ProjSerializer,
    SprintSerializer,
    TaskSerializer,
    TaskStepSerializer,
)

# from datetime import date

PAGINATE_BY = settings.PAGINATE_BY
PAGINATE_ORPHANS = settings.PAGINATE_ORPHANS


def error(req: HttpRequest, *args, **kwargs):
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
    par = self.request.GET.dict() | self.kwargs
    model_url = str(par.get("model", ""))
    pk = str(par.get("pk", "0"))
    # oper = str(par.get("oper", "detail"))
    url_name = model.META.url_name

    match oper:
        case "list":
            list_queryset = model.objects.all()
            if model_url == Sprint.META.url_name:
                pk = Sprint.objects.filter(id=pk).get().proj_id
            elif model_url == Task.META.url_name:
                pk = Task.objects.filter(id=pk).get().proj_id

            match par.get(url_name, ""):
                case "on":
                    list_queryset = list_queryset.exclude(date_end=None)
                case "all":
                    pass
                case _:
                    par[url_name] = "off"
                    list_queryset = list_queryset.filter(date_end=None)

            obj = ListView(
                queryset=list_queryset,
                template_name="list_proj.html",
                ordering=("-date_beg", "-id"),
                paginate_by=PAGINATE_BY,
                paginate_orphans=PAGINATE_ORPHANS,
                page_kwarg=f"{url_name}_page",
            )
        case "add":
            self.request.POST._mutable = True
            self.request.POST["author"] = self.request.user.id
            self.request.POST._mutable = False

            obj = CreateView(
                fields=["author", "name", "desc", "date_end", "date_max"],
                template_name="detail_proj.html",
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
                queryset=model.objects.filter(id=pk),
                success_url=reverse(
                    "list",
                    kwargs={
                        "model": model_url,
                    },
                ),
            )
        case "detail" | _:
            obj = ListView(
                queryset=model.objects.filter(id=pk),
                template_name="detail_proj.html",
            )

    obj.kwargs = self.kwargs
    obj.model = model
    obj.request = self.request
    obj.context_object_name = "data"
    obj.fld = {v.name: v for v in obj.model._meta.get_fields()}
    obj.url_name = url_name
    obj.par = par
    obj.get_par = "&".join(map("=".join, par.items()))
    obj.ser = ProjSerializer
    # obj.api = {v.data["id"]: v.data for v in map(ProjSerializer, obj.queryset)}
    return obj


def SprintTemplate(self: TemplateView, key):
    model = Sprint
    par = self.request.GET.dict() | self.kwargs
    model_url = str(par.get("model", ""))
    pk = str(par.get("pk", "0"))
    url_name = model.META.url_name

    match key:
        case "list":
            list_queryset = model.objects.all()
            if model_url == Proj.META.url_name:
                list_queryset = list_queryset.filter(proj_id=pk)
            elif model_url == Task.META.url_name:
                pk = Task.objects.filter(id=pk).get().proj_id

            match par.get(url_name, ""):
                case "on":
                    list_queryset = list_queryset.exclude(date_end=None)
                case "all":
                    pass
                case _:
                    par[url_name] = "off"
                    list_queryset = list_queryset.filter(date_end=None)

            obj = ListView(
                queryset=list_queryset,
                template_name="list_sprint.html",
                ordering="-date_beg",
                paginate_by=PAGINATE_BY,
                paginate_orphans=PAGINATE_ORPHANS,
                page_kwarg=f"{url_name}_page",
            )
        case "add":
            pass
        case "edit":
            obj = UpdateView(
                queryset=model.objects.filter(id=pk),
                # template_name="detail_sprint.html",
                fields=["name", "desc", "date_end", "date_max", "proj"],
                success_url=reverse_lazy(
                    "oper",
                    kwargs={
                        "oper": "detail",
                        "model": model_url,
                        "pk": pk,
                    },
                ),
            )
        case "delete":
            pass
        case _:
            obj = ListView(
                queryset=model.objects.filter(id=pk),
                template_name="detail_sprint.html",
            )

    obj.kwargs = self.kwargs
    obj.model = model
    obj.request = self.request
    obj.context_object_name = "data"
    obj.projs = Proj.objects.filter(date_end=None)
    obj.fld = {v.name: v for v in obj.model._meta.get_fields()}
    obj.url_name = url_name
    obj.par = par
    obj.get_par = "&".join(map("=".join, par.items()))
    obj.ser = SprintSerializer
    return obj


def TaskTemplate(self: TemplateView, key):
    model = Task
    par = self.request.GET.dict() | self.kwargs
    model_url = str(par.get("model", ""))
    pk = str(par.get("pk", "0"))
    url_name = model.META.url_name

    match key:
        case "list":
            list_queryset = model.objects.all()
            if model_url == Sprint.META.url_name:
                list_queryset = list_queryset.filter(sprint_id=pk)
            elif model_url == Proj.META.url_name:
                list_queryset = list_queryset.filter(proj_id=pk)

            match par.get(url_name, ""):
                case "on":
                    list_queryset = list_queryset.exclude(date_end=None)
                case "all":
                    pass
                case _:
                    par[url_name] = "off"
                    list_queryset = list_queryset.filter(date_end=None)

            obj = ListView(
                queryset=list_queryset,
                template_name="list_task.html",
                ordering="-date_beg",
                paginate_by=PAGINATE_BY,
                paginate_orphans=PAGINATE_ORPHANS,
                page_kwarg=f"{url_name}_page",
            )
        case "add":
            pass
        case "edit":
            obj = UpdateView(
                queryset=model.objects.filter(id=pk),
                # template_name="detail_task.html",
                fields=["name", "desc", "date_end", "date_max", "proj", "sprint"],
                success_url=reverse_lazy(
                    "oper",
                    kwargs={
                        "oper": "detail",
                        "model": model_url,
                        "pk": pk,
                    },
                ),
            )
        case "delete":
            pass
        case _:
            obj = ListView(
                queryset=model.objects.filter(id=pk),
                template_name="detail_task.html",
            )

    obj.kwargs = self.kwargs
    obj.model = model
    obj.request = self.request
    obj.context_object_name = "data"
    obj.fld = {v.name: v for v in obj.model._meta.get_fields()}
    obj.projs = Proj.objects.filter(date_end=None)
    obj.sprints = Sprint.objects.filter(date_end=None)
    # obj.sprints = Sprint.objects.filter(date_end=None).filter(
    #     proj_id=model.objects.filter(id=pk).get().proj.id
    # )
    obj.url_name = url_name
    obj.par = par
    obj.get_par = "&".join(map("=".join, par.items()))
    obj.ser = TaskSerializer
    return obj


def TaskStepTemplate(self: TemplateView, key):
    model = TaskStep
    par = self.request.GET.dict() | self.kwargs
    pk = str(par.get("pk", "0"))
    url_name = model.META.url_name

    match key:
        case "list":
            list_queryset = model.objects.filter(task_id=pk)

            obj = ListView(
                queryset=list_queryset,
                template_name="list_task_step.html",
                ordering="-date_end",
                paginate_by=PAGINATE_BY,
                paginate_orphans=PAGINATE_ORPHANS,
                page_kwarg=f"{url_name}_page",
            )
        case _:
            pass

    obj.kwargs = self.kwargs
    obj.model = model
    obj.request = self.request
    obj.context_object_name = "data"
    obj.fields = {v.name: v for v in obj.model._meta.get_fields()}
    obj.url_name = url_name
    obj.par = par
    obj.get_par = "&".join(map("=".join, par.items()))
    obj.ser = TaskStepSerializer
    return obj


class Index(TemplateView):
    template_name = "index.html"

    def chk_par(self):
        self.kwargs["oper"] = str(
            self.kwargs.get("oper", "") or self.request.GET.get("oper", "list")
        )
        self.kwargs["model"] = str(
            self.kwargs.get("model", "") or self.request.GET.get("model", "")
        )
        self.kwargs["pk"] = str(
            self.kwargs.get("pk", "") or self.request.GET.get("pk", "0")
        )

    def post(self, request, *args, **kwargs):
        self.chk_par()
        match self.kwargs.get("model"):
            case Proj.META.url_name:
                obj = ProjTemplate(self, self.kwargs.get("oper"))
            case Sprint.META.url_name:
                obj = SprintTemplate(self, self.kwargs.get("oper"))
            case Task.META.url_name:
                obj = TaskTemplate(self, self.kwargs.get("oper"))
            case _:
                url = reverse(
                    "detail",
                    kwargs={
                        "model": self.kwargs.get("model"),
                        "pk": self.kwargs.get("pk"),
                    },
                )
                return HttpResponseRedirect(url)

        return obj.post(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.chk_par()

        objs = []

        match self.kwargs.get("model"), self.kwargs.get("pk"):
            case Proj.META.url_name, "0":
                context["title"] = "Все проекты"
                context["header"] = "Все проекты"
                objs.append(ProjTemplate(self, self.kwargs["oper"]))
            case Sprint.META.url_name, "0":
                context["title"] = "Все спринты"
                context["header"] = "Все спринты"
                objs.append(SprintTemplate(self, "list"))
            case Task.META.url_name, "0":
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
