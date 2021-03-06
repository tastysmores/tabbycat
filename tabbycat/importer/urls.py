from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^data/$',                             views.data_index,                   name='data_index'),

    url(r'^data/institutions/$',                views.add_institutions,             name='add_institutions'),
    url(r'^data/institutions/edit/$',           views.edit_institutions,            name='edit_institutions'),
    url(r'^data/institutions/confirm/$',        views.confirm_institutions,         name='confirm_institutions'),

    url(r'^data/teams/$',                       views.add_teams,                    name='add_teams'),
    url(r'^data/teams/edit/$',                  views.edit_teams,                   name='edit_teams'),
    url(r'^data/teams/confirm/$',               views.confirm_teams,                name='confirm_teams'),

    url(r'^data/adjudicators/$',                views.add_adjudicators,             name='add_adjudicators'),
    url(r'^data/adjudicators/edit/$',           views.edit_adjudicators,            name='edit_adjudicators'),
    url(r'^data/adjudicators/confirm/$',        views.confirm_adjudicators,         name='confirm_adjudicators'),

    url(r'^data/venues/$',                      views.add_venues,                   name='add_venues'),
    url(r'^data/venues/edit/$',                 views.edit_venues,                  name='edit_venues'),
    url(r'^data/venues/confirm/$',              views.confirm_venues,               name='confirm_venues'),

    url(r'^data/venue_preferences/$',           views.add_venue_preferences,        name='add_venue_preferences'),
    url(r'^data/venue_preferences/edit/$',      views.edit_venue_preferences,       name='edit_venue_preferences'),
    url(r'^data/venue_preferences/confirm/$',   views.confirm_venue_preferences,    name='confirm_venue_preferences'),
]
