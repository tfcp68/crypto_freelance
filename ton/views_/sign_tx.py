from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from ton.decorators import error_decorator
from ton import models
from django.views.decorators.csrf import csrf_exempt
import time


@csrf_exempt
@login_required()
@error_decorator
def SignTxView(request):
    if request.method == "GET":
        return get(request)
    return post(request)


# class SignTxView(View):
#     @login_required()
#     @error_decorator
def get(request):
    redirect_to = request.GET.get("redirect_to")
    transaction_id = request.GET.get("transaction")
    transaction = __get_transaction(transaction_id)
    return __render_tx(request, transaction, redirect_to)


def __get_transaction(id):
    return get_object_or_404(models.TxData, pk=id)


def __render_tx(request, transaction, redirect_to):
    context = {
        "transaction": transaction,
        "redirect_to": redirect_to
    }
    return render(request, "ton/sign_tx.html", context=context)


# @login_required()
# @error_decorator
def post(request):
    redirect_to = request.POST.get("redirect_to", None)
    if redirect_to is None or not redirect_to:
        raise PermissionDenied()
    time.sleep(5)
    return redirect(redirect_to)
