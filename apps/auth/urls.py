from django.urls import path

from apps.auth.views import SigninView, UserView

urlpatterns = [
    path('/users/signin', SigninView.as_view()),
    path('/users', UserView.as_view())
]
