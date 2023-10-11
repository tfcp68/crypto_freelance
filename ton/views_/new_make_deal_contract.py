from django.views.generic import View
from django.shortcuts import render, redirect, get_object_or_404
from urllib.parse import urlencode
from ton.forms import NewMakeDealContractForm
from ton import models
from ton.decorators import error_decorator


@error_decorator
def NewMakeDealContractView(request):
    if request.method == "GET":
        return get(request)
    return post(request)

# class NewMakeDealContractView(View):
#     @error_decorator
def get(request):
    form = NewMakeDealContractForm()
    context = {
        "form": form,
    }
    return render(request, "ton/new_make_deal_contract.html", context=context)

# @error_decorator
def post(request):
    user = get_object_or_404(models.MarketplaceUser, user=request.user)
    sender = user.ton_address
    form = NewMakeDealContractForm(request.POST)
    if not form.is_valid():
        return redirect("ton-new-make-deal-contract")
    form_data_kwargs = form.get_data()
    form_data_kwargs["user_address"] = sender
    url = f"/ton/contract/make_deal/new/preview?{urlencode(form_data_kwargs)}"
    return redirect(url)
