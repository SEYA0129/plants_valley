from django.db import models
from django.utils.crypto import get_random_string
import os
 
 
def create_id():
    return get_random_string(22)
 
 
def upload_image_to(instance, filename):
    item_id = instance.id
    return os.path.join('items', item_id, filename)
 
 
class Tag(models.Model):
    slug = models.CharField(max_length=32, primary_key=True) #urlに表示　基本的に英字
    name = models.CharField(max_length=32)
 
    def __str__(self):
        return self.name
 
 
class Category(models.Model):
    slug = models.CharField(max_length=32, primary_key=True) #urlに表示　基本的に英字
    name = models.CharField(max_length=32)
 
    def __str__(self):
        return self.name
 
 
class Item(models.Model):
    id = models.CharField(default=create_id, primary_key=True,
                          max_length=22, editable=False)
    name = models.CharField(default='', max_length=50)
    price = models.PositiveIntegerField(default=0)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField(default='', blank=True)
    sold_count = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(default="", blank=True,
                              upload_to=upload_image_to) #orderモデル用に設定。基本的にItemPictureのordering=1と同じ画像にすること
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag)
 
    def __str__(self):
        return self.name #django管理画面のアイテムnameを表示 name以外も表示できる


class ItemPictures(models.Model):
    image = models.ImageField(default="", blank=True, upload_to='item_pictures')
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE
    )
    order = models.IntegerField()

    class Meta:
        db_table = 'item_pictures'
        ordering = ['order']

    def __str__(self):
        return self.item.name + ':' + str(self.order)