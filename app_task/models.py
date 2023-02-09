from django.db import models
from django.conf import settings
from datetime import datetime  # noqa


class Proj(models.Model):
    name = models.CharField(
        help_text="Название проекта", verbose_name="Название", max_length=120
    )
    desc = models.TextField(
        help_text="Описание проекта", verbose_name="Описание", max_length=250
    )
    date_beg = models.DateTimeField(
        help_text="Дата создания проекта",
        verbose_name="Создано",
        default=datetime.now,
    )
    date_end = models.DateTimeField(
        help_text="Дата завершения проекта",
        verbose_name="Завершено",
        null=True,
        blank=True,
    )
    date_max = models.DateTimeField(
        help_text="Планируемая дата завершения проекта",
        verbose_name="План",
        null=True,
        blank=True,
    )
    author = models.ForeignKey(
        help_text="Автор проекта",
        verbose_name="Автор",
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="author_projs",
    )

    def __str__(self) -> str:
        return f"{self.id}: {self.name}"

    class META:
        url_name = "proj"


class Sprint(models.Model):
    name = models.CharField(
        help_text="Название спринта", verbose_name="Название", max_length=120
    )
    desc = models.TextField(
        help_text="Описание спринта", verbose_name="Описание", max_length=250
    )
    date_beg = models.DateTimeField(
        help_text="Дата создания спринта",
        verbose_name="Создано",
        default=datetime.now,
    )
    date_end = models.DateTimeField(
        help_text="Дата завершения спринта",
        verbose_name="Завершено",
        null=True,
        blank=True,
    )
    date_max = models.DateTimeField(
        help_text="Планируемая дата завершения спринта",
        verbose_name="План",
        null=True,
        blank=True,
    )
    author = models.ForeignKey(
        help_text="Автор спринта",
        verbose_name="Автор",
        to=settings.AUTH_USER_MODEL,
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
        url_name = "sprint"


class Task(models.Model):
    name = models.CharField(
        help_text="Название задачи", verbose_name="Название", max_length=120
    )
    desc = models.TextField(
        help_text="Описание задачи", verbose_name="Описание", max_length=250
    )
    date_beg = models.DateTimeField(
        help_text="Дата создания задачи",
        verbose_name="Создано",
        default=datetime.now,
    )
    date_end = models.DateTimeField(
        help_text="Дата завершения задачи",
        verbose_name="Завершено",
        null=True,
        blank=True,
    )
    date_max = models.DateTimeField(
        help_text="Планируемая дата завершения задачи",
        verbose_name="План",
        null=True,
        blank=True,
    )
    author = models.ForeignKey(
        help_text="Автор задачи",
        verbose_name="Автор",
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="author_tasks",
    )
    user = models.ForeignKey(
        help_text="Исполнитель задачи",
        verbose_name="Исполнитель",
        to=settings.AUTH_USER_MODEL,
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
    #     to="self",  # на эту же таблицу
    #     # при удалении категории НЕ удалится все поддерево, null где надо
    #     on_delete=models.SET_NULL,
    #     blank=True,
    #     null=True,  # Может не быть предыдущей (родительской) задачи
    #     # имя, по которому (родительской) задачи можно найти следующую
    #     related_name="parent_next",
    # )

    def __str__(self) -> str:
        return f"{self.id}: {self.name}"

    class META:
        url_name = "task"


class TaskStep(models.Model):
    desс = models.TextField(
        help_text="Выполненая работа по задаче",
        verbose_name="Что сделано",
        max_length=250,
        null=True,
        blank=True,
    )
    date_end = models.DateTimeField(
        help_text="Дата завершения шага",
        verbose_name="Завершён",
        null=True,
        blank=True,
    )
    user = models.ForeignKey(
        help_text="Исполнитель шага",
        verbose_name="Исполнитель",
        to=settings.AUTH_USER_MODEL,
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
        return f"{self.id}: {self.work_beg[:30]}"

    class META:
        url_name = "task_step"
