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
def MakeDealContractAcceptInvitationView(request, pk):
    return post(request, pk)


# class MakeDealContractAcceptInvitationView(View):
#     @login_required()
#     @error_decorator
def post(request, pk):
    contract = models.Contract.objects.get(pk=pk)
    api = ContractAPI(contract.contract_address)
    tx_data = api.accept_invitation()
    fee = api.estimate_fee(tx_data)
    transaction = make_tx(
        contract.contract_address,
        str(from_nano(fee)),
        contract.state_init,
        tx_data
    )
    return __to_sign_tx(contract.pk, transaction)


def __to_sign_tx(pk, transaction):
    redirect_to = f"/ton/contract/make_deal/info/{pk}"
    tx_id = save_transaction(transaction)
    request_args = {
        "transaction": tx_id,
        "redirect_to": redirect_to
    }
    sign_tx_url = f"/ton/signtx/?{urlencode(request_args)}"
    return redirect(sign_tx_url)
