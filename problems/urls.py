from django.urls import path

from . import views

urlpatterns = [
    path("", views.problem_list, name="problem_list"),
    path("api/", views.problem_list_api, name="problem_list_api"),
    path("<int:problem_id>/", views.problem_detail, name="problem_detail"),
    path("<int:problem_id>/submit/", views.submit_code, name="submit_code"),
    path("<int:problem_id>/ai-review/", views.ai_review_code, name="ai_review_code"),
]
