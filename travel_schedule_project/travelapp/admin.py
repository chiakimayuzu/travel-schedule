from django.contrib import admin
from .models import TouristSpot

class TouristSpotAdmin(admin.ModelAdmin):
    list_display = ('spot_name', 'address', 'latitude', 'longitude')

admin.site.register(TouristSpot, TouristSpotAdmin)