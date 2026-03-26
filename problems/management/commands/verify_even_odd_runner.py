from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from problems.test_runner import run_test_cases


class Command(BaseCommand):
    help = "Verify runner uses output*.txt as expected outputs for Even/Odd."

    def add_arguments(self, parser):
        parser.add_argument("--problem-id", type=int, default=2)

    def handle(self, *args, **options):
        problem_id = options["problem_id"]

        # Known-correct solution for the current Problem 2 statement.
        code = (
            "n = int(input().strip())\n"
            "print('Even' if n % 2 == 0 else 'Odd')\n"
        )

        results = run_test_cases("py", code, problem_id)

        # problems/management/commands/<cmd>.py -> problems/
        problems_dir = Path(__file__).resolve().parents[2]
        base_dir = problems_dir / "testcases" / f"problem_{problem_id}"
        expected_from_files = []
        i = 1
        while True:
            inp = base_dir / f"input{i}.txt"
            outp = base_dir / f"output{i}.txt"
            if not inp.exists() or not outp.exists():
                break
            expected_from_files.append(outp.read_text(encoding="utf-8").strip())
            i += 1

        self.stdout.write(f"Found {len(expected_from_files)} testcases in {base_dir}")

        if len(results) != len(expected_from_files):
            raise SystemExit(
                f"Mismatch: runner returned {len(results)} results but found {len(expected_from_files)} output files."
            )

        for idx, (r, exp) in enumerate(zip(results, expected_from_files), start=1):
            if r.get("expected") != exp:
                raise SystemExit(
                    f"Expected mismatch at testcase #{idx}: runner.expected={r.get('expected')!r}, file={exp!r}"
                )
            if not r.get("passed"):
                raise SystemExit(
                    f"Judgement failed at testcase #{idx}: input_file={idx}, expected={exp!r}, actual={r.get('actual')!r}"
                )

        self.stdout.write(self.style.SUCCESS("OK: runner expected mapping + verdict all passed."))

