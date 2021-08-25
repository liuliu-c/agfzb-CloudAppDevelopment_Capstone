from django.contrib import admin
from .models import CarModel, CarMake


# Register your models here.

# CarModelInline class
class CarModelInline(admin.StackedInline):
    model = CarModel 
    extra = 6
# CarModelAdmin class

# CarMakeAdmin class with CarModelInline
class CarMakeAdmin(admin.ModelAdmin):
    inlines = [CarModelInline]
# Register models here
admin.site.register(CarMake)
admin.site.register(CarModel)