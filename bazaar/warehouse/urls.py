from django.conf.urls import patterns, url

from .views import MovementFormView

urlpatterns = patterns(
    '',
    url(r'^movements/in/$', MovementFormView.as_view(), name="movement"),
)
