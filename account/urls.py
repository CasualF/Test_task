from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('', views.UserView)

urlpatterns = [
    path('users/', include(router.urls)),
    path('register/', views.UserRegistrationView.as_view()),
    path('login/', TokenObtainPairView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('refresh/', TokenRefreshView.as_view()),
    path('activate/', views.ActivationView.as_view()),
    path('profile/', views.ProfileView.as_view()),
]
