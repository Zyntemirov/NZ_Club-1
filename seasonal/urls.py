from django.urls import path
from seasonal.views import *


urlpatterns = [
    path('stories/', StoriesView.as_view()),
    path('stories/update/user_watched/', UserWatchedStoriesView.as_view()),
    path('stories/detail/<int:stories_id>/', StoriesDetailView.as_view()),
    path('stories/like/', CreateLikeStoriesView.as_view()),
    path('stories/like/<int:id>/', DeleteLikeStoriesView.as_view()),
    path('stories/complaint/', CreateStoriesComplaintView.as_view()),

    path('category/list', CategoryListView.as_view()),
    path('city/list', CityListView.as_view()),
    path('views/apartment/detail/<int:id>', ViewsDetailApartmentView.as_view()),
    path('apartment/update/user_watched/', UserWatchedApartmentView.as_view()),
    path('apartment/by/me/', ApartmentView.as_view()),
    path('apartment/comments/detail/<int:apartment_id>', CommentsDetailApartmentView.as_view()),
    path('create/comment', CreateCommentView.as_view()),
    path('apartment/detail/<int:id>', ApartmentDetailView.as_view()),
    path('apartment/like/', CreateApartmentLikeView.as_view()),
    path('apartment/like/<int:id>/', DeleteApartmentLikeView.as_view()),
    path('apartment/<str:search>', ApartmentSearchView.as_view()),
    path('apartment/filter/', ApartmentFilterOrListView.as_view()),
    path('apartment/request/', ApartmentRequestView.as_view()),
    path('apartment/request/room/', ApartmentRequestRoomView.as_view()),
    path('apartment/room/list/<int:apartment_id>', ApartmentRoomListView.as_view()),
    path('booking/request/', BookingRequestView.as_view()),
    path('booking/success/', BookingNotification.as_view()),
    path('booking/history/', BookingHistory.as_view()),
    path('room/booking_date/<int:room_id>/', RoomBookingDateView.as_view())
]
