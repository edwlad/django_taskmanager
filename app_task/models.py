from django.db import models
from django.contrib.auth.models import User
from datetime import date  # noqa
from .managers import TaskManager, SprintManager, ProjManager


class Proj(models.Model):
    objects = ProjManager()

    name = models.CharField(
        help_text="Название проекта", verbose_name="Название", max_length=120
    )
    desc = models.TextField(help_text="Описание проекта", verbose_name="Описание")
    date_beg = models.DateField(
        help_text="Дата создания проекта",
        verbose_name="Создано",
        default=date.today,
    )
    date_end = models.DateField(
        help_text="Дата завершения проекта",
        verbose_name="Завершено",
        null=True,
        blank=True,
    )
    date_max = models.DateField(
        help_text="Планируемая дата завершения проекта",
        verbose_name="План",
        null=True,
        blank=True,
    )
    author = models.ForeignKey(
        help_text="Автор проекта",
        verbose_name="Автор",
        to=User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="author_projs",
    )

    def __str__(self) -> str:
        return f"{self.id}: {self.name}"

    def save(self, **kwargs) -> None:
        return super().save(**kwargs)

    class META:
        url_name = "projs"
        url_id = "projs_id"
        url_page = "projs_p"
        url_filt = "projs_f"


class Sprint(models.Model):
    objects = SprintManager()

    name = models.CharField(
        help_text="Название спринта", verbose_name="Название", max_length=120
    )
    desc = models.TextField(help_text="Описание спринта", verbose_name="Описание")
    date_beg = models.DateField(
        help_text="Дата создания спринта",
        verbose_name="Создано",
        default=date.today,
    )
    date_end = models.DateField(
        help_text="Дата завершения спринта",
        verbose_name="Завершено",
        null=True,
        blank=True,
    )
    date_max = models.DateField(
        help_text="Планируемая дата завершения спринта",
        verbose_name="План",
        null=True,
        blank=True,
    )
    author = models.ForeignKey(
        help_text="Автор спринта",
        verbose_name="Автор",
        to=User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="author_sprints",
    )
    proj = models.ForeignKey(
        help_text="Проект",
        verbose_name="Проект",
        to="Proj",
        on_delete=models.CASCADE,
        related_name="proj_sprints",
    )

    def __str__(self) -> str:
        return f"{self.id}: {self.name}"

    class META:
        url_name = "sprints"
        url_id = "sprints_id"
        url_page = "sprints_p"
        url_filt = "sprints_f"


class Task(models.Model):
    objects = TaskManager()

    name = models.CharField(
        help_text="Название задачи", verbose_name="Название", max_length=120
    )
    desc = models.TextField(help_text="Описание задачи", verbose_name="Описание")
    date_beg = models.DateField(
        help_text="Дата создания задачи",
        verbose_name="Создано",
        default=date.today,
    )
    date_end = models.DateField(
        help_text="Дата завершения задачи",
        verbose_name="Завершено",
        null=True,
        blank=True,
    )
    date_max = models.DateField(
        help_text="Планируемая дата завершения задачи",
        verbose_name="План",
        null=True,
        blank=True,
    )
    author = models.ForeignKey(
        help_text="Автор задачи",
        verbose_name="Автор",
        to=User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="author_tasks",
    )
    user = models.ForeignKey(
        help_text="Исполнитель задачи",
        verbose_name="Исполнитель",
        to=User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="user_tasks",
    )
    proj = models.ForeignKey(
        help_text="Проект",
        verbose_name="Проект",
        to="Proj",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="proj_tasks",
    )
    sprint = models.ForeignKey(
        help_text="Спринт",
        verbose_name="Спринт",
        to="Sprint",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="sprint_tasks",
    )
    # parent = models.ForeignKey(
    #     help_text="Предыдущиая задача",
    #     verbose_name="Зависит от",
    #     to="self",
    #     on_delete=models.SET_NULL,
    #     blank=True,
    #     null=True,
    #     related_name="parent_next",
    # )

    def __str__(self) -> str:
        return f"{self.id}: {self.name}"

    def save(self, **kwargs) -> None:
        if self.sprint:
            self.proj = self.sprint.proj
        return super().save(**kwargs)

    class META:
        url_name = "tasks"
        url_id = "tasks_id"
        url_page = "tasks_p"
        url_filt = "tasks_f"


class TaskStep(models.Model):
    desc = models.TextField(
        help_text="Выполненая работа по задаче",
        verbose_name="Что сделано",
    )
    date_end = models.DateField(
        help_text="Дата завершения шага", verbose_name="Завершён", default=date.today
    )
    user = models.ForeignKey(
        help_text="Исполнитель шага",
        verbose_name="Исполнитель",
        to=User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="user_steps",
    )
    task = models.ForeignKey(
        help_text="Задача",
        verbose_name="Задача",
        to="Task",
        on_delete=models.CASCADE,
        related_name="task_steps",
    )

    def __str__(self) -> str:
        return f"{self.id}: {self.desс[:30]}"

    class META:
        url_name = "task_steps"
        url_id = "tsteps_id"
        url_page = "tsteps_p"
        url_filt = "tsteps_f"
