import datetime

from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from ton import models
from python_contracts import ContractAPI
from ton.tx_utils import make_tx
from urllib.parse import urlencode
from ton.decorators import error_decorator
from ton.db_utils import save_transaction
from ton.money_utils import from_nano


@login_required()
@error_decorator
def FinishExecutionView(request, pk):
    return post(request, pk)


# class FinishExecutionView(View):
#     @login_required()
#     @error_decorator
def post(request, pk):
    contract = models.Contract.objects.get(pk=pk)
    api = ContractAPI(contract.contract_address)
    execution_time_end = api.get_execution_time_end()
    if datetime.datetime.now() > execution_time_end:
        raise PermissionError()
    return __build_sign_tx_url(contract, api)


def __build_sign_tx_url(contract, api):
    tx_data = api.finish_execution()
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
