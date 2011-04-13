# -*- coding: utf-8 -*-

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
