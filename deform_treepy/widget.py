# Copyright (c) 2014 by Ecreall under licence AGPL terms
# avalaible on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi
import deform
import colander
import json
from colander import null
from persistent.dict import PersistentDict
from deform.widget import default_resource_registry

from deform_treepy import _


class DictSchemaType(colander.String):

    def serialize(self, node, appstruct):
        if appstruct is null:
            return null

        result = appstruct
        if not isinstance(appstruct, (str, dict, PersistentDict)):
            raise colander.Invalid(
                node, _('${val} cannot be serialized',
                        mapping={'val': appstruct})
                )

        return result

    def deserialize(self, node, cstruct):
        if not cstruct:
            return null

        if not isinstance(cstruct, dict):
            raise colander.Invalid(
                node, _('${val} cannot be deserialized',
                        mapping={'val': cstruct})
                )

        return cstruct


class KeywordsTreeWidget(deform.widget.TextInputWidget):
    template = 'deform_treepy:templates/tree.pt'
    readonly_template = 'deform_treepy:templates/readonly/tree.pt'
    requirements = (('jquery.maskedinput', None),
                    ('treepy', None))

    def dumps(self, options):
        return json.dumps(dict(options))

    def serialize(self, field, cstruct, **kw):
        if cstruct in (null, None):
            cstruct = '{}'

        if isinstance(cstruct, (dict, PersistentDict)):
            cstruct = json.dumps(dict(cstruct))

        readonly = kw.get('readonly', self.readonly)
        template = readonly and self.readonly_template or self.template
        values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **values)

    def deserialize(self, field, pstruct):
        if pstruct is null:
            return null
        if self.strip:
            pstruct = pstruct.strip()
        if not pstruct:
            return null
        return json.loads(pstruct)


default_resource_registry.set_js_resources(
    'treepy', None,
    'deform_treepy:static/js/treepy.js',
    'deform_treepy:static/js/treepy_langs.js',
    'deform_treepy:static/vakata-jstree/dist/jstree.js',
    'pontus:static/select2/dist/js/select2.js')

default_resource_registry.set_css_resources(
    'treepy', None,
    'deform_treepy:static/vakata-jstree/dist/themes/default/style.min.css',
    'deform_treepy:static/css/treepy.css',
    'pontus:static/select2/dist/css/select2.min.css')
