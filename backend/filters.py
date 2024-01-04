from django_filters.rest_framework import DjangoFilterBackend

class AllDjangoFilterBackend(DjangoFilterBackend):
    """
    Filters DRF views by any of the objects properties.
    """

    def get_filterset_class(self, view, queryset=None):
        """
        Return the `FilterSet` class used to filter the queryset.
        """
        filterset_class = getattr(view, "filterset_class", None)
        filterset_fields = getattr(view, "filterset_fields", None)

        if filterset_fields or filterset_class:
            return super().get_filterset_class(view, queryset)

        class AutoFilterSet(self.filterset_base):
            class Meta:
                model = queryset.model
                fields = "__all__"

        return AutoFilterSet

   