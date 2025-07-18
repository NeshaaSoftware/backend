from dal_select2.views import Select2QuerySetView
from django.contrib.auth.mixins import UserPassesTestMixin

from .models import FinancialAccount


class FinancialAccountAutocompleteView(UserPassesTestMixin, Select2QuerySetView):
    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        qs = FinancialAccount.objects.all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs
