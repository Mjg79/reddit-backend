from django.urls import path
from rest_framework import routers
from .views import *

app_name = 'accounts'

router = routers.DefaultRouter()
router.include_root_view = False

router.register('register', UserView, basename='user_register')

urlpatterns = router.urls + [
    path('login/', LoginView.as_view(), name='login'),
    path('update/', UserUpdateView.as_view(), name='update'),
    path('followers/', FollowersView.as_view(), name='followers'),
]
