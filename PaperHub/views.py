from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated 
from django.contrib.auth.models import User
from .models import PaperHubUser,Moderator,Admin
from .serializers import UserSignupSerializer
from .serializers import PaperHubUserSerializer,ModeratorSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
from django.shortcuts import get_object_or_404
from elasticsearchApp.models import Article

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
        
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            },
            'access_token': access_token,
            'refresh_token': refresh_token,
        }, status=status.HTTP_201_CREATED)
    else:
        return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_favorite(request, user_id, article_id):
    user_profile = get_object_or_404(User, pk=user_id)
    paperhub_user = PaperHubUser.objects.get(user=user_profile)
    article = get_object_or_404(Article, pk=article_id)

    if article not in paperhub_user.favorite_articles.all():
        paperhub_user.favorite_articles.add(article)
        return Response({'detail': 'Article added to favorites.'}, status=201)  # 201 Created
    else:
        user_profile.favorite_articles.remove(article)
        return Response({'detail': 'Article removed from favorites.'}, status=200)  # 200 OK
    

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'PUT':
        user.username = request.data.get('username', user.username)
        user.email = request.data.get('email', user.email)
        
        # Update the password using set_password method
        password = request.data.get('password')
        if password:
            user.set_password(password)

        user.save()
        return Response(status=200)

    return Response(status=200)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_moderator(request, user_id):
    try:
        moderator = Moderator.objects.get(id=user_id)
    except Moderator.DoesNotExist:
        return Response({'error': 'Moderator not found'}, status=status.HTTP_404_NOT_FOUND)

    data = request.data.get('user', {})
    serializer = ModeratorSerializer(instance=moderator, data=data, partial=True)

    if serializer.is_valid():
        # Update User information
        user = moderator.user
        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.set_password(data.get('password', user.password))  # Hash the password

        # Save the updated User
        user.save()

        # Save the updated PaperHubUser
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_moderators(request):
    try:
        # Get all moderators
        moderators = Moderator.objects.all()

        # Serialize the moderators with user details
        moderators_data = []
        for moderator in moderators:
            user_data = {
                'id': moderator.user.id,
                'username': moderator.user.username,
                'email': moderator.user.email,
                # Add other user fields as needed
            }
            moderator_data = {
                'id': moderator.id,
                'role': moderator.role,
                'user': user_data,
            }
            moderators_data.append(moderator_data)

        return Response(moderators_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_moderator(request):
    # Get user data from the request, adjust this based on your requirements
    username = request.data.get('modName')
    email = request.data.get('email')
    password = request.data.get('password')

    # Create a new user
    user = User.objects.create(username=username, email=email)
    user.set_password(password)
    user.is_staff = True
    user.save()

    # Check if the user is already a moderator
    if Moderator.objects.filter(user=user).exists():
        return Response({"detail": "User is already a moderator"}, status=status.HTTP_400_BAD_REQUEST)

    moderator = Moderator.objects.create(user=user, role='moderator')

    return Response({"detail": "Moderator added successfully"}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_moderator(request, moderator_id):
    try:
        moderator = Moderator.objects.get(id=moderator_id)
        user = moderator.user
        if not Moderator.objects.filter(user=user).exists():
            return Response({"detail": "User is not a moderator"}, status=status.HTTP_400_BAD_REQUEST)
        moderator.delete()
        user.delete()

        return Response({"detail": "Moderator deleted successfully"}, status=status.HTTP_200_OK)

    except Moderator.DoesNotExist:
        return Response({"detail": "Moderator not found"}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_article(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    if article.approved == True:
        return Response({"detail": "Article is already approved."}, status=400)

    article.approved = True
    article.save()

    return Response({"detail": "Article has been approved successfully."}, status=200)

