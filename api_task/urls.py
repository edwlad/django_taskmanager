from rest_framework.routers import DefaultRouter
from api_task.views import ProjApi, SprintApi, TaskApi, TaskStepApi
from app_task.models import Proj, Sprint, Task, TaskStep

# router = DefaultRouter(trailing_slash=False)
router = DefaultRouter()

# app_name = "articlesapp"

router.register(
    prefix=Proj.META.url_name,
    viewset=ProjApi,
    basename=Proj.META.url_name,
)
router.register(
    prefix=Sprint.META.url_name,
    viewset=SprintApi,
    basename=Sprint.META.url_name,
)
router.register(
    prefix=Task.META.url_name,
    viewset=TaskApi,
    basename=Task.META.url_name,
)
router.register(
    prefix=TaskStep.META.url_name,
    viewset=TaskStepApi,
    basename=TaskStep.META.url_name,
)

urlpatterns = router.urls
