# from django.shortcuts import render  # noqa
from rest_framework import viewsets
from rest_framework import mixins
from app_task.models import Proj, Sprint, Task, TaskStep
from api_task.serializers import (
    ProjSerializer,
    SprintSerializer,
    TaskSerializer,
    TaskStepSerializer,
)
import api_task.functions as functions

# import app_task.functions as functions
# from rest_framework.response import Response
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
    model = Proj
    serializer_class = ProjSerializer

    def get_queryset(self):
        qs = self.model.objects.order_by("-date_beg", "-id")
        qs = functions.filter(qs, self.request)
        return qs


class SprintApi(
    mixins.ListModelMixin,  # GET /articles
    mixins.RetrieveModelMixin,  # GET /articles/1
    # mixins.CreateModelMixin, # POST /articles
    # mixins.DestroyModelMixin, # DELETE /articles/1
    # mixins.UpdateModelMixin, # PUT /articles/1
    viewsets.GenericViewSet,
):
    model = Sprint
    serializer_class = SprintSerializer

    def get_queryset(self):
        qs = self.model.objects.order_by("-date_beg", "-id")
        qs = functions.filter(qs, self.request)
        return qs


class TaskApi(
    mixins.ListModelMixin,  # GET /articles
    mixins.RetrieveModelMixin,  # GET /articles/1
    # mixins.CreateModelMixin,  # POST /articles
    # mixins.DestroyModelMixin,  # DELETE /articles/1
    # mixins.UpdateModelMixin,  # PUT /articles/1
    viewsets.GenericViewSet,
):
    model = Task
    serializer_class = TaskSerializer

    def get_queryset(self):
        qs = self.model.objects.order_by("-date_beg", "-id")
        qs = functions.filter(qs, self.request)
        return qs


class TaskStepApi(
    mixins.ListModelMixin,  # GET /articles
    mixins.RetrieveModelMixin,  # GET /articles/1
    # mixins.CreateModelMixin, # POST /articles
    # mixins.DestroyModelMixin, # DELETE /articles/1
    # mixins.UpdateModelMixin, # PUT /articles/1
    viewsets.GenericViewSet,
):
    model = TaskStep
    serializer_class = TaskStepSerializer

    def get_queryset(self):
        qs = self.model.objects.order_by("-date_end", "-id")
        qs = functions.filter(qs, self.request)
        return qs
