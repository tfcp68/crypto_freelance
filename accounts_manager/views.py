from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, User
from django.contrib.auth import login, authenticate

from . import forms
from ton.models import MarketplaceUser
from yafree.settings import LOGIN_REDIRECT_URL
from .utils import pay_test_balance


# Create your views here.

def register(request):
    if request.method == "GET":
        registration_form = UserCreationForm()
        address_input = forms.AddressForm()
        args = {
            "registration_form": registration_form,
            "address_form": address_input,
        }
        return render(request, "accounts_manager/register.html", context=args)

    # if POST request
    registration_form = UserCreationForm(request.POST)
    address_form = forms.AddressForm(request.POST)

    if registration_form.is_valid() and address_form.is_valid():
        registration_form.save()
        user = authenticate_new_user(registration_form)
        ton_address = address_form.cleaned_data.get("ton_address")
        eth_address = address_form.cleaned_data.get("eth_address")
        marketplace_user = MarketplaceUser.objects.create(
            user=user,
            ton_address=ton_address,
            eth_address=eth_address
        )
        marketplace_user.save()
        login(request, user)
        pay_test_balance(eth_address)
        return redirect(LOGIN_REDIRECT_URL)

    args = {
        "registration_form": registration_form,
        "address_form": address_form,
    }
    return render(request, "accounts_manager/register.html", context=args)


def authenticate_new_user(registration_form) -> 'User':
    username = registration_form.cleaned_data.get("username")
    password = registration_form.cleaned_data.get("password1")
    user = authenticate(username=username, password=password)
    return user


def me(request):
    return render(request, "base_generic.html")
