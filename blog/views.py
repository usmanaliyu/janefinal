from django.shortcuts import render, redirect
from django.views.generic import ListView, TemplateView, DetailView
from .models import Blog, BlogComment
from .forms import BlogCommentForm
from core.models import Category
from django.contrib import messages
from core.models import Item
from core.forms import ReviewForm, CheckoutForm, RefundForm, CouponForm, ContactForm, NewsletterForm
from django.db.models import Q
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .serializers import BlogSerializer
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
# Create your views here.


class BlogView(ListAPIView):
    queryset = Blog.objects.all().order_by('-time')
    permission_classes = (AllowAny,)
    serializer_class = BlogSerializer


class BlogDetailView(RetrieveAPIView):
    queryset = Blog.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = BlogSerializer
    lookup_field = 'slug'
