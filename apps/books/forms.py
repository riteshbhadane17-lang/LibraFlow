from django import forms


class BookForm(forms.Form):
    book_id = forms.CharField(max_length=20, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. BK-0001"}))
    title = forms.CharField(max_length=255, widget=forms.TextInput(attrs={"class": "form-control"}))
    author = forms.CharField(max_length=255, widget=forms.TextInput(attrs={"class": "form-control"}))
    isbn = forms.CharField(max_length=20, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "978-3-16-148410-0"}))
    category = forms.CharField(max_length=100, widget=forms.TextInput(attrs={"class": "form-control"}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}))
    cover_image = forms.URLField(required=False, widget=forms.URLInput(attrs={"class": "form-control"}))
    total_copies = forms.IntegerField(min_value=1, initial=1, widget=forms.NumberInput(attrs={"class": "form-control"}))


class BookSearchForm(forms.Form):
    query = forms.CharField(required=False, widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Search title, author or ISBN..."}))
    category = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
    available_only = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
