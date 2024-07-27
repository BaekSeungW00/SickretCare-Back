from rest_framework import serializers
from posts.models import Post, Category, Comment, Commodity
from users.serializers import UserSerializer

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['name']

class CommoditySerializer(serializers.ModelSerializer):

    class Meta:
        model = Commodity
        fields = ['link', 'price']


class PostSerializer(serializers.ModelSerializer):
    comments_num = serializers.SerializerMethodField()
    author = UserSerializer(required=False)
    category = CategorySerializer(required=False)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'created_at', 'comments_num', 'author', 'category']

    # 게시물의 댓글 개수
    def get_comments_num(self, obj):
        return Comment.objects.filter(post=obj).count()

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(required=False)
    post = PostSerializer(required=False)

    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_at', 'author']