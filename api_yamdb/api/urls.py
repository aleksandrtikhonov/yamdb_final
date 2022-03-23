from django.urls import include, path, re_path
from rest_framework import routers

from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    MyTokenObtainPairView, ReviewViewSet, TitleViewSet,
                    UserDetail, UserList, UserSelfDetail, send_token)

router = routers.DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('genres', GenreViewSet)
router.register('titles', TitleViewSet)
router.register(
    r'titles\/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router.register(
    r'titles\/(?P<title_id>\d+)/reviews\/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)


urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', send_token),
    path(
        'v1/auth/token/',
        MyTokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path('v1/users/', UserList.as_view()),
    path('v1/users/me/', UserSelfDetail.as_view()),
    re_path(r'v1/users/(?P<username>[\w.@+-]+)/$', UserDetail.as_view()),
]
