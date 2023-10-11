from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from ton import models
from python_contracts import ContractAPI
from ton.constants import TIME_CONSTANT_TO_MULT
import datetime
from ton.tx_utils import make_tx
from urllib.parse import urlencode
from ton.decorators import error_decorator
from ton.db_utils import save_transaction
from ton.money_utils import from_nano


@login_required()
@error_decorator
def AddExecutionTimeView(request, pk):
    return post(request, pk)


# class AddExecutionTimeView(View):
#     @login_required()
#     @error_decorator
def post(request, pk):
    contract = models.Contract.objects.get(pk=pk)
    api = ContractAPI(contract.contract_address)
    additional_time = int(request.POST.get("additional_time"))
    additional_time_format = request.POST.get("additional_time_format")
    additional_time_in_seconds = additional_time * TIME_CONSTANT_TO_MULT[additional_time_format]
    timedelta = datetime.timedelta(seconds=additional_time_in_seconds)
    return __build_sign_tx_url(contract, api, timedelta)


def __build_sign_tx_url(contract, api, additional_time):
    tx_data = api.add_task_execution_time(additional_time)
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
