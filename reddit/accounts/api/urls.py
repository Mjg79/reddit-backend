from django.urls import path
from rest_framework import routers
from .views import UserView, FollowView, ProfileView, LoginView, UserUpdateView, ForgetpPasswordView
from rest_framework_simplejwt import views as jwt_views

app_name = 'accounts'

router = routers.DefaultRouter()
router.include_root_view = False

router.register('register', UserView, basename='user_register')
router.register('follow', FollowView, basename='follow')
router.register('profile', ProfileView, basename='profile')

urlpatterns = router.urls + [
    path('login/', LoginView.as_view(), name='login'),
    path('update/', UserUpdateView.as_view(), name='update'),
    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('forgot-password/', ForgetpPasswordView.as_view(), name='forgot-password')
]
