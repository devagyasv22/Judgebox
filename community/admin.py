from django.contrib import admin

from community.models import Comment, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "problem", "created_at", "updated_at")
    search_fields = ("title", "body", "author__username", "tags")
    list_filter = ("created_at", "problem")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "author", "created_at")
    search_fields = ("body", "author__username", "post__title")
    list_filter = ("created_at", "post")

