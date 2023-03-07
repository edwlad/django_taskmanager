from django.test import TestCase
from app_task.models import Proj, Sprint, Task, TaskStep  # noqa
import app_task.functions as functions
from django.db.models import F, Q, Case, When  # noqa


class BaseCorrectTestCase(TestCase):
    """Проверка корректности данных в базе при случайной генерации"""

    CNT = 200
    CLOSE = 60
    CLEAR = True
    PARENT = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        functions.gen_data(
            cnt=cls.CNT, close=cls.CLOSE, clear=cls.CLEAR, parent=cls.PARENT
        )
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

        self.assertFalse(
            qs.exclude(parent=None).filter(sprint_id=None).exists(),
            "есть предыдущая задача, но нет спринта у текущей задачи",
        )
        self.assertFalse(
            qs.exclude(parent=None).filter(parent_id=F("id")).exists(),
            "есть предыдущая задача, но задача ссылаетя сама на себя",
        )
        # self.assertFalse(
        #     qs.exclude(Q(parent=None) | Q(parent_nexts=None)).exists(),
        #     "есть предыдущая задача, но у текущей задачи есть дети",
        # )
        self.assertFalse(
            qs.exclude(Q(parent=None) | Q(parent__parent=None)).exists(),
            "есть предыдущая задача, но у предыдущей задачи есть родитель",
        )
        self.assertFalse(
            qs.exclude(Q(parent=None) | Q(parent__sprint_id=F("sprint_id"))).exists(),
            "предыдущая задача не в списке задач спринта текущей задачи",
        )

    def test_task_step(self):
        qs = TaskStep.objects.all()
        self.assertFalse(qs.filter(date_end=None).exists(), "нет даты создания записи")
        self.assertFalse(qs.filter(author=None).exists(), "нет автора записи")
        self.assertFalse(qs.filter(task_id=None).exists(), "нет задачи для записи")


class BaseModifyTestCase(TestCase):
    """Проверка изменений данных в базе"""

    CNT = 0
    CLOSE = 0
    CLEAR = True
    PARENT = True

    def setUp(self):
        super().setUp()
        functions.gen_data(
            cnt=self.CNT, close=self.CLOSE, clear=self.CLEAR, parent=self.PARENT
        )
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
