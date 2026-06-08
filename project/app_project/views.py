import urllib.request
import os
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.db.models import ProtectedError
from .models import *
from .forms import *


def download_image_from_url(url):
    try:
        result = urllib.request.urlopen(url, timeout=10)
        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(result.read())
        img_temp.flush()
        ext = os.path.splitext(url.split('/')[-1].split('?')[0])[1] or '.jpg'
        filename = f"{uuid.uuid4().hex}{ext}"
        return filename, File(img_temp)
    except Exception:
        return None, None


def index(request):
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
                # Download from URL if provided
                for field_name in ['photo_book', 'photo_author']:
                    url = book_form.cleaned_data.get(f'{field_name}_url')
                    if url and not request.FILES.get(field_name):
                        filename, file_obj = download_image_from_url(url)
                        if filename and file_obj:
                            getattr(instance, field_name).save(filename, file_obj, save=False)
                instance.save()
                return redirect('index')

    context = {
        'categories': categories.objects.all(),
        'books': book.objects.all(),
        'form': BookForm(),
        'categoryform': CategoryForm(),
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
            for field_name in ['photo_book', 'photo_author']:
                url = form.cleaned_data.get(f'{field_name}_url')
                if url and not request.FILES.get(field_name):
                    filename, file_obj = download_image_from_url(url)
                    if filename and file_obj:
                        getattr(instance, field_name).save(filename, file_obj, save=False)
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
