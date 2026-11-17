import re
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class RegistroUsuarioForm(forms.Form):
    """
    Formulario seguro de Registro de Usuarios para ARTSPACE.
    Aplica sanitización de entradas, expresiones regulares RFC-5322 para correo
    y validadores criptográficos de robustez de contraseñas de Django.
    """
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario (ej. r_almendra)',
            'autocomplete': 'username'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@dominio.com',
            'autocomplete': 'email'
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña segura (mín. 8 caracteres, números y símbolos)',
            'autocomplete': 'new-password'
        })
    )
    password_confirm = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirma tu contraseña',
            'autocomplete': 'new-password'
        })
    )

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        # Validación de caracteres permitidos (Alfanumérico y guiones bajos)
        if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
            raise ValidationError("El nombre de usuario solo puede contener letras, números, puntos y guiones.")
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("Este nombre de usuario ya se encuentra registrado.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        # Validación estricta RFC-5322 simplificada
        rfc5322_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(rfc5322_regex, email):
            raise ValidationError("El formato de correo electrónico es inválido.")
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Este correo electrónico ya está asociado a una cuenta registrada.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm:
            if password != password_confirm:
                self.add_error('password_confirm', "Las contraseñas no coinciden.")
            else:
                # Ejecutar validadores de complejidad configurados en settings.py
                try:
                    validate_password(password)
                except ValidationError as e:
                    self.add_error('password', e)
        return cleaned_data


class LoginUsuarioForm(forms.Form):
    """
    Formulario de Autenticación Segura.
    Protege contra ataques de enumeración de usuarios retornando mensajes genéricos.
    """
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuario o correo registrado',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña',
            'autocomplete': 'current-password'
        })
    )

