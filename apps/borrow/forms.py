from django import forms


class BorrowForm(forms.Form):
    member_id = forms.CharField(max_length=20, widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "LIB-2026-0001"}))
    book_id = forms.CharField(max_length=20, widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "BK-0001"}))


class ReturnForm(forms.Form):
    member_id = forms.CharField(max_length=20, widget=forms.TextInput(attrs={"class": "form-control"}))
    book_id = forms.CharField(max_length=20, widget=forms.TextInput(attrs={"class": "form-control"}))


class ReportFilterForm(forms.Form):
    STATUS_CHOICES = [("", "All"), ("borrowed", "Borrowed"), ("returned", "Returned"), ("overdue", "Overdue")]
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False,
                                widget=forms.Select(attrs={"class": "form-select"}))
    member_id = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
