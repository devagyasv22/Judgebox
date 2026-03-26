from django.db import models

DIFFICULTY_CHOICES = (
    ("easy", "Easy"),
    ("medium", "Medium"),
    ("hard", "Hard"),
)


class Problem(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)  # for cleaner URLs
    statement = models.TextField()
    input_format = models.TextField()
    output_format = models.TextField()
    constraints = models.TextField()
    sample_input = models.TextField()
    sample_output = models.TextField()
    difficulty = models.CharField(
        max_length=10, choices=DIFFICULTY_CHOICES, default="medium", db_index=True
    )
    tags = models.CharField(
        max_length=500,
        blank=True,
        default="",
        help_text="Comma-separated tags",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    discussion_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at", "id"]

    def __str__(self):
        return self.title

    def tag_list(self):
        return [t.strip() for t in self.tags.split(",") if t.strip()]

from .testcases_model import TestCase
