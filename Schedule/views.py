from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response

from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

from .serializers import LessonSerializer, ResultModelSerializer
from .models import (
    Lesson,
    StudyGroup,
    Classroom,
    LessonType,
    TimeSlot,
    Discipline,
    Teacher,
    ResultModel
)

from . import services

import json
import requests
import time
import datetime


class LessonViewSet(ReadOnlyModelViewSet):  # I want to use this class for pagination test later
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()


class ResultTableView(APIView):

    def post(self, request):
        request_data = request.data
        check_request = ScheduleHandler(request_data=request_data)
        check_request.check_group()

        if check_request.status == 404:
            return Response([], status=status.HTTP_404_NOT_FOUND)

        get_group_id = check_request.group_id
        queryset = ResultModel.objects.filter(study_group__id=get_group_id)

        serializer = ResultModelSerializer(queryset, many=True)

        string_ = json.dumps(serializer.data, ensure_ascii=False)
        data = json.loads(string_)

        def custom_key(key):
            return key['time_slot']['slot']

        if not data[0]['study_group']['sub_groups']:  # if not sub_groups
            for day in data[0]['timetable']:
                if day['lessons'][0]['discipline'] is None:
                    day['lessons'] = []

        if data[0]['study_group']['sub_groups']:  # if sub_groups
            for day in data[0]['timetable']:

                if day['lessons'][0]['discipline'] is None and day['lessons'][1]['discipline'] is None:
                    day['lessons'] = []

                for lesson in day['lessons']:
                    if lesson['discipline'] is None:
                        day['lessons'].remove(lesson)

                try:
                    day['lessons'].sort(key=custom_key)
                except TypeError:
                    pass
                except KeyError:
                    pass

        return Response(data, status=status.HTTP_200_OK)


class ScheduleHandler:

    def __init__(self, request_data):
        self.request = request_data
        self.status = None
        self.group_id = None

    def check_group(self):
        try:
            self.group_id = StudyGroup.objects.get(name=self.request['name']).id
            self.status = 200

        except ObjectDoesNotExist:
            self.status = 404


def log_func(text):
    time.localtime()
    print(f'[*] [{time.localtime().tm_mday}/{time.localtime().tm_mon}/{time.localtime().tm_year} '
          f'{time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec}] " {text} "')


@csrf_exempt
@api_view(['GET', 'POST'])
def add_full_data(request):
    """ Use api method to add full schedule because celery crontab don't work in windows (i use this OS to
    development now). Celery crontab work in linux version of this app"""

    if request.method == 'GET':

        log_func("Addition of basic data (study groups, institutes, etc.) launched")
        services.add_base_data()
        log_func("Adding base data has been completed")
        time.sleep(1)

        log_func("Addition of schedule data launched")
        services.add_schedule()
        log_func("Adding schedule data has been completed")
        time.sleep(1)

        log_func("Addition of result table launched")
        services.create_result_table()
        log_func("Adding result table has been completed")

        return JsonResponse({'status': 'ok'}, status=status.HTTP_200_OK)
