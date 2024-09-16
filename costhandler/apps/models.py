from django.db import models
from django.contrib.auth.models import User

class Pricelist(models.Model):
    id = models.AutoField(primary_key=True)
    pricelist_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)  # New description field
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_dt = models.DateTimeField(auto_now_add=True)  # Add created_dt field

    def __str__(self):
        return self.pricelist_name

class PricelistEntry(models.Model):
    id = models.AutoField(primary_key=True)
    group_name = models.CharField(max_length=100, null=True, blank=True)  # Allow null
    item_name = models.CharField(max_length=300)  # Change entry_name to item_name and set max length to 300
    pricelist = models.ForeignKey(Pricelist, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10)
    unit = models.CharField(max_length=10, null=True, blank=True)  # Allow null
    min_duration = models.IntegerField(null=True, blank=True)  # Allow null
    created_dt = models.DateTimeField(auto_now_add=True)  # Add created_dt field

    def __str__(self):
        return self.item_name

class List(models.Model):
    id = models.AutoField(primary_key=True)
    created_dt = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True, blank=True)
    comment = models.CharField(max_length=500, null=True, blank=True)  # Add comment field
    extra_costs = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)  # Add extra_costs field
    extra_costs_currency = models.CharField(max_length=10, null=True, blank=True, default='EUR')  # Add extra_costs_currency field

    def __str__(self):
        return self.name if self.name else "Unnamed List"
    
class ListEntry(models.Model):
    id = models.AutoField(primary_key=True)
    pricelist_entry = models.ForeignKey(PricelistEntry, on_delete=models.CASCADE)
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    created_dt = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField(default=1)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    comment = models.CharField(max_length=500, null=True, blank=True)
    extra_costs = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    person = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.pricelist_entry.item_name

    @property
    def total_cost(self):
        # Handle cases where price, quantity, or extra_costs might be missing
        price = self.pricelist_entry.price or 0
        quantity = self.quantity or 1
        extra_cost = self.extra_costs or 0
        return price * quantity + extra_cost