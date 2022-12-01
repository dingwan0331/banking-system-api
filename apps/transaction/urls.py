from django.urls import path

from apps.transaction.views import TransactionView

urlpatterns = [
    path('/<int:account_id>/transactions', TransactionView.as_view())
]
