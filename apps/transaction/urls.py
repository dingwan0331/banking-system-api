from django.urls import path

from apps.transaction.views import TransactionView

urlpatterns = [
    path('/deposit', TransactionView.as_view())
]
