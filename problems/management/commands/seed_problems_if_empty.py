from django.core.management.base import BaseCommand
from problems.models import Problem
from django.core.management import call_command

class Command(BaseCommand):
    help = "Seed problems from JSON only if DB is empty."

    def add_arguments(self, parser):
        parser.add_argument("--path", default="OJ/data/problems_seed.json")

    def handle(self, *args, **opts):
        if Problem.objects.exists():
            self.stdout.write(self.style.SUCCESS("Problems already exist, skipping seed."))
            return
        self.stdout.write("Seeding problems…")
        call_command("import_problems", opts["path"])
        self.stdout.write(self.style.SUCCESS("Seeding done."))