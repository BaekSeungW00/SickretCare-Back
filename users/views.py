import string
import random
import jwt
from config.settings import SECRET_KEY
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password, make_password
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from .models import *
from .serializers import *
from notifications.models import Timer

ACCESS_COOKIE_AGE = 15 * 60
REFRESH_COOKIE_AGE = 3 * 24 * 60 * 60

# 회원가입
class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def create(self, request):
        if request.data.get('password1') != request.data.get('password2'):
            return Response({'error': '두 비밀번호가 일치하지 않습니다. '}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=request.data.get('email')).exists():
            return Response({'error': '이메일이 중복됩니다. '}, status=status.HTTP_409_CONFLICT)
        if User.objects.filter(nickname=request.data.get('nickname')).exists():
            return Response({'error': '닉네임이 중복됩니다. '}, status=status.HTTP_409_CONFLICT)
        
        data = {
            'email': request.data.get('email'),
            'password': request.data.get('password1'),
            'username': request.data.get('username'),
            'nickname': request.data.get('nickname')
        }
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def perform_create(self, serializer):
        serializer.save()
        user = User.objects.get(id=serializer.data.get('id'))
        timer = Timer.objects.create(user=user)
        timer.save()

# 회원 정보 조회 및 수정, 회원 탈퇴
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def user_retrieve_update_destroy_api_view(request):
    user = request.user
    
    # 회원 정보 조회
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    # 회원 정보 수정
    elif request.method == 'PUT':
        nickname = request.data.get('nickname')
        fcm_token = request.data.get('fcm_token')
        password = request.data.get('password')
        new_password = request.data.get('new_password')
        
        # 비밀번호 변경
        if (password is not None) and (new_password is not None):
            if not check_password(password, user.password):
                return Response({'error': '비밀번호가 일치하지 않음. '}, status=status.HTTP_400_BAD_REQUEST)
            else:
                user.set_password(new_password)
        elif not((password is None) and (new_password is None)):
            return Response({'error': '현재 비밀번호와 새로운 비밀번호를 모두 입력하세요. '}, status=status.HTTP_400_BAD_REQUEST)
            
        
        # 닉네임 변경
        if nickname is not None:
            user.nickname = nickname
        
        if fcm_token is not None:
            user.fcm_token = fcm_token
            
        user.save()
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    # 회원 탈퇴
    elif request.method == 'DELETE':
        password1 = request.data.get('password1')
        password2 = request.data.get('password2')
        
        if (password1 is not None) and (password2 is not None):
            if password1 != password2:
                return Response({'error': '두 비밀번호가 일치하지 않습니다. '}, status=status.HTTP_400_BAD_REQUEST)
            if not check_password(password1, user.password):
                return Response({'error': '비밀번호가 틀렸습니다. '}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': '비밀번호를 모두 입력하세요. '}, status=status.HTTP_400_BAD_REQUEST)
        
        user.delete()
        return Response({'deleted': '회원 탈퇴 완료'}, status=status.HTTP_204_NO_CONTENT)
        
        
# 로그인
@api_view(['POST'])
def login_api_view(request): 
    email = request.data.get('email')
    password = request.data.get('password')
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': '해당 이메일의 유저가 존재하지 않습니다. '}, status=status.HTTP_404_NOT_FOUND)
    
    if not check_password(password, user.password):
        return Response({'error': '비밀번호가 맞지 않습니다. '}, status=status.HTTP_401_UNAUTHORIZED)
    
    refresh_token = RefreshToken.for_user(user)
    access_token = refresh_token.access_token
    serializer = UserSerializer(user)
    
    return Response(
        status=status.HTTP_200_OK,
        data={
            "refresh_token": str(refresh_token),
            "access_token": str(access_token), 
            "user": serializer.data,
        }
    )
    

# 리프레시
@api_view(['POST'])
def refresh_api_view(request):
    refresh_token = request.data.get('refresh_token')
    if not refresh_token:
        return Response({'error': 'Refresh token이 전달되지 않았습니다. '}, status=status.HTTP_401_UNAUTHORIZED)
    refresh = RefreshToken(refresh_token)
    
    try:
        user_id = get_user_id_from_refresh_token(str(refresh))
        user = User.objects.get(id=user_id)
    except jwt.ExpiredSignatureError:
        return Response({'error': '만료된 Refresh token 입니다. '}, status=status.HTTP_401_UNAUTHORIZED)
    except jwt.InvalidTokenError:
        return Response({'error': '잘못된 Refresh token 입니다. '}, status=status.HTTP_401_UNAUTHORIZED)
    except User.DoesNotExist:
        return Response({'error': '존재하지 않는 사용자의 Refresh token 입니다. '}, status=status.HTTP_401_UNAUTHORIZED)

    
    new_access_token = refresh.access_token
    return Response(
        status=status.HTTP_200_OK,
        data={
            "refresh_token": str(refresh_token),
            "access_token": str(new_access_token),
            "user": UserSerializer(user).data
        }
    )

# JWT 분석
def get_user_id_from_refresh_token(token):
    secret_key = SECRET_KEY
    algorithm = 'HS256'
    payload = jwt.decode(token, secret_key, algorithms=[algorithm])
    user_id = payload.get('user_id')
    return user_id   

# 로그아웃
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_api_view(request):
    response = Response({'detail': '로그아웃에 성공했습니다. '}, status=status.HTTP_200_OK)
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response

# 임시 비밀번호 발급
from config.settings import EMAIL_HOST_USER

@api_view(['POST'])
def reset_pw_api_view(request):
    email = request.data.get('email')
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': '해당 이메일로 가입된 계정이 없습니다. '}, status=status.HTTP_404_NOT_FOUND)

    characters = string.digits + string.ascii_lowercase
    code = ''.join(random.choices(characters, k=6))
    
    subject = "SickretCare 임시 비밀번호 알림"
    message = f'임시 비밀번호는 <{code}> 입니다. 로그인 후 마이페이지에서 비밀번호를 수정해주세요. '
    from_email = EMAIL_HOST_USER
    recipient_list = [email]

    try:
        send_mail(
            subject=subject, message=message, from_email=from_email, 
            recipient_list=recipient_list, fail_silently=False
            )
    except Exception as e: # 서버 오류 시 예외 처리
        return Response({'error': '이메일 전송 중 오류가 발생했습니다. '}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    user.set_password(code)
    user.save()
    
    return Response({'detail': '임시 비밀번호로 변경되었습니다. '}, status=status.HTTP_200_OK)