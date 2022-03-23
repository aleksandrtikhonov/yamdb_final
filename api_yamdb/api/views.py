from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg

from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from api_yamdb.settings import EMAIL_HOST_USER
from reviews.models import Category, Genre, Review, Title
from .filters import TitleFilter
from .permissions import IsAdmin, IsAdminOrReadOnly, IsAuthorOrStaffOrReadOnly
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, MyTokenObtainPairSerializer,
                          ReviewSerializer, SignUpSerializer,
                          TitleDisplaySerializer, TitleSerializer,
                          UserSerializer)
from .viewsets import CreateListDeleteViewSet

User = get_user_model()


class CategoryViewSet(CreateListDeleteViewSet):
    """Обработка запросов к категориям."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CreateListDeleteViewSet):
    """Обработка запросов к жанрам."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Обработка запросов к произведениям."""
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).order_by('-id')
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return TitleDisplaySerializer
        return TitleSerializer


class UserList(generics.ListCreateAPIView):
    """Обработка запросов к пользователям."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    """Обработка запросов к пользователям."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(
            queryset,
            username=self.kwargs['username']
        )
        return obj


class UserSelfDetail(generics.RetrieveUpdateAPIView):
    """Обработка запросов к своему пользователю."""
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(
            queryset,
            username=self.request.user.username
        )
        return obj

    def perform_update(self, serializer):
        request_role = serializer.validated_data.get('role')
        if (
            self.request.user.is_user
            and request_role is not None
            and request_role != self.request.user.role
        ):
            serializer.validated_data['role'] = 'user'
        serializer.save()


class MyTokenObtainPairView(TokenObtainPairView):
    """Обработка запросов токенов."""

    serializer_class = MyTokenObtainPairSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = MyTokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(
            User,
            username=serializer.initial_data['username']
        )
        if not default_token_generator.check_token(
            user,
            serializer.initial_data['confirmation_code']
        ):
            return Response(
                {'confirmation_code': 'Неверный код подтверждения.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes((permissions.AllowAny, ))
def send_token(request):
    """
    Отправка кода подтверждения по почте.
    """
    if request.method != 'POST':
        return

    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # Создадим пользователя, если такого нет
    user_obj, created = User.objects.get_or_create(
        username=serializer.data['username'],
        email=serializer.data['email'],
    )
    # Отправим письмо с кодом подтверждения
    confirmation_code = default_token_generator.make_token(user_obj)
    send_mail(
        'Подтверждение регистрации пользователя',
        f'Код подтверждения: {confirmation_code}',
        EMAIL_HOST_USER,
        [serializer.data['email']],
        fail_silently=False,
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewViewSet(viewsets.ModelViewSet):
    """Обработка запросов к отзывам"""
    serializer_class = ReviewSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrStaffOrReadOnly,
    )

    def get_queryset(self, **kwargs):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id',)
        )
        return title.reviews.all()

    def perform_create(self, serializer, **kwargs):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id',)
        )
        serializer.save(
            author=self.request.user,
            title=title
        )


class CommentViewSet(viewsets.ModelViewSet):
    """Обработка запросов к комментариям на произведения"""
    serializer_class = CommentSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrStaffOrReadOnly,
    )

    def get_queryset(self, **kwargs):
        review = get_object_or_404(
            Review,
            title__id=self.kwargs.get('title_id'),
            id=self.kwargs.get('review_id',)
        )
        return review.comment.all()

    def perform_create(self, serializer, **kwargs):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title__id=self.kwargs.get('title_id')
        )
        serializer.save(
            author=self.request.user,
            review=review
        )
