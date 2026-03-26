from django.urls import path

from . import views

urlpatterns = [
    path("", views.contest_list, name="contest_list"),
    path("<int:contest_id>/", views.contest_detail, name="contest_detail"),
    path("<int:contest_id>/register/", views.contest_register, name="contest_register"),
    path("<int:contest_id>/dashboard/", views.contest_dashboard, name="contest_dashboard"),
    path("<int:contest_id>/problem/<int:problem_id>/", views.contest_problem, name="contest_problem"),
    path("<int:contest_id>/problem/<int:problem_id>/submit/", views.contest_submit, name="contest_submit"),
    path("<int:contest_id>/standings/", views.contest_leaderboard, name="contest_leaderboard"),
    path("<int:contest_id>/submissions/", views.contest_submissions_review, name="contest_submissions"),
    path("<int:contest_id>/summary/", views.contest_ended, name="contest_ended"),
]
