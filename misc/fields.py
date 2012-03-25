# -*- coding: utf-8 -*-
from django import forms
from django.db import models
from django.db.models import OneToOneField
from django.db.models.fields.related import SingleRelatedObjectDescriptor


class TagInput(forms.Widget):

    def __init__(self, attrs=None, choices=()):
        if attrs is not None:
            self.attrs = attrs.copy()
        else:
            self.attrs = {}
        self.choices = list(choices)

    def render(self, name, value, attrs=None):
        if value is None: value = ''
        str = ""
        values = ""
        for user in self.choices.queryset:
            if len(str) > 0:
                str += ", "
                values += ", "
            dn = user.get_profile().display_name
            if dn != user.username:
                str += "\"" + dn + " aka " + user.username + "\""
            else:
                str += "\"" + user.username + "\""
            values += "\"" + unicode(user.id) + "\""
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        final_attrs['choice'] = str
        final_attrs['values'] = values
        final_attrs['value'] = conditional_escape(force_unicode(value))
        return mark_safe(u"""
        <div class="tagit-div">
			<ul id="%(name)s" class="%(class)s">
                <li class="tagit-new">
                    <input class="tagit-input ui-autocomplete-input" type="text" autocomplete="off" role="textbox" aria-autocomplete="list" aria-haspopup="true" />
                </li>
            </ul>
            <input name="%(name)s" type="text" id="%(name)s_value" value="%(value)s" />
		</div>
        <script>
        $(document).ready(function(){
            $("#%(name)s").tagit({
                availableTags: [%(choice)s],
                values: [%(values)s],
            });
        });
        </script>
        """ % final_attrs)

		

class AutoSingleRelatedObjectDescriptor(SingleRelatedObjectDescriptor):
    def __get__(self, instance, instance_type=None):
        try:
            return super(AutoSingleRelatedObjectDescriptor, self).__get__(instance, instance_type)
        except self.related.model.DoesNotExist:
            obj = self.related.model(**{self.related.field.name: instance})
            obj.save()
            return obj


class AutoOneToOneField(OneToOneField):
    '''
    OneToOneField creates related object on first call if it doesnt exist yet.
    Use it instead of original OneToOne field.

    example:
        
        class MyProfile(models.Model):
            user = AutoOneToOneField(User, primary_key=True)
            home_page = models.URLField(max_length=255, blank=True)
            icq = models.IntegerField(max_length=255, null=True)
    '''
    def contribute_to_related_class(self, cls, related):
        setattr(cls, related.get_accessor_name(), AutoSingleRelatedObjectDescriptor(related))
