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
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

from rest_framework.urlpatterns import format_suffix_patterns
from time_tracking.event.views import EventViewSet
from time_tracking.vacation.views import VacationViewSet
from time_tracking.work_statistic.views import (
    EmployeesArrivalAndLeavingTimesStatisticsDetail,
    WorkTimeStatisticsDetail,
    WorkTimeUsersAvailableStatistics,
    WorkingHoursToLeavingHoursStatisticsDetail,
)
from time_tracking.work_time.views import WorkTimeViewSet


# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')
router.register(r'vacation', VacationViewSet, basename='vacation')

router.register(r'work-time', WorkTimeViewSet, basename='worktime')

router.register(r'work-time-statistics',
                WorkTimeUsersAvailableStatistics,
                basename='worktime-available-statistics')

router.register(r'work-time-statistic/arrive-and-leave-times',
                EmployeesArrivalAndLeavingTimesStatisticsDetail,
                basename='work-arrival-and-leaving-time-statistic')

router.register(r'team-statistics/work-to-leave-time-average',
                WorkingHoursToLeavingHoursStatisticsDetail,
                basename='work-hours-to-leave-hours-statistic')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
]

urlpatterns += format_suffix_patterns([
    path(r'work-time-statistic/<slug:period>/<int:user_id>/',
         WorkTimeStatisticsDetail.as_view(),
         name='work-time-periods-statistic'),
])

urlpatterns += [
    path('api-token-auth/', views.obtain_auth_token, name='api-token-auth'),
    path('api-auth/', include('rest_framework.urls')),
]
