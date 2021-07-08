from rest_framework import status
from rest_framework.generics import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from seasonal.serializers import *
from django.db.models import Q
from datetime import timedelta


class StoriesView(ListAPIView):
    serializer_class = StoriesSerializer
    queryset = Stories.objects.all()


class UserWatchedStoriesView(UpdateAPIView):
    serializer_class = CreateViewStoriesHistorySerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        stories = Stories.objects.get(id=request.data['stories_id'])
        user = get_user_model().objects.get(id=request.data['user_id'])
        if stories and user:
            if user not in stories.views.all():
                ViewStories.objects.create(
                    user=user,
                    stories=stories,
                )
                stories.views.add(user)
                stories.save()

            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class StoriesDetailView(ListAPIView):
    serializer_class = StoriesSerializer

    def get_queryset(self):
        queryset = Stories.objects.filter(id=self.kwargs['stories_id'])
        return queryset


class StoriesByBlockNumberView(ListAPIView):
    serializer_class = StoriesSerializer

    def get_queryset(self):
        queryset = Stories.objects.filter(block=self.kwargs['number'])
        return queryset


class CreateLikeStoriesView(CreateAPIView):
    serializer_class = CreateLikeStoriesSerializer
    permission_classes = [IsAuthenticated]


class DeleteLikeStoriesView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        like_stories = LikeStories.objects.filter(stories_id=kwargs['id'], user=user)
        like_stories.delete()
        return Response(status.HTTP_204_NO_CONTENT)


class CreateStoriesComplaintView(CreateAPIView):
    serializer_class = CreateStoriesComplaintSerializer
    permission_classes = [IsAuthenticated]


class CategoriesView(ListAPIView):
    serializer_class = SeasonalCategorySerializer
    queryset = Category.objects.all()


class VideoDetailView(RetrieveAPIView):
    serializer_class = SeasonalVideoDetailSerializer

    def get(self, request, *args, **kwargs):
        queryset = SeasonalVideo.objects.all()
        video_detail = get_object_or_404(queryset, id=kwargs['id'])
        serializer = SeasonalVideoDetailSerializer(video_detail, context={'request': request})
        return Response(serializer.data)


class ViewsDetailVideoView(ListAPIView):
    serializer_class = SeasonalViewsDetailVideoSerializer

    def get(self, request, *args, **kwargs):
        queryset = SeasonalVideo.objects.all()
        views = get_object_or_404(queryset, id=self.kwargs['id'])
        serializer = SeasonalViewsDetailVideoSerializer(views, context={'request': request})
        return Response(serializer.data['views'])


class CreateVideoLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        video = SeasonalVideo.objects.get(id=request.data['id'])
        user = get_user_model().objects.get(id=request.user.id)
        if user not in video.likes.all():
            video.likes.add(user)
            video.save()
            return Response({'message': 'This user liked'}, status.HTTP_201_CREATED)
        return Response({'message': 'This user already liked'}, status.HTTP_204_NO_CONTENT)


class DeleteVideoLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        video = SeasonalVideo.objects.get(id=kwargs['id'])
        video.likes.remove(user)
        return Response(status.HTTP_204_NO_CONTENT)


class CommentsDetailVideoView(ListAPIView):
    serializer_class = SeasonalCommentsDetailVideoSerializer
    queryset = SeasonalComment

    def get(self, request, *args, **kwargs):
        queryset = SeasonalVideo.objects.all()
        comments = get_object_or_404(queryset, id=self.kwargs['id'])
        serializer = SeasonalCommentsDetailVideoSerializer(comments, context={'request': request})
        return Response(serializer.data['comments'])


class VideoSearchView(ListAPIView):
    serializer_class = SeasonalVideoSerializer

    def get_queryset(self):
        queryset = SeasonalVideo.objects.filter(title__icontains=self.kwargs['search'], status='2')
        return queryset


class VideoByCategoryView(ListAPIView):
    serializer_class = SeasonalVideoSerializer

    def get_queryset(self):
        queryset = SeasonalVideo.objects.filter(
            category=self.kwargs['category_id']).order_by('create_at').reverse()
        return queryset


class VideoTop10View(ListAPIView):
    serializer_class = SeasonalVideoSerializer

    def get_queryset(self):
        user = get_user_model().objects.get(id=self.kwargs['user_id'])
        if user:
            queryset = SeasonalVideo.objects.filter(
                is_top=True).exclude(views__in=[user]).order_by('create_at')[:10]
            return queryset
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class VideosView(ListAPIView):
    serializer_class = SeasonalVideoSerializer

    def get_queryset(self):
        user = self.request.user
        if user:
            queryset = SeasonalVideo.objects.filter(
                Q(is_top=False) | Q(views__in=[user])).distinct()[::-1]
            return queryset
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class VideoDonateView(ListAPIView):
    serializer_class = SeasonalVideoSerializer

    def get_queryset(self):
        queryset = SeasonalVideo.objects.filter(status='2', type='3', is_active=True)
        return queryset


class UserFullyWatchedView(UpdateAPIView):
    serializer_class = SeasonalVideoUpdateDetailSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        video = SeasonalVideo.objects.get(id=request.data['video_id'])
        user = get_user_model().objects.get(id=request.data['user_id'])
        if video and user:
            if request.data['view']:
                bonus = 0
                for item in video.tariffs.all():
                    if item.views > len(video.views.all()):
                        bonus = item.price
                        break

                if user not in video.watched_videos.all():
                    ViewHistory.objects.create(
                        user=user,
                        bonus=bonus,
                        video=video,
                    )
                    profile = user.profile
                    profile.balance = profile.balance + bonus
                    profile.view_count = profile.view_count + 1
                    profile.save()

                if bonus == 0:
                    video.is_top = False
                video.watched_videos.add(user)
                video.save()

            if request.data['favorite']:
                video.favorites.add(user)
                video.save()

            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserNotFullyWatchedView(UpdateAPIView):
    serializer_class = SeasonalVideoUpdateDetailSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        video = SeasonalVideo.objects.get(id=request.data['video_id'])
        user = get_user_model().objects.get(id=request.data['user_id'])
        if video and user:
            if request.data['view']:
                video.views.add(user)
                video.save()

            if request.data['favorite']:
                video.favorites.add(user)
                video.save()

            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UpVideoInSevenDayView(UpdateAPIView):
    serializer_class = SeasonalUpVideoInSevenDaySerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        video = SeasonalVideo.objects.get(id=request.data['video_id'],
                                          owner=request.data['owner_id'])
        user = get_user_model().objects.get(id=request.data['owner_id'])
        if user and video and (video.create_at.date() + timedelta(
                days=2)) <= datetime.now().date():
            video.create_at = datetime.now()
            video.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class CreateCommentView(CreateAPIView):
    serializer_class = SeasonalCreateCommentSerializer
    permission_classes = [IsAuthenticated]


class CreateRequestView(CreateAPIView):
    serializer_class = SeasonalCreateRequestSerializer
    permission_classes = [IsAuthenticated]


class VideoFilterView(ListAPIView):
    serializer_class = SeasonalVideoSerializer

    def get_queryset(self):
        type_video = self.request.query_params.get('type_video', '')
        region = self.request.query_params.get('region')
        queryset = SeasonalVideo.objects.filter(status='2')

        if type_video == 'donate':
            queryset = queryset.filter(type='3')
        elif type_video == 'vip':
            queryset = queryset.filter(type='2')
        if region:
            queryset = queryset.filter(owner__profile__region=region)
        return queryset
