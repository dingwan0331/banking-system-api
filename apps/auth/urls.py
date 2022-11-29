from django.urls import path

from .views import SigninView

urlpatterns = [
    path('/users/signin', SigninView.as_view())
]
