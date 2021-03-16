from django import forms

class ReservationForm(forms.Form):
    reserve_date = forms.DataTimeField(required=True)