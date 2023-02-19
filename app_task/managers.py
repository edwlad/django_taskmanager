# from django.db import models
from django.db.models import QuerySet
from django.db.models import F, Manager, Min, Case, When, Max, Window
from django.db.models.functions import FirstValue
from django.db import models  # noqa
from datetime import date, timedelta  # noqa


class TaskManager(Manager):
    def get_queryset(self) -> QuerySet:
        qs: QuerySet = super().get_queryset()
        qs = qs.annotate(  # вычисление планируемой даты закрытия
            date_plan=Case(
                When(proj__date_max=None, sprint__date_max=None, then=F("date_max")),
                When(proj__date_max=None, date_max=None, then=F("sprint__date_max")),
                When(sprint__date_max=None, date_max=None, then=F("proj__date_max")),
                When(
                    proj__date_max=None,
                    then=Min(F("date_max"), F("sprint__date_max")),
                ),
                When(
                    sprint__date_max=None,
                    then=Min(F("date_max"), F("proj__date_max")),
                ),
                When(
                    date_max=None,
                    then=Min(F("proj__date_max"), F("sprint__date_max")),
                ),
                default=Min(F("date_max"), F("proj__date_max"), F("sprint__date_max")),
            )
        )
        qs = qs.annotate(  # вычисление количества дней до планируемой даты закрытия
            days_plan=Case(
                When(date_end=None, date_plan=None, then=timedelta(0)),
                When(date_end=None, then=F("date_plan") - date.today()),
                When(date_plan=None, then=timedelta(0)),
                default=F("date_plan") - F("date_end"),
            ),
        )

        qs = qs.annotate(date_end_task=F("date_beg"))
        # print(qs.query)
        return qs


class SprintManager(Manager):
    def get_queryset(self) -> QuerySet:
        qs: QuerySet = super().get_queryset()
        qs = qs.annotate(
            date_plan=Case(
                When(proj__date_max=None, then=F("date_max")),
                When(date_max=None, then=F("proj__date_max")),
                default=Min(F("date_max"), F("proj__date_max")),
            )
        )
        qs = qs.annotate(
            days_plan=Case(
                When(date_end=None, date_plan=None, then=timedelta(0)),
                When(date_end=None, then=F("date_plan") - date.today()),
                When(date_plan=None, then=timedelta(0)),
                default=F("date_plan") - F("date_end"),
            )
        )
        qs = qs.annotate(
            date_end_task=Window(
                expression=FirstValue(Max("sprint_tasks__date_end")),
                partition_by=F("id"),
            )
        )
        qs = qs.annotate(date_end_sprint=Max(F("date_end_task"), F("date_beg")))
        # print(qs.query)
        return qs


class ProjManager(Manager):
    def get_queryset(self) -> QuerySet:
        qs: QuerySet = super().get_queryset()
        qs = qs.annotate(date_plan=F("date_max"))
        qs = qs.annotate(
            days_plan=Case(
                When(date_end=None, date_plan=None, then=timedelta(0)),
                When(date_end=None, then=F("date_plan") - date.today()),
                When(date_plan=None, then=timedelta(0)),
                default=F("date_plan") - F("date_end"),
            )
        )

        qs = qs.annotate(
            date_end_sprint=Window(
                expression=FirstValue(Max("proj_sprints__date_end")),
                partition_by=F("id"),
            )
        )
        qs = qs.annotate(
            date_end_task=Window(
                expression=FirstValue(Max("proj_tasks__date_end")),
                partition_by=F("id"),
            )
        )

        qs = qs.annotate(
            date_end_proj=Max(F("date_end_sprint"), F("date_end_task"), F("date_beg"))
        )

        # print(qs.query)
        return qs
