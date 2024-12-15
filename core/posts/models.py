from django.db import models
from accounts.models import Profile


class Post(models.Model):

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("deleted", "Deleted"),
    ]

    content = models.CharField(max_length=255)
    image = models.ImageField(upload_to="posts/images/", blank=True)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    allowed_comment = models.BooleanField(default=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):

        return f"{self.content} ({self.get_status_display()})"


class Comment(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content


class Like(models.Model):

    Like_CHOICES = [
        (" ", " "),
        ("like", "Like"),
        ("dislike", "Dislike"),
    ]
    liked_by = models.ForeignKey(Profile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    reaction = models.CharField(max_length=7, choices=Like_CHOICES, default=" ")

    def __str__(self):
        return f"{self.liked_by} liked {self.post}"
