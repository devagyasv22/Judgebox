from collections import defaultdict

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from problems.test_runner import run_test_cases

from .models import Contest, ContestRegistration, ContestSubmission


def _contest_status(contest):
    now = timezone.now()
    if now < contest.start_time:
        return "upcoming"
    if contest.end_time < now:
        return "ended"
    return "running"


def _leaderboard_rows(contest):
    """Codeforces-style: solved count, penalty = sum(first_AC_minutes + 10*failed_before_AC)."""
    start = contest.start_time
    subs = (
        ContestSubmission.objects.filter(contest=contest)
        .select_related("user")
        .order_by("submitted_at")
    )
    first_ac = {}
    wrong_before = defaultdict(lambda: defaultdict(int))

    for s in subs:
        uid, pid = s.user_id, s.problem_id
        key = (uid, pid)
        if s.verdict == "AC":
            if key not in first_ac:
                first_ac[key] = s.submitted_at
        else:
            if key not in first_ac:
                wrong_before[uid][pid] += 1

    User = get_user_model()
    users = {uid for (uid, _) in first_ac}
    rows = []
    for uid in users:
        u = User.objects.get(pk=uid)
        solved_pids = [pid for (u2, pid) in first_ac if u2 == uid]
        penalty = 0.0
        for pid in solved_pids:
            key = (uid, pid)
            ac_t = first_ac[key]
            penalty += (ac_t - start).total_seconds() / 60.0
            penalty += wrong_before[uid][pid] * 10.0
        rows.append(
            {
                "user": u,
                "solved": len(solved_pids),
                "penalty": round(penalty, 2),
                "total_problems": contest.problems.count(),
            }
        )

    rows.sort(key=lambda r: (-r["solved"], r["penalty"]))
    for i, row in enumerate(rows, start=1):
        row["rank"] = i
    return rows


def contest_list(request):
    now = timezone.now()
    tab = request.GET.get("tab", "all")
    sort = request.GET.get("sort", "start")

    upcoming = Contest.objects.filter(start_time__gt=now).order_by("start_time")
    running = Contest.objects.filter(start_time__lte=now, end_time__gte=now).order_by("end_time")
    ended = Contest.objects.filter(end_time__lt=now).order_by("-end_time")

    if tab == "upcoming":
        contests = list(upcoming)
    elif tab == "running":
        contests = list(running)
    elif tab == "ended":
        contests = list(ended)
    else:
        contests = list(Contest.objects.order_by("-start_time")[:60])

    if sort == "title":
        contests.sort(key=lambda c: c.title.lower())
    elif sort == "duration":
        contests.sort(key=lambda c: c.duration_minutes(), reverse=True)

    featured = list(upcoming[:5])

    reg_ids = set()
    if request.user.is_authenticated:
        reg_ids = set(
            ContestRegistration.objects.filter(user=request.user, contest_id__in=[c.id for c in contests]).values_list(
                "contest_id", flat=True
            )
        )

    return render(
        request,
        "contest/contest_list.html",
        {
            "contests": contests,
            "featured": featured,
            "tab": tab,
            "sort": sort,
            "registered_ids": reg_ids,
            "now": now,
        },
    )


def contest_detail(request, contest_id):
    contest = get_object_or_404(Contest, pk=contest_id)
    status = _contest_status(contest)
    registered = False
    if request.user.is_authenticated:
        registered = ContestRegistration.objects.filter(user=request.user, contest=contest).exists()
    problem_count = contest.problems.count()
    participant_count = ContestRegistration.objects.filter(contest=contest).count()

    return render(
        request,
        "contest/contest_detail.html",
        {
            "contest": contest,
            "status": status,
            "registered": registered,
            "problem_count": problem_count,
            "participant_count": participant_count,
        },
    )


@login_required
@require_POST
def contest_register(request, contest_id):
    contest = get_object_or_404(Contest, pk=contest_id)
    if _contest_status(contest) == "ended":
        messages.error(request, "This contest has ended.")
        return redirect("contest_detail", contest_id=contest.id)
    ContestRegistration.objects.get_or_create(user=request.user, contest=contest)
    messages.success(request, "Registered successfully.")
    return redirect("contest_detail", contest_id=contest.id)


@login_required
def contest_dashboard(request, contest_id):
    contest = get_object_or_404(Contest, pk=contest_id)
    status = _contest_status(contest)
    if status == "upcoming":
        messages.info(request, "Contest has not started yet.")
        return redirect("contest_detail", contest_id=contest.id)
    reg = ContestRegistration.objects.filter(user=request.user, contest=contest).exists()
    if not reg and status == "running":
        messages.warning(request, "Register to participate.")
        return redirect("contest_detail", contest_id=contest.id)

    problems = list(contest.problems.all().order_by("id"))
    for i, p in enumerate(problems, start=1):
        p._letter = chr(ord("A") + i - 1) if i <= 26 else str(i)

    return render(
        request,
        "contest/contest_dashboard.html",
        {
            "contest": contest,
            "status": status,
            "problems": problems,
        },
    )


@login_required
def contest_problem(request, contest_id, problem_id):
    contest = get_object_or_404(Contest, pk=contest_id)
    problem = get_object_or_404(contest.problems.all(), pk=problem_id)
    status = _contest_status(contest)
    if status == "ended":
        messages.info(request, "Contest ended — view problems from the problem set.")
    if status == "running":
        if not ContestRegistration.objects.filter(user=request.user, contest=contest).exists():
            messages.error(request, "You must register for this contest.")
            return redirect("contest_detail", contest_id=contest.id)

    problems = list(contest.problems.all().order_by("id"))
    for i, p in enumerate(problems, start=1):
        p._letter = chr(ord("A") + i - 1) if i <= 26 else str(i)

    recent = (
        ContestSubmission.objects.filter(contest=contest, user=request.user, problem=problem)
        .order_by("-submitted_at")[:8]
    )

    return render(
        request,
        "contest/contest_problem.html",
        {
            "contest": contest,
            "problem": problem,
            "problems": problems,
            "recent_submissions": recent,
            "status": status,
        },
    )


@login_required
@require_POST
def contest_submit(request, contest_id, problem_id):
    contest = get_object_or_404(Contest, pk=contest_id)
    problem = get_object_or_404(contest.problems.all(), pk=problem_id)
    if _contest_status(contest) != "running":
        messages.error(request, "Submissions are only allowed during the contest window.")
        return redirect("contest_problem", contest_id=contest.id, problem_id=problem.id)
    if not ContestRegistration.objects.filter(user=request.user, contest=contest).exists():
        messages.error(request, "Register first.")
        return redirect("contest_detail", contest_id=contest.id)

    language = request.POST.get("language", "py")
    code = request.POST.get("code", "")
    if language not in ("cpp", "py", "java"):
        language = "py"

    results = run_test_cases(language, code, problem.id)
    if not results:
        verdict = "CE"
    elif any(tc.get("error") for tc in results):
        verdict = "CE"
    else:
        all_passed = all(tc.get("passed", False) for tc in results)
        verdict = "AC" if all_passed else "WA"
    runtime_ms = None

    ContestSubmission.objects.create(
        user=request.user,
        contest=contest,
        problem=problem,
        code=code,
        language=language,
        verdict=verdict,
        runtime_ms=runtime_ms,
    )
    messages.success(request, f"Verdict: {verdict}")
    return redirect("contest_problem", contest_id=contest.id, problem_id=problem.id)


def contest_leaderboard(request, contest_id):
    contest = get_object_or_404(Contest, pk=contest_id)
    status = _contest_status(contest)
    rows = _leaderboard_rows(contest)
    q = (request.GET.get("q") or "").strip().lower()
    if q:
        rows = [r for r in rows if q in r["user"].username.lower()]

    my_rank = None
    if request.user.is_authenticated:
        for r in rows:
            if r["user"].id == request.user.id:
                my_rank = r["rank"]
                break

    filter_mode = request.GET.get("filter", "all")
    if filter_mode == "me" and request.user.is_authenticated:
        idx = next((i for i, r in enumerate(rows) if r["user"].id == request.user.id), None)
        if idx is not None:
            lo = max(0, idx - 25)
            hi = min(len(rows), idx + 26)
            rows = rows[lo:hi]

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse(
            {
                "status": status,
                "rows": [
                    {
                        "rank": r["rank"],
                        "username": r["user"].username,
                        "solved": r["solved"],
                        "penalty": r["penalty"],
                        "total": r["total_problems"],
                    }
                    for r in rows
                ],
            }
        )

    return render(
        request,
        "contest/contest_leaderboard.html",
        {
            "contest": contest,
            "rows": rows,
            "status": status,
            "my_rank": my_rank,
            "filter_mode": filter_mode,
        },
    )


def contest_submissions_review(request, contest_id):
    contest = get_object_or_404(Contest, pk=contest_id)
    subs = (
        ContestSubmission.objects.filter(contest=contest)
        .select_related("user", "problem")
        .order_by("-submitted_at")
    )
    verdict = request.GET.get("verdict")
    lang = request.GET.get("language")
    prob = request.GET.get("problem")
    if verdict:
        subs = subs.filter(verdict=verdict)
    if lang:
        subs = subs.filter(language=lang)
    if prob:
        subs = subs.filter(problem_id=prob)

    return render(
        request,
        "contest/contest_submissions.html",
        {
            "contest": contest,
            "submissions": subs,
        },
    )


def contest_ended(request, contest_id):
    contest = get_object_or_404(Contest, pk=contest_id)
    rows = _leaderboard_rows(contest)[:20]
    return render(
        request,
        "contest/contest_ended.html",
        {"contest": contest, "top_rows": rows},
    )
