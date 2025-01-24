from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    GetTokenView,
    ReviewViewSet,
    SignUpView,
    TitleViewSet,
    UserViewSet,
)

router_v1 = DefaultRouter()

router_v1.register("titles", TitleViewSet)
router_v1.register("genres", GenreViewSet)
router_v1.register("categories", CategoryViewSet)
router_v1.register("users", UserViewSet)
router_v1.register(
    r"titles/(?P<title_id>\d+)/reviews", ReviewViewSet, basename="reviews"
)
router_v1.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentViewSet,
    basename="comments",
)

urlpatterns = [
    path("v1/auth/signup/", SignUpView.as_view(), name="signup"),
    path("v1/auth/token/", GetTokenView.as_view(), name="token_obtain_pair"),
    path(
        "v1/genres/<slug:slug>/",
        GenreViewSet.as_view({"delete": "destroy"}),
        name="genre-delete",
    ),
    path(
        "v1/categories/<slug:slug>/",
        CategoryViewSet.as_view({"delete": "destroy"}),
        name="category-delete",
    ),
    path("v1/", include(router_v1.urls)),
]
