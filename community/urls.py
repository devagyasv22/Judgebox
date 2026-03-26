from django.urls import path

from community import views


urlpatterns = [
    path("", views.community_list, name="community_list"),
    path("new/", views.community_new, name="community_new"),
    path("<int:pk>/", views.community_detail, name="community_detail"),
    path("<int:pk>/comment/", views.community_comment, name="community_comment"),
    path("upvote/post/<int:pk>/", views.community_post_upvote, name="community_post_upvote"),
    path("upvote/comment/<int:pk>/", views.community_comment_upvote, name="community_comment_upvote"),
]

