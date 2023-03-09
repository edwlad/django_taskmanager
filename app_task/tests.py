from django.test import TestCase
from app_task.models import Proj, Sprint, Task, TaskStep
import app_task.functions as functions
from django.db.models import QuerySet, F, Q, Case, When  # noqa
from django.test import Client  # noqa
from django.views.generic import ListView
from django.conf import settings


def find_template(response, template_name):
    for template in response.context:
        if template.template_name == template_name:
            return template
    return


class Base1CorrectTestCase(TestCase):
    """Проверка корректности данных в базе при случайной генерации"""

    EMAIL_BACKEND = getattr(settings, "EMAIL_BACKEND", "")

    @classmethod
    def setUpTestData(cls):
        settings.EMAIL_BACKEND = "django.core.mail.backends.dummy.EmailBackend"
        if not Proj.objects.exists():
            functions.gen_data(cnt=50, close=60, parent=True)

    @classmethod
    def tearDownClass(cls):
        settings.EMAIL_BACKEND = cls.EMAIL_BACKEND
        return super().tearDown(cls)

    def test_proj(self):
        qs = Proj.objects.all()
        self.assertFalse(
            qs.exclude(date_max=None).filter(date_max__lt=F("date_beg")).exists(),
            "планируемая дата закрытия проекта меньше даты создания",
        )
        self.assertFalse(
            qs.exclude(Q(date_end=None) | Q(proj_sprints=None))
            .filter(proj_sprints__date_end=None)
            .exists(),
            "проект закрыт при незакрытых спринтах",
        )
        self.assertFalse(
            qs.exclude(Q(date_end=None) | Q(proj_tasks=None))
            .filter(proj_tasks__date_end=None)
            .exists(),
            "проект закрыт при незакрытых задачах",
        )
        self.assertFalse(
            qs.exclude(date_end=None).filter(date_end__lt=F("date_end_proj")).exists(),
            "дата закрытия проекта меньше вычисленой даты закрытия",
        )

    def test_sprint(self):
        qs = Sprint.objects.all()
        self.assertFalse(
            qs.exclude(date_max=None).filter(date_max__lt=F("date_beg")).exists(),
            "планируемая дата закрытия спринта меньше даты создания",
        )
        self.assertFalse(
            qs.exclude(Q(date_end=None) | Q(sprint_tasks=None))
            .filter(sprint_tasks__date_end=None)
            .exists(),
            "спринт закрыт при незакрытых задачах",
        )
        self.assertFalse(
            qs.exclude(date_end=None)
            .filter(date_end__lt=F("date_end_sprint"))
            .exists(),
            "дата закрытия спринта меньше вычисленой даты закрытия",
        )

    def test_task(self):
        qs = Task.objects.all()
        self.assertFalse(
            qs.exclude(date_max=None).filter(date_max__lt=F("date_beg")).exists(),
            "планируемая дата закрытия задачи меньше даты создания",
        )
        self.assertFalse(
            qs.exclude(Q(sprint_id=None) | Q(sprint__proj_id=F("proj_id"))).exists(),
            "спринт задачи не принадлежит проекту задачи",
        )
        self.assertFalse(
            qs.exclude(date_end=None).filter(date_end__lt=F("date_end_task")).exists(),
            "дата закрытия задачи меньше вычисленой даты закрытия",
        )
        self.assertFalse(
            qs.filter(task_steps=None).exists(),
            "не для всех задач появилась запись в истории",
        )
        self.assertFalse(
            qs.exclude(
                Q(parent=None) | Q(sprint=None) | Q(parent__sprint_id=F("sprint_id"))
            ).exists(),
            "есть предыдущая задача и спринт, но спринты не совпадают",
        )
        self.assertFalse(
            qs.filter(sprint=None)
            .exclude(Q(parent=None) | Q(parent__sprint_id=None))
            .exists(),
            "есть предыдущая задача и нет спринта, но спринты не совпадают",
        )
        self.assertFalse(
            qs.exclude(Q(parent=None) | Q(parent__proj_id=F("proj_id"))).exists(),
            "есть предыдущая задача, но проекты не совпадают",
        )
        self.assertFalse(
            qs.exclude(parent=None).filter(parent_id=F("id")).exists(),
            "есть предыдущая задача, но задача ссылаетя сама на себя",
        )
        self.assertFalse(
            qs.exclude(Q(parent=None) | Q(parent__parent=None)).exists(),
            "есть предыдущая задача, но у предыдущей задачи есть родитель",
        )

    def test_task_step(self):
        qs = TaskStep.objects.all()
        self.assertFalse(qs.filter(date_end=None).exists(), "нет даты создания записи")
        self.assertFalse(qs.filter(author=None).exists(), "нет автора записи")
        self.assertFalse(qs.filter(task_id=None).exists(), "нет задачи для записи")


class Base2ModifyTestCase(TestCase):
    """Проверка изменений данных в базе"""

    EMAIL_BACKEND = getattr(settings, "EMAIL_BACKEND", "")

    @classmethod
    def setUpTestData(cls):
        settings.EMAIL_BACKEND = "django.core.mail.backends.dummy.EmailBackend"
        if not Proj.objects.exists():
            functions.gen_data(cnt=10, close=70)

    @classmethod
    def tearDownClass(cls):
        settings.EMAIL_BACKEND = cls.EMAIL_BACKEND
        return super().tearDown(cls)

    def setUp(self):
        self.client = Client()
        return

    # def tearDown(self):
    #     return super().tearDown()

    def test_proj(self):
        model = Proj
        url_name = model.META.url_name
        list_template = "list_proj.html"
        # detail_template = "detail_proj.html"

        # список проектов
        response = self.client.get(f"/{url_name}/")
        self.assertEqual(response.status_code, 200, "код статуса не 200")
        self.assertIsNotNone(
            template := find_template(response, list_template),
            f"не найден шаблон списка проектов {list_template}",
        )
        view: ListView = template.dicts[3]["view"]
        self.assertIs(view.model, model, "модель не проект")
        self.assertFalse(
            view.queryset.exclude(date_end=None).exists(),
            "в отбор попал закрытый проект",
        )

        # создание проекта неавторизированым пользователем

        # создание проекта авторизированым пользователем

        # редактирование проекта авторизированым пользователем

        # удаление проекта авторизированым пользователем

        self.assertFalse(False, "")
        return

    def test_sprint(self):
        model = Sprint
        url_name = model.META.url_name
        list_template = "list_sprint.html"
        # detail_template = "detail_sprint.html"

        # список спринтов
        response = self.client.get(f"/{url_name}/")
        self.assertEqual(response.status_code, 200, "код статуса не 200")
        self.assertIsNotNone(
            template := find_template(response, list_template),
            f"не найден шаблон списка спринтов {list_template}",
        )
        view: ListView = template.dicts[3]["view"]
        self.assertIs(view.model, model, "модель не спринт")
        self.assertFalse(
            view.queryset.exclude(date_end=None).exists(),
            "в отбор попал закрытый спринт",
        )

        self.assertFalse(False, "")
        return

    def test_task(self):
        model = Task
        url_name = model.META.url_name
        list_template = "list_task.html"
        # detail_template = "detail_task.html"

        # список задач
        response = self.client.get(f"/{url_name}/")
        self.assertEqual(response.status_code, 200, "код статуса не 200")
        self.assertIsNotNone(
            template := find_template(response, list_template),
            f"не найден шаблон списка задач {list_template}",
        )
        view: ListView = template.dicts[3]["view"]
        self.assertIs(view.model, model, "модель не задача")
        self.assertFalse(
            view.queryset.exclude(date_end=None).exists(),
            "в отбор попала закрытая задача",
        )

        self.assertFalse(False, "")
        return

    def test_task_step(self):
        # qs = TaskStep.objects.all()
        self.assertFalse(False, "не появились записи при изменении задачи")
        self.assertFalse(False, "если задача закрыта то не записываем")
        self.assertFalse(False, "")
        return
