from django.contrib import admin
from .models import Rating, Toilet, Icon, ToiletImage, UserSetting, UpdateToilet, UpdateToiletImage

# Register your models here.
admin.site.register(Icon)
admin.site.register(Rating)
admin.site.register(UserSetting)


#admin.site.register(UpdateToilet)
#admin.site.register(TestToilet)
#admin.site.register(ToiletImage)

class ToiletImageAdmin(admin.StackedInline):
    model = ToiletImage

@admin.register(Toilet)
class ToiletAdmin(admin.ModelAdmin):
    inlines = [ToiletImageAdmin]

    class Meta:
       model = Toilet

@admin.register(ToiletImage)
class ToiletImageAdmin(admin.ModelAdmin):
    pass




class UpdateToiletImageAdmin(admin.StackedInline):
    model = UpdateToiletImage

@admin.register(UpdateToilet)
class UpdateToiletAdmin(admin.ModelAdmin):
    inlines = [UpdateToiletImageAdmin]

    class Meta:
       model = UpdateToilet
       
@admin.register(UpdateToiletImage)
class UpdateToiletImageAdmin(admin.ModelAdmin):
    pass
