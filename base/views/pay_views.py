from django.shortcuts import redirect
from django.views.generic import View, TemplateView
from django.conf import settings
from stripe.api_resources import tax_rate
from base.models import Item, Order, ItemPictures
import stripe
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
import json
from django.contrib import messages



 
 
stripe.api_key = settings.STRIPE_API_SECRET_KEY

 
 
class PaySuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/success.html'
 
    def get(self, request, *args, **kwargs):
        # checkout_sessionで渡したクエリを取得
        order_id = request.GET.get('order_id')

        #id と現userでOrderオブジェクトのリストを取得
        orders = Order.objects.filter(user=request.user, id=order_id)

        # もし要素数が１でなければ以降に進まないようにここでreturn
        if len(orders) != 1:
            #好みでリダイレクトメッセージを表示しても良い
            return super().get(request, *args, **kwargs)
        
        # １つの要素を変数へ代入
        order = orders[0]

        # すでにis_confirmed=Trueなら以降には進まないようにここでreturn
        if order.is_confirmed:
            #好みでリダイレクトメッセージを表示しても良い
            return super().get(request, *args, **kwargs)        

        order.is_confirmed = True  # 注文確定
        order.save()
 
        # カート情報削除
        if 'cart' in request.session:
            del request.session['cart']
 
        return super().get(request, *args, **kwargs)
 
 
class PayCancelView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/cancel.html'
 
    def get(self, request, *args, **kwargs):
        # 現userの仮Orderオブジェクトのリストを取得
        orders = Order.objects.filter(user=request.user, is_confirmed=False)        

        for order in orders:
            # 在庫数と販売数を元の状態に戻す
            for elem in json.loads(order.items):
                item = Item.objects.get(pk=elem['pk'])
                item.sold_count -= elem['quantity']
                item.stock += elem['quantity']
                item.save()
        # 仮オーダーを全て削除
        orders.delete()
 
        return super().get(request, *args, **kwargs)
 
 
tax_rate = stripe.TaxRate.create(
    display_name='消費税',
    description='消費税',
    country='JP',
    jurisdiction='JP',
    percentage=settings.TAX_RATE * 100,
    inclusive=False,  # 外税を指定（内税の場合はTrue）
)
 
 
def create_line_item(unit_amount, name, quantity):
    return {
        'price_data': {
            'currency': 'JPY',
            'unit_amount': unit_amount,
            'product_data': {'name': name, }
        },
        'quantity': quantity,
        'tax_rates': [tax_rate.id]
    }
 
 
def check_profile_filled(profile):
    if profile.name is None or profile.name == '':
        return False
    elif profile.zipcode is None or profile.zipcode == '':
        return False
    elif profile.prefecture is None or profile.prefecture == '':
        return False
    elif profile.city is None or profile.city == '':
        return False
    elif profile.address1 is None or profile.address1 == '':
        return False
    return True
 
 
class PayWithStripe(LoginRequiredMixin, View):
 
    def post(self, request, *args, **kwargs):
        # プロフィールが埋まっているかどうか確認
        if not check_profile_filled(request.user.profile):
            messages.warning(request, '配送に必要なのでプロフィールを埋めて下さい。')
            return redirect('/profile/')
 
        cart = request.session.get('cart', None)
        if cart is None or len(cart) == 0:
            messages.error(request, 'カートが空です。')
            return redirect('/')
 
        items = []  # Orderモデル用に追記
        line_items = []
        for item_pk, quantity in cart['items'].items():
            item = Item.objects.get(pk=item_pk)
            line_item = create_line_item(
                item.price, item.name, quantity)
            line_items.append(line_item)
 
            # Orderモデル用に追記
            items.append({
                'pk': item.pk,
                'name': item.name,
                'image': str(item.image),
                'price': item.price,
                'quantity': quantity,
            })
 
            # 在庫をこの時点で引いておく、注文キャンセルの場合は在庫を戻す
            # 販売数も加算しておく
            item.stock -= quantity
            item.sold_count += quantity
            item.save()
 
        # 仮注文を作成（is_confirmed=False)
        order = Order.objects.create(
            user=request.user,
            uid=request.user.pk,
            items=json.dumps(items),
            shipping=serializers.serialize("json", [request.user.profile]),
            amount=cart['total'],
            tax_included=cart['tax_included_total']
        )
 
        checkout_session = stripe.checkout.Session.create(
            customer_email=request.user.email,
            payment_method_types=['card', 'konbini'],
            # The parameter is optional. The default value of expires_after_days is 3.
            payment_method_options={
             'konbini' : {
                'expires_after_days': 5,
                },
                },
            line_items=line_items,
            #配送料を選択する
            shipping_options=[
            {
             'shipping_rate_data': {
                 'type': 'fixed_amount',
                 'fixed_amount': {
                    'amount': 1000,
                    'currency': 'JPY',
                  },
             'display_name': 'お急ぎの方',
          # Delivers between 5-7 business days
             'delivery_estimate': {
                'minimum': {
                  'unit': 'business_day',
                  'value': 2,
                },
                'maximum': {
                  'unit': 'business_day',
                  'value': 7,
                },
              }
            }
          },
          {
            'shipping_rate_data': {
              'type': 'fixed_amount',
              'fixed_amount': {
                'amount': 500,
                'currency': 'JPY',
              },
              'display_name': 'ゆっくりでもいい方',
          # Delivers in exactly 1 business day
              'delivery_estimate': {
                'minimum': {
                  'unit': 'business_day',
                  'value': 7,
                },
                'maximum': {
                  'unit': 'business_day',
                  'value': 14,
                },
              }
            }
          },
            ],
            mode='payment',
            # success_url には、クエリで注文IDを渡しておく
            success_url=f'{settings.MY_URL}/pay/success/?order_id={order.pk}',
            cancel_url=f'{settings.MY_URL}/pay/cancel/',
        )
        return redirect(checkout_session.url)

