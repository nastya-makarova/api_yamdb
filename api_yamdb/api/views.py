from http import HTTPStatus

from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    filters,
    mixins,
    permissions,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from reviews.models import Category, Genre, Review, Title
from users.models import User
from .filters import TitleFilter
from .permissions import (
    IsAdminOrDeny,
    IsAdminOrReadOnly,
    ReviewCommentPermissions,
)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    GetTokenSerializer,
    ReviewSerializer,
    SignUpSerializer,
    TitleCreateSerializer,
    TitleSerializer,
    UserGetMeSerializer,
    UserGetUsernameSerializer,
    UserSerializer,
)
from .service import (
    generate_password,
    get_tokens_for_user,
    send_confirmation_email,
)


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с моделью Titles."""

    queryset = (
        Title.objects.all()
        .annotate(rating=Avg("reviews__score"))
        .order_by("id",)
    )
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ["get", "post", "patch", "delete"]
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        """Метод определяет, какой сериализатор использовать.
        TitleSerializer для операций 'list' и 'retrieve'.
        TitleCreateSerializer для других действий (например, 'create').
        """
        if self.action in ("list", "retrieve"):
            return TitleSerializer
        return TitleCreateSerializer


class BaseSlugViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Базовый ViewSet для работы с моделями Category и Genre."""

    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)

    def destroy(self, request, slug):
        instance = get_object_or_404(self.queryset, slug=slug)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GenreViewSet(BaseSlugViewSet):
    """ViewSet для работы с моделью Genre."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(BaseSlugViewSet):
    """ViewSet для работы с моделью Category."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с моделью User."""
    http_method_names = ["get", "post", "patch", "delete"]
    queryset = User.objects.all()
    permission_classes = (IsAdminOrDeny,)
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["username"]

    @action(
        methods=["get", "patch"],
        detail=False,
        url_path="me",
        permission_classes=(permissions.IsAuthenticated,),
    )
    def get_me(self, request):

        if request.method == "GET":
            serializer = UserGetMeSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == "PATCH":
            serializer = UserGetMeSerializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["get", "patch", "delete"],
        url_path=r"(?P<username>[\w.@+-]+)",
        detail=False,
    )
    def get_username(self, request, username):
        request_user = get_object_or_404(User, username=username)
        user = request.user
        if request.method == "GET":
            serializer = UserGetUsernameSerializer(request_user)
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        if request.method == "PATCH":
            serializer = UserGetUsernameSerializer(
                request_user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        if request.method == "DELETE":
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class SignUpView(APIView):
    """ViewSet для получения пароля подтверждения."""

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            confirmation_code = generate_password()
            request_user, created = User.objects.get_or_create(
                username=serializer.validated_data["username"],
                email=serializer.validated_data["email"],
                defaults={"confirmation_code": confirmation_code},
            )
            if not created:
                request_user.confirmation_code = confirmation_code
                request_user.save()
            send_confirmation_email(
                message=confirmation_code,
                recepient_list=[request.data["email"]],
            )
            return Response(serializer.data, status=HTTPStatus.OK)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)


class GetTokenView(APIView):
    """ViewSet для получения токена."""

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = User.objects.get(
                username=serializer.validated_data["username"]
            )
            token = get_tokens_for_user(user)
            return Response(token, status=status.HTTP_200_OK)


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с моделью Review."""

    http_method_names = ["get", "post", "patch", "delete"]
    serializer_class = ReviewSerializer
    permission_classes = (ReviewCommentPermissions,)

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get("title_id"))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с моделью Comment."""

    http_method_names = ["get", "post", "patch", "delete"]
    serializer_class = CommentSerializer
    permission_classes = (ReviewCommentPermissions,)

    def get_review(self):
        return get_object_or_404(Review, pk=self.kwargs.get("review_id"))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
