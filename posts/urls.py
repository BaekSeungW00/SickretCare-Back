from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.PostListAPIView.as_view(), name='post-list'),
    path('get/<int:id>/', views.PostRetrieveDeleteAPIView.as_view(), name='post-getdelete'),
    path('upload/', views.PostUploadAPIView.as_view(), name='post-upload'),
    path('liked/', views.LikedPostAPIView.as_view(), name='liked-post'),
    path('mypost/', views.MyPostAPIView.as_view(), name='my-post'),
    path('comment/upload/<int:post_id>/', views.CommentUploadAPIView.as_view(), name='comment-upload'),
    path('comment/delete/<int:comment_id>/', views.CommentDeleteAPIView.as_view(), name='comment-delete'),
    path('like/<int:post_id>/', views.post_like_api_view, name='post-like'),
    path('commodity/list/', views.CommoditySearchAPIView.as_view(), name='commodity-list'),
    path('commodity/upload/', views.CommodityUploadAPIView.as_view(), name='commodity-upload'),
]