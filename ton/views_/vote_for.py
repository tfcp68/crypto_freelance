from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from ton import models
from python_contracts import ContractAPI
from ton.db_utils import save_text, save_transaction
from ton.text_utils import hash_text
from ton.tx_utils import make_tx
from text_objects import Vote
from urllib.parse import urlencode
from ton.forms import VotingForm
from ton.money_utils import from_nano
import datetime
from ton.decorators import error_decorator


@login_required()
@error_decorator
def VoteForView(request, pk):
    if request.method == "GET":
        return get(request, pk)
    return post(request, pk)


# class VoteForView(View):
#     @login_required()
#     @error_decorator
def get(request, pk):
    user = get_object_or_404(models.MarketplaceUser, user=request.user)
    contract = get_object_or_404(models.Contract, pk=pk)
    api = ContractAPI(contract.contract_address)

    if api.is_judge(user.ton_address):
        return redirect('ton-judgment-contact-info', pk)

    form = VotingForm()
    bid = api.get_security_deposit()

    ctx = {
        "form": form,
        "bid": f"{from_nano(bid):.2f}",
    }
    return render(request, "ton/vote_for.html", context=ctx)


# @login_required()
# @error_decorator
def post(request, pk):
    form = VotingForm(request.POST)
    if not form.is_valid():
        return redirect("ton-judgment-contract-info", pk=pk)

    details = form.cleaned_data["details"]
    vote_id = save_text(details, models.Vote)
    verdict = form.cleaned_data["vote_for"] == VotingForm.CHOICES[0][0]
    vote = Vote(
        vote_id,
        hash_text(details),
        datetime.datetime.now(),
        verdict
    )
    contract = get_object_or_404(models.Contract, pk=pk)
    api = ContractAPI(contract.contract_address)

    return __build_sign_tx_url(contract, api, vote)


def __build_sign_tx_url(contract, api, vote):
    tx_data = api.vote(vote)
    bid = api.get_security_deposit()
    fee = api.estimate_fee(tx_data)
    transaction = make_tx(
        api.contract_address,
        str(from_nano(bid) + from_nano(fee)),
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
