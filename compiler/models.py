from django.conf import settings
from django.db import models

LANGUAGE_CHOICES = (
    ("cpp", "C++"),
    ("py", "Python"),
    ("java", "Java"),
)

class CodeSubmission(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="code_submissions",
    )
    problem = models.ForeignKey(
        "problems.Problem",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="submissions",
    )
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES)
    code = models.TextField()
    input_data = models.TextField(blank=True, null=True)
    output_data = models.TextField(blank=True, null=True)
    passed = models.BooleanField(default=False)
    verdict = models.CharField(max_length=32, blank=True, default="")
    runtime_ms = models.IntegerField(null=True, blank=True)
    memory_kb = models.IntegerField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.language} submission at {self.submitted_at}"
