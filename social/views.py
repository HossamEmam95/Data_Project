from django.contrib.auth import (
    authenticate, login, logout
    )
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.hashers import make_password
from django.views.generic import CreateView, UpdateView, ListView
from django.shortcuts import render, HttpResponseRedirect, reverse

from .forms import LoginForm, RegisterForm, PostForm, CommentForm
from .models import User, Post, Group, Comment, Like, CustomerGroup, FriendShip


def home(request):
    user = request.user
    if user.is_authenticated:
        groups = Group.objects.filter(group_user__user=request.user)
        friends = User.objects.filter(user_friend__user2=user)
        posts = Post.objects.filter(user=user)
        stats = stats_calc(user.id)
        context = {
            'user': user,
            'friends': friends,
            'groups': groups,
            'posts': posts,
            'stats': stats,
        }
    else:
        context = {}

    return render(request, 'home.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request=request, username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect(reverse('home'))
    else:
        form = LoginForm()
    return render(request, 'login.html', {"form": form})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))


class Register(CreateView):
    template_name = 'register.html'
    success_url = reverse_lazy('home')
    model = User
    form_class = RegisterForm

    def form_valid(self, form):
        password = form.cleaned_data['password']
        instance = form.instance
        instance.password = make_password(password)
        instance.save()
        login(self.request, instance)
        return super(Register, self).form_valid(form)


class CreatePostTimeLine(CreateView):
    template_name = 'create_post.html'
    success_url = reverse_lazy('timeline')
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        instance = form.instance
        instance.user = self.request.user
        instance.scope = Post.TIMELINE
        return super(CreatePostTimeLine, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super(CreatePostTimeLine, self).get_context_data(**kwargs)
        ctx['title'] = "Create"
        return ctx


class ListPosts(ListView):
    template_name = 'timeline.html'
    model = Post
    paginate_by = 15

    def get_context_data(self, **kwargs):
        if self.request.user.is_authenticated:
            context = super(ListPosts, self).get_context_data(**kwargs)
            friends = User.objects.filter(user_friend__user2=self.request.user)
            groups = Group.objects.filter(group_user__user=self.request.user)
            users = User.objects.exclude(
                user_friend__user2=self.request.user).exclude(
                id=self.request.user.id)
            q_s1 = list(Post.objects.filter(user=self.request.user))
            q_s2 = list(Post.objects.filter(user__in=friends, scope=Post.TIMELINE))
            q_s3 = list(Post.objects.filter(group__in=groups).exclude(user=self.request.user))
            q_s = q_s1 + q_s2 + q_s3
            print("friends: {}".format(friends))
            print("Q_s1: {} \n Q_s2: {}\n Q_s3: {}".format(q_s1, q_s2, q_s3))
            posts = {}
            for post in q_s:
                flag = 0
                if len(Like.objects.filter(user=self.request.user, post=post)) > 0:
                    flag = 1
                like = None
                if flag:
                    like = Like.objects.get(user=self.request.user, post=post).id
                posts[str(post.id)] = {
                    'post': post,
                    'comments': Comment.objects.filter(post=post),
                    'num_likes': len(Like.objects.filter(post=post)),
                    'post_flag': flag,
                    'like_id': like,
                }
            context['posts'] = posts
            context['users'] = users
            context['post_form'] = PostForm()
            context['comment_form'] = CommentForm()
            context['groups'] = Group.objects.all()
        else:
            context = {}
        return context


class UpdatePost(UpdateView):
    template_name = 'create_post.html'
    success_url = reverse_lazy('timeline')
    model = Post
    fields = ('body',)

    def get_context_data(self, **kwargs):
        ctx = super(UpdatePost, self).get_context_data(**kwargs)
        ctx['title'] = "Update"
        return ctx


class UpdatePostGroup(UpdateView):
    template_name = 'create_post.html'
    model = Post
    fields = ('body',)

    def get_context_data(self, **kwargs):
        ctx = super(UpdatePostGroup, self).get_context_data(**kwargs)
        ctx['title'] = "Update"
        return ctx

    def get_success_url(self):
       return reverse_lazy('group_detail', kwargs={'pk': self.object.group.id})


def delete_post(request, pk):
    post = Post.objects.get(id=pk)
    post.delete()
    return HttpResponseRedirect(reverse('timeline'))


def delete_post_group(request, pk, hamada):
    post = Post.objects.get(id=pk)
    group = Group.objects.get(id=hamada)
    post.delete()
    return HttpResponseRedirect(reverse('group_detail', kwargs={'pk': group.id}))


class CreatePostGroup(CreateView):
    template_name = 'create_post.html'
    model = Post
    fields = ('body', )

    def form_valid(self, form):
        instance = form.instance
        instance.user = self.request.user
        instance.group = Group.objects.get(id=self.kwargs['pk'])
        instance.scope = Post.GROUP
        return super(CreatePostGroup, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super(CreatePostGroup, self).get_context_data(**kwargs)
        ctx['title'] = "Create"
        return ctx

    def get_success_url(self):
        post = Post.objects.last()
        return reverse_lazy('group_detail', kwargs={'pk': post.group.id})


class CreateGroup(CreateView):
    template_name = 'create_group.html'
    success_url = reverse_lazy('home')
    model = Group
    fields = ('name',)

    def form_valid(self, form):
        instance = form.instance
        instance.admin = self.request.user
        instance.save()
        CustomerGroup.objects.create(user=self.request.user, group=instance)
        return super(CreateGroup, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super(CreateGroup, self).get_context_data(**kwargs)
        ctx['title'] = "Create"
        return ctx


class UpdateGroup(UpdateView):
    template_name = 'create_group.html'
    success_url = reverse_lazy('timeline')
    model = Group
    fields = ('name', 'admin',)

    def get_context_data(self, **kwargs):
        ctx = super(UpdateGroup, self).get_context_data(**kwargs)
        ctx['title'] = "Update"
        return ctx


def group_detail(request, pk):
    group = Group.objects.get(id=pk)
    flag1 = CustomerGroup.objects.filter(user=request.user).exists()
    posts = {}
    for post in Post.objects.filter(group=group):
        flag = 0
        if len(Like.objects.filter(user=request.user, post=post)) > 0:
            flag = 1

        like = None
        if flag:
            like = Like.objects.get(user=request.user, post=post).id
        posts[str(post.id)] = {
            'post': post,
            'num_likes': len(Like.objects.filter(post=post)),
            'like_id': like,
            'comments': Comment.objects.filter(post=post),
            'post_flag': flag,
            'post_form': PostForm(),
            'Comment_form': CommentForm(),

        }
    members = CustomerGroup.objects.filter(group=group)
    users = User.objects.filter().exclude(user_group__group=group)
    context = {
        'group': group,
        'posts': posts,
        'members': members,
        'users': users,
        'flag1': flag1,
    }
    print(context)

    return render(request, 'detail_group.html', context)


def delete_group(request, pk):
    group = Group.objects.get(id=pk)
    group.delete()
    return HttpResponseRedirect(reverse('timeline'))


class CreateComment(CreateView):
    template_name = 'create_post.html'
    model = Comment
    success_url = reverse_lazy('timeline')
    form_class = CommentForm

    def form_valid(self, form):
        instance = form.instance
        instance.user = self.request.user
        instance.post = Post.objects.get(id=self.kwargs['pk'])
        return super(CreateComment, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super(CreateComment, self).get_context_data(**kwargs)
        ctx['title'] = "Create"
        return ctx


class CreateCommentGroup(CreateView):
    template_name = 'create_post.html'
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        instance = form.instance
        instance.user = self.request.user
        instance.post = Post.objects.get(id=self.kwargs['pk'])
        return super(CreateCommentGroup, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super(CreateCommentGroup, self).get_context_data(**kwargs)
        ctx['title'] = "Create"
        return ctx

    def get_success_url(self):
        return reverse_lazy('group_detail', kwargs={'pk': self.kwargs['group']})


class UpdateComment(UpdateGroup):
    model = Comment
    success_url = reverse_lazy('timeline')
    template_name = 'create_comment.html'
    fields = ('body',)

    def get_context_data(self, **kwargs):
        ctx = super(UpdateGroup, self).get_context_data(**kwargs)
        ctx['post'] = Post.objects.get(id=kwargs['pk'])
        return ctx


def delete_comment(request, pk):
    comment = Comment.objects.get(id=pk)
    comment.delete()
    return HttpResponseRedirect(reverse('timeline'))


def create_post_like(request, pk):
    post = Post.objects.get(id=pk)
    try:
        Like.objects.get(post=post, user=request.user)
    except Like.DoesNotExist:
        Like.objects.create(
            post=post,
            user=request.user,
        )
    return HttpResponseRedirect(reverse('timeline'))


def create_comment_like(request, pk):
    comment = Comment.objects.get(id=pk)
    try:
        Like.objects.get(comment=comment, user=request.user)
    except Like.DoesNotExist:
        Like.objects.create(
            comment=comment,
            user=request.user,
        )
    return HttpResponseRedirect(reverse('timeline'))


def remove_like(request, pk):
    like = Like.objects.get(id=pk)
    like.delete()
    return HttpResponseRedirect(reverse('timeline'))


def remove_like_group(request, pk, id):
    group = Group.objects.get(id=id)
    like = Like.objects.get(id=pk)
    like.delete()
    return HttpResponseRedirect(reverse('group_detail', kwargs={'pk': group.id}))


def create_post_like_group(request, pk, id):
    group = Group.objects.get(id=id)
    post = Post.objects.get(id=pk)
    try:
        Like.objects.get(post=post, user=request.user)
    except Like.DoesNotExist:
        Like.objects.create(
            post=post,
            user=request.user,
        )
    return HttpResponseRedirect(reverse('group_detail', kwargs={'pk': group.id}))


def add_to_group(request, pk, id):
    group = Group.objects.get(id=pk)
    user = User.objects.get(id=id)
    CustomerGroup.objects.create(
        group=group,
        user=user,
    )
    return HttpResponseRedirect(reverse('group_detail', kwargs={'pk': pk}))


def user_profile(request, pk):
    user = User.objects.get(id=pk)
    posts = Post.objects.filter(user=user, scope=Post.TIMELINE)
    friends = list(User.objects.filter(user_friend__user2=request.user))
    print('friends: {}'.format(friends))
    mutual_friends = [user]
    flag = FriendShip.objects.filter(user1=request.user, user2=user).exists()
    for friend in friends:
        m_f = list(User.objects.filter(user_friend__user1=friend, user_friend__user2__in=friends))
        print('m_F:  {}'.format(m_f))
        for f in m_f:
            if f not in mutual_friends:
                mutual_friends.append(f)
    mutual_friends.pop(0)

    stats = stats_calc(pk)
    context = {
        'user': user,
        'posts': posts,
        'mutual_friends': mutual_friends,
        'flag': flag,
        'stats': stats,
    }

    return render(request, 'user_profile.html', context)


def create_friendship(request, pk):
    user1 = request.user
    user2 = User.objects.get(id=pk)
    FriendShip.objects.create(user1=user1, user2=user2)
    FriendShip.objects.create(user1=user2, user2=user1)

    return HttpResponseRedirect(reverse('user_profile', kwargs={'pk': pk}))


def remove_friendship(request, pk):
    user1 = request.user
    current_friend = User.objects.get(id=pk)
    f1 = FriendShip.objects.get(user1=user1, user2=current_friend)
    f2 = FriendShip.objects.get(user1=current_friend, user2=user1)
    f1.delete()
    f2.delete()
    return HttpResponseRedirect(reverse('user_profile', kwargs={'pk': pk}))



def join_group(request, pk):
    group = Group.objects.get(id=pk)
    CustomerGroup.objects.create(user=request.user, group=group)
    return HttpResponseRedirect(reverse('group_detail', kwargs={'pk': pk}))


def leave_group(request, pk):
    group = Group.objects.get(id=pk)
    d = CustomerGroup.objects.get(user=request.user, group=group)
    d.delete()
    return HttpResponseRedirect(reverse('group_detail', kwargs={'pk': pk}))


def stats_calc(pk):
    user = User.objects.get(id=pk)
    posts = Post.objects.filter(user=user)
    num_posts = len(posts)
    num_friends = len(FriendShip.objects.filter(user1=user))
    num_likes_m = len(Like.objects.filter(user=user))
    num_likes_r = 0
    for post in posts:
        num_likes_r += len(Like.objects.filter(post=post))

    stats = {'stats': {
        'num_posts': num_posts,
        'num_friends': num_friends,
        'num_likes_r': num_likes_r,
        'num_likes_m': num_likes_m,
    }
    }
    return stats