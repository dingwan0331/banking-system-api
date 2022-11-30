from django.urls import path, include

from .views import DepositView

urlpatterns = [
    path('/deposit', DepositView.as_view())
]
