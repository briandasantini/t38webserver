from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

app_name = "job"

urlpatterns = [
    path("cpepmatch/", cPEPView.as_view(), name="cpepmatch"),
    path("rsremd/", RSREMDView.as_view(), name="rsremd"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)