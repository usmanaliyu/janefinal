from django.shortcuts import render, redirect
from django.views.generic import ListView, TemplateView, DetailView
from .models import Blog, BlogComment
from .forms import BlogCommentForm
from core.models import Category
from django.contrib import messages
from core.models import Item
from core.forms import ReviewForm, CheckoutForm, RefundForm, CouponForm, ContactForm, NewsletterForm
from django.db.models import Q
# Create your views here.


class BlogView(ListView):
    model = Blog
    context_object_name = 'blog'
    paginate_by = 16
    template_name = 'blog-grid.html'

    def get_context_data(self, **kwargs):
        context = super(BlogView, self).get_context_data(**kwargs)
        context.update({

            'category_list': Category.objects.all()
        })
        return context


class BlogDetailView(DetailView):
    model = Blog
    context_object_name = 'blog'
    template_name = 'blog-single.html'

    def get_context_data(self, **kwargs):
        context = super(BlogDetailView, self).get_context_data(**kwargs)
        context.update({
            'form': BlogCommentForm(),
            'category_list': Category.objects.all()
        })
        return context

    def post(self, request, *args, **kwargs):
        form = BlogCommentForm(self.request.POST or None)

        if form.is_valid():
            comment = form.cleaned_data.get('comment')
            post = self.get_object()
            user = self.request.user
            blog = BlogComment(
                comment=comment,
                user=user,
                post=post
            )
            blog.save()
            messages.success(
                self.request, "Yay!! you are amazing for leaving a comment")
            return redirect('blog:blog-detail', slug=post.slug)
        messages.error(self.request, "You didn't leave a comment. o wrong nau")
        return redirect('blog:blog-detail', slug=self.get_object().slug)

    def get_object(self, **kwargs):
        qs = super().get_object(**kwargs)
        return qs


class SearchListView(ListView):
    model = Item
    context_object_name = 'queryset'

    template_name = "search.html"

    def get_context_data(self, **kwargs):
        context = super(SearchListView, self).get_context_data(**kwargs)
        query = self.request.GET.get('q')
        context.update({

            "category_list": Category.objects.all(),
            'query': query
        })

        return context

    def get_queryset(self):
        query = self.request.GET.get('q', None)
        if query is not None:
            search = Q(title__icontains=query) | Q(
                description__icontains=query)
            queryset = Item.objects.filter(search).distinct()[:20]
            return queryset
        return render(self.request, 'search.html')
