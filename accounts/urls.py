from django.urls import path
from django.urls import path, include
from django.views.generic.base import RedirectView
from .views import (
    SignUpView,
    dashboard_view,
    profile_view,
    problem_set_view,
    contest_view,
    community_view,
    edit_profile,

)

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("profile/", profile_view, name="profile"),
    path("problem-set/", problem_set_view, name="problem_set"),
    path("contest/", RedirectView.as_view(pattern_name='contest_list', permanent=False)),
    path("community/", community_view, name="community"),
    path('compiler/',include('compiler.urls')),
    path('profile/edit/', edit_profile, name='edit_profile'),

]