from django.conf.urls import patterns, url

from .views import MovementInFormView, MovementOutFormView

urlpatterns = patterns(
    '',
    url(r'^movements/in/$', MovementInFormView.as_view(), name="movement-in"),
    url(r'^movements/out/$', MovementOutFormView.as_view(), name="movement-out"),
)
