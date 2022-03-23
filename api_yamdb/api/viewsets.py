from rest_framework import mixins, viewsets, filters

from .permissions import IsAdminOrReadOnly


class CreateListDeleteViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin,
    mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    """
    Вьюсет, исключающий PUT/PATCH запросы,
    DETAIL просмотр запрещен.
    """
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    pass
