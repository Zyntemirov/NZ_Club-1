from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from video.serializers import UserSerializer, RecursiveSerializer, FilterReviewSerializer
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
        model = ViewStories
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
    user = UserSerializer()
    children = RecursiveSerializer(many=True)

    class Meta:
        list_serializer_class = FilterReviewSerializer
        model = SeasonalComment
        fields = ['id', 'user', 'text', 'create_at', 'children']


class SeasonalCommentsDetailApartmentSerializer(serializers.ModelSerializer):
    comments = SeasonalCommentDetailSerializer(many=True)

    class Meta:
        model = SeasonalApartment
        fields = ['comments']


class ApartmentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApartmentImage
        fields = '__all__'


class SeasonalApartmentSerializer(serializers.ModelSerializer):
    images = ApartmentImageSerializer(many=True)
    views = serializers.SerializerMethodField('get_views_count')
    favorites = serializers.SerializerMethodField('get_favorites_count')
    comments = serializers.SerializerMethodField('get_comments_count')
    is_favorite = serializers.SerializerMethodField('has_user_favorite')
    is_liked = serializers.SerializerMethodField('has_user_likes')
    likes = serializers.SerializerMethodField('get_likes_count')

    def has_user_favorite(self, apartment):
        if self.context["request"].user in apartment.favorites.all():
            return True
        else:
            return False

    def get_views_count(self, apartment):
        return apartment.views.count()

    def get_favorites_count(self, apartment):
        return apartment.favorites.count()

    def get_comments_count(self, apartment):
        return apartment.comments.count()

    def get_likes_count(self, apartment):
        return apartment.likes.count()

    def has_user_likes(self, apartment):
        if self.context["request"].user in apartment.likes.all():
            return True
        return False

    class Meta:
        model = SeasonalApartment
        fields = ['id', 'name', 'description', 'cover_image', 'video_link', 'category', 'views',
                  'favorites', 'comments', 'is_favorite', 'get_type_display',
                  'is_liked', 'likes', 'images']


class SeasonalApartmentDetailSerializer(serializers.ModelSerializer):
    images = ApartmentImageSerializer(many=True)
    category = SeasonalCategorySerializer()
    views = serializers.SerializerMethodField('get_views_count')
    favorites = serializers.SerializerMethodField('get_favorites_count')
    comments_count = serializers.SerializerMethodField('get_comments_count')
    is_favorite = serializers.SerializerMethodField('has_user_favorite')
    last_comment = serializers.SerializerMethodField('get_last_comment_text')
    likes = serializers.SerializerMethodField('get_likes')
    is_liked = serializers.SerializerMethodField('has_user_like')
    comments = SeasonalCommentDetailSerializer(many=True)
    owner = UserSerializer()

    def has_user_favorite(self, apartment):
        if self.context["request"].user in apartment.favorites.all():
            return True
        else:
            return False

    def has_user_like(self, apartment):
        if self.context['request'].user in apartment.likes.all():
            return True
        return False

    def get_views_count(self, apartment):
        return apartment.views.count()

    def get_favorites_count(self, apartment):
        return apartment.favorites.count()

    def get_comments_count(self, apartment):
        return apartment.comments.count()

    def get_last_comment_text(self, apartment):
        if apartment.comments.all().last() is not None:
            return {
                'text': str(apartment.comments.all().last().text),
                'user': str(apartment.comments.all().last().user)
            }
        else:
            return None

    def get_likes(self, obj):
        return obj.likes.count()

    class Meta:
        model = SeasonalApartment
        fields = ['id', 'category', 'name', 'description', 'video_link', 'create_at',
                  'views', 'favorites', 'comments_count', 'is_favorite',
                  'last_comment', 'likes', 'is_liked', 'comments', 'owner', 'images']
        depth = True


class SeasonalViewsDetailApartmentSerializer(serializers.ModelSerializer):
    views = UserSerializer(many=True)

    class Meta:
        model = SeasonalApartment
        fields = ['views']


class SeasonalCreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeasonalComment
        fields = ['text', 'apartment', 'parent']

    def create(self, validated_data):
        user = self.context['request'].user
        comment = SeasonalComment.objects.create(user=user, **validated_data)
        return comment


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'


class ApartmentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeasonalApartment
        fields = ('name', 'description', 'address', 'phone', 'video_by_user', 'category', 'cover_image',)


class BookingRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingRequest
        exclude = ('user',)


class BookingHistorySerializer(serializers.ModelSerializer):
    user = UserSerializer()
    room = RoomSerializer()

    class Meta:
        model = BookingRequest
        fields = '__all__'


class CreateViewApartmentHistorySerializer(serializers.ModelSerializer):
    apartment_id = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=True)

    class Meta:
        model = ViewHistory
        fields = ['apartment_id', 'user_id']
