from django.contrib import admin
from django.contrib.admin.views.main import ChangeList

def admin_tagify(short_description=None, allow_tags=True):
    """
    Decorator that add short_description and allow_tags to ModelAdmin list_display function.

    Example:
        
        class AlbumAdmin(admin.ModelAdmin):                                                                                                                        
            list_display = ['title', 'year', 'artist', 'total_tacks', 'view_track']

            @admin_tagify("View track")
            def view_songs(self, obj):
                return "<a href=\"%s?album=%d\">%d tracks</a>" % (reverse("admin:music_track_changelist"), obj.id, obj.tracks.count())
    """
    def tagify(func):
        func.allow_tags = bool(allow_tags)
        if short_description:
            func.short_description = short_description
        return func

    return tagify


def foreign_field_func(field_name, short_description=None, admin_order_field=None): 
    """
    Allow to use ForeignKey field attributes at list_display in a simple way.

    Example:
        
        from misc.admin import foreign_field_func as ff

        class SongAdmin(admin.ModelAdmin):                                                                                                                        
            list_display = ['name', 'time', 'artist', 'album', ff('track__num', "Track number"), ff('album__total_tracks')]
    """  
    def accessor(obj): 
        val = obj 
        for part in field_name.split('__'): 
            val = getattr(val, part) 
        return val 
    
    if short_description: 
        accessor.short_description = short_description 
    else: 
        accessor.__name__ = field_name 
    if admin_order_field: 
        accessor.admin_order_field = admin_order_field 
    else: 
        accessor.admin_order_field  = (field_name,) 
    
    return accessor 


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

class SoftDeleteAdmin(admin.ModelAdmin):
    """Custom admin page for models with SoftDeleteManager."""
    list_display = ('id', '__unicode__', 'alive', )
    list_filter = ('alive', )

    def queryset(self, request):
        """Returns a Queryset of all model instances that can be edited by the 
        admin site. This is used by changelist_view."""
        query_set = self.model._default_manager.all_with_deleted()
        ordering = self.ordering or ()
        if ordering:
            query_set = query_set.order_by(*ordering)
        return query_set
