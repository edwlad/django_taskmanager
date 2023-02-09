from django.shortcuts import render  # noqa
from django.http.response import HttpResponse  # noqa
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
    match key:
        case "list":
            pass
        case _:
            obj = DetailView(
                # queryset=Task.objects.annotate(title=models.Value("Проект")),
                template_name="detail_proj.html",
            )
    obj.model = Proj
    obj.fields = {v.name: v for v in obj.model._meta.get_fields()}
    obj.url_name = obj.model.META.url_name
    obj.request = request
    obj.kwargs = kwargs
    obj.context_object_name = "data"
    try:
        render = obj.get(obj.request)
    except Exception as err:
        text = f"ERROR: {type(err).__name__} - {err}"
        print(text)
        return error(request, content=text)
    render.context_data["sprints"] = obj.object.proj_sprints.all()
    render.context_data["tasks"] = obj.object.proj_tasks.all()
    return render


def TaskTemplate(request, key, **kwargs):
    match key:
        case "list":
            pass
        case _:
            obj = DetailView(
                # queryset=Task.objects.annotate(title=models.Value("Задача")),
                template_name="detail_task.html",
            )
    obj.model = Task
    obj.fields = {v.name: v for v in obj.model._meta.get_fields()}
    obj.url_name = obj.model.META.url_name
    obj.request = request
    obj.kwargs = kwargs
    obj.context_object_name = "data"
    try:
        render = obj.get(obj.request)
    except Exception as err:
        text = f"ERROR: {type(err).__name__} - {err}"
        print(text)
        return error(request, content=text)
    return render


def TaskStepTemplate(request, key, **kwargs):
    match key:
        case "list":
            obj = ListView(
                queryset=TaskStep.objects.filter(task_id=kwargs.get("pk", -1)),
                template_name="list_task_step.html",
                ordering="-date_end",
            )
        case _:
            pass
    obj.model = TaskStep
    obj.fields = {v.name: v for v in obj.model._meta.get_fields()}
    obj.url_name = obj.model.META.url_name
    obj.request = request
    obj.kwargs = kwargs
    obj.context_object_name = "data"
    try:
        render = obj.get(obj.request)
    except Exception as err:
        text = f"ERROR: {type(err).__name__} - {err}"
        print(text)
        return error(request, content=text)
    return render


class Index(TemplateView):
    template_name = "index.html"
    # model = Proj
    # paginate_by = 2
    # context_object_name = "data"

    def get_queryset(self):
        # self.params = self.request.GET.copy()
        # self.params.update(self.request.POST)
        # self.params.update(self.kwargs)
        queryset = self.model.objects.all()
        match self.request.GET.get("f", "off"):
            case "off":
                queryset = queryset.filter(date_end=None)
            case "on":
                queryset = queryset.exclude(date_end=None)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["details"] = []

        match self.kwargs.get("model", ""):
            case Proj.META.url_name:
                context["title"] = "Просмотр проекта"
                context["header"] = "Просмотр проекта"
                context["details"].append(
                    ProjTemplate(self.request, "detail", **self.kwargs)
                )
            case Sprint.META.url_name:
                context["title"] = "Просмотр спринта"
                context["header"] = "Просмотр спринта"
            case Task.META.url_name:
                context["title"] = "Просмотр задачи"
                context["header"] = "Просмотр задачи"
                context["details"].append(
                    TaskTemplate(self.request, "detail", **self.kwargs)
                )
                context["details"].append(
                    TaskStepTemplate(self.request, "list", **self.kwargs)
                )
            case TaskStep.META.url_name:
                self.model = TaskStep
            case _:
                self.model = Task
        # try:
        #     context["details"] = [v.get(self.request) for v in objs]
        # except Exception as err:
        #     print("ERROR:", type(err).__name__, "-", err)
        #     pass

        # context["data"] = self.get_queryset()
        # context.update(self.params.items())
        # context["buttons"] = ("add", "items")
        # context["model"] = self.model.META.url_name
        return context
