from django.urls import path
from rest_framework import routers
from accounts.api.views import LoginView, UserView, UserUpdateView

app_name = 'accounts'

router = routers.DefaultRouter()
router.include_root_view = False

router.register('register', UserView, basename='user_register')

urlpatterns = router.urls + [
    path('login/', LoginView.as_view(), name='login'),
    path('update/', UserUpdateView.as_view(), name='update'),

]