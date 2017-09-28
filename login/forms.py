from django import forms

class login_form(forms.Form):
    input_email = forms.EmailField(label = 'input_email', max_length=50);
    input_password = forms.CharField(label = 'input_password', max_length=45);
