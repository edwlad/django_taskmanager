# from django.shortcuts import render  # noqa
from rest_framework import viewsets
from app_task.models import Proj, Sprint, Task, TaskStep
from .serializers import (
    ProjSerializer,
    SprintSerializer,
    TaskSerializer,
    TaskStepSerializer,
)

# from rest_framework import permissions
# from rest_framework import mixins


# Create your views here.
# class ArticleViewSet(
#     mixins.ListModelMixin, # GET /articles
#     mixins.CreateModelMixin, # POST /articles
#     mixins.RetrieveModelMixin, # GET /articles/1
#     mixins.DestroyModelMixin, # DELETE /articles/1
#     mixins.UpdateModelMixin, # PUT /articles/1
#     viewsets.GenericViewSet
# ):


class ProjApi(viewsets.ModelViewSet):
    queryset = Proj.objects.all().order_by("-date_beg")
    serializer_class = ProjSerializer
    # permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    # filterset_class =  ArticleFilterSet


class SprintApi(viewsets.ModelViewSet):
    queryset = Sprint.objects.all().order_by("-date_beg")
    serializer_class = SprintSerializer


class TaskApi(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by("-date_beg")
    serializer_class = TaskSerializer


class TaskStepApi(viewsets.ModelViewSet):
    queryset = TaskStep.objects.all().order_by("-date_end")
    serializer_class = TaskStepSerializer
