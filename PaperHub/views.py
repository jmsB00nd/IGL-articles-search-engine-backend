from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated 
from django.contrib.auth.models import User
from .models import PaperHubUser,Moderator,Admin
from .serializers import UserSignupSerializer
from .serializers import PaperHubUserSerializer,ModeratorSerializer
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
        
        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
    else:
        return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_favorite(request, user_id, article_id):
    user_profile = get_object_or_404(PaperHubUser, pk=user_id)
    article = get_object_or_404(Article, pk=article_id)

    if article not in user_profile.favorite_articles.all():
        user_profile.favorite_articles.add(article)
        return Response({'detail': 'Article added to favorites.'}, status=201)  # 201 Created
    else:
        user_profile.favorite_articles.remove(article)
        return Response({'detail': 'Article removed from favorites.'}, status=200)  # 200 OK

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    try:
        # Retrieve the PaperHubUser instance
        paperhub_user = PaperHubUser.objects.get(id=user_id)
    except PaperHubUser.DoesNotExist:
        return Response({'error': 'PaperHubUser not found'}, status=status.HTTP_404_NOT_FOUND)

    # Retrieve the user data from the request
    data = request.data.get('user', {})

    # Update User information
    user = paperhub_user.user
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.password = data.get('password', user.password)  # You might want to handle password hashing here

    # Save the updated User
    user.save()

    # Update PaperHubUser information
    paperhub_user.role = data.get('role', paperhub_user.role)

    # Update favorite_articles if provided
    favorite_articles = data.get('favorite_articles')
    if favorite_articles is not None:
        paperhub_user.favorite_articles.set(favorite_articles)

    # Update saved_articles if provided
    saved_articles = data.get('saved_articles')
    if saved_articles is not None:
        paperhub_user.saved_articles.set(saved_articles)

    # Save the updated PaperHubUser
    paperhub_user.save()

    # Serialize and return the updated data
    serializer = PaperHubUserSerializer(paperhub_user)
    return Response(serializer.data, status=status.HTTP_200_OK)
    
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

    # Create a moderator instance and associate it with the user
    moderator = Moderator.objects.create(user=user, role='moderator')

    return Response({"detail": "Moderator added successfully"}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_moderator(request, moderator_id):
    try:
        # Find the moderator by ID
        moderator = Moderator.objects.get(id=moderator_id)

        # Get the associated user
        user = moderator.user

        # Check if the user is a moderator
        if not Moderator.objects.filter(user=user).exists():
            return Response({"detail": "User is not a moderator"}, status=status.HTTP_400_BAD_REQUEST)

        # Delete the moderator instance
        moderator.delete()

        # Optionally, you can also delete the associated user
        user.delete()

        return Response({"detail": "Moderator deleted successfully"}, status=status.HTTP_200_OK)

    except Moderator.DoesNotExist:
        return Response({"detail": "Moderator not found"}, status=status.HTTP_404_NOT_FOUND)