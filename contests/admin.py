from django.contrib import admin

from .models import Contest, ContestRegistration, ContestSubmission


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ("title", "contest_type", "start_time", "end_time")
    search_fields = ("title", "description")
    filter_horizontal = ("problems",)


@admin.register(ContestRegistration)
class ContestRegistrationAdmin(admin.ModelAdmin):
    list_display = ("user", "contest", "registered_at")
    list_filter = ("contest",)


@admin.register(ContestSubmission)
class ContestSubmissionAdmin(admin.ModelAdmin):
    list_display = ("user", "contest", "problem", "verdict", "submitted_at")
    list_filter = ("verdict", "contest")
