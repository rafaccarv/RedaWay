from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, UserCreationForm
from django.core.exceptions import ValidationError
import bleach

from .models import Note, User


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "photo")
        labels = {"first_name": "Nome", "last_name": "Sobrenome", "email": "E-mail", "photo": "Foto de perfil"}
        widgets = {"email": forms.EmailInput(attrs={"autocomplete": "email"}), "photo": forms.ClearableFileInput(attrs={"accept": "image/jpeg,image/png,image/webp"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["photo"].required = False
        self.fields["photo"].help_text = "Opcional · JPG, PNG ou WebP · até 5 MB. Sua foto não fica pública."

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        duplicates = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise ValidationError("Este e-mail já está cadastrado. Entre na sua conta ou use outro e-mail.")
        return email

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if photo and not getattr(photo, "_committed", False):
            if photo.size > 5 * 1024 * 1024:
                raise ValidationError("A foto deve ter no máximo 5 MB.")
            from PIL import Image, UnidentifiedImageError
            try:
                photo.seek(0)
                image = Image.open(photo)
                if image.format not in {"JPEG", "PNG", "WEBP"}:
                    raise ValidationError("Use uma imagem JPG, PNG ou WebP.")
                image.verify()
            except (UnidentifiedImageError, OSError, ValueError):
                raise ValidationError("Não foi possível validar essa imagem.")
            finally:
                photo.seek(0)
        return photo


class RegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["photo"].required = False
        self.fields["photo"].help_text = "Opcional · JPG, PNG ou WebP · até 5 MB. Sua foto não fica pública."

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "photo")
        labels = {"first_name": "Nome", "last_name": "Sobrenome", "email": "E-mail", "photo": "Foto de perfil"}
        widgets = {"photo": forms.ClearableFileInput(attrs={"accept": "image/jpeg,image/png,image/webp"})}

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Este e-mail já está cadastrado. Entre na sua conta ou use outro e-mail.")
        return email

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if photo and not getattr(photo, "_committed", False):
            if photo.size > 5 * 1024 * 1024:
                raise ValidationError("A foto deve ter no máximo 5 MB.")
            from PIL import Image, UnidentifiedImageError
            try:
                photo.seek(0)
                image = Image.open(photo)
                if image.format not in {"JPEG", "PNG", "WEBP"}:
                    raise ValidationError("Use uma imagem JPG, PNG ou WebP.")
                image.verify()
            except (UnidentifiedImageError, OSError, ValueError):
                raise ValidationError("Não foi possível validar essa imagem.")
            finally:
                photo.seek(0)
        return photo


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="E-mail", widget=forms.EmailInput(attrs={"autocomplete": "email"}))

    def clean_username(self):
        return self.cleaned_data["username"].strip().lower()


class NormalizedPasswordResetForm(PasswordResetForm):
    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()


NOTE_ALLOWED_TAGS = {
    "p", "div", "br", "strong", "b", "em", "i", "u", "mark",
    "ul", "ol", "li", "blockquote", "h2", "h3",
}


def sanitize_note_html(value):
    return bleach.clean(
        value or "", tags=NOTE_ALLOWED_TAGS, attributes={}, protocols=set(),
        strip=True, strip_comments=True,
    )


class NoteForm(forms.ModelForm):
    body = forms.CharField(required=False, widget=forms.HiddenInput(), max_length=100_000)

    class Meta:
        model = Note
        fields = ("title", "topic", "body")
        labels = {"title": "Título", "topic": "Tema", "body": "Conteúdo"}
        widgets = {
            "title": forms.TextInput(attrs={"class": "note-title-input", "placeholder": "Título da nota", "maxlength": 160}),
            "topic": forms.TextInput(attrs={"class": "note-topic-input", "placeholder": "Adicione um tema", "maxlength": 120}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["title"].initial = "Nova nota"

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if not title:
            raise ValidationError("Dê um título para esta nota.")
        return title

    def clean_topic(self):
        return self.cleaned_data.get("topic", "").strip()

    def clean_body(self):
        return sanitize_note_html(self.cleaned_data.get("body", ""))
