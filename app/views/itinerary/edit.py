# coding=utf-8

from ...forms import ItineraryForm
from ...models import Itinerary, Tag, Location, Expense
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.timezone import get_current_timezone
from datetime import datetime


@login_required
def edit_itinerary(request, id):
    itinerary = get_object_or_404(Itinerary, pk=id, owner=request.user)
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
            tz = get_current_timezone()

            for i in range(len(location_names)):
                if location_names[i] and travel_methods[i] and visit_dates[i]:
                    dt = datetime.strptime(visit_dates[i], "%Y-%m-%dT%H:%M").astimezone(tz)
                    loc = Location.objects.create(
                        itinerary=itinerary,
                        name=location_names[i],
                        travel_method=travel_methods[i],
                        note=transport_notes[i],
                        visit_date=dt,
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
