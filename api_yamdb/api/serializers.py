import datetime as dt

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    """
    Обслуживает модель 'Category'.
    """
    slug = serializers.SlugField(
        max_length=50,
        validators=[UniqueValidator(
            queryset=Category.objects.all(),
            message='Такая категория уже существует.'
        )]
    )

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """
    Обслуживает модель 'Genre'.
    """
    slug = serializers.SlugField(
        max_length=50,
        validators=[UniqueValidator(
            queryset=Genre.objects.all(),
            message='Такой жанр уже существует.'
        )]
    )

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategoryDisplaySerializer(serializers.ModelSerializer):
    """
    Обслуживает модель 'Category'.
    Используется на чтение внутри 'TitleDisplaySerializer'.
    """
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreDisplaySerializer(serializers.ModelSerializer):
    """
    Обслуживает модель 'Genre'.
    Используется на чтение внутри 'TitleDisplaySerializer'.
    """
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """
    Обслуживает модель 'Title'.
    Используется на запись.
    """
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    def validate_year(self, value):
        current_year = dt.date.today().year
        if 0 < value <= current_year:
            return value
        raise serializers.ValidationError(
            'Проверьте год выхода'
        )

    class Meta:
        model = Title
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Title.objects.all(),
                fields=('name', 'year', 'category')
            )
        ]


class TitleDisplaySerializer(serializers.ModelSerializer):
    """
    Обслуживает модель 'Title'.
    Используется на чтение.
    """
    category = CategoryDisplaySerializer(read_only=True)
    genre = GenreDisplaySerializer(read_only=True, many=True)
    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year',
            'rating', 'description',
            'genre', 'category'
        )


class SignUpSerializer(serializers.Serializer):
    """
    Создает пользователей через API,
    отправляет код подтверждения на эл.почту.
    """
    username = serializers.CharField(
        max_length=150,
        allow_blank=False,
    )
    email = serializers.EmailField(
        max_length=254,
        allow_blank=False,
    )

    def validate(self, data):
        data_username = data['username']
        data_email = data['email']
        user_q = User.objects.filter(
            (Q(email=data_email) & ~Q(username=data_username))
            | (~Q(email=data_email) & Q(username=data_username))
        )
        if user_q:
            raise serializers.ValidationError(
                'В базе уже есть пользователь с указанным username или email'
            )
        return data

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError('Измените username!')
        return value


class UserSerializer(serializers.ModelSerializer):
    """
    Обслуживает модель 'User'.
    Применяется для создания пользователей администратором
    и получения/корректировки данных пользователями.
    """
    username = serializers.CharField(
        allow_blank=False,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        allow_blank=False,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )
        model = User


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Новый сериалайзер для получения токена.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.CharField()
        self.fields['confirmation_code'] = serializers.CharField()
        del self.fields['password']  # Вместо пароля confirmation_code

    def validate(self, attrs):
        user = get_object_or_404(User, username=attrs['username'])
        refresh = self.get_token(user)
        data = {'token': str(refresh.access_token), }

        return data


class ReviewSerializer(serializers.ModelSerializer):
    """
    Обслуживает модель 'Review'.
    """
    author = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date',)

    def validate(self, data):
        author = self.context.get('request').user
        title_id = get_object_or_404(
            Title,
            id=self.context.get('view').kwargs.get('title_id')
        )
        if (self.context.get('request').method == 'POST'
            and Review.objects.filter(
                title_id=title_id,
                author_id=author.id).exists()):
            raise serializers.ValidationError(
                'Возможно оставить только один отзыв')
        return data


class CommentSerializer(serializers.ModelSerializer):
    """
    Обслуживает модель 'Comment'.
    """
    author = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date',)

    def validate(self, data):
        get_object_or_404(
            Review,
            id=self.context.get('view').kwargs.get('review_id'),
            title_id=self.context.get('view').kwargs.get('title_id')
        )
        return data
