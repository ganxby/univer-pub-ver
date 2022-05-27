from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()

router.register(r'lessons', views.LessonViewSet)

urlpatterns = [
    path('', include(router.urls)),

    path('test-v1/', views.test),
    path('add-full-data/', views.add_full_data),

    path('result-table/', views.ResultTableView.as_view())
]
