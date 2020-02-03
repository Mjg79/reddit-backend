from django.urls import path
from rest_framework import routers
from .views import DashboardView, PostView, ChannelView

app_name = 'socials'

router = routers.DefaultRouter()
router.include_root_view = False

router.register('post', PostView, basename='post')
router.register('channel', ChannelView, basename='channel')

urlpatterns = router.urls + [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    # path('news/', 'ez', name='news'),
    # path('activities/', 'ez', name='activities'),
    # path('hots/', 'ez', name='hots')
]
