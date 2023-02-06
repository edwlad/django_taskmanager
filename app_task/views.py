from django.shortcuts import render  # noqa
from django.http.response import HttpResponse  # noqa
from django.http.request import HttpRequest  # noqa
from django.views.generic import (
    ListView,
    DetailView,
    UpdateView,
    CreateView,
    DeleteView,
)
from .models import Proj, Sprint, Task, TaskStep
from django.urls import reverse, reverse_lazy
from datetime import datetime


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


class Index(ListView):
    template_name = "index.html"
    model = Proj
    # paginate_by = 2
    context_object_name = "context"

    def get_queryset(self):
        filt = self.request.GET.get("f", "off")
        queryset = self.model.objects.all()
        if filt == "on":
            return queryset.exclude(date_end=None)
        elif filt == "all":
            return queryset
        return queryset.filter(date_end=None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["buttons"] = ("add", "items")
        context["is_index"] = True
        return context
