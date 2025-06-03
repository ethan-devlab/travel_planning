# coding=utf-8

from ...forms import ItineraryForm
from ...models import Tag, Location, Expense
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.timezone import get_current_timezone
from datetime import datetime


@login_required
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
            tz = get_current_timezone()

            for i in range(len(location_names)):
                if location_names[i] and travel_methods[i] and visit_dates[i]:
                    loc = Location.objects.create(
                        itinerary=itinerary,
                        name=location_names[i],
                        travel_method=travel_methods[i],
                        note=transport_notes[i],
                        visit_date=datetime.astimezone(tz).strftime(visit_dates[i], "%Y-%m-%dT%H:%M"),
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
