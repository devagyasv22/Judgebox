from datetime import timedelta

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView

from compiler.models import CodeSubmission
from contests.models import Contest, ContestRegistration, ContestSubmission

from .forms import ProfileForm
from .models import UserProfile
from .utils import get_cf_data


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in form.fields.values():
            field.widget.attrs["class"] = "form-control"
        return form


@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = ProfileForm(instance=profile)

    return render(request, "edit_profile.html", {"form": form})


@login_required
def dashboard_view(request):
    user = request.user
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)

    solved_today = (
        CodeSubmission.objects.filter(user=user, passed=True, submitted_at__date=today, problem__isnull=False)
        .values("problem")
        .distinct()
        .count()
    )

    contests_week = ContestRegistration.objects.filter(user=user, registered_at__date__gte=week_ago).count()

    subs = CodeSubmission.objects.filter(user=user, problem__isnull=False).order_by("-submitted_at")[:15]
    solved_recent = CodeSubmission.objects.filter(user=user, passed=True).order_by("-submitted_at")[:8]

    heatmap = {}
    for row in (
        CodeSubmission.objects.filter(user=user, submitted_at__gte=today - timedelta(days=365))
        .annotate(d=TruncDate("submitted_at"))
        .values("d")
        .annotate(c=Count("id"))
    ):
        if row["d"]:
            heatmap[row["d"].isoformat()] = row["c"]

    heatmap_cells = []
    for i in range(40):
        d = today - timedelta(days=39 - i)
        heatmap_cells.append(min(4, heatmap.get(d.isoformat(), 0)))

    recommended = []
    try:
        from problems.models import Problem
        from problems.stats import annotate_problems_for_user

        pool = Problem.objects.exclude(
            id__in=CodeSubmission.objects.filter(user=user, passed=True).values_list("problem_id", flat=True)
        )[:12]
        recommended = annotate_problems_for_user(pool, user)[:6]
    except Exception:
        pass

    now = timezone.now()
    upcoming = Contest.objects.filter(start_time__gt=now).order_by("start_time")[:5]

    return render(
        request,
        "dashboard.html",
        {
            "solved_today": solved_today,
            "contests_week": contests_week,
            "streak": 0,
            "best_rank": "—",
            "recent_submissions": subs,
            "recent_solved": solved_recent,
            "heatmap": heatmap,
            "heatmap_cells": heatmap_cells,
            "recommended": recommended,
            "upcoming_contests": upcoming,
        },
    )


@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    cf_data = get_cf_data(profile.codeforces_handle) if profile.codeforces_handle else None
    is_full_url = bool(profile.codeforces_handle and profile.codeforces_handle.startswith("http"))

    subs = CodeSubmission.objects.filter(user=request.user).order_by("-submitted_at")[:50]
    solved_distinct = (
        CodeSubmission.objects.filter(user=request.user, passed=True, problem__isnull=False)
        .values("problem")
        .distinct()
        .count()
    )
    contest_rows = (
        ContestSubmission.objects.filter(user=request.user)
        .values("contest_id", "contest__title")
        .annotate(n=Count("id"))
        .order_by("-n")[:20]
    )

    return render(
        request,
        "profile.html",
        {
            "profile": profile,
            "cf_data": cf_data,
            "is_full_url": is_full_url,
            "submissions": subs,
            "solved_distinct": solved_distinct,
            "contest_participation": contest_rows,
        },
    )


@login_required
def problem_set_view(request):
    return redirect("problem_list")


@login_required
def contest_view(request):
    return redirect("contest_list")


def community_view(request):
    # Redirect the old placeholder route to the new community feature.
    return redirect("community_list")
