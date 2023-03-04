from rest_framework import serializers
from app_task.models import Proj, Sprint, Task, TaskStep

# from django.contrib.auth import get_user_model


class NonModelSerializer(serializers.Serializer):
    """Сериализатор с не-модельными полями."""


class ProjSerializer(serializers.ModelSerializer):
    # author = serializers.SlugRelatedField(slug_field="username", read_only=True)
    author = serializers.StringRelatedField(read_only=True)
    date_plan = serializers.DateField(read_only=True)
    days_plan = serializers.DurationField(read_only=True)
    date_end_proj = serializers.DateField(read_only=True)
    # proj_sprints = serializers.SlugRelatedField(
    #     read_only=True, many=True, slug_field="name"
    # )
    # proj_tasks = serializers.SlugRelatedField(
    #     read_only=True, many=True, slug_field="name"
    # )

    class Meta:
        model = Proj
        # depth = 1
        # fields = tuple(v.name for v in model._meta.get_fields())
        fields = (
            "id",
            "author_id",
            "name",
            "desc",
            "date_beg",
            "date_end",
            "date_max",
            "author",
            "date_plan",
            "days_plan",
            "date_end_proj",
            # "proj_sprints",
            # "proj_tasks",
        )
        read_only_fields = fields


class SprintSerializer(serializers.ModelSerializer):
    proj = serializers.StringRelatedField(read_only=True)
    author = serializers.StringRelatedField(read_only=True)
    date_plan = serializers.DateField(read_only=True)
    days_plan = serializers.DurationField(read_only=True)
    date_end_sprint = serializers.DateField(read_only=True)

    class Meta:
        model = Sprint
        # depth = 1
        # fields = tuple(v.name for v in model._meta.get_fields())
        fields = (
            "id",
            "proj_id",
            "author_id",
            "name",
            "desc",
            "date_beg",
            "date_end",
            "date_max",
            "proj",
            "author",
            "date_plan",
            "days_plan",
            "date_end_sprint",
            # "sprint_tasks",
        )
        read_only_fields = fields


class TaskSerializer(serializers.ModelSerializer):
    # partial = True
    proj = serializers.StringRelatedField(read_only=True)
    sprint = serializers.StringRelatedField(read_only=True)
    parent = serializers.StringRelatedField(read_only=True)
    author = serializers.StringRelatedField(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    date_plan = serializers.DateField(read_only=True)
    days_plan = serializers.DurationField(read_only=True)
    date_end_task = serializers.DateField(read_only=True)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    class Meta:
        model = Task
        # depth = 1
        # fields = tuple(v.name for v in model._meta.get_fields())
        fields = (
            "id",
            "proj_id",
            "sprint_id",
            "parent_id",
            "author_id",
            "user_id",
            "name",
            "desc",
            "date_beg",
            "date_end",
            "date_max",
            "proj",
            "sprint",
            "parent",
            "author",
            "user",
            "date_plan",
            "days_plan",
            "date_end_task",
        )
        read_only_fields = fields


class TaskStepSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    task = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = TaskStep
        # fields = tuple(v.name for v in model._meta.get_fields())
        fields = (
            "id",
            "author_id",
            "task_id",
            "date_end",
            "desc",
            "author",
            "task",
        )
        read_only_fields = fields
