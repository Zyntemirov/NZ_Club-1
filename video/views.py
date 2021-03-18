from datetime import timedelta

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework import pagination

from .serializers import *
from video.models import *
from rest_framework.generics import *
from django.db.models import Q


class MyPagination(pagination.PageNumberPagination):
    page_size = 3


# list get API
class CategoriesView(viewsets.generics.ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all().order_by('id').reverse()


class VideoTrainingView(viewsets.generics.ListAPIView):
    serializer_class = VideoTrainingSerializer
    queryset = VideoTraining.objects.all().order_by('id').reverse()


class VideosView(viewsets.generics.ListAPIView):
    serializer_class = VideoSerializer

    # pagination_class = MyPagination

    def get_queryset(self):
        user = self.request.user
        if user:
            queryset = Video.objects.filter(Q(is_top=False) | Q(views__in=[user])).order_by(
                'create_at').reverse().distinct()
            return queryset
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class VideoDetailView(viewsets.generics.RetrieveAPIView):
    serializer_class = VideoDetailSerializer

    def get(self, request, *args, **kwargs):
        queryset = Video.objects.all()
        video_detail = get_object_or_404(queryset, id=kwargs['id'])
        serializer = VideoDetailSerializer(video_detail, context={'request': request})
        return Response(serializer.data)


class ViewsDetailVideoView(viewsets.generics.ListAPIView):
    serializer_class = ViewsDetailVideoSerializer

    def get(self, request, *args, **kwargs):
        queryset = Video.objects.all()
        views = get_object_or_404(queryset, id=self.kwargs['id'])
        serializer = ViewsDetailVideoSerializer(views, context={'request': request})
        return Response(serializer.data['views'])


class CommentsDetailVideoView(viewsets.generics.ListAPIView):
    serializer_class = CommentsDetailVideoSerializer
    queryset = Comment

    def get(self, request, *args, **kwargs):
        queryset = Video.objects.all()
        comments = get_object_or_404(queryset, id=self.kwargs['id'])
        serializer = CommentsDetailVideoSerializer(comments, context={'request': request})
        return Response(serializer.data['comments'])


class VideoTop10View(viewsets.generics.ListAPIView):
    serializer_class = VideoSerializer

    def get_queryset(self):
        user = get_user_model().objects.get(id=self.kwargs['user_id'])
        if user:
            queryset = Video.objects.filter(is_top=True).exclude(views__in=[user]).order_by('create_at')[:10]
            return queryset
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class VideoByCategoryView(viewsets.generics.ListAPIView):
    serializer_class = VideoSerializer

    def get_queryset(self):
        queryset = Video.objects.filter(category=self.kwargs['category_id']).order_by('create_at').reverse()
        return queryset


class VideoByOwnerView(viewsets.generics.ListAPIView):
    serializer_class = VideoSerializer

    def get_queryset(self):
        queryset = Video.objects.filter(owner=self.kwargs['owner_id'])
        return queryset


class VideoSearchView(viewsets.generics.ListAPIView):
    serializer_class = VideoSerializer

    def get_queryset(self):
        queryset = Video.objects.filter(title__icontains=self.kwargs['search'])
        return queryset


class VideoFilterView(ListAPIView):
    serializer_class = VideoSerializer

    def get_queryset(self):
        queryset = Video.objects.filter(owner__region=self.kwargs['region'])
        return queryset


class FaqSearchView(viewsets.generics.ListAPIView):
    serializer_class = FAQSerializer

    def get_queryset(self):
        queryset = FAQ.objects.filter(question__icontains=self.kwargs['search'])
        return queryset


class FAQView(viewsets.generics.ListAPIView):
    serializer_class = FAQSerializer
    queryset = FAQ.objects.all().order_by('id').reverse()


class UserWatchedBannerView(viewsets.generics.UpdateAPIView):
    serializer_class = CreateViewBannerHistorySerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        banner = Banner.objects.get(id=request.data['banner_id'])
        user = get_user_model().objects.get(id=request.data['user_id'])
        if banner and user:
            if user not in banner.views.all():
                ViewBanner.objects.create(
                    user=user,
                    banner=banner,
                )
                banner.views.add(user)
                banner.save()

            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class BannerView(viewsets.generics.ListAPIView):
    serializer_class = BannerSerializer
    queryset = Banner.objects.all().order_by('id').reverse()


class BannerDetailView(viewsets.generics.ListAPIView):
    serializer_class = BannerSerializer

    def get_queryset(self):
        queryset = Banner.objects.filter(id=self.kwargs['banner_id'])
        return queryset


class BannerByBlockNumberView(viewsets.generics.ListAPIView):
    serializer_class = BannerSerializer

    def get_queryset(self):
        queryset = Banner.objects.filter(block=self.kwargs['number'])
        return queryset


# update put, patch API
class UserFullyWatchedView(viewsets.generics.UpdateAPIView):
    serializer_class = VideoUpdateDetailSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        video = Video.objects.get(id=request.data['video_id'])
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


class UserNotFullyWatchedView(viewsets.generics.UpdateAPIView):
    serializer_class = VideoUpdateDetailSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        video = Video.objects.get(id=request.data['video_id'])
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


class UpVideoInSevenDayView(viewsets.generics.UpdateAPIView):
    serializer_class = UpVideoInSevenDaySerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        video = Video.objects.get(id=request.data['video_id'], owner=request.data['owner_id'])
        user = get_user_model().objects.get(id=request.data['owner_id'])
        if user and video and (video.create_at.date() + timedelta(days=2)) <= datetime.now().date():
            video.create_at = datetime.now()
            video.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# create post API
class CreateCommentView(viewsets.generics.CreateAPIView):
    serializer_class = CreateCommentSerializer
    permission_classes = [IsAuthenticated]


class CreateRequestView(viewsets.generics.CreateAPIView):
    serializer_class = CreateRequestSerializer
    permission_classes = [IsAuthenticated]
