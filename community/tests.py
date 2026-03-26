from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from community.models import Comment, Post


class CommunityAuthTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u1", password="pass12345")
        self.post = Post.objects.create(
            title="Hello",
            body="First post",
            author=self.user,
            tags="help, dp",
        )

    def test_anonymous_can_view_list_and_detail(self):
        resp = self.client.get(reverse("community_list"))
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(reverse("community_detail", kwargs={"pk": self.post.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_anonymous_cannot_create_post_or_comment(self):
        resp = self.client.get(reverse("community_new"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp["Location"])
        self.assertIn("next=", resp["Location"])

        resp = self.client.post(reverse("community_comment", kwargs={"pk": self.post.pk}), data={"body": "hi"})
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp["Location"])

        self.assertEqual(Comment.objects.count(), 0)

    def test_logged_in_can_create_post_and_comment(self):
        self.client.login(username="u1", password="pass12345")

        resp = self.client.post(
            reverse("community_new"),
            data={
                "title": "New topic",
                "body": "Body text",
                "tags": "graphs, dp",
                "problem": "",
            },
            follow=False,
        )
        # Redirect to detail
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Post.objects.count(), 2)

        created_post = Post.objects.exclude(pk=self.post.pk).get()
        resp2 = self.client.post(
            reverse("community_comment", kwargs={"pk": created_post.pk}),
            data={"body": "Nice!"},
            follow=False,
        )
        self.assertEqual(resp2.status_code, 302)
        self.assertTrue(Comment.objects.filter(post=created_post).exists())

    def test_logged_in_can_upvote_post_and_comment(self):
        self.client.login(username="u1", password="pass12345")

        # Upvote the existing post.
        resp = self.client.post(reverse("community_post_upvote", kwargs={"pk": self.post.pk}))
        self.assertEqual(resp.status_code, 302)
        self.post.refresh_from_db()
        self.assertEqual(self.post.upvote_total, 1)

        # Create a comment then upvote it.
        comment = Comment.objects.create(post=self.post, author=self.user, body="Nice")
        resp2 = self.client.post(reverse("community_comment_upvote", kwargs={"pk": comment.pk}))
        self.assertEqual(resp2.status_code, 302)
        comment.refresh_from_db()
        self.assertEqual(comment.upvote_total, 1)

    def test_anonymous_cannot_upvote(self):
        resp = self.client.post(reverse("community_post_upvote", kwargs={"pk": self.post.pk}))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp["Location"])

        comment = Comment.objects.create(post=self.post, author=self.user, body="Nice")
        resp2 = self.client.post(reverse("community_comment_upvote", kwargs={"pk": comment.pk}))
        self.assertEqual(resp2.status_code, 302)
        self.assertIn("/accounts/login/", resp2["Location"])

