from django.conf.urls import url

from . import views

urlpatterns = [
    # Old busted
    url(r'^create_old/$',
        views.create_adj_allocation,
        name='create_adj_allocation'),
    url(r'^edit_old/$',
        views.draw_adjudicators_edit,
        name='draw_adjudicators_edit'),
    url(r'^_get_old/$',
        views.draw_adjudicators_get,
        name='draw_adjudicators_get'),
    url(r'^_update_importance/$',
        views.update_debate_importance,
        name='update_debate_importance'),
    url(r'^conflicts_old/$',
        views.adj_conflicts,
        name='adj_conflicts'),
    url(r'^save/$',
        views.SaveAdjudicatorsView.as_view(),
        name='save_adjudicators'),
    # New Hotness
    url(r'^edit/$',
        views.EditAdjudicatorAllocationView.as_view(),
        name='edit_adj_allocation'),
    url(r'^create/$',
        views.CreateAutoAllocation.as_view(),
        name='create_auto_allocation'),
    url(r'^importance/set/$',
        views.SaveDebateImportance.as_view(),
        name='save_debate_importance'),
    url(r'^panel/set/$',
        views.SaveDebatePanel.as_view(),
        name='save_debate_panel'),
]
