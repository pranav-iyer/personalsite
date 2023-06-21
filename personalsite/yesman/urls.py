from django.urls import include, path
from django_filters import rest_framework as filters
from rest_framework import routers, serializers, viewsets

from . import views
from .models import YesItem


class YesItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = YesItem
        fields = ["id", "info", "created", "completed"]


class YesItemFilterSet(filters.FilterSet):
    active = filters.BooleanFilter(field_name="completed", lookup_expr="isnull")

    class Meta:
        model = YesItem
        fields = ["info", "active"]


class YesItemViewSet(viewsets.ModelViewSet):
    queryset = YesItem.objects.all()
    serializer_class = YesItemSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = YesItemFilterSet


router = routers.DefaultRouter()
router.register(r"yesitems", YesItemViewSet)

app_name = "yesman"
urlpatterns = [
    path("", views.YesListActiveView.as_view(), name="list"),
    path("create/", views.YesListCreateView.as_view(), name="create"),
    path("complete/<int:pk>/", views.complete_yesitem, name="complete"),
    path("remind/<int:pk>/", views.remind_yesitem, name="remind"),
    path("api/", include(router.urls)),
]
