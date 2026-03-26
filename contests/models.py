# contests/models.py
from django.conf import settings
from django.db import models
from django.utils.text import slugify

from problems.models import Problem


class Contest(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True, null=True)
    description = models.TextField(blank=True)
    contest_type = models.CharField(max_length=80, default="Educational")
    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField(db_index=True)
    problems = models.ManyToManyField(Problem, related_name="contests")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.slug:
            base = slugify(self.title)[:200] or "contest"
            candidate = base
            n = 0
            while Contest.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                n += 1
                candidate = f"{base}-{n}"
            self.slug = candidate
            super().save(update_fields=["slug"])

    def has_started(self):
        from django.utils import timezone

        return timezone.now() >= self.start_time

    def has_ended(self):
        from django.utils import timezone

        return timezone.now() > self.end_time

    def is_running(self):
        return self.has_started() and not self.has_ended()

    def duration_minutes(self):
        delta = self.end_time - self.start_time
        return max(1, int(delta.total_seconds() // 60))

    def __str__(self):
        return self.title


class ContestRegistration(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="contest_regs"
    )
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name="registrations")
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "contest")


class ContestSubmission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name="submissions")
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    code = models.TextField()
    language = models.CharField(max_length=20)
    verdict = models.CharField(max_length=20)  # AC, WA, TLE, etc.
    runtime_ms = models.IntegerField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["submitted_at"]
