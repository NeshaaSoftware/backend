from dal_select2.views import Select2QuerySetView
from django.contrib.auth.mixins import UserPassesTestMixin

from .models import Course


class CourseAutocompleteView(UserPassesTestMixin, Select2QuerySetView):
    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        qs = Course.objects.all()
        if self.q:
            qs = qs.filter(course_name__icontains=self.q)
        return qs
