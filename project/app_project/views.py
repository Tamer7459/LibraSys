import os
import uuid
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.files.base import ContentFile
from django.db.models import ProtectedError
from .models import *
from .forms import *


def download_image_from_url(url):
    try:
        result = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        if result.status_code != 200:
            return None, None, f'رابط الصورة لا يعمل (خطأ {result.status_code})'
        data = result.content
        ext = os.path.splitext(url.split('/')[-1].split('?')[0])[1] or '.jpg'
        filename = f"{uuid.uuid4().hex}{ext}"
        return filename, ContentFile(data), None
    except Exception as e:
        return None, None, f'فشل تحميل الصورة: {str(e)}'


def index(request):
    book_form = BookForm()
    cat_form = CategoryForm()

    if request.method == 'POST':
        if 'name' in request.POST:
            cat_form = CategoryForm(request.POST)
            if cat_form.is_valid():
                cat_form.save()
                return redirect('index')
        else:
            book_form = BookForm(request.POST, request.FILES)
            if book_form.is_valid():
                instance = book_form.save(commit=False)
                dl_ok = True
                for field_name in ['photo_book', 'photo_author']:
                    url = book_form.cleaned_data.get(f'{field_name}_url')
                    if url and not request.FILES.get(field_name):
                        filename, file_obj, error = download_image_from_url(url)
                        if filename and file_obj:
                            getattr(instance, field_name).save(filename, file_obj, save=False)
                        elif error:
                            messages.error(request, error)
                            dl_ok = False
                if dl_ok:
                    instance.save()
                    return redirect('index')

    context = {
        'categories': categories.objects.all(),
        'books': book.objects.all(),
        'form': book_form,
        'categoryform': cat_form,
        'allbooks': book.objects.filter(active=True).count(),
        'booksolid': book.objects.filter(status='solid').count(),
        'bookrental': book.objects.filter(status='rental').count(),
        'bookavailable': book.objects.filter(status='available').count(),
    }
    return render(request, 'pages/index.html', context)


def books(request):
    search = book.objects.all()
    title = None
    if 'search_name' in request.GET:
        title = request.GET['search_name']
        if title:
            search = search.filter(title__icontains=title)
    context = {
        'categories': categories.objects.all(),
        'books': search,
        'form': BookForm(),
        'categoryform': CategoryForm(),
    }
    return render(request, 'pages/books.html', context)


def update(request, id):
    book_id = get_object_or_404(book, id=id)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book_id)
        if form.is_valid():
            instance = form.save(commit=False)
            dl_ok = True
            for field_name in ['photo_book', 'photo_author']:
                url = form.cleaned_data.get(f'{field_name}_url')
                if url and not request.FILES.get(field_name):
                    filename, file_obj, error = download_image_from_url(url)
                    if filename and file_obj:
                        getattr(instance, field_name).save(filename, file_obj, save=False)
                    elif error:
                        messages.error(request, error)
                        dl_ok = False
            if dl_ok:
                instance.save()
                return redirect('index')
    else:
        form = BookForm(instance=book_id)
    context = {
        'form': form,
        'book': book_id,
    }
    return render(request, 'pages/update.html', context)


def delete(request, id):
    book_instance = get_object_or_404(book, id=id)
    if request.method == 'POST':
        book_instance.delete()
        return redirect('index')
    context = {
        'book': book_instance,
    }
    return render(request, 'pages/delete.html', context)


def delete_category(request, id):
    category = get_object_or_404(categories, id=id)
    if book.objects.filter(category=category).exists():
        messages.error(request, f'لا يمكن حذف التصنيف "{category.name}" لأنه يحتوي على كتب')
        return redirect('index')
    category.delete()
    messages.success(request, f'تم حذف التصنيف "{category.name}" بنجاح')
    return redirect('index')
