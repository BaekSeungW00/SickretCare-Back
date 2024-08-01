from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.response import Response

class CookieBasedJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        raw_token = request.COOKIES.get('access_token')
        if raw_token is None:
            return None
        
        try:
            validated_token = self.get_validated_token(raw_token)
        except (InvalidToken, TokenError) as e:
            # 토큰 오류 발생 시 쿠키에서 액세스 토큰 삭제
            response = Response(request)
            response.delete_cookie('access_token')
            return None

        return self.get_user(validated_token), validated_token
