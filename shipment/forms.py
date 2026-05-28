from django import forms
from .models import Shipment


class ShipmentForm(forms.ModelForm):

    class Meta:
        model = Shipment

   
        fields = [
            'shipment_id',
            'origin',
            'destination',
            'carrier',
            'departure',
            'eta',
        ]

        widgets = {
            'shipment_id': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'e.g. SHP-2001'
            }),
            'origin': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'e.g. Mumbai'
            }),
            'destination': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'e.g. Delhi'
            }),
            'carrier': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'e.g. Maersk'
            }),
            'departure': forms.DateTimeInput(
                attrs={
                    'class': 'form-control form-control-lg',
                    'type': 'datetime-local'
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'eta': forms.DateInput(attrs={
                'class': 'form-control form-control-lg',
                'type': 'date'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['departure'].input_formats = ('%Y-%m-%dT%H:%M',)