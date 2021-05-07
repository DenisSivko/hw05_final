from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post

User = get_user_model()

ENTRIES_ON_PAGE = 10


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, ENTRIES_ON_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "posts/index.html", {"page": page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    group_posts = group.posts.all()
    paginator = Paginator(group_posts, ENTRIES_ON_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, "page": page})


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == "GET" or not form.is_valid():
        is_new = True
        return render(request, "posts/new.html", {
            "form": form, "is_new": is_new
        })
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect("index")


def profile(request, username):
    author_card = get_object_or_404(User, username=username)
    post_list = author_card.posts.all()
    paginator = Paginator(post_list, ENTRIES_ON_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    following = (
        request.user.is_authenticated
        and Follow.objects.filter(
            user=request.user, author=author_card
        ).exists()
    )
    return render(request, "posts/profile.html", {
        "page": page,
        "author_card": author_card,
        "following": following
    })


def post_view(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    author_card = post.author
    form = CommentForm()
    comments = post.comments.all()
    following = (
        request.user.is_authenticated
        and Follow.objects.filter(
            user=request.user, author=author_card
        ).exists()
    )
    return render(request, "posts/post.html", {
        "author_card": author_card,
        "post": post,
        "form": form,
        "comments": comments,
        "following": following
    })


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    if request.user != post.author:
        return redirect("post_view", username=username, post_id=post_id)
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )
    if request.method == "GET" or not form.is_valid():
        return render(request, "posts/new.html", {"form": form, "post": post})
    form.save()
    return redirect("post_view", username=username, post_id=post_id)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("post_view", username=username, post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, ENTRIES_ON_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "posts/follow.html", {"page": page})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.filter(user=request.user, author=author).delete()
    return redirect("profile", username=username)
