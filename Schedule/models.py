from django.db import models


class LessonType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64)
    name_in_1c = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class TimeSlot(models.Model):
    slot = models.IntegerField(primary_key=True)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return str(self.slot)


class Classroom(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64)
    short_name = models.CharField(max_length=7, blank=True, null=True)

    def __str__(self):
        return self.name


class Institute(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class StudySubGroup(models.Model):
    id = models.AutoField(primary_key=True)
    number_in_group = models.CharField(max_length=64)
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class StudyGroup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)
    sub_groups = models.ManyToManyField(StudySubGroup, blank=True)

    def __str__(self):
        return self.name


class Discipline(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Teacher(models.Model):
    id = models.CharField(primary_key=True, max_length=64)
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Lesson(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField()
    dayID = models.IntegerField()
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE)
    sub_group = models.ForeignKey(StudySubGroup, on_delete=models.CASCADE, blank=True, null=True)
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE, blank=True, null=True)
    lesson_type = models.ForeignKey(LessonType, on_delete=models.CASCADE, blank=True, null=True)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, blank=True, null=True)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, blank=True, null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return str(self.date) + ' -- ' + str(self.group)


class TestLessonsForGroup(models.Model):
    date = models.DateField()
    dayID = models.IntegerField()
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE)
    lessons = models.ManyToManyField(Lesson, blank=True)

    def __str__(self):
        return str(self.date) + ' -- ' + str(self.dayID) + ' -- ' + str(self.group)


class ResultModel(models.Model):
    study_group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE)
    timetable = models.ManyToManyField(TestLessonsForGroup, blank=True)

    def __str__(self):
        return self.study_group.name
