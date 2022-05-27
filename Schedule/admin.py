from django.contrib import admin
from .models import (
    Lesson,
    StudyGroup,
    StudySubGroup,
    Classroom,
    LessonType,
    TimeSlot,
    Discipline,
    Teacher,
    Institute,
    TestLessonsForGroup,
    ResultModel
)

admin.site.register(StudyGroup)
admin.site.register(StudySubGroup)
admin.site.register(Discipline)
admin.site.register(Classroom)
admin.site.register(Teacher)
admin.site.register(LessonType)
admin.site.register(TimeSlot)
admin.site.register(Institute)
admin.site.register(ResultModel)


@admin.register(Lesson)
class Lesson(admin.ModelAdmin):
    list_display = ('date', 'group', 'sub_group', 'dayID')
    list_filter = ('group', 'date')


@admin.register(TestLessonsForGroup)
class TestLessonsForGroup(admin.ModelAdmin):
    list_display = ('date', 'group', 'dayID')
    list_filter = ('group', 'date')
