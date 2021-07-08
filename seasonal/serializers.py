from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from video.serializers import UserSerializer
from seasonal.models import *


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


class SeasonalCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class SeasonalCommentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeasonalComment
        fields = '__all__'


class SeasonalCommentsDetailVideoSerializer(serializers.ModelSerializer):
    comments = SeasonalCommentDetailSerializer(many=True)

    class Meta:
        model = SeasonalVideo
        fields = ['comments']


class SeasonalVideoSerializer(serializers.ModelSerializer):
    views = serializers.SerializerMethodField('get_views_count')
    favorites = serializers.SerializerMethodField('get_favorites_count')
    comments = serializers.SerializerMethodField('get_comments_count')
    is_favorite = serializers.SerializerMethodField('has_user_favorite')
    is_liked = serializers.SerializerMethodField('has_user_likes')
    likes = serializers.SerializerMethodField('get_likes_count')

    def has_user_favorite(self, video):
        if self.context["request"].user in video.favorites.all():
            return True
        else:
            return False

    def get_views_count(self, video):
        return video.views.count()

    def get_favorites_count(self, video):
        return video.favorites.count()

    def get_comments_count(self, video):
        return video.comments.count()

    def get_likes_count(self, video):
        return video.likes.count()

    def has_user_likes(self, video):
        if self.context["request"].user in video.likes.all():
            return True
        return False

    class Meta:
        model = SeasonalVideo
        fields = ['id', 'title', 'text', 'image', 'category', 'views',
                  'favorites', 'comments', 'is_favorite', 'get_type_display',
                  'is_liked', 'likes']


class SeasonalVideoDetailSerializer(serializers.ModelSerializer):
    category = SeasonalCategorySerializer()
    views = serializers.SerializerMethodField('get_views_count')
    favorites = serializers.SerializerMethodField('get_favorites_count')
    comments_count = serializers.SerializerMethodField('get_comments_count')
    owner = UserSerializer()
    is_favorite = serializers.SerializerMethodField('has_user_favorite')
    last_comment = serializers.SerializerMethodField('get_last_comment_text')
    likes = serializers.SerializerMethodField('get_likes')
    is_liked = serializers.SerializerMethodField('has_user_like')
    comments = SeasonalCommentDetailSerializer(many=True)

    def has_user_favorite(self, video):
        if self.context["request"].user in video.favorites.all():
            return True
        else:
            return False

    def has_user_like(self, video):
        if self.context['request'].user in video.likes.all():
            return True
        return False

    def get_views_count(self, video):
        return video.views.count()

    def get_favorites_count(self, video):
        return video.favorites.count()

    def get_comments_count(self, video):
        return video.comments.count()

    def get_last_comment_text(self, video):
        if video.comments.all().last() is not None:
            return {
                'text': str(video.comments.all().last().text),
                'user': str(video.comments.all().last().user)
            }
        else:
            return None

    def get_likes(self, obj):
        return obj.likes.count()

    class Meta:
        model = SeasonalVideo
        fields = ['id', 'category', 'title', 'text', 'video', 'create_at',
                  'owner', 'views', 'favorites', 'comments_count', 'is_favorite',
                  'last_comment', 'likes', 'is_liked', 'get_type_display', 'comments']
        depth = True


class SeasonalViewsDetailVideoSerializer(serializers.ModelSerializer):
    views = UserSerializer(many=True)

    class Meta:
        model = SeasonalVideo
        fields = ['views']


class SeasonalVideoUpdateDetailSerializer(serializers.ModelSerializer):
    video_id = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=True)
    view = serializers.BooleanField(default=False)
    favorite = serializers.BooleanField(default=False)

    class Meta:
        model = SeasonalVideo
        fields = ['video_id', 'user_id', 'view', 'favorite']


class SeasonalUpVideoInSevenDaySerializer(serializers.ModelSerializer):
    video_id = serializers.IntegerField(required=True)
    owner_id = serializers.IntegerField(required=True)

    class Meta:
        model = SeasonalVideo
        fields = ['video_id', 'owner_id']


class SeasonalCreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeasonalComment
        fields = ['text', 'video', 'parent']

    def create(self, validated_data):
        user = self.context['request'].user
        comment = SeasonalComment.objects.create(user=user, **validated_data)
        return comment


class SeasonalCreateRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ['address', 'phone', 'sum', 'promo_code', 'category']
