from django.db.models import Q
from django.contrib.auth import (
    authenticate, login, logout
    )
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.hashers import make_password
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.shortcuts import render, HttpResponseRedirect, reverse

from .forms import LoginForm, RegisterForm
from .models import User, Post, Group, Comment, Like, CustomerGroup, FriendShip


def home(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    users = User.objects.all()
    logedin = request.user
    return render(request, 'home.html', {"users": users, "logedin": logedin})


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
    fields = ('body', )

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
        context = super(ListPosts, self).get_context_data(**kwargs)
        friends = FriendShip.objects.filter(Q(user1=self.request.user) | Q(user2=self.request.user))
        filtered_posts = Post.objects.filter(
            Q(user=self.request.user) |
            Q(user__user_friend__in=friends) |
            Q(user__user_friend1__in=friends)
        )
        posts = {}
        for post in context['post_list']:
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
        context['groups'] = Group.objects.all()
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
            'like': like,
            'comments': Comment.objects.filter(post=post),
            'post_flag': flag,

        }
    members = CustomerGroup.objects.filter(group=group)
    users = User.objects.filter().exclude(user_group__group=group)
    context = {
        'group': group,
        'posts': posts,
        'members': members,
        'users': users,
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
    fields = ('body',)

    def form_valid(self, form):
        instance = form.instance
        instance.user = self.request.user
        instance.post = Post.objects.get(id=self.kwargs['pk'])
        return super(CreateComment, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super(CreateComment, self).get_context_data(**kwargs)
        ctx['title'] = "Create"
        return ctx


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


def join_group(request, pk, id):
    group = Group.objects.get(id=pk)
    user = User.objects.get(id=id)
    CustomerGroup.objects.create(
        group=group,
        user=user,
    )
    return HttpResponseRedirect(reverse('group_detail', kwargs={'pk': pk}))
