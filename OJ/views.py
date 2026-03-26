from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.utils import timezone

from compiler.models import CodeSubmission
from contests.models import Contest
from problems.models import Problem


def home(request):
    total_problems = Problem.objects.count()
    solved_count = 0
    accuracy = None
    rank_display = "—"

    if request.user.is_authenticated:
        subs = CodeSubmission.objects.filter(user=request.user, problem__isnull=False)
        total_sub = subs.count()
        ac = subs.filter(passed=True).count()
        solved_count = CodeSubmission.objects.filter(user=request.user, passed=True).values("problem").distinct().count()
        if total_sub:
            accuracy = round(100.0 * ac / total_sub, 1)

    featured = Problem.objects.order_by("-created_at")[:8]
    now = timezone.now()
    upcoming = Contest.objects.filter(start_time__gt=now).order_by("start_time")[:5]

    announcements = [
        {"title": "Welcome to the new UI", "body": "Problems, contests, and the editor have been refreshed.", "date": now.date()},
    ]

    return render(
        request,
        "home.html",
        {
            "total_problems": total_problems,
            "solved_count": solved_count,
            "accuracy": accuracy,
            "rank_display": rank_display,
            "featured_problems": featured,
            "upcoming_contests": upcoming,
            "announcements": announcements,
        },
    )


def search(request):
    q = (request.GET.get("q") or "").strip()
    problems = []
    contests = []
    users = []
    if len(q) >= 1:
        problems = Problem.objects.filter(title__icontains=q)[:10]
        contests = Contest.objects.filter(title__icontains=q)[:10]
        User = get_user_model()
        users = User.objects.filter(username__icontains=q)[:10]
    return render(
        request,
        "search.html",
        {"q": q, "problems": problems, "contests": contests, "users": users},
    )
