from django.urls import path, include

from rest_framework import routers, serializers, viewsets
from django_filters import rest_framework as filters

from . import views
from .models import Search


class SearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Search
        fields = ["id", "timestamp", "text"]


class SearchFilterSet(filters.FilterSet):
    view_date = filters.Filter(field_name="timestamp", lookup_expr="date")


class SearchViewSet(viewsets.ModelViewSet):
    queryset = Search.objects.all()
    serializer_class = SearchSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = SearchFilterSet


router = routers.DefaultRouter()
router.register(r"searches", SearchViewSet)


app_name = "searches"
urlpatterns = [
    path("log/", views.log_search_view, name="log"),
    path("shortcut/", views.search_shortcut_view, name="shortcut"),
    path("api/", include(router.urls)),
]
