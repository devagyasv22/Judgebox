from django.db import models
from problems.models import Problem


class TestCase(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='testcases')
    # Controls execution order when judging (1-indexed is conventional).
    order = models.PositiveIntegerField(default=1, db_index=True)
    # Whether this testcase is meant to be shown on the problem page.
    is_sample = models.BooleanField(default=False, db_index=True)
    # Hidden testcases are used for judging but not shown in the UI.
    is_hidden = models.BooleanField(default=False, db_index=True)
    input_data = models.TextField()
    expected_output = models.TextField()

def __str__(self):
    return f"TestCase for Problem {self.problem.id}"
