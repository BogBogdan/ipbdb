# Optional:
# Use this file to connect views from views.py in the same
# directory to their URLs.

#from django.conf.urls.defaults import *
from django.conf.urls import url
from node import views
#from django.conf import settings


#urlpatterns = patterns(settings.NODENAME+'.node.views',
#                      url(r'^$', 'index'),
#		      url(r'^test/$', 'test'),
#                      url(r'^get_species/(?P<coll_type_id>\w+)/$', 'get_species'),
#		      url(r'^get_states/(?P<species_id>[\w-]+)/(?P<coll_type_id>\w+)/$', 'get_states'),
#                      url(r'^get_cs_types/(?P<state_id>\w+)/(?P<coll_type_id>\w+)/$', 'get_cs_types'),
#                      )

urlpatterns = [
        url(r'^search_results/$', views.search_results),
        url(r'^plots/$', views.plots_index),
        url(r'^plots/(?P<td_id>\d+)/$', views.plot_detail),
        url(r'^plots/(?P<td_id>\d+)/data\.json$', views.plot_json),
        url(r'^plots/(?P<td_id>\d+)/data\.csv$', views.plot_csv),
        url(r'^$', views.index),
        url(r'^get_species/(?P<coll_type_id>\w+)/$', views.get_species),
	    url(r'^get_states/(?P<species_id>[\w-]+)/(?P<coll_type_id>\w+)/$', views.get_states),
        url(r'^get_cs_types/(?P<state_id>\w+)/(?P<coll_type_id>\w+)/$', views.get_cs_types),
        ]
