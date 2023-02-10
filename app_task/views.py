from django.shortcuts import render  # noqa
from django.http.response import HttpResponse, Http404  # noqa
from django.http.request import HttpRequest  # noqa
from django.db import models  # noqa
from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
    # UpdateView,
    # CreateView,
    # DeleteView,
)
from .models import Proj, Sprint, Task, TaskStep

# from django.urls import reverse, reverse_lazy
# from datetime import datetime


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


def ProjTemplate(request, key, **kwargs):
    model = Proj
    # model_url = kwargs.get("model", "")
    # pk_url = kwargs.get("pk", 0)

    list_queryset = model.objects.all()
    match key:
        case "list":
            obj = ListView(
                queryset=list_queryset,
                template_name="list_proj.html",
                ordering="-date_beg",
            )
        case _:
            obj = DetailView(
                # queryset=Task.objects.annotate(title=models.Value("Проект")),
                template_name="detail_proj.html",
            )
    obj.model = model
    obj.request = request
    obj.kwargs = kwargs
    obj.context_object_name = "data"
    obj.fields = {v.name: v for v in obj.model._meta.get_fields()}
    obj.url_name = obj.model.META.url_name
    return obj


def SprintTemplate(request, key, **kwargs):
    model = Sprint
    model_url = kwargs.get("model", "")
    pk_url = kwargs.get("pk", 0)

    if model_url == Proj.META.url_name:
        list_queryset = model.objects.filter(proj_id=pk_url)
    else:
        list_queryset = model.objects.all()
    match key:
        case "list":
            obj = ListView(
                queryset=list_queryset,
                template_name="list_sprint.html",
                ordering="-date_beg",
            )
        case _:
            obj = DetailView(
                # queryset=model.objects.annotate(title=models.Value("Проект")),
                template_name="detail_sprint.html",
            )
    obj.model = model
    obj.request = request
    obj.kwargs = kwargs
    obj.context_object_name = "data"
    obj.fields = {v.name: v for v in obj.model._meta.get_fields()}
    obj.url_name = obj.model.META.url_name
    return obj


def TaskTemplate(request, key, **kwargs):
    model = Task
    model_url = kwargs.get("model", "")
    pk_url = kwargs.get("pk", 0)

    if model_url == Sprint.META.url_name:
        list_queryset = model.objects.filter(sprint_id=pk_url)
    elif model_url == Proj.META.url_name:
        list_queryset = model.objects.filter(proj_id=pk_url)
    else:
        list_queryset = model.objects.all()
    match key:
        case "list":
            obj = ListView(
                queryset=list_queryset,
                template_name="list_task.html",
                ordering="-date_beg",
            )
        case _:
            obj = DetailView(
                # queryset=model.objects.annotate(title=models.Value("Задача")),
                template_name="detail_task.html",
            )
    obj.model = model
    obj.request = request
    obj.kwargs = kwargs
    obj.context_object_name = "data"
    obj.fields = {v.name: v for v in obj.model._meta.get_fields()}
    obj.url_name = obj.model.META.url_name
    return obj


def TaskStepTemplate(request, key, **kwargs):
    model = TaskStep
    # model_url = kwargs.get("model", "")
    pk_url = kwargs.get("pk", 0)

    match key:
        case "list":
            obj = ListView(
                queryset=model.objects.filter(task_id=pk_url),
                template_name="list_task_step.html",
                ordering="-date_end",
            )
        case _:
            pass
    obj.model = model
    obj.request = request
    obj.kwargs = kwargs
    obj.context_object_name = "data"
    obj.fields = {v.name: v for v in obj.model._meta.get_fields()}
    obj.url_name = obj.model.META.url_name
    return obj


class Index(TemplateView):
    template_name = "index.html"

    # def get_queryset(self):
    #     queryset = self.model.objects.all()
    #     match self.request.GET.get("f", "off"):
    #         case "off":
    #             queryset = queryset.filter(date_end=None)
    #         case "on":
    #             queryset = queryset.exclude(date_end=None)

    #     return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_url = kwargs.get("model", "")
        pk_url = kwargs.get("pk", 0)
        objs = []

        match model_url, pk_url:
            case "projs" | Proj.META.url_name, 0:
                context["title"] = "Все проекты"
                context["header"] = "Все проекты"
                objs.append(ProjTemplate(self.request, "list", **self.kwargs))
            case "sprints" | Sprint.META.url_name, 0:
                context["title"] = "Все спринты"
                context["header"] = "Все спринты"
                objs.append(SprintTemplate(self.request, "list", **self.kwargs))
            case "tasks" | Task.META.url_name, 0:
                context["title"] = "Все задачи"
                context["header"] = "Все задачи"
                objs.append(TaskTemplate(self.request, "list", **self.kwargs))
            case Proj.META.url_name, _:
                context["title"] = "Просмотр проекта"
                context["header"] = "Просмотр проекта"
                objs.append(ProjTemplate(self.request, "detail", **self.kwargs))
                objs.append(SprintTemplate(self.request, "list", **self.kwargs))
                objs.append(TaskTemplate(self.request, "list", **self.kwargs))
            case Sprint.META.url_name, _:
                context["title"] = "Просмотр спринта"
                context["header"] = "Просмотр спринта"
                objs.append(SprintTemplate(self.request, "detail", **self.kwargs))
                objs.append(TaskTemplate(self.request, "list", **self.kwargs))
            case Task.META.url_name, _:
                context["title"] = "Просмотр задачи"
                context["header"] = "Просмотр задачи"
                objs.append(TaskTemplate(self.request, "detail", **self.kwargs))
                objs.append(TaskStepTemplate(self.request, "list", **self.kwargs))
            case TaskStep.META.url_name, _:
                context["title"] = "Просмотр шага"
                context["header"] = "Просмотр шага"
            case _:
                pass
        try:
            context["details"] = [v.get(self.request) for v in objs]
        except Exception as err:
            text = f"ERROR: {type(err).__name__} - {err}"
            print(text)
            context["details"] = [{"rendered_content": text}]

        return context
