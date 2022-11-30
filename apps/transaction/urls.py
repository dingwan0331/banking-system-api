from django.urls import path

from apps.transaction.views import DepositView

urlpatterns = [
    path('/deposit', DepositView.as_view())
]
