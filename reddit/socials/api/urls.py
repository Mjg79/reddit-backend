from django.urls import path
from rest_framework import routers
from .views import DashboardView

app_name = 'socials'

router = routers.DefaultRouter()
router.include_root_view = False

urlpatterns = router.urls + [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    # path('posts/', 'ez', name='posts'),
    # path('news/', 'ez', name='news'),
    # path('activities/', 'ez', name='activities'),
    # path('hots/', 'ez', name='hots')
]
