from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import *
from django.conf import settings


class UserSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField('get_image')

    def get_image(self, user):
        return settings.GLOBAL_HOST + user.profile.image.url

    class Meta:
        model = get_user_model()
        ref_name = 'comment.user'
        fields = ['id', 'username', 'email', 'image']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ReplySerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Comment
        fields = ['id', 'text', 'create_at', 'user']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id']


class VideoTrainingSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoTraining
        fields = '__all__'


class CommentDetailSerializer(serializers.ModelSerializer):
    replies = ReplySerializer(many=True)
    user = UserSerializer()

    class Meta:
        model = Comment
        ref_name = 'comment.user'
        fields = ['id', 'text', 'create_at', 'user', 'replies']


class CreateReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields = ['comment', 'text', 'user']


class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['text', 'video', 'user']


class VideoSerializer(serializers.ModelSerializer):
    views = serializers.SerializerMethodField('get_views_count')
    favorites = serializers.SerializerMethodField('get_favorites_count')
    comments = serializers.SerializerMethodField('get_comments_count')
    is_favorite = serializers.SerializerMethodField('has_user_favorite')

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

    class Meta:
        model = Video
        fields = ['id', 'title', 'text', 'image', 'category', 'views',
                  'favorites', 'comments', 'is_favorite', 'get_status_display']


class VideoDetailSerializer(serializers.ModelSerializer):
    views = serializers.SerializerMethodField('get_views_count')
    favorites = serializers.SerializerMethodField('get_favorites_count')
    comments = serializers.SerializerMethodField('get_comments_count')
    owner = UserSerializer()
    is_favorite = serializers.SerializerMethodField('has_user_favorite')
    last_comment = serializers.SerializerMethodField('get_last_comment_text')

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

    def get_last_comment_text(self, video):
        if video.comments.all().last() is not None:
            return {
                'text': str(video.comments.all().last().text),
                'user': str(video.comments.all().last().user)
            }
        else:
            return None

    class Meta:
        model = Video
        fields = ['id', 'title', 'text', 'phone_1', 'phone_2', 'phone_3', 'instagram', 'facebook', 'web_site', 'video',
                  'create_at',
                  'owner', 'views', 'favorites', 'comments', 'is_favorite', 'last_comment']


class ViewsDetailVideoSerializer(serializers.ModelSerializer):
    views = UserSerializer(many=True)

    class Meta:
        model = Video
        fields = ['views']


class CommentsDetailVideoSerializer(serializers.ModelSerializer):
    comments = CommentDetailSerializer(many=True)

    class Meta:
        model = Video
        fields = ['comments']


class VideoUpdateDetailSerializer(serializers.ModelSerializer):
    video_id = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=True)
    view = serializers.BooleanField(default=False)
    favorite = serializers.BooleanField(default=False)

    class Meta:
        model = Video
        fields = ['video_id', 'user_id', 'view', 'favorite']


class UpVideoInSevenDaySerializer(serializers.ModelSerializer):
    video_id = serializers.IntegerField(required=True)
    owner_id = serializers.IntegerField(required=True)

    class Meta:
        model = Video
        fields = ['video_id', 'owner_id']


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'


class BannerSerializer(serializers.ModelSerializer):
    views = UserSerializer(many=True)

    class Meta:
        model = Banner
        fields = ['id', 'video', 'image', 'block', 'views']


class CreateRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ['address', 'phone', 'sum', 'promo_code', 'category']


class CreateViewHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ['user', 'bonus', 'video', 'create_at']


class CreateViewBannerHistorySerializer(serializers.ModelSerializer):
    banner_id = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=True)

    class Meta:
        model = Request
        fields = ['banner_id', 'user_id']
