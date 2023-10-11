from django.views.generic import View
from django.shortcuts import render, redirect, get_object_or_404
from ton import models
from python_contracts import ContractAPI, ContractStates
from ton.forms import MakeDealContractExecutorsChoiceForm
from ton.tx_utils import make_tx
from urllib.parse import urlencode
from ton.decorators import error_decorator
from ton.money_utils import from_nano
from ton.db_utils import save_transaction
import time


@error_decorator
def MakeDealContractInfoView(request, pk):
    if request.method == "GET":
        return get(request, pk)
    return post(request, pk)


# class MakeDealContractInfoView(View):
#     @error_decorator
def get(request, pk):
    user = models.MarketplaceUser.objects.get(user=request.user)
    context = __get_base_context(pk)
    __update_context_by_button_states(context, user)
    __update_executors_data(context)
    __update_choice_form_state(context, user)
    return render(request, "ton/make_deal_contract_info.html", context=context)


def __get_base_context(contract_pk):
    contract_obj = get_object_or_404(models.Contract, pk=contract_pk)
    contract = ContractAPI(contract_obj.contract_address)

    context = __get_contract_data(contract)
    task_text = models.Task.objects.get(pk=context["task_data"].id).text
    context.update(
        pk=contract_pk,
        address=contract_obj.contract_address,
        created_at=contract_obj.created,
        customer=contract_obj.customer,
        task_text=task_text
    )
    return context


def __get_contract_data(api):
    __wait_for_state_update(api)
    state = api.get_state()
    price = api.get_price()
    security_deposit = api.get_security_deposit()
    data = {
        "state": state,
        "is_closed": state != ContractStates.MAKE_DEAL,
        "task_data": api.get_task_data(),
        "price": f"{from_nano(price):.2f}",
        "security_deposit": f"{from_nano(security_deposit):.2f}",
        "security_deposit_percent": int(security_deposit / price * 100),
        "potential_executors": api.get_potential_executors(),
        "chosen_executors": api.get_chosen_executors(),
        "executor": None if state < ContractStates.EXECUTION \
            else models.MarketplaceUser.objects.get(ton_address=api.get_executor()),
    }
    return data


def __wait_for_state_update(api):
    state = api.get_state()
    while state < ContractStates.MAKE_DEAL:
        time.sleep(1)
        state = api.get_state()

def __update_context_by_button_states(context, user):
    context["show_execution_contract_button"] = context["state"] > ContractStates.MAKE_DEAL \
                                                and user in (context["customer"], context["executor"])
    if context["is_closed"]:
        return
    potential_executors = context["potential_executors"]
    chosen_executors = context["chosen_executors"]
    context["show_respond_button"] = user.ton_address not in potential_executors + chosen_executors + \
                                     [context["customer"].ton_address]
    context["show_accept_invitation_button"] = user.ton_address in chosen_executors


def __update_executors_data(context):
    if context["is_closed"]:
        return
    potential_executors = context["potential_executors"]
    chosen_executors = context["chosen_executors"]
    potential_set = set(potential_executors)
    chosen_set = set(chosen_executors)
    potential_set = potential_set.difference(chosen_set)
    context["potential_executors"] = __get_accounts(potential_set)
    context["chosen_executors"] = __get_accounts(chosen_set)


def __get_accounts(address_set):
    return list(models.MarketplaceUser.objects.filter(ton_address__in=address_set))


def __update_choice_form_state(context, user):
    if context["is_closed"]:
        return
    potential_executors = context["potential_executors"]
    true_condition = user == context["customer"] and potential_executors
    context["executor_choices_form"] = MakeDealContractExecutorsChoiceForm(potential_executors) \
        if true_condition else None


# @error_decorator
def post(request, pk):
    user = models.MarketplaceUser.objects.get(user=request.user)

    contract = models.Contract.objects.get(pk=pk)
    if user != contract.customer:
        raise PermissionError()

    return __process_choose_executors_operation(request, contract)


def __process_choose_executors_operation(request, contract):
    chosen_executors = __extract_chosen_executors(request)
    if not chosen_executors:
        return redirect("ton-make-deal-contract-info")
    __save_chosen_executors(chosen_executors, contract)
    return __sign_choose_executors_tx(contract, chosen_executors)


def __extract_chosen_executors(request):
    chosen = map(int, request.POST.getlist("executors"))
    if not chosen:
        return list()
    return models.MarketplaceUser.objects.filter(pk__in=chosen)


def __save_chosen_executors(chosen_executors, contract):
    for executor in chosen_executors:
        models.Invitation.objects.create(contract=contract, executor=executor)


def __sign_choose_executors_tx(contract, chosen_executors):
    executors_addresses = [executor.ton_address for executor in chosen_executors]
    tx_data, fee = __get_tx_data(contract.contract_address, executors_addresses)
    return __build_sign_tx_url(contract, tx_data, fee)


def __get_tx_data(contract_address, executors_addresses):
    api = ContractAPI(contract_address)
    body = api.choose_executors(executors_addresses)
    fee = api.estimate_fee(body)
    return body, fee


def __build_sign_tx_url(contract, tx_data, fee):
    transaction = make_tx(
        contract.contract_address,
        str(from_nano(fee)),
        contract.state_init,
        tx_data
    )
    redirect_to = f"/ton/contract/make_deal/info/{contract.pk}"
    tx_id = save_transaction(transaction)
    request_args = {
        "transaction": tx_id,
        "redirect_to": redirect_to,
    }
    url = f"/ton/signtx/?{urlencode(request_args)}"
    return redirect(url)
