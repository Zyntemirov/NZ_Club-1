from django.urls import path
from video.views import *

urlpatterns = [
    path('faqs', FAQView.as_view()),
    path('banners', BannerView.as_view()),
    path('banner/update/user_watched', UserWatchedBannerView.as_view()),
    path('banners/detail/<int:banner_id>', BannerDetailView.as_view()),
    # path('banners/block/<int:number>', BannerByBlockNumberView.as_view()),
    path('banners/like/', CreateLikeBannerView.as_view()),
    path('banners/like/delete/<int:id>/', DeleteLikeBannerView.as_view()),
    path('banners/complaint/', CreateComplaintView.as_view()),
    path('categories', CategoriesView.as_view()),
    path('video/detail/<int:id>', VideoDetailView.as_view()),
    path('views/video/detail/<int:id>', ViewsDetailVideoView.as_view()),
    path('create/video/like/', CreateVideoLikeView.as_view()),
    path('delete/video/like/<int:id>/', DeleteVideoLikeView.as_view()),
    path('comments/video/detail/<int:id>', CommentsDetailVideoView.as_view()),
    path('video/<str:search>', VideoSearchView.as_view()),
    path('video_training', VideoTrainingView.as_view()),
    path('videos/by/me/', VideosView.as_view()),
    path('videos/donate/', VideoDonateView.as_view()),
    path('videos/by/<int:category_id>', VideoByCategoryView.as_view()),
    path('videos/my/<int:owner_id>', VideoByOwnerView.as_view()),
    path('video/top/10/<int:user_id>', VideoTop10View.as_view()),
    path('faq/<str:search>', FaqSearchView.as_view()),
    path('video/update/user_completely_watched', UserFullyWatchedView.as_view()),
    path('video/update/user_not_completely_watched', UserNotFullyWatchedView.as_view()),
    path('video/update/put_first', UpVideoInSevenDayView.as_view()),
    path('create/comment', CreateCommentView.as_view()),
    path('create/request', CreateRequest2View.as_view()),
    path('filter/', VideoFilterView.as_view())
]
