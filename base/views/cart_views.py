from django.shortcuts import redirect
from django.conf import settings
from django.views.generic import View, ListView
from base.models import Item
from collections import OrderedDict #python標準ライブラリ
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages


class CartListView(LoginRequiredMixin, ListView):
    model = Item
    template_name = 'pages/cart.html'

    def get_queryset(self): #ListViewが持ってるメソッドをオーバーライド
        cart = self.request.session.get('cart', None)
        if cart is None or len(cart) == 0:
            return redirect('/')
        self.queryset = []
        self.total = 0
        for item_pk, quantity in cart['items'].items():
            obj = Item.objects.get(pk=item_pk)
            obj.quantity = quantity
            obj.subtotal = int(obj.price * quantity)
            self.queryset.append(obj)
            self.total += obj.subtotal
        self.tax_included_total = int(self.total * (settings.TAX_RATE + 1))
        cart['total'] = self.total
        cart['tax_included_total'] = self.tax_included_total
        self.request.session['cart'] = cart
        return super().get_queryset()

    def get_context_data(self, **kwargs): #get_context_dataはListViewが元々持ってるメソッド。それを上書きしていく
        context = super().get_context_data(**kwargs) #元々のメソッド。HTMLのobject_listとして使える
        try:
            context["total"] = self.total
            context["tax_included_total"] = self.tax_included_total
        except Exception:
            pass
        return context


class AddCartView(LoginRequiredMixin, View):
    
    def post(self, request): #リクエストのメソッドに応じた処理82
        item_pk = request.POST.get('item_pk')
        item = Item.objects.get(pk=item_pk) #追加2022.9.17
        quantity = int(request.POST.get('quantity'))
        cart = request.session.get('cart', None)
        if cart is None or len(cart) == 0:
            items = OrderedDict() #辞書の順番も保持されるらしい82
            cart = {'items': items}
        if item_pk in cart['items']:
            cart['items'][item_pk] += quantity
        else:
            cart['items'][item_pk] = quantity
        if item.stock < cart['items'][item_pk]: #追加2022.9.17~61行まで
            messages.error(self.request, '大変申し訳ございません。在庫数を超えてしまったようです。お手数をおかけしますが、もう一度最初からやりなおしてください。')
            if 'cart' in request.session:
                del request.session['cart']
            return redirect('/cart/')
        if quantity <= 0 : #追加2022.9.19~64行まで
            messages.info(self.request, '申し訳ございません。1以上の数値を入力してください。')
            return redirect('/cart/')
        request.session['cart'] = cart
        return redirect('/cart/')


@login_required
def remove_from_cart(request, pk):
    cart = request.session.get('cart', None)
    if cart is not None:
        del cart['items'][pk]
        request.session['cart'] = cart
    return redirect('/cart/')