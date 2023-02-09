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
    return obj


def TaskStepTemplate(request, key, **kwargs):
    match key:
        case "list":
            obj = ListView(
                queryset=TaskStep.objects.filter(task_id=kwargs.get("pk", 0)),
                template_name="list_task_step.html",
            )
        case _:
            pass
    obj.model = TaskStep
    obj.fields = {v.name: v for v in obj.model._meta.get_fields()}
    obj.url_name = obj.model.META.url_name
    obj.request = request
    obj.kwargs = kwargs
    obj.context_object_name = "data"
    return obj


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
        objs = []

        match self.kwargs.get("model", ""):
            case Proj.META.url_name:
                self.model = Proj
            case Sprint.META.url_name:
                self.model = Sprint
            case Task.META.url_name:
                context["title"] = "Просмотр задачи"
                context["header"] = "Просмотр задачи"
                objs.append(TaskTemplate(self.request, "detail", **self.kwargs))
                objs.append(TaskStepTemplate(self.request, "list", **self.kwargs))
            case TaskStep.META.url_name:
                self.model = TaskStep
            case _:
                self.model = Task

        try:
            context["details"] = [v.get(self.request) for v in objs]
        except Exception as err:
            print("ERROR:", type(err).__name__, "-", err)
            pass
        # context["data"] = self.get_queryset()
        # context.update(self.params.items())
        # context["buttons"] = ("add", "items")
        # context["model"] = self.model.META.url_name
        return context
