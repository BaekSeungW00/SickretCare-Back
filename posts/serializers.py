from rest_framework import serializers
from posts.models import Post, Category, Comment, Commodity, Like
from users.serializers import UserSerializer

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['name']

class CommoditySerializer(serializers.ModelSerializer):
    category = CategorySerializer(required=False)

    class Meta:
        model = Commodity
        fields = ['id', 'link', 'price', 'category']


class PostSerializer(serializers.ModelSerializer):
    comments_num = serializers.SerializerMethodField()
    likes_num = serializers.SerializerMethodField()

    author = UserSerializer(required=False)
    category = CategorySerializer(required=False)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'created_at', 'comments_num', 'likes_num', 'author', 'category']

    # 게시물의 댓글 개수
    def get_comments_num(self, obj):
        return Comment.objects.filter(post=obj).count()
    
    # 게시물의 좋아요 개수
    def get_likes_num(self, obj):
        return Like.objects.filter(post=obj).count()

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(required=False)

    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_at', 'author', 'post']

class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    post = PostSerializer(required=False)

    class Meta:
        model = Like
        fields = '__all__'