from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter
from bazaar.listings.views import ListingViewSet

from .views import HomeView, MessagesView

router = DefaultRouter()
router.register(r'', ListingViewSet)

bazaar_patterns = patterns(
    '',
    url(r'^$', HomeView.as_view(), name="home"),
    url(r'^accounts/login/$', 'bazaar.views.login', name="login"),
    url(r'^accounts/logout/$', 'bazaar.views.logout', name="logout"),

    # messages
    url(r'^messages/$', MessagesView.as_view(), name="messages"),
    url(r'^api/messages/', include("stored_messages.urls")),
    url(r'^api/listings/', include(router.urls)),

    url(r'', include("bazaar.goods.urls")),
    url(r'', include("bazaar.listings.urls")),
    url(r'', include("bazaar.warehouse.urls")),
)

# uniform namespace for all urls
urlpatterns = patterns(
    '',
    url(r'', include(bazaar_patterns, namespace="bazaar", app_name="bazaar")),
)
