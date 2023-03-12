from django.db import models
from django.contrib.auth import get_user_model
from datetime import date, datetime  # noqa
from app_task.managers import TaskManager, SprintManager, ProjManager

# from django.contrib import messages


class Proj(models.Model):
    objects = ProjManager()

    name = models.CharField(
        help_text="Название проекта", verbose_name="Название", max_length=120
    )
    name_upper = models.CharField(
        help_text="Название проекта в ВЕРХНЕМ регистре",
        verbose_name="НАЗВАНИЕ",
        max_length=120,
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
        return f"({self.id}) {self.name}"

    def save(self, **kwargs) -> None:
        self.name_upper = self.name.upper()

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
                if v.name in ("uweb", "id", "name_upper"):
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

                obj.save(cur_task=v)

        return

    class META:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
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
    name_upper = models.CharField(
        help_text="Название спринта в ВЕРХНЕМ регистре",
        verbose_name="НАЗВАНИЕ",
        max_length=120,
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
        return f"({self.id}) {self.name}"

    def save(self, **kwargs) -> None:
        self.name_upper = self.name.upper()

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
                if v.name in ("uweb", "id", "name_upper"):
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

                obj.save(cur_task=v)

        return

    class META:
        verbose_name = "Спринт"
        verbose_name_plural = "Спринты"
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
    name_upper = models.CharField(
        help_text="Название задачи в ВЕРХНЕМ регистре",
        verbose_name="НАЗВАНИЕ",
        max_length=120,
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
        on_delete=models.CASCADE,
        related_name="proj_tasks",
    )
    sprint = models.ForeignKey(
        help_text="Спринт",
        verbose_name="Спринт",
        to="Sprint",
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
        return f"({self.id}) {self.name}"

    def save(self, **kwargs) -> None:
        self.name_upper = self.name.upper()

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

        # если есть предыдущая задача
        if self.parent:
            if (
                self.parent_id == self.id  # если ссылаетя сама на себя
                or self.parent.parent  # если у предыдущей задачи есть родитель
                or self.parent_nexts.all().exists()  # если у текущей задачи есть дети
            ):
                self.parent = None
            else:
                self.proj = self.parent.proj
                self.sprint = self.parent.sprint

        # проверка - есть ли изменения
        desc = ""
        old = type(self).objects.filter(id=self.id).first()
        if old is None:
            desc = "Создание задачи"
        else:
            for v in self._meta.get_fields():
                if v.name in ("uweb", "id", "name_upper"):
                    continue
                v1 = getattr(self, v.name)
                v2 = getattr(old, v.name)
                if v1 != v2:
                    desc += f"{v.verbose_name.upper()}: {v2} => {v1};\n"

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

            obj.save(cur_task=self, forse=True)

            # если есть зависимые задачи то правим проект и спринт
            # и записываем в историю
            if nexts := list(self.parent_nexts.all()):
                for task in nexts:
                    obj = TaskStep()
                    obj.author = self.uweb
                    obj.desc = f'Изменения в "родительской" задаче: {self}:\n' + desc
                    obj.save(cur_task=task)

                    if task.sprint != self.sprint or task.proj != self.proj:
                        task.uweb = self.uweb
                        task.sprint = self.sprint
                        task.proj = self.proj
                        task.save()

        return

    class META:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        url_name = "tasks"
        url_id = "tasks_id"
        url_page = "tasks_p"
        url_filt = "tasks_f"
        url_user = "tasks_u"


class TaskStep(models.Model):
    desc = models.TextField(
        help_text="Выполненная работа по задаче",
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
    auto_create = models.BooleanField(
        help_text="Запись создана автоматически",
        verbose_name="Автосоздано",
        default=True,
    )
    task = models.ForeignKey(
        help_text="Задача",
        verbose_name="Задача",
        to="Task",
        on_delete=models.CASCADE,
        related_name="task_steps",
    )

    def __str__(self) -> str:
        return f"{self.id}: {self.desc[:30]}"

    def save(self, cur_task=None, forse=False, **kwargs) -> None:
        if not isinstance(cur_task, Task):
            self.auto_create = False
            cur_task = Task.objects.filter(id=self.task_id).first()

        # если задача закрыта то не записываем
        if not forse and (not cur_task or cur_task.date_end):
            return

        self.task_id = cur_task.id
        return super().save(**kwargs)

    class META:
        verbose_name = "Шаг"
        verbose_name_plural = "Шаги"
        url_name = "task_steps"
        url_id = "tsteps_id"
        url_page = "tsteps_p"
        url_filt = "tsteps_f"
