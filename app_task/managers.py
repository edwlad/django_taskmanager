from django.db.models import F, Q, Case, When, Min, Max, Window  # noqa
from django.db.models.functions import FirstValue  # noqa
from django.db import models  # noqa
from datetime import date, timedelta  # noqa


class TaskManager(models.Manager):
    def get_queryset(self):
        qs: models.QuerySet = super().get_queryset()
        sq = qs.annotate(
            v1=Case(
                When(
                    proj__date_max=None,
                    then=models.Value("9999-12-31", output_field=models.DateField()),
                ),
                default=F("proj__date_max"),
            ),
            v2=Case(
                When(
                    sprint__date_max=None,
                    then=models.Value("9999-12-31", output_field=models.DateField()),
                ),
                default=F("sprint__date_max"),
            ),
            v3=Case(
                When(
                    date_max=None,
                    then=models.Value("9999-12-31", output_field=models.DateField()),
                ),
                default=F("date_max"),
            ),
        ).values("v1", "v2", "v3")
        sq = (
            sq.annotate(
                v=Case(
                    When(Q(v1__lte=F("v2")) & Q(v1__lte=F("v3")), then=F("v1")),
                    When(v2__lte=F("v3"), then=F("v2")),
                    default=F("v3"),
                ),
            )
            .values("v")
            .order_by("v")[:1]
        )

        qs = qs.annotate(  # вычисление планируемой даты закрытия
            date_plan=Case(
                When(
                    proj__date_max=None, sprint__date_max=None, date_max=None, then=None
                ),
                default=models.Subquery(sq),
            )
        )

        qs = qs.annotate(  # вычисление количества дней до планируемой даты закрытия
            days_plan=Case(
                When(Q(date_plan=None) | Q(date_end__isnull=False), then=timedelta(0)),
                default=F("date_plan") - date.today(),
            ),
        )

        qs = qs.annotate(date_end_task=F("date_beg"))
        # print(qs.query)
        return qs


class SprintManager(models.Manager):
    def get_queryset(self):
        qs: models.QuerySet = super().get_queryset()
        qs = qs.annotate(
            date_plan=Case(
                When(proj__date_max=None, then=F("date_max")),
                When(
                    Q(date_max=None) | Q(date_max__gt=F("proj__date_max")),
                    then=F("proj__date_max"),
                ),
                default=F("date_max"),
            )
        )
        qs = qs.annotate(
            days_plan=Case(
                When(Q(date_plan=None) | Q(date_end__isnull=False), then=timedelta(0)),
                default=F("date_plan") - date.today(),
            )
        )

        qs = qs.annotate(date_end_task=Max("sprint_tasks__date_end"))

        qs = qs.annotate(
            date_end_sprint=Case(
                When(date_end_task=None, then=F("date_beg")),
                When(date_beg__gte=F("date_end_task"), then=F("date_beg")),
                default=F("date_end_task"),
            )
        )
        # print(qs.query)
        return qs


class ProjManager(models.Manager):
    def get_queryset(self):
        qs: models.QuerySet = super().get_queryset()
        qs = qs.annotate(date_plan=F("date_max"))
        qs = qs.annotate(
            days_plan=Case(
                When(Q(date_plan=None) | Q(date_end__isnull=False), then=timedelta(0)),
                default=F("date_plan") - date.today(),
            )
        )

        qs = qs.annotate(date_end_sprint=Max("proj_sprints__date_end"))

        qs = qs.annotate(date_end_task=Max("proj_tasks__date_end"))

        qs = qs.annotate(
            date_end_proj=Case(
                When(date_end_sprint=None, date_end_task=None, then=F("date_beg")),
                When(
                    date_end_sprint=None,
                    date_end_task__lte=F("date_beg"),
                    then=F("date_beg"),
                ),
                When(
                    date_end_sprint=None,
                    date_end_task__gt=F("date_beg"),
                    then=F("date_end_task"),
                ),
                When(date_beg__gte=F("date_end_task"), then=F("date_beg")),
                default=F("date_end_task"),
                # F("date_end_sprint"), F("date_end_task"), F("date_beg")
            )
        )
        # qs = qs.annotate(
        #     date_end_proj=Max(
        #         ExpressionWrapper(
        #             F("date_end_sprint"), output_field=models.DateField()
        #         ),
        #         ExpressionWrapper(F("date_end_task"),output_field=models.DateField()),
        #         ExpressionWrapper(F("date_beg"), output_field=models.DateField()),
        #     )
        # )
        # qs = qs.annotate(
        #     date_end_proj=models.Value(None, output_field=models.DateField())
        # )

        # print(qs.query)
        return qs
