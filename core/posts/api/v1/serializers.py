from rest_framework import serializers
from posts.models import Post, Comment, Like
from accounts.models import Profile


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ["id", "content", "image", "allowed_comment", "status", "author"]
        read_only_fields = ["author"]

    def to_representation(self, instance):

        rep = super().to_representation(instance)
        rep["author"] = instance.author.user.username
        rep.pop("status")
        if self.context.get("id") is not None:
            rep["comments"] = CommentSerializer(
                Comment.objects.filter(post=instance), many=True
            ).data
            rep["like"] = LikeSerializer(
                Like.objects.filter(post=instance, reaction="like"), many=True
            ).data
            rep["dislike"] = LikeSerializer(
                Like.objects.filter(post=instance, reaction="dislike"), many=True
            ).data

        return rep

    def create(self, validated_data):
        request = self.context.get("request")
        try:
            validated_data["author"] = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            raise serializers.ValidationError({"author": "Profile not found."})
        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):

    class Meta:

        model = Comment
        fields = "__all__"
        read_only_fields = ["author", "post"]

    def create(self, validated_data):

        post = self.context.get("post")
        request = self.context.get("request")
        try:
            validated_data["author"] = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            raise serializers.ValidationError({"author": "Profile not found."})

        validated_data["post"] = post

        return super().create(validated_data)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["author"] = instance.author.user.username
        rep.pop("post")

        return rep


class CommentDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = "__all__"

    def to_representation(self, instance):

        rep = super().to_representation(instance)
        rep.pop("post")
        rep["author"] = instance.author.user.username

        return rep


class OtherUserPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = "__all__"

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep.pop("status")
        rep["author"] = instance.author.user.username
        return rep


class LikeSerializer(serializers.ModelSerializer):

    class Meta:

        model = Like
        fields = "__all__"
        read_only_fields = ["post", "liked_by"]

    def validate(self, attrs):

        post = self.context.get("post")
        request = self.context.get("request")
        profile = Profile.objects.get(user=request.user)

        if Like.objects.filter(post=post, liked_by=profile).exists():
            if request.method == "PUT":
                return super().validate(attrs)
            raise serializers.ValidationError(
                {"details": "You have already reacted to this post."}
            )
        return super().validate(attrs)

    def create(self, validated_data):
        post = self.context.get("post")
        request = self.context.get("request")
        try:
            validated_data["liked_by"] = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            raise serializers.ValidationError({"author": "Profile not found."})

        validated_data["post"] = post
        return super().create(validated_data)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["liked_by"] = instance.liked_by.user.username
        rep.pop("post")

        return rep

    def update(self, instance, validated_data):
        if "reaction" in validated_data:
            instance.reaction = validated_data["reaction"]
        instance.save()
        return instance
