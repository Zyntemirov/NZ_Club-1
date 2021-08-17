from rest_framework import status
from rest_framework.generics import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from seasonal.serializers import *
from django.db.models import Q
from django.conf import settings
from datetime import timedelta
from accounts.models import userProfile
from django.core.management.utils import get_random_secret_key
from django.template.loader import render_to_string

import hashlib


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


class CityListView(ListAPIView):
    serializers = SeasonalCitySerializer
    queryset = City.objects.all()


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
                Q(is_checked=True) | Q(views__in=[user])).distinct().reverse()
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
        city_id = self.request.query_params.get('city_id')
        queryset = SeasonalApartment.objects.filter(is_checked=True)

        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if region:
            queryset = queryset.filter(owner__profile__region=region)
        if city_id:
            queryset = queryset.filter(city_id=city_id)
        return queryset


class ApartmentRequestView(CreateAPIView):
    serializer_class = ApartmentRequestSerializer
    queryset = Request.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        apartment = serializer.save(owner=request.user)

        if request.FILES.getlist('images'):
            for image in request.FILES.getlist('images'):
                ad_image = ApartmentRequestImage(apartment=apartment, image=image)
                ad_image.save()
        else:
            return Response({'image': 'This field is required!'}, status.HTTP_403_FORBIDDEN)

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


class BookingRequestView(GenericAPIView):
    serializer_class = BookingRequestSerializer
    queryset = BookingRequest.objects.all()

    def post(self, request):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user)
        data = request.data
        if 'card' == data[type]:
            booking = BookingRequest.objects.get(id=serializer.data['id'])
            payment_id = get_random_secret_key()
            g = render_to_string('yoomoney.html', {
                'recipient': settings.PAYMENT_RECIPIENT,
                'payment_id': payment_id,
                'comment': data['comment'],
                'count': data['total_price']
                })
            booking.payment_id = payment_id
            booking.save()
            return Response({
                'Booking request': serializer.data,
                'Payment': g
            })
        elif 'point' == data[type]:
            user = get_user_model().objects.get(id=request.user.id)
            user_prof = userProfile.objects.get(user=user)
            total_price = float(data['total_price'])
            if total_price < user_prof.balance:
                return Response({'enough points': "you don't have enough points"})
            user_prof.balance -= total_price
            user_prof.withdrawn_balance += total_price
            user_prof.save()
        return Response(serializer.data, status.HTTP_201_CREATED)


class BookingNotification(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data
        list_ob = [
            str(data['notification_type']),
            str(data['operation_id']),
            str(data['amount']),
            str(data['currency']),
            str(data['datetime']),
            str(data['sender']),
            str(data['codepro']),
            settings.NOTIFICATION_SECRET,
            str(data['label'])
        ]
        hash1 = hashlib.sha1(bytes("&".join(list_ob), 'utf-8'))
        pbhash = hash1.hexdigest()
        if data['sha1_hash'] != pbhash:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        query = BookingRequest.objects.filter(accept=False)
        query = get_object_or_404(query, payment_id=data['label'])
        query.accept = True
        query.total_price = data['amount']
        query.save()
        return Response(status=status.HTTP_200_OK)


class BookingHistory(ListAPIView):
    serializer_class = BookingHistorySerializer

    def get_queryset(self):
        return BookingRequest.objects.filter(user=self.request.user)


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
