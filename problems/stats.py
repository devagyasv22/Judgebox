"""Aggregates for problem list, profile, and API responses."""

from django.db.models import Case, Count, When

from compiler.models import CodeSubmission


def acceptance_rate(problem):
    qs = CodeSubmission.objects.filter(problem=problem)
    total = qs.count()
    if not total:
        return None
    ac = qs.filter(passed=True).count()
    return round(100.0 * ac / total, 1)


def submission_count(problem):
    return CodeSubmission.objects.filter(problem=problem).count()


def user_problem_status(user, problem):
    """Returns 'solved' | 'attempted' | 'none'."""
    if not user.is_authenticated:
        return "none"
    qs = CodeSubmission.objects.filter(problem=problem, user=user)
    if not qs.exists():
        return "none"
    if qs.filter(passed=True).exists():
        return "solved"
    return "attempted"


def annotate_problems_for_user(queryset, user):
    """Adds acceptance_rate, submission_count, user_status per problem (Python-side for SQLite)."""
    problems = list(queryset)
    pids = [p.id for p in problems]
    if not pids:
        return problems

    subs = CodeSubmission.objects.filter(problem_id__in=pids)
    agg = (
        subs.values("problem_id")
        .annotate(
            total=Count("id"),
            ac=Count(Case(When(passed=True, then=1))),
        )
    )
    by_pid = {row["problem_id"]: row for row in agg}

    user_solved = set()
    user_attempted = set()
    if user.is_authenticated:
        uqs = CodeSubmission.objects.filter(problem_id__in=pids, user=user)
        for pid in uqs.filter(passed=True).values_list("problem_id", flat=True).distinct():
            user_solved.add(pid)
        for pid in uqs.values_list("problem_id", flat=True).distinct():
            if pid not in user_solved:
                user_attempted.add(pid)

    for p in problems:
        row = by_pid.get(p.id)
        if row and row["total"]:
            p._acceptance_rate = round(100.0 * row["ac"] / row["total"], 1)
        else:
            p._acceptance_rate = None
        p._submission_count = row["total"] if row else 0
        if p.id in user_solved:
            p._user_status = "solved"
        elif p.id in user_attempted:
            p._user_status = "attempted"
        else:
            p._user_status = "none"

    return problems
