from django.db import models
import datetime 
from django.contrib.auth import get_user_model


def custom_timestamp_id():
    dt = datetime.datetime.now()
    return dt.strftime('%Y%m%d%H%M%S%f') #%f はマイクロ秒


class Order(models.Model): #　注文情報のモデル（注文の履歴）
    id = models.CharField(default=custom_timestamp_id,
                          editable=False, primary_key=True, max_length=50)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    uid = models.CharField(editable=False, max_length=50)
    is_confirmed = models.BooleanField(default=False) # success_view（うまく決済処理できた場合はTrue)
    amount = models.PositiveIntegerField(default=0)
    tax_included = models.PositiveIntegerField(default=0)
    items = models.JSONField()
    shipping = models.JSONField() # userのプロフィール情報の配送先
    shipped_at = models.DateTimeField(blank=True, null=True) #発送日
    canceled_at = models.DateTimeField(blank=True, null=True) #発送キャンセル日
    memo = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    def __str__(self):
        return self.id