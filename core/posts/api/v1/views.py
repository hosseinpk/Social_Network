from rest_framework import generics, status
from accounts.models import Profile
from posts.models import Post, Comment, Like
from .serializers import PostSerializer, CommentSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .permissions import IsPostOwnser, CanCommentOnPost


class PostApiView(generics.GenericAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer

    def get_queryset(self):

        # profile = get_object_or_404(Profile, user=self.request.user)
        # queryset = Post.objects.filter(author=profile)
        queryset = Post.objects.all()
        return queryset

    def post(self, request, *args, **kwargs):

        serializer = PostSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):

        queryset = self.get_queryset().filter(status="published")
        serializer = PostSerializer(
            instance=queryset, many=True, context={request: "request"}
        )

        return Response(serializer.data)


class GetPostDetailsApiView(generics.GenericAPIView):

    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAuthenticated(), IsPostOwnser()]
        return super().get_permissions()

    def get_queryset(self):

        queryset = Post.objects.filter(status="published")
        return queryset

    def get_object(self):

        obj = get_object_or_404(self.get_queryset(), id=self.kwargs["id"])
        return obj

    def get(self, request, *args, **kwargs):

        obj = self.get_object()
        serializer = PostSerializer(
            instance=obj, context={"request": request, "id": obj.id}
        )
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.delete()
        return Response(
            {"detail": "Post deleted successfully."}, status=status.HTTP_204_NO_CONTENT
        )

    def put(self, request, *args, **kwargs):

        obj = self.get_object()
        serializer = self.serializer_class(
            instance=obj, data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):

        obj = self.get_object()
        serializer = self.serializer_class(
            instance=obj, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentApiView(generics.GenericAPIView):

    permission_classes = [IsAuthenticated, CanCommentOnPost]
    serializer_class = CommentSerializer

    def get_object(self):

        return Post.objects.get(id=self.kwargs["id"])

    def get_queryset(self):
        return Comment.objects.filter(post=self.get_object())

    def post(self, request, *args, **kwargs):

        post = self.get_object()
        serializer = CommentSerializer(
            data=request.data, context={"request": request, "post": post}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):

        quryset = self.get_queryset()
        serializer = CommentSerializer(
            instance=quryset, context={"request": request}, many=True
        )
        return Response(serializer.data)
