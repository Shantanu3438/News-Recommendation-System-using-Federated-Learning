from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer, ArticleSerializer
from RecommendationModel.model import set_global_model, extract_global_weight, get_recommendation
import json
from Users.models import articles
import ast
import numpy as np

@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.set_password(request.data['password'])  # Set password before saving
        user.save()
        refresh = RefreshToken.for_user(user)  # Generate JWT token
        return Response({'refresh': str(refresh), 'access': str(refresh.access_token), 'user': serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user is None:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)  # Generate JWT token
    user_data = {
        'user_id': user.id,
        'username': user.username,
        'email': user.email,  # You can include any additional user data you want to return
    }
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': user_data  # Include user data in the response
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
def update_global_model(request):
    local_model_weights = request.data
    final_local_weights = []

    for sub_array in local_model_weights:
        sub_array_list = list(sub_array.values())
        if len(sub_array_list) == 2704:
            final_sub_array = [sub_array_list[i * 52: (i + 1) * 52] for i in range(52)]
            final_local_weights.append(final_sub_array)

        elif len(sub_array_list) == 1664:
            final_sub_array = [sub_array_list[i * 32: (i + 1) * 32] for i in range(52)]
            final_local_weights.append(final_sub_array)
        
        else:
            final_local_weights.append(sub_array_list)

    set_global_model(final_local_weights)
    return Response({'Message': 'Global model updated successfully!'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_global_weight(request):
    global_weight = extract_global_weight()
    return Response(global_weight, status=status.HTTP_200_OK)

@api_view(['POST'])
def get_articles(request):
    user_id = int(request.data.get('user_id'))
    all_articles = articles.objects.all().order_by('-publish_date')[:200]
    all_articles_feature_vector = [ast.literal_eval(article.feature_vector)[0] for article in all_articles]
    recommended_articles = get_recommendation(user_id, all_articles_feature_vector)
    all_articles_sorted = [all_articles[int(index)] for index in recommended_articles]
    top_headline_count = 0
    sports_count = 0
    technology_count = 0
    business_count = 0
    science_count = 0
    selected_articles = all_articles_sorted[:10]
    for article in all_articles_sorted[10:]:
        if top_headline_count != 10 and article.category == 'Top Headlines':
            selected_articles.append(article)
            top_headline_count += 1
        
        if sports_count != 10 and article.category == 'Sports':
            selected_articles.append(article)
            sports_count += 1

        if technology_count != 10 and article.category == 'Technology':
            selected_articles.append(article)
            technology_count += 1

        if business_count != 10 and article.category == 'Business':
            selected_articles.append(article)
            business_count += 1

        if science_count != 10 and article.category == 'Science':
            selected_articles.append(article)
            science_count += 1
    selected_articles = ArticleSerializer(selected_articles, many=True)
    return Response(selected_articles.data, status=status.HTTP_200_OK)