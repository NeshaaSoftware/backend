from django.urls import path

from courses.views import CourseAutocompleteView

urlpatterns = [
    path("course-autocomplete/", CourseAutocompleteView.as_view(), name="course-autocomplete"),
]
