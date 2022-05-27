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
    ResultModel,
    TestLessonsForGroup
)

from datetime import date

import json
import requests
import time
import datetime


def add_base_data():
    StudySubGroup.objects.all().delete()
    StudyGroup.objects.all().delete()
    Institute.objects.all().delete()
    LessonType.objects.all().delete()
    TimeSlot.objects.all().delete()

    js_file_lstypes = open('static/lessontypes.json', 'rb')
    parse_lstypes = json.load(js_file_lstypes)

    for x in parse_lstypes:
        LessonType.objects.create(name=x['name'], name_in_1c=x['name_in_1c'])

    js_file_slots = open('static/timeslots.json', 'rb')
    parse_slots = json.load(js_file_slots)

    for x in parse_slots:
        TimeSlot.objects.create(slot=x['slot'], start_time=x['start_time'], end_time=x['end_time'])

    js_file_inst = open('static/institutions.json', 'rb')
    parse_inst = json.load(js_file_inst)

    for x in parse_inst:
        Institute.objects.create(id=x['id'], name=x['name'])

    json_file = open('static/structure.json', 'rb')
    parse = json.load(json_file)

    for y in parse:
        institute = Institute.objects.get(id=y['id'])
        for z in y['groups']:
            subgroup_list = []
            num_in_group = 1

            for a in z['subGroups']:
                StudySubGroup.objects.create(number_in_group=num_in_group,
                                             name=a['name'])
                num_in_group += 1
                subgroup_list.append(StudySubGroup.objects.get(name=a['name']).id)

            abc = StudyGroup.objects.create(name=z['name'], institute=institute)
            abc.sub_groups.set([x for x in subgroup_list])


def create_result_table():
    days_all = [1, 2, 3, 4, 5, 6]

    ResultModel.objects.all().delete()
    TestLessonsForGroup.objects.all().delete()

    groups = StudyGroup.objects.all()

    def append_lessons_for_group(one_day_f, group_f, week_f):
        date_td = str(one_day_f[week_f].date).split('-')
        week_today = datetime.date(int(date_td[0]), int(date_td[1]),
                                   int(date_td[2])).isocalendar().week

        start_date = time.asctime(time.strptime('2022 %d 1' % week_today, '%Y %W %w'))
        start_date = datetime.datetime.strptime(start_date, '%a %b %d %H:%M:%S %Y')
        dates = [start_date.strftime('%Y-%m-%d')]

        for i in range(1, 6):
            day = start_date + datetime.timedelta(days=i)
            dates.append(day.strftime('%Y-%m-%d'))

        for day in days_all:
            lessons_for_day_and_groupid = Lesson.objects.filter(dayID=day).filter(
                group=group_f.id)

            abc = TestLessonsForGroup.objects.create(
                date=dates[day - 1],
                dayID=day,
                group=group_f
            )
            abc.lessons.set([x for x in lessons_for_day_and_groupid.filter(date=dates[day - 1])])

    for group in groups:
        check_sub_groups = group.sub_groups.all()

        if check_sub_groups:
            for week in range(0, 2):
                one_day = Lesson.objects.filter(dayID=1).filter(sub_group=check_sub_groups[0].id)

                append_lessons_for_group(one_day_f=one_day, group_f=group, week_f=week)

        if not check_sub_groups:
            for week in range(0, 2):
                one_day = Lesson.objects.filter(dayID=1).filter(group_id=group.id)

                append_lessons_for_group(one_day_f=one_day, group_f=group, week_f=week)

    for group in groups:
        grouping_lessons = TestLessonsForGroup.objects.filter(group=group)

        create_lessons_for_group = ResultModel.objects.create(
            study_group=group
        )
        create_lessons_for_group.timetable.set([x for x in grouping_lessons])


def add_schedule():
    """ This function adds a schedule to the database. First, the current week is added according to server time,
        then the next week after the current one is added. If there are no lessons for the day of the week,
        then an "empty day" is added (this field contains dayID, date and group).

        Later the function will be redesigned in accordance with the OOP. """

    counter = 1

    Lesson.objects.all().delete()
    Teacher.objects.all().delete()
    Classroom.objects.all().delete()
    Discipline.objects.all().delete()

    all_groups = StudyGroup.objects.all()

    def check_data(one_lesson_f):
        check_discipline = Discipline.objects.filter(name=one_lesson_f['discipline']['name'])
        if not check_discipline:
            Discipline.objects.create(name=one_lesson_f['discipline']['name'])

        check_classroom = Classroom.objects.filter(
            name=one_lesson_f['classrooms'][0]['room']['name'])
        if not check_classroom:
            Classroom.objects.create(name=one_lesson_f['classrooms'][0]['room']['name'])

        check_teacher = Teacher.objects.filter(id=one_lesson_f['teachers'][0]['id'])
        if not check_teacher:
            Teacher.objects.create(id=one_lesson_f['teachers'][0]['id'],
                                   name=one_lesson_f['teachers'][0]['name'])

    for week in range(0, 2):

        date_td = str(date.today()).split('-')  # get today date
        week_today = datetime.date(int(date_td[0]), int(date_td[1]), int(date_td[2])).isocalendar().week

        startdate = time.asctime(time.strptime('2022 %d 1' % (week_today + week), '%Y %W %w'))
        startdate = datetime.datetime.strptime(startdate, '%a %b %d %H:%M:%S %Y')
        dates = [startdate.strftime('%Y-%m-%d')]

        for i in range(1, 6):
            day = startdate + datetime.timedelta(days=i)
            dates.append(day.strftime('%Y-%m-%d'))

        for group_name in all_groups:

            sub_group = StudyGroup.objects.get(name=group_name).sub_groups.all()

            if not sub_group:
                response = requests.get(
                    f'https://online.i-klgtu.ru/table/hs/campus/timetable/group?'
                    f'id={group_name}&'
                    f'date={dates[0].split("-")[0] + dates[0].split("-")[1] + dates[0].split("-")[2]}&'
                    f'period=week',
                    auth=('kstuapp', 'app39)'))

                print('request: no subgroups |', 'week:', week + 1, '|', group_name)

                json_decode = json.loads(response.text)

                days_have = {1: 'no', 2: 'no', 3: 'no', 4: 'no', 5: 'no', 6: 'no'}
                flag = 0

                for school_day in json_decode:
                    days_have[school_day['order']] = 'yes'

                for state in days_have:

                    if days_have[state] == 'yes':
                        for one_lesson in json_decode[flag]['items']:
                            check_data(one_lesson_f=one_lesson)

                            get_discipline = Discipline.objects.get(name=one_lesson['discipline']['name'])
                            get_group = StudyGroup.objects.get(name=group_name)
                            get_lesson_type = LessonType.objects.get(
                                name_in_1c=one_lesson['lesson_type']['identifiers']['id'])
                            get_time_slot = TimeSlot.objects.get(start_time=one_lesson['start_time'])
                            get_class_room = Classroom.objects.get(name=one_lesson['classrooms'][0]['room']['name'])
                            get_teacher = Teacher.objects.get(id=one_lesson['teachers'][0]['id'])

                            Lesson.objects.create(date=one_lesson['date'],
                                                  dayID=one_lesson['order'],
                                                  group=get_group,
                                                  discipline=get_discipline,
                                                  lesson_type=get_lesson_type,
                                                  time_slot=get_time_slot,
                                                  classroom=get_class_room,
                                                  teacher=get_teacher)

                        flag += 1

                    if days_have[state] == 'no':
                        get_group = StudyGroup.objects.get(name=group_name)

                        Lesson.objects.create(date=dates[state - 1],
                                              dayID=state,
                                              group=get_group)
                # time.sleep(0.5)

            for one_sub_group in sub_group:
                response = requests.get(
                    f'https://online.i-klgtu.ru/table/hs/campus/timetable/group?'
                    f'id={one_sub_group}&'
                    f'date={dates[0].split("-")[0] + dates[0].split("-")[1] + dates[0].split("-")[2]}&'
                    f'period=week',
                    auth=('kstuapp', 'app39)'))

                print('request: with subgroups |', 'week:', week + 1, '|', one_sub_group)

                json_decode = json.loads(response.text)
                days_have = {1: 'no', 2: 'no', 3: 'no', 4: 'no', 5: 'no', 6: 'no'}
                flag = 0

                for school_day in json_decode:
                    days_have[school_day['order']] = 'yes'

                for state in days_have:

                    if days_have[state] == 'yes':
                        for one_lesson in json_decode[flag]['items']:
                            check_data(one_lesson_f=one_lesson)

                            get_discipline = Discipline.objects.get(name=one_lesson['discipline']['name'])
                            get_group = StudyGroup.objects.get(name=group_name)
                            get_sub_group = StudySubGroup.objects.get(name=one_sub_group)
                            get_lesson_type = LessonType.objects.get(
                                name_in_1c=one_lesson['lesson_type']['identifiers']['id'])
                            get_time_slot = TimeSlot.objects.get(start_time=one_lesson['start_time'])
                            get_class_room = Classroom.objects.get(name=one_lesson['classrooms'][0]['room']['name'])
                            get_teacher = Teacher.objects.get(id=one_lesson['teachers'][0]['id'])

                            Lesson.objects.create(date=one_lesson['date'],
                                                  dayID=one_lesson['order'],
                                                  group=get_group,
                                                  sub_group=get_sub_group,
                                                  discipline=get_discipline,
                                                  lesson_type=get_lesson_type,
                                                  time_slot=get_time_slot,
                                                  classroom=get_class_room,
                                                  teacher=get_teacher)

                        flag += 1

                    if days_have[state] == 'no':
                        get_group = StudyGroup.objects.get(name=group_name)
                        get_sub_group = StudySubGroup.objects.get(name=one_sub_group)

                        Lesson.objects.create(date=dates[state - 1],
                                              dayID=state,
                                              group=get_group,
                                              sub_group=get_sub_group)
                # time.sleep(0.5)
            counter += 1
