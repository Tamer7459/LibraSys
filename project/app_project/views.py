from django.shortcuts import render , redirect
from .models import *
from .forms import *
# Create your views here.


def index(request):
    if request.method == 'POST':
        form = BookForm(request.POST , request.FILES)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = BookForm()
    context={
        'categories': categories.objects.all(),
        'books': book.objects.all(),
        'form': BookForm(),
        'categoryform': CategoryForm(),
        'allbooks': book.objects.filter(active=True).count(),
        'booksolid': book.objects.filter(status='solid').count(),
        'bookrental': book.objects.filter(status='rental').count(),
        'bookavailable': book.objects.filter(status='available').count(),


        
    }
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = CategoryForm()
    return render(request, 'pages/index.html', context)


def books(request):
    search = book.objects.all()
    title = None
    if 'search_name' in request.GET:
        title = request.GET['search_name']
        if title:
            search = search.filter(title__icontains=title)
        
    else:
        books = book.objects.all()
    context={
        'categories': categories.objects.all(),
        'books': search,
    }
    return render(request, 'pages/books.html', context)

def update(request, id):
    book_id = book.objects.get(id=id)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book_id)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = BookForm(instance=book_id)
    context = {
        'form': form,
        'book': book_id
    }
    return render(request, 'pages/update.html', context)

def delete(request, id):
    book_instance = book.objects.get(id=id)
    if request.method == 'POST':
        book_instance.delete()
        return redirect('index')
    context = {
        'book': book_instance
    }
    return render(request, 'pages/delete.html', context)