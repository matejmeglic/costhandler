from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
import csv
from django.contrib import messages
from .forms import UserRegistrationForm, PricelistUploadForm, PricelistUploadForm
from .models import Pricelist, PricelistEntry, List, ListEntry
from django.forms import modelformset_factory
import json
from django.shortcuts import get_object_or_404
from .forms import ListForm, ListEntryFormSet



def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Redirect to a home page or dashboard
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def profile(request):
    user = request.user
    pricelists = Pricelist.objects.filter(user=user)

    if request.method == 'POST':
        # Update is_active status for each pricelist
        for pricelist in pricelists:
            is_active = request.POST.get(f'pricelist_{pricelist.id}_is_active') == 'on'
            pricelist.is_active = is_active
            pricelist.save()
        return redirect('profile')  # Redirect to the profile page after saving changes

    return render(request, 'profile.html', {'pricelists': pricelists})

@login_required
def upload_pricelist(request):
    if request.method == 'POST':
        form = PricelistUploadForm(request.POST, request.FILES)
        if form.is_valid():
            if 'csv_file' not in request.FILES:
                messages.error(request, 'No file uploaded. Please upload a CSV file.')
                return redirect('upload_pricelist')
            
            csv_file = request.FILES['csv_file']
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.reader(decoded_file)
            header = next(reader)
            processed_data = []
            for row in reader:
                processed_data.append(row)
                
            # Store the processed data, form data, and pricelist name in the session
            request.session['processed_data'] = processed_data
            request.session['header'] = header
            request.session['pricelist_name'] = form.cleaned_data.get('pricelist_name')
            request.session['description'] = form.cleaned_data.get('description')  # Add description

            messages.success(request, f'Successfully processed {len(processed_data)} rows.')
            return redirect('processed_data')  # Redirect to the new view
        else:
            messages.error(request, 'There was an error with the form. Please try again.')
    else:
        form = PricelistUploadForm()
    return render(request, 'upload.html', {'form': form})


@login_required
def processed_data(request):
    processed_data = request.session.get('processed_data', [])
    header = request.session.get('header', [])
    pricelist_name = request.session.get('pricelist_name', 'Unknown Pricelist')
    return render(request, 'processed_data.html', {
        'processed_data': processed_data,
        'header': header,
        'pricelist_name': pricelist_name
    })

@login_required
def save_pricelist(request):
    if request.method == 'POST':
        processed_data = request.session.get('processed_data', [])
        pricelist_name = request.session.get('pricelist_name', 'Unknown Pricelist')
        description = request.session.get('description', '')  # Retrieve description from the session

        # Create and save the Pricelist with the description
        PL = Pricelist(pricelist_name=pricelist_name, description=description, user=request.user)
        PL.save()

        # Create and save PricelistEntries
        for item in processed_data:
            PLE = PricelistEntry(
                group_name=item[0],
                item_name=item[1],
                pricelist=PL,
                price=item[2],
                currency=item[3],
                unit=item[4],
                min_duration=item[5]
            )
            PLE.save()

        # Clear the session data
        request.session.pop('processed_data', None)
        request.session.pop('pricelist_name', None)
        request.session.pop('description', None)

        return render(request, 'pricelist_saved.html')
    else:
        return render(request, 'error.html')

@login_required
def pricelist_saved(request):
    return render(request, 'pricelist_saved.html')

@login_required
def error(request):
    return render(request, 'error.html')


@login_required
def create_list(request):
    pricelist_entries = PricelistEntry.objects.filter(pricelist__user=request.user)
    
    if request.method == 'POST':
        list_form = ListForm(request.POST)
        list_entry_formset = ListEntryFormSet(
            request.POST,
            queryset=ListEntry.objects.none(),  # No pre-existing entries
            form_kwargs={'pricelist_entries': pricelist_entries}
        )

        if list_form.is_valid() and list_entry_formset.is_valid():
            new_list = list_form.save(commit=False)
            new_list.user = request.user
            new_list.save()

            saved_count = 0
            for form in list_entry_formset:
                if form.cleaned_data and form.cleaned_data.get('pricelist_entry'):
                    list_entry = form.save(commit=False)
                    list_entry.list = new_list
                    list_entry.save()
                    saved_count += 1
                    if saved_count >= 20:  # Only save up to 20 entries
                        break
                    
            return redirect('list_detail', list_id=new_list.id)
    else:
        list_form = ListForm()
        list_entry_formset = ListEntryFormSet(
            queryset=ListEntry.objects.none(),  # Empty queryset
            form_kwargs={'pricelist_entries': pricelist_entries}
        )

    return render(request, 'new-list.html', {
        'list_form': list_form,
        'list_entry_formset': list_entry_formset,
        'pricelist_entries': pricelist_entries,
    })

@login_required
def list_detail(request, list_id):
    list_instance = List.objects.get(id=list_id, user=request.user)
    list_entries = ListEntry.objects.filter(list=list_instance)
    
    # Calculate total cost
    total_cost = sum(
        entry.pricelist_entry.price * entry.quantity + (entry.extra_costs or 0)
        for entry in list_entries
    )

    # Breakdown by person
    person_breakdown = {}
    for entry in list_entries:
        person = entry.person or 'Unknown'
        if person not in person_breakdown:
            person_breakdown[person] = 0
        person_breakdown[person] += entry.pricelist_entry.price * entry.quantity + (entry.extra_costs or 0)

    # Sort breakdown by value in descending order, with "Unknown" last
    sorted_person_breakdown = sorted(
        person_breakdown.items(),
        key=lambda item: (item[0] == 'Unknown', -item[1])
    )

    context = {
        'list_instance': list_instance,
        'list_entries': list_entries,
        'total_cost': total_cost,
        'currency': list_instance.extra_costs_currency or 'EUR',
        'person_breakdown': sorted_person_breakdown
    }

    return render(request, 'list_detail.html', context)

@login_required
def list_overview(request):
    # Retrieve all lists for the user, ordered by creation date descending
    lists = List.objects.filter(user=request.user).order_by('-created_dt')
    
    # Calculate total costs for each list
    list_totals = []
    for list_instance in lists:
        list_entries = ListEntry.objects.filter(list=list_instance)
        total_cost = sum(entry.pricelist_entry.price * entry.quantity + (entry.extra_costs or 0) for entry in list_entries)
        list_totals.append({
            'list': list_instance,
            'total_cost': total_cost,
        })

    return render(request, 'list_overview.html', {
        'list_totals': list_totals,
    })

@login_required
def pricelists_list(request):
    # Retrieve all active pricelists for the user
    pricelists = Pricelist.objects.filter(user=request.user, is_active=True)
    return render(request, 'pricelists_list.html', {'pricelists': pricelists})

@login_required
def pricelist_detail(request, pricelist_id):
    # Retrieve the specific pricelist and its entries
    pricelist = get_object_or_404(Pricelist, id=pricelist_id, user=request.user)
    pricelist_entries = PricelistEntry.objects.filter(pricelist=pricelist)
    return render(request, 'pricelist_detail.html', {
        'pricelist': pricelist,
        'pricelist_entries': pricelist_entries
    })