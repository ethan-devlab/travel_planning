# coding=utf-8

from ...forms import ItineraryForm
from ...models import Tag, Location, Expense
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.timezone import get_current_timezone
from django.contrib import messages
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

            tags_str = request.POST.get("custom_tags", "")
            if tags_str:
                tag_names = [tag.strip() for tag in tags_str.split(",") if tag.strip()]
                for name in tag_names:
                    tag_obj, _ = Tag.objects.get_or_create(name=name)
                    itinerary.tags.add(tag_obj)
            
            collaborators_str = request.POST.get("collaborators", "")
            if collaborators_str:
                collaborator_usernames = [username.strip() for username in collaborators_str.split(",") if username.strip()]
                for username in collaborator_usernames:
                    try:
                        user = request.user.__class__.objects.get(username=username)
                        itinerary.collaborators.add(user)
                    except request.user.__class__.DoesNotExist:
                        messages.error(request, f"User '{username}' does not exist.")

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
                        visit_date=datetime.strptime(visit_dates[i], "%Y-%m-%dT%H:%M").astimezone(tz),
                        latitude=0.0,
                        longitude=0.0
                    )

                    expense_types = request.POST.getlist(f'expense_type_{i}[]')
                    expense_amounts = request.POST.getlist(f'expense_amount_{i}[]')
                    for etype, amount in zip(expense_types, expense_amounts):
                        if etype and amount:
                            Expense.objects.create(
                                location=loc,
                                expense_type=etype,
                                amount=amount
                            )

            return redirect('itinerary_detail', id=itinerary.id)
    else:
        form = ItineraryForm()
    return render(request, 'itinerary/create_itinerary.html', {'form': form})
