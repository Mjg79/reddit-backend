from django.urls import path
from rest_framework import routers
from .views import *

app_name = 'socials'

router = routers.DefaultRouter()
router.include_root_view = False

router.register('post', PostDetailView, basename='post')
router.register('channel', ChanneDetaillView, basename='channel')
router.register('comment', CommentView, basename='comment')


urlpatterns = router.urls + [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('notifs/', NotifView.as_view(), name='notifications'),
    path('news/', NewsView.as_view(), name='news'),
    path('activities/',  ActivitiesView.as_view(), name='activities'),
    path('hots/', HotsView.as_view(), name='hots'),
    path('search/', SearchView.as_view(), name='search'),
    path('channel_change/<int:id>/', ChannelView.as_view(), name='channel_info'),
    path('post_change/<int:id>/', PostModelView.as_view(), name='post_info')
]
