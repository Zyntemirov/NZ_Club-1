from datetime import timedelta

from rest_framework import status
from rest_framework import pagination
from rest_framework.views import APIView
from rest_framework.generics import *
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import *
from video.models import *


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