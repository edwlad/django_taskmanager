from django.shortcuts import render  # noqa
from django.http.response import HttpResponse  # noqa
from django.http.request import HttpRequest  # noqa
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


def get_model(name=""):
    match name:
        case Proj.META.verbose_name:
            return Proj
        case Sprint.META.verbose_name:
            return Sprint
        case Task.META.verbose_name:
            return Task
        case TaskStep.META.verbose_name:
            return TaskStep
    return Proj


class Index(TemplateView):
    template_name = "index.html"
    # model = Proj
    # paginate_by = 2
    # context_object_name = "data"

    def get_queryset(self):
        self.params = self.request.GET.copy()
        # self.params.update(self.request.POST)
        self.params.update(self.kwargs)

        match self.params.get("model", ""):
            case Proj.META.verbose_name:
                self.model = Proj
            case Sprint.META.verbose_name:
                self.model = Sprint
            case Task.META.verbose_name:
                self.model = Task
            case TaskStep.META.verbose_name:
                self.model = TaskStep
            case _:
                self.model = Task

        queryset = self.model.objects.all()
        match self.params.get("f", "off"):
            case "off":
                queryset = queryset.filter(date_end=None)
            case "on":
                queryset = queryset.exclude(date_end=None)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["details"] = []
        context["lists"] = []

        match self.kwargs.get("model", ""):
            case Proj.META.verbose_name:
                self.model = Proj
            case Sprint.META.verbose_name:
                self.model = Sprint
            case Task.META.verbose_name:
                self.model = Task
                obj = TaskDetail(kwargs=self.kwargs)
                obj.object = obj.get_object()
                obj.request = self.request
                # context["details"].append(obj.get_context_data())
                context["context"] = obj.render_to_response(
                    obj.get_context_data()
                ).rendered_content
            case TaskStep.META.verbose_name:
                self.model = TaskStep
            case _:
                self.model = Task

        # context["data"] = self.get_queryset()
        # context.update(self.params.items())
        context["buttons"] = ("add", "items")
        # context["model"] = self.model.META.verbose_name
        return context


class TaskDetail(DetailView):
    template_name = "detail.html"
    context_object_name = "context"
    queryset = Task.objects.all()
