from django.shortcuts import render
from django.contrib.auth.models import User
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.parsers import JSONParser
from rest_framework import status

import json
import requests


@csrf_exempt
def get_current_user(request):
    user_from_db = User.objects.all()
    json_data = json.dumps(str(user_from_db[1].is_active))

    if request.method == 'GET':
        if not user_from_db[1].is_active:
            return JsonResponse({'user': 'not active'}, status=status.HTTP_401_UNAUTHORIZED)

        return JsonResponse({'user': json_data}, status=status.HTTP_200_OK)

    if request.method == 'POST':
        data = JSONParser().parse(request)
        return JsonResponse({'your data': data}, status=status.HTTP_200_OK)


@csrf_exempt
def check_valid_data(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        req = requests.post('http://127.0.0.1:9000/check_user', data=data)
        response = json.loads(req.text)

        if 'login' in response:
            req_to_token = requests.post('http://127.0.0.1:8000/api/token-auth/', data=data)
            response_from_auth = json.loads(req_to_token.text)

            return JsonResponse({'data': response_from_auth}, status=status.HTTP_200_OK)

        return JsonResponse({'data': response}, status=status.HTTP_200_OK)

    return JsonResponse({'status': '200'}, status=status.HTTP_200_OK)
