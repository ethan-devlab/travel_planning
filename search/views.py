# coding=utf-8

from django.http import JsonResponse
from .forms import ItineraryForm, SearchForm
from .models import Itinerary, Tag, Location, Expense
from django.shortcuts import render, get_object_or_404, redirect


def search_itineraries(request):
    form = SearchForm(request.GET or None)
    itineraries = Itinerary.objects.filter(is_public=True)

    if form.is_valid():
        q = form.cleaned_data.get("q")
        travel_method = form.cleaned_data.get("travel_method")
        budget = form.cleaned_data.get("budget")
        location = form.cleaned_data.get("location")
        transport = form.cleaned_data.get("transport")
        start_date = form.cleaned_data.get("start_date")
        end_date = form.cleaned_data.get("end_date")

        if q:
            itineraries = itineraries.filter(title__icontains=q)

        if travel_method:
            itineraries = itineraries.filter(locations__travel_method__icontains=travel_method)

        if budget:
            itineraries = itineraries.filter(budget__icontains=budget)

        if location:
            itineraries = itineraries.filter(locations__name__icontains=location)

        if transport:
            itineraries = itineraries.filter(locations__note__icontains=transport)

        if start_date:
            itineraries = itineraries.filter(start_date__gte=start_date)

        if end_date:
            itineraries = itineraries.filter(end_date__lte=end_date)

        itineraries = itineraries.distinct()

    return render(request, 'search_bar.html', {'form': form, 'results': itineraries})


def itinerary_detail(request, pk):
    itinerary = get_object_or_404(Itinerary, pk=pk, is_public=True)
    return render(request, 'itinerary_detail.html', {'itinerary': itinerary})


def template_list(request):
    templates = Itinerary.objects.filter(is_public=True)
    return render(request, 'template_list.html', {'templates': templates})


def api_itinerary_search(request):
    q = request.GET.get("q", "")
    tags = request.GET.getlist("tags")

    queryset = Itinerary.objects.filter(is_public=True)

    if q:
        queryset = queryset.filter(title__icontains=q)

    for f in tags:
        if ":" not in f:
            continue
        key, val = f.split(":", 1)

        if key == "location":
            queryset = queryset.filter(locations__name__icontains=val)
        elif key == "travel_method":
            queryset = queryset.filter(locations__travel_method__icontains=val)
        elif key == "transport":
            queryset = queryset.filter(locations__travel_method__icontains=val)
        elif key == "budget":
            try:
                budget_value = float(val)
                queryset = queryset.filter(budget__lte=budget_value)
            except ValueError:
                pass
        elif key == "start_date":
            queryset = queryset.filter(start_date__gte=val)
        elif key == "end_date":
            queryset = queryset.filter(end_date__lte=val)

    queryset = queryset.distinct()

    data = [{
        "title": i.title,
        "start_date": i.start_date,
        "end_date": i.end_date,
        "budget": str(i.budget),
        "tags": [tag.name for tag in i.tags.all()],
    } for i in queryset]

    return JsonResponse(data, safe=False)


def create_itinerary(request):
    if request.method == 'POST':
        form = ItineraryForm(request.POST)
        if form.is_valid():
            itinerary = form.save(commit=False)
            itinerary.owner = request.user
            itinerary.save()
            form.save_m2m()

            # ➕ 自訂標籤
            custom_tags_str = request.POST.get("custom_tags", "")
            if custom_tags_str:
                tag_names = [tag.strip() for tag in custom_tags_str.split(",") if tag.strip()]
                for name in tag_names:
                    tag_obj, _ = Tag.objects.get_or_create(name=name)
                    itinerary.tags.add(tag_obj)

            # 🔁 多地點
            location_names = request.POST.getlist('location_name[]')
            travel_methods = request.POST.getlist('travel_method[]')
            transport_notes = request.POST.getlist('transport_note[]')
            visit_dates = request.POST.getlist('visit_date[]')

            for i in range(len(location_names)):
                if location_names[i] and travel_methods[i] and visit_dates[i]:
                    loc = Location.objects.create(
                        itinerary=itinerary,
                        name=location_names[i],
                        travel_method=travel_methods[i],
                        note=transport_notes[i],
                        visit_date=visit_dates[i],
                        latitude=0.0,
                        longitude=0.0
                    )
                    # 支出處理（和 edit_itinerary 相同）
                    expense_types = request.POST.getlist(f'expense_type_{i}[]')
                    expense_amounts = request.POST.getlist(f'expense_amount_{i}[]')
                    for etype, amount in zip(expense_types, expense_amounts):
                        if etype and amount:
                            Expense.objects.create(
                                location=loc,
                                expense_type=etype,
                                amount=amount
                            )

            return redirect('search')
    else:
        form = ItineraryForm()
    return render(request, 'create_itinerary.html', {'form': form})


def my_itineraries(request):
    itineraries = Itinerary.objects.filter(owner=request.user).order_by('-updated_at')
    return render(request, 'my_itineraries.html', {'itineraries': itineraries})


def edit_itinerary(request, pk):
    itinerary = get_object_or_404(Itinerary, pk=pk, owner=request.user)
    locations = itinerary.locations.all()

    if request.method == 'POST':
        form = ItineraryForm(request.POST, instance=itinerary)
        if form.is_valid():
            itinerary = form.save()

            # 更新標籤
            itinerary.tags.clear()
            tag_str = request.POST.get('custom_tags', '')
            for tag_name in [t.strip() for t in tag_str.split(',') if t.strip()]:
                tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
                itinerary.tags.add(tag_obj)

            # 清除原有地點與支出
            itinerary.locations.all().delete()

            # 地點資料
            location_names = request.POST.getlist('location_name[]')
            travel_methods = request.POST.getlist('travel_method[]')
            transport_notes = request.POST.getlist('transport_note[]')
            visit_dates = request.POST.getlist('visit_date[]')

            for i in range(len(location_names)):
                if location_names[i] and travel_methods[i] and visit_dates[i]:
                    loc = Location.objects.create(
                        itinerary=itinerary,
                        name=location_names[i],
                        travel_method=travel_methods[i],
                        note=transport_notes[i],
                        visit_date=visit_dates[i],
                        latitude=0.0,
                        longitude=0.0,
                    )
                    # 對應支出項目
                    expense_types = request.POST.getlist(f'expense_type_{i}[]')
                    expense_amounts = request.POST.getlist(f'expense_amount_{i}[]')
                    for etype, amount in zip(expense_types, expense_amounts):
                        if etype and amount:
                            Expense.objects.create(
                                location=loc,
                                expense_type=etype,
                                amount=amount
                            )

            return redirect('my_itineraries')
    else:
        initial = {
            'custom_tags': ', '.join([t.name for t in itinerary.tags.all()])
        }
        form = ItineraryForm(instance=itinerary, initial=initial)

    return render(request, 'edit_itinerary.html', {
        'form': form,
        'locations': locations
    })


def delete_itinerary(request, pk):
    itinerary = get_object_or_404(Itinerary, pk=pk, owner=request.user)
    itinerary.delete()
    return redirect('my_itineraries')
