from rest_framework import serializers
from posts.models import Post
from accounts.models import Profile
from rest_framework.reverse import reverse


class PostSerializer(serializers.ModelSerializer):

    

    class Meta:
        model = Post
        fields = ["id", "content", "image", "allowed_comment", "status",]
        read_only_fields = ["author"]




    def create(self, validated_data):
        request = self.context.get("request")
        try:
            validated_data["author"] = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            raise serializers.ValidationError({"author": "Profile not found."})
        return super().create(validated_data)
