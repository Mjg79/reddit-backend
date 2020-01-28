from django.urls import path
from rest_framework import routers
from reddit.accounts.api.views import LoginView, UserView

app_name = 'accounts'

router = routers.DefaultRouter()
router.include_root_view = False

urlpatterns = router.urls + [
    path('register/', UserView, name='register'),
    path('login/', LoginView.as_view(), name='login'),
]