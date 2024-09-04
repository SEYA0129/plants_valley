from base.forms import UserCreationForm
from django.contrib import admin
from base.models import Item, Category, Tag, User, Profile, Order, Introduce, Rule, Experience, Education, Software, License, ItemPictures
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django import forms  # 追記
import json  # 追記
 
 
class TagInline(admin.TabularInline):
    model = Item.tags.through
 
 
class ItemAdmin(admin.ModelAdmin):
    inlines = [TagInline]
    exclude = ['tags']
 
 
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
 
 
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password',)}),
        (None, {'fields': ('is_active', 'is_admin',)}),
    )
 
    list_display = ('username', 'email', 'is_active',)
    list_filter = ()
    ordering = ()
    filter_horizontal = ()
 
    add_fieldsets = (
        (None, {'fields': ('username', 'email', 'is_active',)}),
    )
 
    add_form = UserCreationForm

    inlines = (ProfileInline,)

class CustomJsonField(forms.JSONField):
    def prepare_value(self, value):
        if isinstance(value, str):
            try:
                # Try to load JSON data
                loaded = json.loads(value)
                return json.dumps(loaded, indent=2, ensure_ascii=False)
            except (TypeError, json.JSONDecodeError):
                # Handle the case where value is not valid JSON
                return value
        # If value is not a string, just return it as is
        return value

class OrderAdminForm(forms.ModelForm):
    items = CustomJsonField()
    shipping = CustomJsonField()

    class Meta:
        model = Order
        fields = '__all__'

class OrderAdmin(admin.ModelAdmin):
    form = OrderAdminForm
 
admin.site.register(Order, OrderAdmin)  # OrderAdminを追記
admin.site.register(Item, ItemAdmin)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Group)
admin.site.register(Introduce)
admin.site.register(Rule)
admin.site.register(Experience)
admin.site.register(Education)
admin.site.register(Software)
admin.site.register(License)
admin.site.register(ItemPictures)