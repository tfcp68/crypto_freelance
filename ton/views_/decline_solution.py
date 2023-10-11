from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from ton import models
from python_contracts import ContractAPI
from ton.constants import TIME_CONSTANT_TO_MULT
import datetime
from ton.tx_utils import make_tx
from urllib.parse import urlencode
from ton.forms import DeclineSolutionForm
from ton.constants import MINIMAL_JUDGMENT_TIME
from ton.decorators import error_decorator
from ton.money_utils import from_nano
from ton.db_utils import save_transaction


@login_required()
@error_decorator
def DeclineSolutionView(request, pk=None):
    if request.method == "GET":
        return get(request)
    return post(request, pk)


# class DeclineSolutionView(View):
#     @login_required()
#     @error_decorator
def get(request):
    form = DeclineSolutionForm()
    context = {
        "form": form
    }
    return render(request, "ton/decline_solution.html", context=context)


# @login_required()
# @error_decorator
def post(request, pk):
    form = DeclineSolutionForm(request.POST)
    if not form.is_valid():
        return redirect("eth-decline-solution", pk)
    judgment_time = __eval_judgment_time(form)
    contract = models.Contract.objects.get(pk=pk)
    api = ContractAPI(contract.contract_address)
    return __build_sign_tx_url(contract, api, judgment_time)


def __eval_judgment_time(form):
    judgment_time = form.cleaned_data["judgment_time"]
    judgment_time_format = form.cleaned_data["judgment_time_format"]
    judgment_time_seconds = judgment_time * TIME_CONSTANT_TO_MULT[judgment_time_format]
    judgment_time_timedelta = datetime.timedelta(seconds=judgment_time_seconds)
    if judgment_time_timedelta < MINIMAL_JUDGMENT_TIME:
        judgment_time_timedelta = MINIMAL_JUDGMENT_TIME
    return judgment_time_timedelta


def __build_sign_tx_url(contract, api, judgment_time):
    tx_data = api.decline_solution(judgment_time)
    fee = api.estimate_fee(tx_data)
    transaction = make_tx(
        api.contract_address,
        str(from_nano(fee)),
        contract.state_init,
        tx_data
    )
    redirect_to = f"/ton/contract/execution/info/{contract.pk}"
    tx_id = save_transaction(transaction)
    request_args = {
        "transaction": tx_id,
        "redirect_to": redirect_to
    }
    url = f"/ton/signtx/?{urlencode(request_args)}"
    return redirect(url)
