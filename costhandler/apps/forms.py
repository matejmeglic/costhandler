from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import List, ListEntry, PricelistEntry
from django.forms import modelformset_factory, BaseModelFormSet


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class PricelistUploadForm(forms.Form):
    pricelist_name = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea, required=False)  # Add description field
    csv_file = forms.FileField()




# Form for creating a new List
class ListForm(forms.ModelForm):
    class Meta:
        model = List
        fields = ['name', 'comment', 'extra_costs', 'extra_costs_currency']

class ListEntryForm(forms.ModelForm):
    pricelist_entry = forms.ModelChoiceField(
        queryset=PricelistEntry.objects.none(),  # Initially empty, will be populated dynamically
        empty_label="---",  # Displayed as the first option
        widget=forms.Select
    )
    
    class Meta:
        model = ListEntry
        fields = ['pricelist_entry', 'quantity', 'extra_costs', 'person', 'comment']
        widgets = {
            'quantity': forms.NumberInput(attrs={'step': '1'}),
            'extra_costs': forms.NumberInput(attrs={'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        pricelist_entries = kwargs.pop('pricelist_entries', PricelistEntry.objects.none())
        super().__init__(*args, **kwargs)
        # Filter the queryset to only include entries from active pricelists
        self.fields['pricelist_entry'].queryset = pricelist_entries.filter(pricelist__is_active=True)
        # Set choices explicitly, including the empty choice
        self.fields['pricelist_entry'].choices = [('', '---')] + [
            (entry.pk, f"{entry.pricelist.pricelist_name} - {entry.group_name or 'No Group'} - {entry.item_name} - {entry.price} {entry.currency}") 
            for entry in pricelist_entries if entry.pricelist.is_active
        ]




ListEntryFormSet = modelformset_factory(
    ListEntry,
    form=ListEntryForm,
    extra=20,
    can_delete=True
)
