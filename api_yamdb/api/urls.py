from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter

from api.views import (CategoryViewSet, CommentViewSet,
                       GenreViewSet, ReviewViewSet, TitleViewSet)

router_title_genre_category = DefaultRouter()
router_title_genre_category.register(
    r'titles',
    TitleViewSet,
    basename='titles'
)
router_title_genre_category.register(
    r'genres',
    GenreViewSet,
    basename='genres'
)
router_title_genre_category.register(
    r'categories',
    CategoryViewSet,
    basename='categories'
)

router_review = SimpleRouter()
router_review.register(r'reviews', ReviewViewSet, basename='reviews')

router_comment = SimpleRouter()
router_comment.register(r'comments', CommentViewSet, basename='comments')

urlpatterns = [
    path('', include(router_title_genre_category.urls)),
    path('titles/<int:title_id>/',
         include(router_review.urls)),
    path('titles/<int:title_id>/reviews/<int:review_id>/',
         include(router_comment.urls)),
]
