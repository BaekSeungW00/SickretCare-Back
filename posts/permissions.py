from rest_framework import permissions

class IsGet(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method == 'GET'
        
class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user