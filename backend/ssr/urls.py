import json

from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from .store import x32


def x32_data(request, **kwargs):
    return HttpResponse(json.dumps(x32.cache), content_type="application/json")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('x32/', x32_data),

]
