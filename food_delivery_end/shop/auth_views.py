from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class SimpleAuthView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        user_id = request.data.get('user_id')
        username = request.data.get('username')
        first_name = request.data.get('first_name', 'Пользователь')
        
        print(f"🔐 Авторизация: user_id={user_id}, username={username}, first_name={first_name}")
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'}, 
                status=400
            )
        
        try:
            user = User.objects.get(username=username or f'user_{user_id}')
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=username or f'user_{user_id}',
                first_name=first_name,
                email=f'user{user_id}@test.local'
            )
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name
            }
        })