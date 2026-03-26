from django.contrib import admin

from .models import Problem
from .testcases_model import TestCase


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ("title", "difficulty", "slug", "created_at")
    list_filter = ("difficulty",)
    search_fields = ("title", "tags")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'problem', 'input_data', 'expected_output')