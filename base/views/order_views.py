from django.views.generic import ListView, DetailView
from base.models import Order
import json
from django.contrib.auth.mixins import LoginRequiredMixin
 
 
class OrderIndexView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'pages/orders.html'
    ordering = '-created_at'
 
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
 
 
class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'pages/order.html'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        try:
            # Ensure that obj.items and obj.shipping are JSON strings
            context["items"] = json.loads(obj.items) if isinstance(obj.items, str) else obj.items
            context["shipping"] = json.loads(obj.shipping) if isinstance(obj.shipping, str) else obj.shipping
        except (TypeError, json.JSONDecodeError) as e:
            # Handle errors if needed
            context["items"] = []
            context["shipping"] = []
            # Log error if necessary
        return context
