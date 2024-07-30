from django.shortcuts import render, get_list_or_404, get_object_or_404
from rest_framework.decorators import api_view
from posts.models import Post, Comment, Commodity, Category
from posts.serializers import PostSerializer, CommentSerializer, CommoditySerializer, CategorySerializer
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveDestroyAPIView, DestroyAPIView
from rest_framework.response import Response


# 게시물 전체 조회 및 카테고리 별 조회, 정렬 방식 선택 GET
class PostListAPIView(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    
    def get(self, request):
        # 카테고리 필터링
        category = request.GET.get('category', None)
        if category in ['치질', '변비', '과민성대장증후군']:
            post_queryset = Post.objects.filter(category=category)
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
    lookup_field = 'post_id'


# 게시물 생성 POST
class PostUploadAPIView(CreateAPIView):
    queryset = Post.objects.all()
    serailizer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# 내가 좋아요한 게시물 전체 조회, 카테고리별 조회, 정렬 방식 선택 GET
class LikedPostAPIView(ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.filter(like_users=self.request.user)

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


# 내 게시물 전체 조회, 카테고리별 조회, 정렬 방식 선택 GET
class MyPostAPIView(ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.filter(user=self.request.user)
    
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

    def perform_create(self, serializer):
        post_id = self.request.data.get('post_id')
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer.save(user=self.request.user, post=post)

# 댓글 삭제 DELETE
class CommentDeleteAPIView(DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    lookup_field = 'comment_id'
    

# 좋아요 생성 및 삭제 POST
@api_view(['POST'])
def post_like_api_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.like_users.filter(id=request.user.id).exists():
        post.like_users.remove(request.user)
        return Response({"공감을 취소했습니다."}, status=status.HTTP_204_NO_CONTENT)
    else:
        post.like_users.add(request.user)
        return Response({"공감을 눌렀습니다."}, status=status.HTTP_201_CREATED)


# 상품 전체 조회, 카테고리 별 조회 GET
class CommoditySearchAPIView(ListAPIView):
    queryset = Commodity.objects.all()
    serializer_class = CommoditySerializer
    
    def get(self, request):
        # 카테고리 필터링
        category = request.GET.get('category', None)
        if category in ['치질', '변비', '과민성대장증후군']:
            post_queryset = Commodity.objects.filter(category=category)
        
        serializer = self.get_serializer(post_queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 상품 등록 POST
class CommodityUploadAPIView(CreateAPIView):
    queryset = Commodity.objects.all()
    serializer_class = CommoditySerializer
