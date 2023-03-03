# from django.shortcuts import render  # noqa
from rest_framework import viewsets
from rest_framework import mixins
from app_task.models import Proj, Sprint, Task, TaskStep
from .serializers import (
    ProjSerializer,
    SprintSerializer,
    TaskSerializer,
    TaskStepSerializer,
)
import app_task.functions as functions
from rest_framework.response import Response

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


class ProjApi(
    mixins.ListModelMixin,  # GET /articles
    mixins.RetrieveModelMixin,  # GET /articles/1
    # mixins.CreateModelMixin, # POST /articles
    # mixins.DestroyModelMixin, # DELETE /articles/1
    # mixins.UpdateModelMixin, # PUT /articles/1
    viewsets.GenericViewSet,
):
    queryset = Proj.objects.all().order_by("-date_beg")
    serializer_class = ProjSerializer
    # permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    # filterset_class =  ArticleFilterSet


class SprintApi(
    mixins.ListModelMixin,  # GET /articles
    mixins.RetrieveModelMixin,  # GET /articles/1
    # mixins.CreateModelMixin, # POST /articles
    # mixins.DestroyModelMixin, # DELETE /articles/1
    # mixins.UpdateModelMixin, # PUT /articles/1
    viewsets.GenericViewSet,
):
    queryset = Sprint.objects.all().order_by("-date_beg")
    serializer_class = SprintSerializer


class TaskApi(
    mixins.ListModelMixin,  # GET /articles
    mixins.RetrieveModelMixin,  # GET /articles/1
    mixins.CreateModelMixin,  # POST /articles
    mixins.DestroyModelMixin,  # DELETE /articles/1
    mixins.UpdateModelMixin,  # PUT /articles/1
    viewsets.GenericViewSet,
):
    queryset = Task.objects.all().order_by("-date_beg")
    serializer_class = TaskSerializer

    def get_permissions(self):
        perm = super().get_permissions()
        return perm

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        perms = functions.get_perms(request)
        if perms.get("add", False):
            return super().create(request, *args, **kwargs)
        return

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, partial=True, **kwargs)
        perms = functions.get_perms(request)
        if perms.get("edit", False):
            return super().update(request, *args, partial=True, **kwargs)
        return Response()

    def destroy(self, request, *args, **kwargs):
        perms = functions.get_perms(request)
        if perms.get("delete", False):
            return super().destroy(request, *args, **kwargs)
        return


class TaskStepApi(
    mixins.ListModelMixin,  # GET /articles
    mixins.RetrieveModelMixin,  # GET /articles/1
    # mixins.CreateModelMixin, # POST /articles
    # mixins.DestroyModelMixin, # DELETE /articles/1
    # mixins.UpdateModelMixin, # PUT /articles/1
    viewsets.GenericViewSet,
):
    queryset = TaskStep.objects.all().order_by("-date_end")
    serializer_class = TaskStepSerializer
