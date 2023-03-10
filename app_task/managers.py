from django.db.models import F, Q, Case, When, Min, Max, Window  # noqa
from django.db.models.functions import FirstValue  # noqa
from django.db import models  # noqa
from datetime import date, timedelta  # noqa


class TaskManager(models.Manager):
    def get_queryset(self):
        qs: models.QuerySet = super().get_queryset()

        # вычисление планируемой даты закрытия
        qs = qs.annotate(
            date_plan=Case(
                When(proj__date_max=None, sprint__date_max=None, then=F("date_max")),
                When(
                    Q(proj__date_max=None)
                    & (Q(date_max=None) | Q(sprint__date_max__lte=F("date_max"))),
                    then=F("sprint__date_max"),
                ),
                When(
                    Q(sprint__date_max=None)
                    & (Q(date_max=None) | Q(proj__date_max__lte=F("date_max"))),
                    then=F("proj__date_max"),
                ),
                When(
                    Q(sprint__date_max__lte=F("proj__date_max"))
                    & (Q(date_max=None) | Q(sprint__date_max__lte=F("date_max"))),
                    then=F("sprint__date_max"),
                ),
                When(
                    Q(date_max=None) | Q(proj__date_max__lte=F("date_max")),
                    then=F("proj__date_max"),
                ),
                default=F("date_max"),
            ),
        )

        # вычисление количества дней до планируемой даты закрытия
        qs = qs.annotate(
            days_plan=Case(
                When(Q(date_plan=None) | Q(date_end__isnull=False), then=timedelta(0)),
                default=F("date_plan") - date.today(),
            ),
        )

        # вычисление минимальной возможной даты закрытия задачи
        qs = qs.annotate(date_end_task=F("date_beg"))

        return qs


class SprintManager(models.Manager):
    def get_queryset(self):
        qs: models.QuerySet = super().get_queryset()

        # вычисление планируемой даты закрытия
        qs = qs.annotate(
            date_plan=Case(
                When(proj__date_max=None, then=F("date_max")),
                When(
                    Q(date_max=None) | Q(date_max__gte=F("proj__date_max")),
                    then=F("proj__date_max"),
                ),
                default=F("date_max"),
            )
        )

        # вычисление количества дней до планируемой даты закрытия
        qs = qs.annotate(
            days_plan=Case(
                When(Q(date_plan=None) | Q(date_end__isnull=False), then=timedelta(0)),
                default=F("date_plan") - date.today(),
            )
        )

        # вычисление максимальной даты закрытия задач спринта
        qs = qs.annotate(date_end_task=Max("sprint_tasks__date_end"))

        # вычисление минимальной возможной даты закрытия спринта
        qs = qs.annotate(
            date_end_sprint=Case(
                When(
                    Q(date_end_task=None) | Q(date_beg__gte=F("date_end_task")),
                    then=F("date_beg"),
                ),
                default=F("date_end_task"),
            )
        )

        return qs


class ProjManager(models.Manager):
    def get_queryset(self):
        qs: models.QuerySet = super().get_queryset()

        # вычисление планируемой даты закрытия
        qs = qs.annotate(date_plan=F("date_max"))

        # вычисление количества дней до планируемой даты закрытия
        qs = qs.annotate(
            days_plan=Case(
                When(Q(date_plan=None) | Q(date_end__isnull=False), then=timedelta(0)),
                default=F("date_plan") - date.today(),
            )
        )

        # вычисление максимальной даты закрытия спринтов проекта
        qs = qs.annotate(date_end_sprint=Max("proj_sprints__date_end"))

        # вычисление максимальной даты закрытия задач проекта
        qs = qs.annotate(date_end_task=Max("proj_tasks__date_end"))

        # вычисление минимальной возможной даты закрытия проекта
        qs = qs.annotate(
            date_end_proj=Case(
                When(date_end_sprint=None, date_end_task=None, then=F("date_beg")),
                When(
                    Q(date_end_sprint=None) & Q(date_end_task__gte=F("date_beg")),
                    then=F("date_end_task"),
                ),
                When(
                    Q(date_end_task=None) & Q(date_end_sprint__gte=F("date_beg")),
                    then=F("date_end_sprint"),
                ),
                When(
                    Q(date_end_task__gte=F("date_end_sprint"))
                    & Q(date_end_task__gte=F("date_beg")),
                    then=F("date_end_task"),
                ),
                When(
                    Q(date_end_sprint__gte=F("date_beg")),
                    then=F("date_end_sprint"),
                ),
                default=F("date_beg"),
            )
        )

        return qs
