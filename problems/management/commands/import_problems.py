import json
import traceback
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from problems.models import Problem
from problems.testcases_model import TestCase


class Command(BaseCommand):
    help = "Import problems (and their testcases) from a JSON file. Safe to rerun."

    def add_arguments(self, parser):
        default_json = (
            Path(__file__).resolve().parents[3] / "OJ" / "data" / "problems_seed.json"
        )
        parser.add_argument("json_path", nargs="?", type=str, default=str(default_json))

    @staticmethod
    def _normalize_difficulty(value: str) -> str:
        v = (value or "").strip().lower()
        if v in {"easy", "medium", "hard"}:
            return v
        return "medium"

    @staticmethod
    def _parse_tags(tags) -> str:
        if tags is None:
            return ""
        return str(tags)

    def _unique_slug(self, title: str, exclude_problem_id=None) -> str:
        base = slugify(title)[:50] or "problem"
        slug = base
        i = 0
        while True:
            qs = Problem.objects.filter(slug=slug)
            if exclude_problem_id is not None:
                qs = qs.exclude(pk=exclude_problem_id)
            if not qs.exists():
                return slug
            i += 1
            slug = f"{base}-{i}"[:50]

    def handle(self, *args, **options):
        path = Path(options["json_path"])
        self.stdout.write(f"Using JSON file path: {path}")
        self.stdout.write(f"File exists: {path.exists()}")

        if not path.exists():
            self.stderr.write(self.style.ERROR(f"File not found: {path}"))
            return

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise SystemExit(f"Invalid JSON file: {e}")

        # Support both a raw list [...] or an object wrapper {"problems": [...]}
        if isinstance(data, dict) and "problems" in data:
            items = data["problems"]
        elif isinstance(data, list):
            items = data
        else:
            raise SystemExit("Seed JSON must be a list of problem objects or contain a 'problems' key.")

        self.stdout.write(self.style.SUCCESS(f"Found {len(items)} items to process in JSON."))

        before_count = Problem.objects.count()
        self.stdout.write(f"Problem count before import: {before_count}")

        problems_created = 0
        problems_updated = 0
        problems_skipped = 0
        testcases_created = 0
        testcases_deleted = 0

        for item in items:
            # Prefer matching existing problems by slug if provided, else title
            title = (item.get("title") or "").strip()
            slug_field = (item.get("slug") or "").strip()

            if not title:
                self.stderr.write(self.style.WARNING("Skipping an item with missing or empty title."))
                problems_skipped += 1
                continue

            try:
                difficulty = self._normalize_difficulty(item.get("difficulty"))
                tags = self._parse_tags(item.get("tags"))

                testcases = item.get("testcases") or []
                if not isinstance(testcases, list):
                    testcases = []

                # Upsert by case-insensitive title or slug.
                with transaction.atomic():
                    obj = None
                    if slug_field:
                        obj = Problem.objects.filter(slug=slug_field).first()
                    if not obj:
                        obj = Problem.objects.filter(title__iexact=title).first()

                    is_new = obj is None

                    if is_new:
                        problems_created += 1
                        obj = Problem()
                        if slug_field:
                            obj.slug = slug_field
                        self.stdout.write(f"Creating problem: {title}")
                    else:
                        problems_updated += 1
                        self.stdout.write(f"Updating problem: {title}")

                    obj.title = title
                    obj.statement = item.get("statement", "")
                    obj.input_format = item.get("input_format", "")
                    obj.output_format = item.get("output_format", "")
                    obj.constraints = item.get("constraints", "")
                    obj.sample_input = item.get("sample_input", "")
                    obj.sample_output = item.get("sample_output", "")
                    obj.difficulty = difficulty
                    obj.tags = tags
                    obj.discussion_count = int(item.get("discussion_count", 0) or 0)

                    # Ensure slug is unique if it wasn't pre-assigned properly
                    if not obj.slug:
                        obj.slug = self._unique_slug(title, exclude_problem_id=obj.pk)
                    
                    obj.save()

                    existing_tc_qs = TestCase.objects.filter(problem=obj)
                    deleted_count, _ = existing_tc_qs.delete()
                    testcases_deleted += deleted_count

                    new_tcs = []
                    for idx, tc in enumerate(testcases, start=1):
                        inp = tc.get("input", "")
                        expected = tc.get("expected_output", "")

                        if inp is None or expected is None:
                            continue

                        is_sample = bool(tc.get("is_sample", idx == 1))
                        is_hidden = bool(tc.get("is_hidden", False))
                        order = tc.get("order", idx)
                        try:
                            order = int(order)
                        except Exception:
                            order = idx

                        new_tcs.append(
                            TestCase(
                                problem=obj,
                                order=order,
                                is_sample=is_sample,
                                is_hidden=is_hidden,
                                input_data=str(inp),
                                expected_output=str(expected),
                            )
                        )

                    if new_tcs:
                        TestCase.objects.bulk_create(new_tcs)
                        testcases_created += len(new_tcs)
            except Exception as e:
                # Catch specific problem errors and log full stacktrace
                self.stderr.write(self.style.ERROR(f"Error processing problem '{title}': {e}"))
                self.stderr.write(traceback.format_exc())
                problems_skipped += 1

        after_count = Problem.objects.count()
        self.stdout.write(f"Problem count after import: {after_count}")

        self.stdout.write(
            self.style.SUCCESS(
                "Import finished.\n"
                f"Problems: {problems_created} created, {problems_updated} updated, {problems_skipped} skipped\n"
                f"Testcases: {testcases_created} created, {testcases_deleted} deleted"
            )
        )