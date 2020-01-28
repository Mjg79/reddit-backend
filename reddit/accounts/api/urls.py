from django.urls import path
from rest_framework import routers

app_name = 'accounts'

router = routers.DefaultRouter()
router.include_root_view = False

urlpatterns = router.urls + [
    path('login/', LoginView.as_view(), name='login'),
    path('verify/', VerifyView.as_view(), name='verify'),
]