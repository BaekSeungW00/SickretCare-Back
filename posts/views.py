from django.shortcuts import render, get_list_or_404, get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from posts.models import Post, Comment, Commodity, Category, Like
from posts.serializers import PostSerializer, CommentSerializer, CommoditySerializer, CategorySerializer, LikeSerializer
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveDestroyAPIView, DestroyAPIView
from rest_framework.response import Response
from posts.permissions import IsGet, IsOwner
from rest_framework.permissions import AllowAny, IsAuthenticated


# 게시물 전체 조회 및 카테고리 별 조회, 정렬 방식 선택 GET
class PostListAPIView(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [AllowAny]
    
    def get(self, request):
        # 카테고리 필터링
        category = request.GET.get('category', None)
        if category in ['치질', '변비', '과민성대장증후군']:
            post_queryset = Post.objects.filter(category__name=category)
        else:
            post_queryset = Post.objects.all()

        # 정렬 기준 설정
        order_by = request.GET.get('order_by', 'created_at')
        if order_by == '좋아요순':
            post_queryset = post_queryset.order_by('-likes')
        else:
            post_queryset = post_queryset.order_by('-created_at')
        
        serializer = self.get_serializer(post_queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

# 게시물 단일 조회(id) GET, 게시물 삭제 DELETE
class PostRetrieveDeleteAPIView(RetrieveDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsGet | IsOwner]
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, id=kwargs.get('id'))
        serializer = self.get_serializer(instance)
        comments = Comment.objects.filter(post=instance)
        comments_serializer = CommentSerializer(comments, many=True)
        data = {
            'post': serializer.data,
            'comments': comments_serializer.data
        }
        return Response(data)

# 게시물 생성 POST
class PostUploadAPIView(CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request):
        category_name = request.data.get("category")
        title = request.data.get('title')
        content = request.data.get('content')
        category = Category.objects.get(name=category_name)
        post = Post.objects.create(title=title, content=content, category=category, author=request.user)
        serializer = PostSerializer(post)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


# 내가 좋아요한 게시물 전체 조회, 카테고리별 조회, 정렬 방식 선택 GET
class LikedPostAPIView(ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Like.objects.filter(user=self.request.user)

    def get(self, request):
        like_queryset = self.get_queryset().order_by('-created_at')
        post_queryset = []

        for like in like_queryset:
            post_queryset.append(like.post)

        # 카테고리 필터링
        category_name = request.GET.get('category', None)
        if category_name in ['치질', '변비', '과민성대장증후군']:
            category = Category.objects.get(name=category_name)
            post_queryset = post_queryset.filter(category=category)

        serializer = self.get_serializer(post_queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 내 게시물 전체 조회, 카테고리별 조회, 정렬 방식 선택 GET
class MyPostAPIView(ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)
    
    def get(self, request):
        post_queryset = self.get_queryset()

        # 카테고리 필터링
        category = request.GET.get('category', None)
        if category in ['치질', '변비', '과민성대장증후군']:
            post_queryset = post_queryset.filter(category=category)

        # 정렬 기준 설정
        order_by = request.GET.get('order_by', 'created_at')
        if order_by == '좋아요순':
            post_queryset = post_queryset.order_by('-likes')
        else:
            post_queryset = post_queryset.order_by('-created_at')

        serializer = self.get_serializer(post_queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# 댓글 생성 POST
class CommentUploadAPIView(CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, post_id, *args, **kwargs):
        # URL에서 post_id를 가져옴
        content = request.data.get('content')
        
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND)
        
        comment = Comment.objects.create(content=content, post=post, author=request.user)
        serializer = self.get_serializer(comment)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

# 댓글 삭제 DELETE
class CommentDeleteAPIView(DestroyAPIView):
    serializer_class = CommentSerializer
    lookup_field = 'comment_id'
    permission_classes = [IsOwner]

    def get_object(self):
        comment_id = self.kwargs.get('comment_id')
        return Comment.objects.get(id=comment_id)
    

# 좋아요 생성 및 삭제 POST
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_like_api_view(request, post_id):

    post = get_object_or_404(Post, id=post_id)

    like = Like.objects.filter(post=post, user=request.user).first()

    if like:
        # 좋아요가 이미 있다면 기존 좋아요 삭제
        like.delete()
        return Response({"공감을 취소했습니다."}, status=status.HTTP_204_NO_CONTENT)
    else:
        # 좋아요를 누르지 않았다면 새로운 좋아요를 생성
        Like.objects.create(post=post, user=request.user)
        return Response({"공감을 눌렀습니다."}, status=status.HTTP_201_CREATED)


# 상품 전체 조회, 카테고리 별 조회 GET
class CommoditySearchAPIView(ListAPIView):
    queryset = Commodity.objects.all()
    serializer_class = CommoditySerializer
    permission_classes = [AllowAny]
    
    def get(self, request):
        commodity_queryset = self.get_queryset()
        # 카테고리 필터링
        category_name = request.GET.get('category', None)
        if category_name in ['치질', '변비', '과민성대장증후군']:
            category = Category.objects.get(name=category_name)
            commodity_queryset = Commodity.objects.filter(category=category)
        
        serializer = self.get_serializer(commodity_queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



