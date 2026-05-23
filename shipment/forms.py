from django import forms
from .models import Shipment


class ShipmentForm(forms.ModelForm):

    class Meta:

        model = Shipment

        fields = '__all__'

        widgets = {

            'shipment_id': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-lg',
                    'placeholder': 'Enter Shipment ID'
                }
            ),

            'origin': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-lg',
                    'placeholder': 'Enter Origin'
                }
            ),

            'destination': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-lg',
                    'placeholder': 'Enter Destination'
                }
            ),

            'carrier': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-lg',
                    'placeholder': 'Enter Carrier'
                }
            ),

            'risk': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-lg',
                    'placeholder': 'Enter Risk Level'
                }
            ),

            'status': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-lg',
                    'placeholder': 'Enter Shipment Status'
                }
            ),

            'departure': forms.DateTimeInput(
                attrs={
                    'class': 'form-control form-control-lg',
                    'type': 'datetime-local'
                },
                format='%Y-%m-%dT%H:%M'
            ),

            'eta': forms.DateTimeInput(
                attrs={
                    'class': 'form-control form-control-lg',
                    'type': 'datetime-local'
                },
                format='%Y-%m-%dT%H:%M'
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields['departure'].input_formats = (
            '%Y-%m-%dT%H:%M',
        )

        self.fields['eta'].input_formats = (
            '%Y-%m-%dT%H:%M',
        )