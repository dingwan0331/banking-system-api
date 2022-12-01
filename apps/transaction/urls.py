from django.urls import path

from apps.transaction.views import TransactionView

urlpatterns = [
    path('', TransactionView.as_view())
]
