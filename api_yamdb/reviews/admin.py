from django.contrib import admin

from .models import Category, Comment, Genre, GenreTitle, Review, Title, User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        'role',
        'bio',
        'first_name',
        'last_name'
    )
    list_editable = ('role',)
    search_fields = ('username', 'email')
    list_filter = ('role',)
    empty_value_display = '-пусто-'


class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'name',
        'year', 'category',
        'genres_names',
        'description'
    )
    list_editable = ('category',)
    list_filter = ('year', 'category')

    def genres_names(self, obj):
        return (', '.join([
            genre.name for genre in obj.genre.all()
        ]))

    genres_names.short_description = 'Genre'


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


class GenreAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'author',
        'score',
        'pub_date',
    )
    list_editable = ('text', 'author', 'score',)
    search_fields = ('author', 'score',)
    list_filter = ('author',)
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'author',
        'pub_date',
    )
    list_editable = ('text', 'author',)
    search_fields = ('review_id', 'author',)
    list_filter = ('author',)
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(GenreTitle)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
