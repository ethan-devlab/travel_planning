# coding=utf-8

from ...forms import ItineraryForm
from ...models import Itinerary, Tag, Location, Expense
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.timezone import get_current_timezone
from django.http import HttpResponseForbidden
from django.contrib import messages
from datetime import datetime


@login_required
def edit_itinerary(request, id):
    itinerary = get_object_or_404(Itinerary, pk=id)
    if not itinerary.is_public and itinerary.owner != request.user and request.user not in itinerary.collaborators.all():
        return HttpResponseForbidden("You do not have permission to view this itinerary.")

    locations = itinerary.locations.all()

    if request.method == 'POST':
        form = ItineraryForm(request.POST, instance=itinerary)
        if form.is_valid():
            itinerary = form.save()

            # 更新標籤
            itinerary.tags.clear()
            tags_str = request.POST.get('custom_tags', '')
            if tags_str:
                tag_names = [t.strip() for t in tags_str.split(',') if t.strip()]
                for tag_name in tag_names:
                    tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
                    itinerary.tags.add(tag_obj)

            collaborators_str = request.POST.get("collaborators", "")
            if collaborators_str:
                collaborator_usernames = [username.strip() for username in collaborators_str.split(",") if username.strip()]
                for username in collaborator_usernames:
                    try:
                        user = request.user.__class__.objects.get(username=username)
                        itinerary.collaborators.add(user)
                    except request.user.__class__.DoesNotExist:
                        messages.error(request, f"用戶 「{username}」 不存在.")

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
                    loc = Location.objects.create(
                        itinerary=itinerary,
                        name=location_names[i],
                        travel_method=travel_methods[i],
                        note=transport_notes[i],
                        visit_date=datetime.strptime(visit_dates[i], "%Y-%m-%dT%H:%M").astimezone(tz),
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

            messages.success(request, f'行程 「{itinerary.title}」 已成功更新！')
            return redirect(request.path)
    else:
        initial = {
            'custom_tags': ', '.join([t.name for t in itinerary.tags.all()]),
            'collaborators': ', '.join([c.username for c in itinerary.collaborators.all()])
        }
        form = ItineraryForm(instance=itinerary, initial=initial)

    return render(request, 'itinerary/edit_itinerary.html', {
        'form': form,
        'locations': locations
    })
