from django import forms

from .models import UserProfile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "codeforces_handle",
            "bio",
            "github_url",
            "linkedin_url",
            "website_url",
        ]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
        }
