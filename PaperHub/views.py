from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from .models import PaperHubUser
from .serializers import UserSignupSerializer
from django.contrib.auth import login

@api_view(['POST'])
def signup(request):
    serializer = UserSignupSerializer(data=request.data)
    
    if serializer.is_valid():
        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        
        # Create a PaperHubUser instance for the registered user
        PaperHubUser.objects.create(user=user, role='user')
        login(request, user)
        
        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
    else:
        return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)
    

