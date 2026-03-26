# Generated manually to match contests.models

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("problems", "0004_rename_problem_testcase_problem"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Contest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("slug", models.SlugField(blank=True, max_length=220, null=True, unique=True)),
                ("description", models.TextField(blank=True)),
                ("contest_type", models.CharField(default="Educational", max_length=80)),
                ("start_time", models.DateTimeField(db_index=True)),
                ("end_time", models.DateTimeField(db_index=True)),
                (
                    "problems",
                    models.ManyToManyField(related_name="contests", to="problems.problem"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ContestSubmission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.TextField()),
                ("language", models.CharField(max_length=20)),
                ("verdict", models.CharField(max_length=20)),
                ("runtime_ms", models.IntegerField(blank=True, null=True)),
                ("submitted_at", models.DateTimeField(auto_now_add=True)),
                (
                    "contest",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="submissions",
                        to="contests.contest",
                    ),
                ),
                (
                    "problem",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="problems.problem"),
                ),
                (
                    "user",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={
                "ordering": ["submitted_at"],
            },
        ),
        migrations.CreateModel(
            name="ContestRegistration",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("registered_at", models.DateTimeField(auto_now_add=True)),
                (
                    "contest",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="registrations",
                        to="contests.contest",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="contest_regs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("user", "contest")},
            },
        ),
    ]
