from django.urls import path
from seasonal.views import *

urlpatterns = [
    path('stories/', StoriesView.as_view()),
    path('stories/update/user_watched/', UserWatchedStoriesView.as_view()),
    path('stories/detail/<int:stories_id>/', StoriesDetailView.as_view()),
    # path('stories/block/<int:number>', StoriesByBlockNumberView.as_view()), # TODO
    path('stories/like/', CreateLikeStoriesView.as_view()),
    path('stories/like/delete/<int:id>/', DeleteLikeStoriesView.as_view()),
    path('stories/complaint/', CreateStoriesComplaintView.as_view()),
]