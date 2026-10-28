from django import forms


class MemberForm(forms.Form):
    member_id = forms.CharField(max_length=20, widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "LIB-2026-0001"}))
    name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))
    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={"class": "form-control"}))
    membership_type = forms.ChoiceField(
        choices=[("standard", "Standard"), ("premium", "Premium"), ("student", "Student")],
        widget=forms.Select(attrs={"class": "form-select"}))
    max_books = forms.IntegerField(min_value=1, initial=5, widget=forms.NumberInput(attrs={"class": "form-control"}))
