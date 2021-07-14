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


class CategoryListView(ListAPIView):
    serializer_class = SeasonalCategorySerializer
    queryset = Category.objects.all()


class ApartmentDetailView(RetrieveAPIView):
    serializer_class = SeasonalApartmentDetailSerializer

    def get(self, request, *args, **kwargs):
        queryset = SeasonalApartment.objects.filter(is_checked=True)
        apartment_detail = get_object_or_404(queryset, id=kwargs['id'])
        serializer = SeasonalApartmentDetailSerializer(apartment_detail, context={'request': request})
        return Response(serializer.data)


class ViewsDetailApartmentView(ListAPIView):
    serializer_class = SeasonalViewsDetailApartmentSerializer

    def get(self, request, *args, **kwargs):
        queryset = SeasonalApartment.objects.all()
        views = get_object_or_404(queryset, id=self.kwargs['id'])
        serializer = SeasonalViewsDetailApartmentSerializer(views, context={'request': request})
        return Response(serializer.data['views'])


class CreateApartmentLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        video = SeasonalApartment.objects.get(id=request.data['id'])
        user = get_user_model().objects.get(id=request.user.id)
        if user not in video.likes.all():
            video.likes.add(user)
            video.save()
            return Response({'message': 'This user liked'}, status.HTTP_201_CREATED)
        return Response({'message': 'This user already liked'}, status.HTTP_204_NO_CONTENT)


class DeleteApartmentLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        video = SeasonalApartment.objects.get(id=kwargs['id'])
        video.likes.remove(user)
        return Response(status.HTTP_204_NO_CONTENT)


class CommentsDetailApartmentView(ListAPIView):
    serializer_class = SeasonalCommentsDetailApartmentSerializer
    queryset = SeasonalComment

    def get(self, request, *args, **kwargs):
        queryset = SeasonalApartment.objects.all()
        comments = get_object_or_404(queryset, id=self.kwargs['apartment_id'])
        serializer = SeasonalCommentsDetailApartmentSerializer(comments, context={'request': request})
        return Response(serializer.data['comments'])


class ApartmentSearchView(ListAPIView):
    serializer_class = SeasonalApartmentSerializer

    def get_queryset(self):
        queryset = SeasonalApartment.objects.filter(name__icontains=self.kwargs['search'], is_checked=True)
        return queryset


class ApartmentView(ListAPIView):
    serializer_class = SeasonalApartmentSerializer

    def get_queryset(self):
        user = self.request.user
        if user:
            queryset = SeasonalApartment.objects.filter(
                Q(is_checked=True) | Q(views__in=[user])).distinct()[::-1]
            return queryset
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class CreateCommentView(CreateAPIView):
    serializer_class = SeasonalCreateCommentSerializer
    permission_classes = [IsAuthenticated]


class ApartmentFilterOrListView(ListAPIView):
    serializer_class = SeasonalApartmentSerializer

    def get_queryset(self):
        category_id = self.request.query_params.get('category_id', '')
        region = self.request.query_params.get('region')
        queryset = SeasonalApartment.objects.filter(is_checked=True)

        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if region:
            queryset = queryset.filter(owner__profile__region=region)
        return queryset


class ApartmentRequestView(CreateAPIView):
    serializer_class = ApartmentRequestSerializer
    queryset = SeasonalApartment.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        apartment = serializer.save(owner=request.user)

        try:
            for image in request.FILES.getlist('images'):
                ad_image = ApartmentImage(apartment=apartment, image=image)
                ad_image.save()
        except:
            pass

        return Response(serializer.data, status.HTTP_201_CREATED)


class ApartmentRequestRoomView(CreateAPIView):
    serializer_class = RoomSerializer
    queryset = Room.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status.HTTP_201_CREATED)


class ApartmentRoomListView(ListAPIView):
    serializer_class = RoomSerializer

    def get_queryset(self):
        return Room.objects.filter(apartment_id=self.kwargs['apartment_id'])


class BookingRequestView(CreateAPIView):
    serializer_class = BookingRequestSerializer
    queryset = BookingRequest.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status.HTTP_201_CREATED)


class RoomBookingDateView(GenericAPIView):
    queryset = BookingRequest.objects.all()

    def get(self, request, *args, **kwargs):
        queryset = BookingRequest.objects.filter(room=self.kwargs['room_id'])
        reserved_list = []
        for query in queryset:
            reserved_list.append({'entry_date': query.entry_date, 'exit_date': query.exit_date})
        return Response(reserved_list)


class UserWatchedApartmentView(UpdateAPIView):
    serializer_class = CreateViewApartmentHistorySerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        apartment = SeasonalApartment.objects.get(id=request.data['apartment_id'])
        user = get_user_model().objects.get(id=request.data['user_id'])
        if apartment and user:
            if user not in apartment.views.all():
                ViewHistory.objects.create(
                    user=user,
                    apartment=apartment
                )
                apartment.views.add(user)
                apartment.save()

            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
