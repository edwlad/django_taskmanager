from django.http.response import HttpResponseRedirect, HttpResponse  # noqa
from django.http.request import HttpRequest  # noqa
from rest_framework.request import Request
from django.db.models import Model  # noqa
from .models import Proj, Sprint, Task, TaskStep


def get_perms(request: HttpRequest | Request, obj: Model = None):
    kw = {}
    if isinstance(request, HttpRequest):
        kw = getattr(request.resolver_match, "kwargs", {})
    elif isinstance(request, Request):
        kw = request.parser_context.get("kwargs", {})
        kw["model"] = request.parser_context["view"].basename
    user = request.user

    if isinstance(obj, Model):
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
        has_obj = isinstance(obj, Model)
        if not has_obj:
            obj = model

    temp: str = f"{obj._meta.app_label}.{{}}_{obj._meta.model_name}"
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
    p_de = hasattr(obj, "proj") and hasattr(obj.proj, "date_end") and obj.proj.date_end
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
