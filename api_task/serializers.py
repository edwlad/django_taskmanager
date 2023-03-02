from rest_framework import serializers
from app_task.models import Proj, Sprint, Task, TaskStep

# from django.contrib.auth import get_user_model


class NonModelSerializer(serializers.Serializer):
    """Сериализатор с не-модельными полями."""


class ProjSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field="username", read_only=True)
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
        fields = ("id", "author_id", "name", "desc", "date_end", "date_max")
        read_only_fields = (
            "author",
            "date_beg",
            "date_plan",
            "days_plan",
            "date_end_proj",
            # "proj_sprints",
            # "proj_tasks",
        )
        fields += read_only_fields


class SprintSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field="username", read_only=True)
    date_plan = serializers.DateField(read_only=True)
    days_plan = serializers.DurationField(read_only=True)
    date_end_sprint = serializers.DateField(read_only=True)

    class Meta:
        model = Sprint
        # depth = 1
        fields = ("id", "author_id", "name", "desc", "date_end", "date_max")
        read_only_fields = (
            "author",
            "date_beg",
            "date_plan",
            "days_plan",
            "date_end_sprint",
            # "sprint_tasks",
        )
        fields += read_only_fields


class TaskSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field="username", read_only=True)
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)
    date_plan = serializers.DateField(read_only=True)
    days_plan = serializers.DurationField(read_only=True)
    date_end_task = serializers.DateField(read_only=True)

    class Meta:
        model = Task
        # depth = 1
        fields = ("id", "author_id", "user_id", "name", "desc", "date_end", "date_max")
        read_only_fields = (
            "author",
            "user",
            "date_beg",
            "date_plan",
            "days_plan",
            "date_end_task",
        )
        fields += read_only_fields


class TaskStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskStep
        fields = tuple(v.attname for v in Task._meta.fields)
        read_only_fields = fields
