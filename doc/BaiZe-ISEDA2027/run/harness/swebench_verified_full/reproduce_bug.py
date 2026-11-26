#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'django'))
import django
from django import forms

class MyForm(forms.Form):
    my_field = forms.CharField()

if __name__ == "__main__":
    settings_file = os.path.splitext(os.path.basename(__file__))[0]
    django.conf.settings.configure(
        DEBUG=True,
        MIDDLEWARE_CLASSES=[],
        ROOT_URLCONF=settings_file,
    )
    django.setup()
    MyFormSet = forms.formset_factory(
        form=MyForm,
        can_delete=True,
        can_delete_extra=False,
    )
    my_formset = MyFormSet(
        initial=None,
    )
    print(my_formset.empty_form)
