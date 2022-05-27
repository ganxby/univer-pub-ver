from rest_framework import serializers
from .models import Lesson, TestLessonsForGroup, ResultModel, StudyGroup


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyGroup
        fields = ['id', 'name']


class LessonSerializer(serializers.ModelSerializer):
    group = GroupSerializer(read_only=True)

    class Meta:
        model = Lesson
        fields = ['id', 'date', 'group', 'sub_group', 'discipline', 'lesson_type', 'time_slot', 'classroom', 'teacher']
        depth = 2


class TestLessonsForGroupSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = TestLessonsForGroup
        fields = ['date', 'dayID', 'lessons']
        depth = 3


class ResultModelSerializer(serializers.ModelSerializer):
    timetable = TestLessonsForGroupSerializer(many=True, read_only=True)

    class Meta:
        model = ResultModel
        fields = ['study_group', 'timetable']
        depth = 3
