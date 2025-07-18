from django.urls import path

from .views import FinancialAccountAutocompleteView

urlpatterns = [
    path("financialaccount-autocomplete/", FinancialAccountAutocompleteView.as_view(), name="financialaccount-autocomplete"),
]
