# users/urls.py
# it will map the views to a url
from django.urls import path
from .views import SignupView, LoginView, UserDetailView, LogoutView, VerifyPasswordView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', UserDetailView.as_view(), name='user-detail'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify-password/', VerifyPasswordView.as_view(), name='verify-password'),

]