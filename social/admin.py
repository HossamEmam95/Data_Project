from django.contrib import admin
from .models import (User, Post, Comment, Like, Group, CustomerGroup)


class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'birthday', 'email')
    search_fields = ('first_name',)


class PostAdmin(admin.ModelAdmin):
    pass


class CommentAdmin(admin.ModelAdmin):
    pass


class LikeAdmin(admin.ModelAdmin):
    pass


class GroupAdmin(admin.ModelAdmin):
    pass


class CustomerGroupeAdmin(admin.ModelAdmin):
    pass


admin.site.register(User, UserAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(CustomerGroup, CustomerGroupeAdmin)
