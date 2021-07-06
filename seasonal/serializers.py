from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from video.serializers import UserSerializer
from .models import *


class StoriesSerializer(serializers.ModelSerializer):
    views = UserSerializer(many=True)
    likes = serializers.SerializerMethodField('get_likes')
    is_liked = serializers.SerializerMethodField('has_user_like')

    class Meta:
        model = Stories
        fields = ['id', 'video', 'url', 'image', 'views', 'is_liked',
                  'likes', 'created']

    def get_likes(self, obj):
        return LikeStories.objects.filter(stories=obj).count()

    def has_user_like(self, video):
        if LikeStories.objects.filter(
                user=self.context['request'].user).exists():
            return True
        return False


class CreateViewStoriesHistorySerializer(serializers.ModelSerializer):
    stories_id = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=True)

    class Meta:
        model = Request
        fields = ['stories_id', 'user_id']


class CreateLikeStoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikeStories
        fields = ['id', 'user', 'stories']
        validators = [
            UniqueTogetherValidator(
                LikeStories.objects.all(),
                fields=['user', 'stories']
            )
        ]

    def create(self, validated_data):
        like_stories = LikeStories.objects.create(**validated_data)
        return like_stories


class CreateStoriesComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintStories
        fields = ['type', 'text']

    def create(self, validated_data):
        user = self.context['request'].user
        complaint_stories = ComplaintStories(user=user, **validated_data)
        return complaint_stories
