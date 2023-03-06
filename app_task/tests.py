from django.test import TestCase
from app_task.models import Proj, Sprint, Task, TaskStep  # noqa
import app_task.functions as functions
from django.db.models import F, Q, Case, When  # noqa


class IsBaseCorrectTestCase(TestCase):
    """Проверка корректности данных в базе при случайной генерации"""

    CNT = 100
    CLEAR = True
    CLOSE = 60

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        functions.gen_data(cnt=cls.CNT, clear=cls.CLEAR, close=cls.CLOSE)
        return

    # @classmethod
    # def tearDownClass(self) -> None:
    #     return super().tearDownClass()

    def test_proj(self):
        qs = Proj.objects.all()
        self.assertEqual(len(qs), self.CNT, "не верное количество созданых проектов")
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

        # self.assertFalse(False, "если есть предыдущая задача")

    def test_task_step(self):
        qs = TaskStep.objects.all()
        self.assertFalse(qs.filter(date_end=None).exists(), "нет даты создания записи")
        self.assertFalse(qs.filter(author=None).exists(), "нет автора записи")
        self.assertFalse(qs.filter(task_id=None).exists(), "нет задачи для записи")


class IsBaseModifyTestCase(TestCase):
    """Проверка изменений данных в базе"""

    CNT = 4
    CLEAR = True
    CLOSE = 50

    def setUp(self):
        super().setUp()
        functions.gen_data(cnt=self.CNT, clear=self.CLEAR, close=self.CLOSE)
        return

    # def tearDown(self):
    #     return super().tearDown()

    def test_proj(self):
        # qs = Proj.objects.all()
        return

    def test_sprint(self):
        # qs = Sprint.objects.all()
        self.assertFalse(False, "изменился спринт при закрытом проекте")

    def test_task(self):
        # qs = Task.objects.all()
        self.assertFalse(
            False, "если закрыты спринт и/или проект то ничего не сохраняем"
        )

    def test_task_step(self):
        # qs = TaskStep.objects.all()
        self.assertFalse(False, "не появились записи при изменении задачи")
        self.assertFalse(False, "если задача закрыта то не записываем")
