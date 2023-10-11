from django.views.generic import View
from django.shortcuts import render, redirect
from urllib.parse import urlencode
from ton.forms import NewMakeDealContractPreviewForm
from ton import models
from ton.constants import TIME_CONSTANTS
from ton.db_utils import save_text, save_transaction
from ton.text_utils import hash_text
from ton.tx_utils import make_tx
from python_contracts import ContractAPI
from text_objects import TextData
from ton.constants import TIME_CONSTANT_TO_MULT
import datetime
from ton.decorators import error_decorator
from ton.money_utils import from_nano


@error_decorator
def NewMakeDealContractPreviewView(request):
    if request.method == "GET":
        return get(request)
    return post(request)


# class NewMakeDealContractPreviewView(View):
#     @error_decorator
def get(request):
    user = models.MarketplaceUser.objects.get(user=request.user)
    form = NewMakeDealContractPreviewForm(request.GET)
    if not form.is_valid():
        return redirect('ton-new-make-deal-contract')
    form_kwargs = form.get_data()
    ctx = {
        "user_address": user.ton_address,
        "task_execution_time_format_for_human": TIME_CONSTANTS[form_kwargs["task_execution_time_format"]],
    }
    ctx.update(form_kwargs)
    return render(request, "ton/confirm_make_deal_contract.html", context=ctx)


# @error_decorator
def post(request):
    user = models.MarketplaceUser.objects.get(user=request.user)
    form = NewMakeDealContractPreviewForm(request.GET)
    if not form.is_valid():
        return redirect('ton-new-make-deal-contract')
    form_kwargs = form.get_data()
    transactions = __get_transactions(form_kwargs)
    sign_url = __build_sign_url(transactions, user)
    return redirect(sign_url)


def __get_transactions(form_data):
    initial_tx = __get_initial_transaction()
    constructor_tx = __get_constructor_tx(form_data, initial_tx)
    return [initial_tx, constructor_tx]


def __get_initial_transaction():
    api = ContractAPI()
    state_init = api.state_init()
    return make_tx(
        state_init.address,
        str(from_nano(state_init.fee)),
        state_init.initial
    )


def __get_constructor_tx(form_data, initial_tx):
    task_id = save_text(form_data["task_text"], models.Task)
    task_hash = hash_text(form_data["task_text"])
    text_data = TextData(task_id, task_hash, datetime.datetime.now())
    time_mult = TIME_CONSTANT_TO_MULT[form_data["task_execution_time_format"]]
    task_execution_time_in_seconds = form_data["task_execution_time"] * time_mult
    constructor_boc = __get_constructor_boc(
        form_data["security_deposit_percent"],
        task_execution_time_in_seconds,
        text_data
    )
    return make_tx(
        initial_tx["to"],
        str(float(form_data["price"]) + 0.3),
        initial_tx["stateInit"],
        constructor_boc
    )


def __get_constructor_boc(security_deposit_percent,
                          task_execution_time,
                          text_data):
    api = ContractAPI()
    return api.constructor(
        int(security_deposit_percent),
        datetime.timedelta(seconds=task_execution_time),
        text_data
    )


def __build_sign_url(transactions, user):
    contract_pk = __create_contract(transactions[0], user)
    constructor_sign_url = __build_constructor_sign_url(transactions[1], contract_pk)
    deploy_sign_url = __build_deploy_sign_url(transactions[0], constructor_sign_url)
    return deploy_sign_url


def __build_constructor_sign_url(tx, contract_pk):
    tx_id = save_transaction(tx)
    request_args = {
        "transaction": tx_id,
        "redirect_to": f"/ton/contract/make_deal/info/{contract_pk}"
    }
    return f"/ton/signtx/?{urlencode(request_args)}"


def __build_deploy_sign_url(tx, constructor_url):
    tx_id = save_transaction(tx)
    request_args = {
        "transaction": tx_id,
        "redirect_to": constructor_url,
    }
    return f"/ton/signtx/?{urlencode(request_args)}"


def __create_contract(initial_tx, user):
    contract = models.Contract.objects.create(
        contract_address=initial_tx["to"],
        state_init=initial_tx["stateInit"],
        customer=user,
    )
    return contract.pk
