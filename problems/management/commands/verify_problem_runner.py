from pathlib import Path

from django.core.management.base import BaseCommand

from problems.models import Problem
from problems.test_runner import run_test_cases


class Command(BaseCommand):
    help = "Verify runner expected-output mapping for a given problem."

    def add_arguments(self, parser):
        parser.add_argument("--problem-id", type=int, default=1)
        parser.add_argument("--language", type=str, default="py")
        parser.add_argument(
            "--code",
            type=str,
            default="",
            help="Optional code override. If empty, a known-correct solution is used for supported problems.",
        )

    def handle(self, *args, **options):
        problem_id = options["problem_id"]
        language = options["language"]
        override_code = options["code"].strip()

        problem = Problem.objects.get(pk=problem_id)
        title_l = (problem.title or "").lower()

        if not override_code:
            if "sum of two integers" in title_l:
                # Reads two integers from stdin (space or newline separated).
                code = "a,b = map(int, input().split())\nprint(a+b)\n"
            elif "even or odd" in title_l:
                code = "n = int(input().strip())\nprint('Even' if n % 2 == 0 else 'Odd')\n"
            else:
                raise SystemExit(
                    f"No built-in reference solution for problem title: {problem.title!r}. Pass --code to verify."
                )
        else:
            code = override_code

        results = run_test_cases(language, code, problem_id)
        if not results:
            raise SystemExit(f"Runner returned no results for problem_id={problem_id}.")

        expected_count = len(results)
        self.stdout.write(
            f"Problem #{problem_id}: {problem.title!r} -> {expected_count} test(s) judged.\n"
        )

        passed_all = True
        for r in results:
            idx = r.get("testcase")
            ok = bool(r.get("passed"))
            if not ok:
                passed_all = False
            self.stdout.write(
                f"Testcase {idx}: "
                f"expected={r.get('expected')!r} actual={r.get('actual')!r} "
                f"-> {'PASS' if ok else 'FAIL'}"
            )
            if r.get("error"):
                self.stdout.write(f"  error: {r.get('error')}")

        verdict = "AC" if passed_all else "WA"
        self.stdout.write(self.style.SUCCESS(f"\nFinal verdict for reference code: {verdict}"))

