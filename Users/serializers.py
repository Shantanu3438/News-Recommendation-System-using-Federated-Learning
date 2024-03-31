from rest_framework import serializers
from django.contrib.auth.models import User
from Users.models import articles

class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = User 
        fields = ['id', 'username']

class ArticleSerializer(serializers.ModelSerializer):
    class Meta():
        model = articles
        fields = ['id', 'source', 'author', 'title', 'description', 'url', 'image_url', 'publish_date', 'content', 'category', 'feature_vector']