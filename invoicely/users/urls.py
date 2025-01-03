# users/urls.py
# it will map the views to a url
from django.urls import path
from .views import SignupView, LoginView, UserDetailView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', UserDetailView.as_view(), name='user-detail'),
]