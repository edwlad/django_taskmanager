from django.db import models
from django.conf import settings
from datetime import datetime  # noqa


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
    sreps = models.ForeignKey(  # связь внешним ключом
        help_text="Подзадачи задания",
        verbose_name="Подзадачи",
        to=".TaskSteps",  # на модель аутентификации пользователей
        on_delete=models.CASCADE,  # При удалении задачи удаляются все подзадачи
        blank=True,
        null=True,
        # имя, для обращения из подзадачи к задаче
        related_name="task",
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
        # имя, для обращения из объекта пользователя можно к его списку задач
        related_name="user_tasks",
    )
    parent = models.ForeignKey(  # связь внешним ключом
        help_text="Предыдущий шаг",  # текст для человека
        to="self",  # на эту же таблицу
        # при удалении категории НЕ удалится все поддерево, null где надо
        on_delete=models.SET_NULL,
        blank=True,
        null=True,  # Может не быть предыдущей (родительской) задачи
        # имя, по которому (родительской) задачи можно найти следующую
        related_name="next",
    )
