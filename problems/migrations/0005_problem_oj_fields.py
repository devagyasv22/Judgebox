import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("problems", "0004_rename_problem_testcase_problem"),
    ]

    operations = [
        migrations.AddField(
            model_name="problem",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="problem",
            name="difficulty",
            field=models.CharField(
                choices=[("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")],
                db_index=True,
                default="medium",
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name="problem",
            name="tags",
            field=models.CharField(blank=True, default="", help_text="Comma-separated tags", max_length=500),
        ),
        migrations.AddField(
            model_name="problem",
            name="discussion_count",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
