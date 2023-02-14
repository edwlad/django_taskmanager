# from django.db import models
from django.db.models import QuerySet
from django.db.models import F, Manager, Min, Case, When
from datetime import date, timedelta


class TaskManager(Manager):
    def get_queryset(self) -> QuerySet:
        qs: QuerySet = super().get_queryset()
        qs = qs.annotate(
            date_plan=Case(
                When(proj__date_max=None, sprint__date_max=None, then=F("date_max")),
                When(proj__date_max=None, date_max=None, then=F("sprint__date_max")),
                When(sprint__date_max=None, date_max=None, then=F("proj__date_max")),
                When(
                    proj__date_max=None, then=Min(F("date_max"), F("sprint__date_max"))
                ),
                When(
                    sprint__date_max=None, then=Min(F("date_max"), F("proj__date_max"))
                ),
                When(
                    date_max=None, then=Min(F("proj__date_max"), F("sprint__date_max"))
                ),
                default=Min(F("date_max"), F("proj__date_max"), F("sprint__date_max")),
            )
        ).annotate(
            days_plan=Case(
                When(date_end=None, then=F("date_plan") - date.today()),
                default=timedelta(0),
            ),
        )
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
        ).annotate(
            days_plan=Case(
                When(date_end=None, then=F("date_plan") - date.today()),
                default=timedelta(0),
            ),
        )
        # print(qs.query)
        return qs


class ProjManager(Manager):
    def get_queryset(self) -> QuerySet:
        qs: QuerySet = super().get_queryset()
        qs = qs.annotate(date_plan=F("date_max")).annotate(
            days_plan=Case(
                When(date_end=None, then=F("date_plan") - date.today()),
                default=timedelta(0),
            ),
        )
        # print(qs.query)
        return qs
