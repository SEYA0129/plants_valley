from django.shortcuts import render
from django.views.generic import ListView, DetailView
from base.models import Item, Category, Tag
 
 
class IndexListView(ListView):
    model = Item
    template_name = 'pages/index.html'
    queryset = Item.objects.filter(is_published=True)

    def get_queryset(self):
        query = super().get_queryset()
        order_by_price = self.request.GET.get('order_by_price', 0)
        if order_by_price == '1':
            query = query.order_by('price')
        elif order_by_price == '2':
            query = query.order_by('-price')
        return query

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_by_price = self.request.GET.get('order_by_price', 0)
        if order_by_price == '1':
            context['ascending'] = True
        elif order_by_price == '2':
            context['descending'] = True
        return context
 
class ItemDetailView(DetailView):
    model = Item
    template_name = 'pages/item.html'
 
 
class CategoryListView(ListView):
    model = Item
    template_name = 'pages/list.html'
    paginate_by = 4
 
    def get_queryset(self):
        self.category = Category.objects.get(slug=self.kwargs['pk'])
        return Item.objects.filter(is_published=True, category=self.category)
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Category #{self.category.name}'
        return context
 
 
class TagListView(ListView):
    model = Item
    template_name = 'pages/list.html'
    paginate_by = 4
 
    def get_queryset(self):
        self.tag = Tag.objects.get(slug=self.kwargs['pk'])
        return Item.objects.filter(is_published=True, tags=self.tag)
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Tag #{self.tag.name}"
        return context
