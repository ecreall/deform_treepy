# -*- coding: utf8 -*-
# Copyright (c) 2015 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.i18n import TranslationStringFactory


_ = TranslationStringFactory('treepy')


def includeme(config):
    config.include('.')
    config.scan('.')
    config.add_static_view('deform_treepy', 'deform_treepy:static', cache_max_age=86400)
