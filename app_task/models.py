from django.db import models
from django.conf import settings
from datetime import datetime  # noqa


class Projs(models.Model):
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
    author = models.ForeignKey(  # связь внешним ключом
        help_text="Автор проекта",
        verbose_name="Автор",
        to=settings.AUTH_USER_MODEL,  # на модель аутентификации пользователей
        on_delete=models.SET_NULL,  # При удалении пользователя задача не удалится
        blank=True,
        null=True,
        # имя, для обращения из объекта пользователя к его списку задач
        related_name="tasks_author",
    )


class Sprints(models.Model):
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
    author = models.ForeignKey(  # связь внешним ключом
        help_text="Автор спринта",
        verbose_name="Автор",
        to=settings.AUTH_USER_MODEL,  # на модель аутентификации пользователей
        on_delete=models.SET_NULL,  # При удалении пользователя задача не удалится
        blank=True,
        null=True,
        # имя, для обращения из объекта пользователя к его списку задач
        related_name="tasks_author",
    )


class Tasks(models.Model):
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
    author = models.ForeignKey(  # связь внешним ключом
        help_text="Автор задачи",
        verbose_name="Автор",
        to=settings.AUTH_USER_MODEL,  # на модель аутентификации пользователей
        on_delete=models.SET_NULL,  # При удалении пользователя задача не удалится
        blank=True,
        null=True,
        # имя, для обращения из объекта пользователя к его списку задач
        related_name="author_tasks",
    )
    proj = models.ForeignKey(
        help_text="Проект",
        verbose_name="Проект",
        to="Projs",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="proj_tasks",
    )
    sprint = models.ForeignKey(
        help_text="Спринт",
        verbose_name="Спринт",
        to="Sprints",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="sprint_tasks",
    )


class TaskSteps(models.Model):
    work_beg = models.TextField(
        help_text="Необходимая работа по шагу",
        verbose_name="Что сделать",
        max_length=250,
    )
    work_end = models.TextField(
        help_text="Выполненая работа по шагу",
        verbose_name="Что сделано",
        max_length=250,
        null=True,
        blank=True,
    )
    date_beg = models.DateTimeField(
        help_text="Дата начала шага",
        verbose_name="Начат",
        # default=datetime.now,
        null=True,
        blank=True,
    )
    date_end = models.DateTimeField(
        help_text="Дата завершения шага",
        verbose_name="Завершён",
        null=True,
        blank=True,
    )
    user = models.ForeignKey(  # связь внешним ключом
        help_text="Исполнитель шага",
        verbose_name="Исполнитель",
        to=settings.AUTH_USER_MODEL,  # на модель аутентификации пользователей
        on_delete=models.SET_NULL,  # При удалении пользователя задача не удалится
        blank=True,
        null=True,
        # имя, для обращения из объекта пользователя к его списку шагов как исполнителя
        related_name="steps_user",
    )
    author = models.ForeignKey(  # связь внешним ключом
        help_text="Автор шага",
        verbose_name="Автор",
        to=settings.AUTH_USER_MODEL,  # на модель аутентификации пользователей
        on_delete=models.SET_NULL,  # При удалении пользователя задача не удалится
        blank=True,
        null=True,
        # имя, для обращения из объекта пользователя к его списку шагов как автора
        related_name="author_steps",
    )
    # parent = models.ForeignKey(  # связь внешним ключом
    #     help_text="Предыдущий шаг",  # текст для человека
    #     to="self",  # на эту же таблицу
    #     # при удалении категории НЕ удалится все поддерево, null где надо
    #     on_delete=models.SET_NULL,
    #     blank=True,
    #     null=True,  # Может не быть предыдущей (родительской) задачи
    #     # имя, по которому (родительской) задачи можно найти следующую
    #     related_name="next",
    # )
    task = models.ForeignKey(  # связь внешним ключом
        help_text="Задача",
        verbose_name="Задача",
        to="Tasks",  # на модель аутентификации пользователей
        on_delete=models.CASCADE,  # При удалении задачи удаляются все подзадачи
        # имя, для обращения из подзадачи к задаче
        related_name="task_steps",
    )
