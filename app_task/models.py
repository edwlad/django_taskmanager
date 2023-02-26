from django.db import models
from django.contrib.auth import get_user_model
from datetime import date, datetime  # noqa
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
        to=get_user_model(),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="author_projs",
    )
    uweb = models.ForeignKey(
        help_text="Последний прользователь редактировавший проект",
        verbose_name="Редактор",
        to=get_user_model(),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return f"{self.id}: {self.name}"

    def save(self, **kwargs) -> None:
        # если планируемая дата меньше даты создания
        if self.date_max and self.date_max < self.date_beg:
            self.date_max = self.date_beg

        # если есть не закрытые задачи или спринты то дату закрытия убираем
        if (
            Sprint.objects.filter(proj_id=self.id).filter(date_end=None).exists()
            or Task.objects.filter(proj_id=self.id).filter(date_end=None).exists()
        ):
            self.date_end = None

        # если дата закрытия проекта меньше вычисленой даты закрытия то правим
        if self.date_end and self.date_end < self.date_end_proj:
            self.date_end = self.date_end_proj

        # проверка - есть ли изменения
        desc = ""
        old = type(self).objects.filter(id=self.id).first()
        if old is None:
            desc = "Создание проекта"
        else:
            for v in self._meta.get_fields():
                if v.name in ("uweb", "id"):
                    continue
                v1 = getattr(self, v.name)
                v2 = getattr(old, v.name)
                if v1 != v2:
                    desc += f"{v.verbose_name}: {v2} => {v1};\n"

        # если есть изменения сохраняем и создаём запись в истории
        if desc:
            super().save(**kwargs)

            # выбор задач проекта
            qs = Task.objects.filter(proj_id=self.id)

            for v in qs:
                obj = TaskStep()
                obj.author = self.uweb
                if old and self.date_end and old.date_end is None:
                    obj.desc = "Закрытие проекта\n" + desc
                elif old:
                    obj.desc = "Изменения в проекте:\n" + desc
                else:
                    obj.desc = desc

                obj.save(parrent=v)

        return

    class META:
        url_name = "projs"
        url_id = "projs_id"
        url_page = "projs_p"
        url_filt = "projs_f"
        url_user = "projs_u"


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
        to=get_user_model(),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="author_sprints",
    )
    uweb = models.ForeignKey(
        help_text="Последний прользователь редактировавший спринт",
        verbose_name="Редактор",
        to=get_user_model(),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
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

    def save(self, **kwargs) -> None:
        # если закрыт проект то ничего не сохраняем
        if self.proj and self.proj.date_end:
            return

        # если планируемая дата меньше даты создания
        if self.date_max and self.date_max < self.date_beg:
            self.date_max = self.date_beg

        # если есть не закрытые задачи то дату закрытия убираем
        if Task.objects.filter(sprint_id=self.id).filter(date_end=None).exists():
            self.date_end = None

        # если дата закрытия спринта меньше вычисленой даты закрытия то правим
        if self.date_end and self.date_end < self.date_end_sprint:
            self.date_end = self.date_end_sprint

        # проверка - есть ли изменения
        desc = ""
        old = type(self).objects.filter(id=self.id).first()
        if old is None:
            desc = "Создание спринта"
        else:
            for v in self._meta.get_fields():
                if v.name in ("uweb", "id"):
                    continue
                v1 = getattr(self, v.name)
                v2 = getattr(old, v.name)
                if v1 != v2:
                    desc += f"{v.verbose_name}: {v2} => {v1};\n"

        # если есть изменения сохраняем и создаём запись в истории
        if desc:
            super().save(**kwargs)

            # выбор задач спринта
            qs = Task.objects.filter(sprint_id=self.id)

            # если есть задачи где проект не совпадает с проектом спринта
            # то меняем проект у задач
            qs.exclude(proj_id=self.proj_id).update(proj_id=self.proj_id)

            for v in qs:
                obj = TaskStep()
                obj.author = self.uweb
                if old and self.date_end and old.date_end is None:
                    obj.desc = "Закрытие спринта\n" + desc
                elif old:
                    obj.desc = "Изменения в спринте:\n" + desc
                else:
                    obj.desc = desc

                obj.save(parrent=v)

        return

    class META:
        url_name = "sprints"
        url_id = "sprints_id"
        url_page = "sprints_p"
        url_filt = "sprints_f"
        url_user = "sprints_u"


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
        to=get_user_model(),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="author_tasks",
    )
    user = models.ForeignKey(
        help_text="Исполнитель задачи",
        verbose_name="Исполнитель",
        to=get_user_model(),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="user_tasks",
    )
    uweb = models.ForeignKey(
        help_text="Последний прользователь редактировавший задачу",
        verbose_name="Редактор",
        to=get_user_model(),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    proj = models.ForeignKey(
        help_text="Проект",
        verbose_name="Проект",
        to="Proj",
        # blank=True,
        # null=True,
        # on_delete=models.SET_NULL,
        on_delete=models.CASCADE,
        related_name="proj_tasks",
    )
    sprint = models.ForeignKey(
        help_text="Спринт",
        verbose_name="Спринт",
        to="Sprint",
        # on_delete=models.SET_NULL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="sprint_tasks",
    )
    parent = models.ForeignKey(
        help_text="Предыдущая задача",
        verbose_name="Зависит от",
        to="self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="parent_nexts",
    )

    def __str__(self) -> str:
        return f"{self.id}: {self.name}"

    def save(self, **kwargs) -> None:
        # если закрыты спринт и/или проект то ничего не сохраняем
        if self.sprint and self.sprint.date_end or self.proj and self.proj.date_end:
            return

        # если планируемая дата меньше даты создания
        if self.date_max and self.date_max < self.date_beg:
            self.date_max = self.date_beg

        # если есть спринт то проект изменяем на проект спринта
        if self.sprint:
            self.proj_id = self.sprint.proj_id

        # если дата закрытия задачи меньше вычисленой даты закрытия то правим
        if self.date_end and self.date_end < self.date_end_task:
            self.date_end = self.date_end_task

        # проверка - есть ли изменения
        desc = ""
        old = type(self).objects.filter(id=self.id).first()
        if old is None:
            desc = "Создание задачи"
        else:
            for v in self._meta.get_fields():
                if v.name in ("uweb", "id"):
                    continue
                v1 = getattr(self, v.name)
                v2 = getattr(old, v.name)
                if v1 != v2:
                    desc += f"{v.verbose_name}: {v2} => {v1};\n"

        # если есть изменения сохраняем и создаём запись в истории
        if desc:
            super().save(**kwargs)

            obj = TaskStep()
            obj.author = self.uweb
            if old and self.date_end and old.date_end is None:
                obj.desc = "Закрытие задачи\n" + desc
            elif old:
                obj.desc = "Изменения в задаче:\n" + desc
            else:
                obj.desc = desc

            obj.save(parrent=self)

        return

    class META:
        url_name = "tasks"
        url_id = "tasks_id"
        url_page = "tasks_p"
        url_filt = "tasks_f"
        url_user = "tasks_u"


class TaskStep(models.Model):
    desc = models.TextField(
        help_text="Выполненая работа по задаче",
        verbose_name="Что сделано",
    )
    date_end = models.DateTimeField(
        help_text="Дата завершения шага", verbose_name="Завершён", default=datetime.now
    )
    author = models.ForeignKey(
        help_text="Исполнитель шага",
        verbose_name="Исполнитель",
        to=get_user_model(),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="author_steps",
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

    def save(self, parrent=None, **kwargs) -> None:
        if not isinstance(parrent, Task):
            parrent = Task.objects.filter(id=self.task_id).first()

        # если задача закрыта то не записываем
        if not parrent or parrent.date_end:
            return

        self.task_id = parrent.id
        return super().save(**kwargs)

    class META:
        url_name = "task_steps"
        url_id = "tsteps_id"
        url_page = "tsteps_p"
        url_filt = "tsteps_f"
