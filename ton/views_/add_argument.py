import datetime

from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from ton import models
from python_contracts import ContractAPI
from ton.db_utils import save_text
from ton.text_utils import hash_text
from ton.tx_utils import make_tx
from text_objects import TextData
from urllib.parse import urlencode
from ton.decorators import error_decorator
from ton.money_utils import from_nano
from ton.db_utils import save_transaction


@login_required()
@error_decorator
def AddArgumentView(request, pk):
    return post(request, pk)


# class AddArgumentView(View):
#     @login_required()
#     @error_decorator
def post(request, pk):
    contract = models.Contract.objects.get(pk=pk)
    api = ContractAPI(contract.contract_address)

    argument_text = request.POST.get("argument")
    argument_id = save_text(argument_text, models.Argument)
    argument_data = TextData(
        argument_id,
        hash_text(argument_text),
        datetime.datetime.now()
    )

    return __build_sign_tx_url(contract, api, argument_data)


def __build_sign_tx_url(contract, api, solution):
    tx_data = api.add_argument(solution)
    fee = api.estimate_fee(tx_data)
    transaction = make_tx(
        api.contract_address,
        str(from_nano(fee)),
        contract.state_init,
        tx_data
    )
    redirect_to = f"/ton/contract/judgment/info/{contract.pk}"
    tx_id = save_transaction(transaction)
    request_args = {
        "transaction": tx_id,
        "redirect_to": redirect_to
    }
    url = f"/ton/signtx/?{urlencode(request_args)}"
    return redirect(url)
