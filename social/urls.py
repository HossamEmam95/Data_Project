from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^login', views.login_view, name="login"),
    url(r'^home', views.home, name="home"),
    url(r'^logout', views.logout_view, name='logout'),
    url(r'^register', views.Register.as_view(), name='register'),
    url(
        r'^post-timeline/',
        views.CreatePostTimeLine.as_view(),
        name='create_timeline'),
    url(
        r'^post-group/(?P<pk>[0-9]+)/',
        views.CreatePostGroup.as_view(),
        name='create_post_group'),
    url(r'timeline/', views.ListPosts.as_view(), name='timeline'),
    url(
        r'^update_post/(?P<pk>[0-9]+)/',
        views.UpdatePost.as_view(),
        name='update_post'),
    url(
        r'^update_post_group/(?P<pk>[0-9]+)/',
        views.UpdatePostGroup.as_view(),
        name='update_post_group'),
    url(
        r'^delete_post/(?P<pk>[0-9]+)/',
        views.delete_post,
        name='delete_post'),
    url(
        r'^delete_post_group/(?P<pk>[0-9]+)/(?P<hamada>[0-9]+)/',
        views.delete_post_group,
        name='delete_post_group'),
    url(
        r'^create_group/',
        views.CreateGroup.as_view(),
        name='create_group'),
    url(
        r'^group_detail/(?P<pk>[0-9]+)/',
        views.group_detail,
        name='group_detail'),
    url(
        r'^update_group/(?P<pk>[0-9]+)/',
        views.UpdateGroup.as_view(),
        name='update_group'),
    url(
        r'^delete_group/(?P<pk>[0-9]+)/',
        views.delete_group,
        name='delete_group'),
    url(
        r'^create_comment/(?P<pk>[0-9]+)/',
        views.CreateComment.as_view(),
        name='create_comment'),
    url(
        r'^delete_comment/(?P<pk>[0-9]+)/',
        views.delete_comment,
        name='delete_comment'),
    url(
        r'^create_like/(?P<pk>[0-9]+)/',
        views.create_post_like,
        name='create_like'),
    url(
        r'^remove_like/(?P<pk>[0-9]+)/',
        views.remove_like,
        name='remove_like'),
    url(
        r'^remove_like_group/(?P<pk>[0-9]+)/(?P<id>[0-9]+)/',
        views.remove_like_group,
        name='remove_like_group'),
    url(
        r'^create_like_group/(?P<pk>[0-9]+)/(?P<id>[0-9]+)/',
        views.create_post_like_group,
        name='create_like_group'),
    url(
        r'^add_to_group/(?P<pk>[0-9]+)/(?P<id>[0-9]+)/',
        views.add_to_group,
        name='add_to_group'),
    url(
        r'^user_profile/(?P<pk>[0-9]+)/',
        views.user_profile,
        name='user_profile'),
    url(
        r'^add_friend/(?P<pk>[0-9]+)/',
        views.create_friendship,
        name='add_friend'),
    url(
        r'^remove_friend/(?P<pk>[0-9]+)/',
        views.remove_friendship,
        name='remove_friend'),
    url(
        r'^join_group/(?P<pk>[0-9]+)/',
        views.join_group,
        name='join_group'),
    url(
        r'^leave_group/(?P<pk>[0-9]+)/',
        views.leave_group,
        name='leave_group'),


]
