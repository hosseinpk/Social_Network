from django.contrib import admin
from posts.models import Post, Comment, Like


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "content",
        "author",
        "status",
        "allowed_comment",
        "created_at",
    )
    #readonly_fields = ("status", "allowed_comment")  
    search_fields = (
        "content",
        "author__user__username",
    )
    list_filter = (
        "status",
        "allowed_comment",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "content",
        "author",
        "post",
        "created_at",
    )
    search_fields = (
        "content",
        "author__user__username",
        "post__content",
    )
    
    list_filter = (
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = (
        "liked_by",
        "post",
        "created_at",
    )
    search_fields = (
        "liked_by__user__username",
        "post__content",
    )
     
    list_filter = ("created_at",)
