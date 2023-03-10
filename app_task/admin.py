from django.contrib import admin
from .models import Proj, Sprint, Task, TaskStep
from datetime import date  # noqa

# from django.db import models

# @admin.action(description="Отметить как выполненное")
# def make_on_end(modeladmin, request, queryset: models.QuerySet):
#     pass
#     # queryset.update(date_end=date.today())


# @admin.action(description="Отменить выполнение")
# def make_off_end(modeladmin, request, queryset: models.QuerySet):
#     pass
#     # queryset.update(date_end=None)


# @admin.action(description="Изменить статус выполнения")
# def make_not_end(modeladmin, request, queryset: models.QuerySet):
#     pass
#     for item in queryset:
#         item.chk_end = not item.chk_end
#         item.save()
#     queryset.update(
#         date_end=models.Case(
#             models.When(date_end=None, then=date.today()),
#             default=None,
#         ),
#     )


@admin.register(Proj)
class ProjAdmin(admin.ModelAdmin):
    list_display = tuple(v.attname for v in Proj._meta.fields)
    readonly_fields = ("uweb",)
    # actions = (make_on_end, make_off_end, make_not_end)

    def save_model(self, request, obj, form, change) -> None:
        # запись пользователа изменившего запись в специальное поле
        obj.uweb_id = request.user.id
        return super().save_model(request, obj, form, change)


@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):
    list_display = tuple(v.attname for v in Sprint._meta.fields)
    readonly_fields = ("uweb",)
    # actions = (make_on_end, make_off_end, make_not_end)

    def save_model(self, request, obj, form, change) -> None:
        # запись пользователа изменившего запись в специальное поле
        obj.uweb_id = request.user.id
        return super().save_model(request, obj, form, change)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = tuple(v.attname for v in Task._meta.fields)
    readonly_fields = ("uweb",)
    # actions = (make_on_end, make_off_end, make_not_end)

    def save_model(self, request, obj, form, change) -> None:
        # запись пользователа изменившего запись в специальное поле
        obj.uweb_id = request.user.id
        return super().save_model(request, obj, form, change)


@admin.register(TaskStep)
class TaskStepAdmin(admin.ModelAdmin):
    list_display = tuple(v.attname for v in TaskStep._meta.fields)
    # actions = (make_on_end, make_off_end, make_not_end)
