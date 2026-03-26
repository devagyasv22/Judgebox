import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("compiler", "0002_alter_codesubmission_language"),
        ("problems", "0005_problem_oj_fields"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="codesubmission",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="code_submissions",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="codesubmission",
            name="problem",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="submissions",
                to="problems.problem",
            ),
        ),
        migrations.AddField(
            model_name="codesubmission",
            name="passed",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="codesubmission",
            name="verdict",
            field=models.CharField(blank=True, default="", max_length=32),
        ),
        migrations.AddField(
            model_name="codesubmission",
            name="runtime_ms",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="codesubmission",
            name="memory_kb",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterModelOptions(
            name="codesubmission",
            options={"ordering": ["-submitted_at"]},
        ),
    ]
