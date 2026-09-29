from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from .models import ExchangeRequest, Profile


class StyledFormMixin:
    def _style_fields(self):
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class LoginForm(StyledFormMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()


class RegistrationForm(StyledFormMixin, UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "first_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        if commit:
            user.save()
        return user


class ProfileForm(StyledFormMixin, forms.ModelForm):
    first_name = forms.CharField(max_length=150, label="Display name")

    class Meta:
        model = Profile
        fields = ("first_name", "bio", "skills_to_teach", "skills_to_learn")
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
            "skills_to_teach": forms.CheckboxSelectMultiple(),
            "skills_to_learn": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].initial = self.instance.user.first_name
        self._style_fields()
        self.fields["skills_to_teach"].widget.attrs.pop("class", None)
        self.fields["skills_to_learn"].widget.attrs.pop("class", None)

    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.user.first_name = self.cleaned_data["first_name"]
        if commit:
            profile.user.save(update_fields=["first_name"])
            profile.save()
            self.save_m2m()
        return profile


class ExchangeRequestForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ExchangeRequest
        fields = ("message",)
        widgets = {
            "message": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Introduce yourself and suggest what you could exchange.",
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()


class AdminUserCreationForm(StyledFormMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()


class AdminUserUpdateForm(StyledFormMixin, forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput,
        help_text="Leave blank to keep the current password.",
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "is_active", "password")


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password:
            validate_password(password, self.instance)
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
