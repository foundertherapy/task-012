"""time_tracking URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views

from rest_framework.urlpatterns import format_suffix_patterns
from time_tracking.event.views import EventViewSet
from time_tracking.work_statistic import views as statistic_views
from time_tracking.vacation.views import VacationViewSet
from time_tracking.work_time.views import (
    WorkTimeViewSet,
    WorkTimeCheckInViewSet,
    WorkTimeCheckOutViewSet
)


# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')
router.register(r'vacation', VacationViewSet, basename='vacation')

router.register(r'workTime/check-in',
                WorkTimeCheckInViewSet, basename='worktime-checkin')
router.register(r'workTime/check-out',
                WorkTimeCheckOutViewSet, basename='worktime-checkout')
router.register(r'workTime', WorkTimeViewSet, basename='worktime')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
]

urlpatterns += format_suffix_patterns([
    path('workTimeStatistic/week',
         statistic_views.week_statistics_detail,
         name='worktime-week-statistic'),
    path('workTimeStatistic/quarter',
         statistic_views.quarter_statistics_detail,
         name='worktime-quarter-statistic'),
    path('workTimeStatistic/year',
         statistic_views.year_statistics_detail,
         name='worktime-year-statistic'),
    path('workTimeStatistic/arrive-and-leave',
         statistic_views.employees_arrival_to_leaving_time_detail,
         name='work-arrival-and-leaving-time-statistic'),
    path('workTimeStatistic/work-to-leave-avarage',
         statistic_views.working_ours_to_leaving_hours_detail,
         name='work-hours-to-leav-hours-statistic'),
])

urlpatterns += [
    path('api-token-auth/', views.obtain_auth_token, name='api-token-auth'),
    path('api-auth/', include('rest_framework.urls')),
]
