# problems/views.py
import json
import subprocess
import traceback
import uuid
from pathlib import Path

import google.generativeai as genai
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt

from compiler.forms import CodeSubmissionForm
from compiler.models import CodeSubmission

from .models import Problem
from .stats import annotate_problems_for_user
from .test_runner import run_test_cases
from .testcases_model import TestCase

if getattr(settings, "GEMINI_API_KEY", None):
    genai.configure(api_key=settings.GEMINI_API_KEY)


@login_required
@csrf_exempt
def ai_review_code(request, problem_id):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    code = request.POST.get("code")
    result = request.POST.get("result", "")

    if not code:
        return JsonResponse({"error": "No code provided"}, status=400)

    try:
        if not getattr(settings, "GEMINI_API_KEY", None):
            return JsonResponse({"error": "AI review is not configured."}, status=503)
        genai.configure(api_key=settings.GEMINI_API_KEY)
        prompt = (
            f"Review this solution:\n{code}\n\n"
            f"Test Case Result: {result}\n"
            f"Provide helpful improvement suggestions."
        )
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)

        feedback_text = ""
        if hasattr(response, "text"):
            feedback_text = response.text.strip()
        elif hasattr(response, "candidates"):
            feedback_text = "".join(
                part.text for part in response.candidates[0].content.parts
            )

        if not feedback_text:
            return JsonResponse({"error": "Empty AI response"}, status=502)

        return JsonResponse({"feedback": feedback_text})

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": repr(e)}, status=500)


def _serialize_problem(request, p):
    tags = p.tag_list() if hasattr(p, "tag_list") else []
    return {
        "id": p.id,
        "title": p.title,
        "slug": p.slug,
        "difficulty": p.get_difficulty_display(),
        "difficulty_key": p.difficulty,
        "tags": tags,
        "acceptance_rate": getattr(p, "_acceptance_rate", None),
        "submission_count": getattr(p, "_submission_count", 0),
        "discussion_count": p.discussion_count,
        "user_status": getattr(p, "_user_status", "none"),
        "url": f"/problems/{p.id}/",
    }


def problem_list(request):
    print("DEBUG: Total problems in DB:", Problem.objects.count())
    qs = Problem.objects.all()
    problems = annotate_problems_for_user(qs, request.user)
    print("DEBUG: Queryset count passed to template:", len(problems))
    payload = [_serialize_problem(request, p) for p in problems]
    return render(
        request,
        "problems/problem_list.html",
        {
            "problems": problems,
            "problems_payload": payload,
        },
    )


def problem_list_api(request):
    qs = Problem.objects.all()
    q = (request.GET.get("q") or "").strip().lower()
    difficulty = request.GET.get("difficulty")
    tag = (request.GET.get("tag") or "").strip().lower()
    status_filter = request.GET.get("status")
    sort = request.GET.get("sort", "id")

    if q:
        qs = qs.filter(title__icontains=q)
    if difficulty and difficulty in ("easy", "medium", "hard"):
        qs = qs.filter(difficulty=difficulty)
    if tag:
        qs = qs.filter(tags__icontains=tag)

    problems = annotate_problems_for_user(qs, request.user)

    if status_filter == "solved":
        problems = [p for p in problems if getattr(p, "_user_status", "none") == "solved"]
    elif status_filter == "attempted":
        problems = [p for p in problems if getattr(p, "_user_status", "none") == "attempted"]
    elif status_filter == "unsolved":
        problems = [p for p in problems if getattr(p, "_user_status", "none") == "none"]

    if sort == "difficulty":
        order = {"easy": 0, "medium": 1, "hard": 2}
        problems.sort(key=lambda p: order.get(p.difficulty, 1))
    elif sort == "acceptance":
        problems.sort(
            key=lambda p: (getattr(p, "_acceptance_rate", None) is None, -(getattr(p, "_acceptance_rate") or 0))
        )
    elif sort == "recent":
        problems.sort(key=lambda p: p.created_at, reverse=True)
    elif sort == "popular":
        problems.sort(key=lambda p: getattr(p, "_submission_count", 0), reverse=True)

    return JsonResponse({"results": [_serialize_problem(request, p) for p in problems]})


def problem_detail(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    form = CodeSubmissionForm()
    recent = []
    if request.user.is_authenticated:
        recent = CodeSubmission.objects.filter(problem=problem, user=request.user).order_by("-submitted_at")[:12]
    return render(
        request,
        "problems/problem_detail.html",
        {
            "problem": problem,
            "form": form,
            "testcases": TestCase.objects.filter(problem=problem, is_hidden=False).order_by("order", "id"),
            "submission": None,
            "recent_submissions": recent,
        },
    )


@login_required
def submit_code(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    form = CodeSubmissionForm(request.POST or None)
    testcases = TestCase.objects.filter(problem=problem, is_hidden=False).order_by("order", "id")

    context = {
        "problem": problem,
        "form": form,
        "testcases": testcases,
        "custom_output": None,
        "results": None,
        "submission": None,
        "recent_submissions": [],
    }

    if request.user.is_authenticated:
        context["recent_submissions"] = CodeSubmission.objects.filter(
            problem=problem, user=request.user
        ).order_by("-submitted_at")[:12]

    if request.method == "POST" and form.is_valid():
        submission = form.save(commit=False)
        submission.problem = problem
        if request.user.is_authenticated:
            submission.user = request.user
        action = request.POST.get("action")

        if action == "custom":
            custom_input = form.cleaned_data.get("input_data", "") or ""
            context["custom_output"] = run_code(submission.language, submission.code, custom_input)

        elif action == "run_all":
            results = run_test_cases(submission.language, submission.code, problem_id)
            if not results:
                verdict = "CE"
                all_passed = False
            elif any(tc.get("error") for tc in results):
                verdict = "CE"
                all_passed = False
            else:
                all_passed = all(tc.get("passed", False) for tc in results)
                verdict = "AC" if all_passed else "WA"

            submission.output_data = str(results)
            submission.passed = all_passed
            submission.verdict = verdict
            submission.save()

            context["results"] = results
            context["submission"] = submission
            if request.user.is_authenticated:
                context["recent_submissions"] = CodeSubmission.objects.filter(
                    problem=problem, user=request.user
                ).order_by("-submitted_at")[:12]

    return render(request, "problems/problem_detail.html", context)


def run_code(language, code, input_data):
    workdir_str = getattr(settings, 'SUBMISSION_WORKDIR', '/tmp/judgebox')
    uid = str(uuid.uuid4())
    base_path = Path(workdir_str) / uid
    base_path.mkdir(parents=True, exist_ok=True)

    extensions = {"cpp": "cpp", "py": "py", "java": "java"}
    ext = extensions.get(language, "txt")

    code_path = base_path / f"temp_{uid}.{ext}"
    input_path = base_path / f"input_{uid}.txt"
    output_path = base_path / f"output_{uid}.txt"

    code_path.write_text(code)
    input_path.write_text(input_data or "")

    try:
        if language == "cpp":
            exe = base_path / f"prog_{uid}"
            compile_proc = subprocess.run(
                ["g++", str(code_path), "-o", str(exe)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if compile_proc.returncode != 0:
                return f"Compilation Error:\n{compile_proc.stderr}"
            try:
                subprocess.run(
                    [str(exe)],
                    stdin=open(input_path, "r"),
                    stdout=open(output_path, "w"),
                    timeout=2,
                )
            except subprocess.TimeoutExpired:
                return "Time Limit Exceeded"

        elif language == "py":
            try:
                subprocess.run(
                    ["python3", str(code_path)],
                    stdin=open(input_path, "r"),
                    stdout=open(output_path, "w"),
                    timeout=2,
                )
            except subprocess.TimeoutExpired:
                return "Time Limit Exceeded"

        elif language == "java":
            java_file = base_path / f"Main_{uid}.java"
            java_file.write_text(code)
            compile_proc = subprocess.run(
                ["javac", str(java_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if compile_proc.returncode != 0:
                return f"Compilation Error:\n{compile_proc.stderr}"
            try:
                subprocess.run(
                    ["java", "-cp", str(base_path), f"Main_{uid}"],
                    stdin=open(input_path, "r"),
                    stdout=open(output_path, "w"),
                    timeout=2,
                )
            except subprocess.TimeoutExpired:
                return "Time Limit Exceeded"

        else:
            return "Unsupported language"

        return output_path.read_text()

    finally:
        pass
