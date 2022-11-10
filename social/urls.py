from django.urls import path
from .views import PostListView, PostDetailView,PostEditView,PostDeleteView,CommentDeleteView,UserProfileView,ProfileEditView,AddFollower,RemoveFollower,AddLike,AddDislike,UserSearch,FollowersList,AddCommentLike,AddCommentDislike,CommentReplyView,PostNotification,FollowNotification

urlpatterns = [
    path('',PostListView.as_view(),name="post-list"),
    path('post/<int:pk>/',PostDetailView.as_view(),name="post"),
    path('post/edit/<int:pk>/',PostEditView.as_view(),name="post-edit"),
    path('post/delete/<int:pk>/',PostDeleteView.as_view(),name="post-delete"),
    # Django does not support pk for 2 times in a same location, that's why i used post_pk for post and pk for comment
    path('post/<int:post_pk>/comment/delete/<int:pk>/', CommentDeleteView.as_view(), name='comment-delete'),
    path('post/<int:post_pk>/comment/<int:pk>/like',AddCommentLike.as_view(),name="comment-like"),
    path('post/<int:post_pk>/comment/<int:pk>/dislike',AddCommentDislike.as_view(),name="comment-dislike"),
    path('post/<int:post_pk>/comment/<int:pk>/reply',CommentReplyView.as_view(),name="comment-reply"),
    path('post/<int:pk>/like', AddLike.as_view(), name='like'),
    path('post/<int:pk>/dislike', AddDislike.as_view(), name='dislike'),
    path('profile/<int:pk>/',UserProfileView.as_view(),name="profile"),
    path('profile/edit/<int:pk>/',ProfileEditView.as_view(),name="profile-edit"),
    path('profile/<int:pk>/followers/',FollowersList.as_view(),name="followers-list"),
    path('profile/<int:pk>/followers/add',AddFollower.as_view(),name="add-follower"),
    path('profile/<int:pk>/followers/remove',RemoveFollower.as_view(),name="remove-follower"),
    path('search/',UserSearch.as_view(),name="search-profile"),
    path('notification/<int:notification_pk>/post<int:post_pk>',PostNotification.as_view(),name="post-notification"),
    path('notification/<int:notification_pk>/post<int:profile_pk>',FollowNotification.as_view(),name="follow-notification"),
 ]