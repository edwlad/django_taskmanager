from django.contrib import admin
from .models import Proj, Sprint, Task, TaskStep
from django.db import models
from datetime import datetime


@admin.action(description="Отметить как выполненное")
def make_on_end(modeladmin, request, queryset: models.QuerySet):
    queryset.update(date_end=datetime.now())


@admin.action(description="Отменить выполнение")
def make_off_end(modeladmin, request, queryset: models.QuerySet):
    queryset.update(date_end=None)


@admin.action(description="Изменить статус выполнения")
def make_not_end(modeladmin, request, queryset: models.QuerySet):
    # for item in queryset:
    #     item.chk_end = not item.chk_end
    #     item.save()
    queryset.update(
        date_end=models.Case(
            models.When(date_end=None, then=datetime.now()),
            default=None,
        ),
    )


@admin.register(Proj)
class ProjAdmin(admin.ModelAdmin):
    list_display = tuple(v.attname for v in Proj._meta.fields)
    actions = (make_on_end, make_off_end, make_not_end)


@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):
    list_display = tuple(v.attname for v in Sprint._meta.fields)
    actions = (make_on_end, make_off_end, make_not_end)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = tuple(v.attname for v in Task._meta.fields)
    actions = (make_on_end, make_off_end, make_not_end)


@admin.register(TaskStep)
class TaskStepAdmin(admin.ModelAdmin):
    list_display = tuple(v.attname for v in TaskStep._meta.fields)
    actions = (make_on_end, make_off_end, make_not_end)
