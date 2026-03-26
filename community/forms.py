from django import forms

from community.models import Comment, Post
from problems.models import Problem


class PostForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        help_text="Comma-separated tags. Example: dp, graphs",
        widget=forms.TextInput(),
    )
    problem = forms.ModelChoiceField(
        required=False,
        queryset=Problem.objects.all(),
        empty_label="(No linked problem)",
    )

    class Meta:
        model = Post
        fields = ["title", "body", "tags", "problem"]
        widgets = {
            "title": forms.TextInput(),
            "body": forms.Textarea(attrs={"rows": 8}),
        }

    def clean_tags(self):
        raw = self.cleaned_data.get("tags") or ""
        parts = [p.strip() for p in raw.split(",") if p.strip()]
        # Persist as comma-separated normalized tags.
        return ", ".join(parts)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 4}),
        }

