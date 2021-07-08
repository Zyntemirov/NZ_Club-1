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

    path('categories', CategoriesView.as_view()),

    path('video/detail/<int:id>', VideoDetailView.as_view()),
    path('views/video/detail/<int:id>', ViewsDetailVideoView.as_view()),
    path('create/video/like/', CreateVideoLikeView.as_view()),
    path('delete/video/like/<int:id>/', DeleteVideoLikeView.as_view()),
    path('comments/video/detail/<int:id>', CommentsDetailVideoView.as_view()),
    path('video/<str:search>', VideoSearchView.as_view()),
    path('videos/by/<int:category_id>', VideoByCategoryView.as_view()),
    path('video/top/10/<int:user_id>', VideoTop10View.as_view()),
    path('videos/by/me/', VideosView.as_view()),
    path('videos/donate/', VideoDonateView.as_view()),
    path('video/update/user_completely_watched', UserFullyWatchedView.as_view()),
    path('video/update/user_not_completely_watched', UserNotFullyWatchedView.as_view()),
    path('video/update/put_first', UpVideoInSevenDayView.as_view()),
    path('create/comment', CreateCommentView.as_view()),
    path('create/request', CreateRequestView.as_view()),
    path('filter/', VideoFilterView.as_view())

]
