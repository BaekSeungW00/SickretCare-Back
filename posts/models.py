from django.db import models
from config import settings


class Category(models.Model):
    name = models.CharField(max_length=15)
    
class Commodity(models.Model):
    title = models.CharField(max_length=30, null=True)
    link  = models.CharField(max_length=300)
    price = models.IntegerField(null=True)
    stars = models.CharField(max_length=5, null=True)
    image_link = models.CharField(max_length=500, null=True)
    category = models.ForeignKey(Category, null=True, on_delete=models.CASCADE, related_name='commodities')
    
class Post(models.Model):
    title = models.CharField(max_length=30)
    content = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts')
    
class Comment(models.Model):
    content = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')

class Like(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)