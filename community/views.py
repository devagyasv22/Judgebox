from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, F, Q
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from community.forms import PostForm, CommentForm
from community.models import Comment, Post
from problems.models import Problem


def _normalize_tags_param(v: str):
    if not v:
        return ""
    return v.strip().lower()


def community_list(request):
    q = (request.GET.get("q") or "").strip()
    tag = _normalize_tags_param(request.GET.get("tag"))
    problem_id = request.GET.get("problem_id") or ""
    sort = request.GET.get("sort") or "new"

    posts_qs = Post.objects.select_related("author", "problem").all()

    if q:
        posts_qs = posts_qs.filter(Q(title__icontains=q) | Q(body__icontains=q))

    if tag:
        # tags stored as comma-separated string; use icontains for MVP.
        posts_qs = posts_qs.filter(tags__icontains=tag)

    if problem_id:
        try:
            posts_qs = posts_qs.filter(problem_id=int(problem_id))
        except ValueError:
            pass

    # Annotate comment count for sorting/display.
    posts_qs = posts_qs.annotate(comment_count=Count("comments", distinct=True))

    if sort == "popular":
        posts_qs = posts_qs.order_by("-comment_count", "-created_at")
    else:
        posts_qs = posts_qs.order_by("-created_at")

    per_page = 10
    paginator = Paginator(posts_qs, per_page)
    page_number = request.GET.get("page") or 1
    page_obj = paginator.get_page(page_number)

    # Compute distinct tag list for sidebar/filter UX.
    tags = []
    try:
        # Split all tags quickly (MVP). For large datasets, switch to a Tag model.
        for p in Post.objects.all().values_list("tags", flat=True):
            tags.extend([t.strip() for t in (p or "").split(",") if t.strip()])
        tags = sorted(set(tags), key=lambda s: s.lower())
    except Exception:
        tags = []

    problems = Problem.objects.all().order_by("id")[:200]

    return render(
        request,
        "community/list.html",
        {
            "q": q,
            "tag": tag,
            "problem_id": problem_id,
            "sort": sort,
            "page_obj": page_obj,
            "tags": tags,
            "problems": problems,
        },
    )


@login_required
def community_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("community_detail", pk=post.pk)
    else:
        form = PostForm()

    return render(request, "community/new.html", {"form": form})


def community_detail(request, pk: int):
    post = get_object_or_404(Post, pk=pk)
    comments = (
        Comment.objects.filter(post=post)
        .select_related("author")
        .order_by("-created_at")
    )
    comment_form = CommentForm()
    return render(
        request,
        "community/detail.html",
        {
            "post": post,
            "comments": comments,
            "comment_form": comment_form,
            "login_required": not request.user.is_authenticated,
        },
    )


@login_required
@require_POST
def community_post_upvote(request, pk: int):
    post = get_object_or_404(Post, pk=pk)
    Post.objects.filter(pk=post.pk).update(upvote_total=F("upvote_total") + 1)
    return HttpResponseRedirect(reverse("community_detail", kwargs={"pk": pk}) + "#comments")


@login_required
@require_POST
def community_comment_upvote(request, pk: int):
    comment = get_object_or_404(Comment, pk=pk)
    Comment.objects.filter(pk=comment.pk).update(upvote_total=F("upvote_total") + 1)
    return HttpResponseRedirect(
        reverse("community_detail", kwargs={"pk": comment.post_id}) + "#comments"
    )



@login_required
@require_POST
def community_comment(request, pk: int):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if not form.is_valid():
        return redirect("community_detail", pk=pk)

    body = (form.cleaned_data.get("body") or "").strip()
    if not body:
        return redirect("community_detail", pk=pk)

    Comment.objects.create(post=post, author=request.user, body=body)

    return HttpResponseRedirect(reverse("community_detail", kwargs={"pk": pk}) + "#comments")

