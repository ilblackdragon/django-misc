from django.contrib.admin.views.main import ChangeList


class SpecialOrderingChangeList(ChangeList):
    """
    Override change list for improve multiordering in admin change list.
    `Django will only honor the first element in the list/tuple ordering attribute; any others will be ignored.`
    
    Example:

        class SongAdmin(admin.ModelAdmin):
            list_display = ['name', 'time', 'artist', 'album', 'track', 'total_tracks']
            special_ordering = {'artist': ('artist', 'album', 'track'), 'album': ('album', 'track')}
            default_special_ordering = 'artist'

            def get_changelist(self, request, **kwargs):
                return SpecialOrderingChangeList
    """
    def apply_special_ordering(self, queryset):
        order_type, order_by = [self.params.get(param, None) for param in ('ot', 'o')]
        special_ordering = self.model_admin.special_ordering
        if special_ordering:
            try:
                if order_type and order_by:
                    order_field = self.list_display[int(order_by)]
                    ordering = special_ordering[order_field]
                    if order_type == 'desc':
                        ordering = ['-' + field for field in ordering]
                else:
                    ordering = special_ordering[self.model_admin.default_special_ordering]
                queryset = queryset.order_by(*ordering)
            except IndexError:
                return queryset
            except KeyError:
                return queryset
        return queryset

    def get_query_set(self):
        queryset = super(SpecialOrderingChangeList, self).get_query_set()
        queryset = self.apply_special_ordering(queryset)
        return queryset
