from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from urllib.parse import urlencode
# import datetime
# import json
from web3.exceptions import ContractLogicError

from . import models
from . import forms
from .utility import *
from api.utility import hash_text
from api.contract_interfaces import *
from api.contract_interfaces.objects import *
from .allowed_tokens import get_token_from_symbol


# Create your views here.

def index(request):
    return render(request, "eth/index.html")


def default_accounts(request):
    accounts_data = __load_default_accounts_data()
    ctx = {
        "account_data": accounts_data,
    }
    return render(request, "eth/default_accounts.html", context=ctx)


def __load_default_accounts_data():
    file_path = settings.BASE_DIR / "default_accounts.txt"
    with open(file_path, 'r') as f:
        raw_data = f.read().split('\n')

    result = list()
    for item in raw_data:
        item_split = item.split()
        account_data = {
            "login": item_split[0],
            "password": item_split[1],
            "eth_address": item_split[2],
            "secret": item_split[3],
        }
        result.append(account_data)
    return result


@csrf_exempt
def something_went_wrong(request):
    return render(request, "eth/something_went_wrong.html")


def __error_decorator(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as E:
            print(E)
            return redirect("eth-something-went-wrong")

    return wrapper


@login_required
@csrf_exempt
@__error_decorator
def sign_tx(request):
    if request.method == "GET":
        return __sign_tx_GET(request)
    return __sign_tx_POST(request)


def __sign_tx_GET(request):
    # tx_str = request.GET.get("tx").replace("'", '"')
    # tx = eval(tx_str)
    tx_hash = request.GET.get("tx")
    tx_storage = get_tx_storage()
    tx = tx_storage.get_tx(tx_hash)
    if tx is None:
        return redirect("eth-something-went-wrong")
    tx_storage.delete_tx(tx_hash)
    ctx = {
        "tx": hexify_tx(tx),
    }
    return render(request, "eth/sign_tx.html", context=ctx)


def __sign_tx_POST(request):
    sign_type_to_func = {
        MAKE_DEAL_CONTRACT_SIGN_TYPE: __save_signed_make_deal_contract,
        EXECUTION_CONTRACT_SIGN_TYPE: __save_signed_execution_contract,
        JUDGMENT_CONTRACT_SIGN_TYPE: __save_signed_judgment_contract,
        DEFAULT_TRANSACTION_SIGN_TYPE: __approving_transaction_process,
        ACCEPT_SOLUTION_SIGN_TYPE: __accept_solution_process,
    }
    sign_type = request.POST.get("sign_type")
    if sign_type is None:
        raise PermissionDenied()
    return sign_type_to_func[int(sign_type)](request)


def __save_signed_make_deal_contract(request):
    tx_hash = request.POST.get("tx_hash").replace('"', "")
    tx_receipt = get_tx_receipt(tx_hash)
    contract_address = tx_receipt.contractAddress

    user = models.MarketplaceUser.objects.get(user=request.user)

    smart_contract = MakeDealContractInterface(contract_address)
    task_info_contract_address = smart_contract.get_task_info_contract_address(user.eth_address)

    contract = models.MakeDealContract.objects.create(contract_address=contract_address,
                                                      customer=user,
                                                      task_info_contract_address=task_info_contract_address)
    return redirect('eth-make-deal-contract-info', contract.pk)


def __save_signed_execution_contract(request):
    tx_hash = request.POST.get("tx_hash").replace('"', "")
    tx_receipt = get_tx_receipt(tx_hash)

    user = models.MarketplaceUser.objects.get(user=request.user)

    contract_address = MakeDealContractInterface.get_execution_contract_address(tx_receipt)
    make_deal_contract = models.MakeDealContract.objects.get(contract_address=tx_receipt.to)
    make_deal_contract.is_closed = True

    contract = models.ExecutionContract.objects.create(contract_address=contract_address,
                                                       make_deal_contract=make_deal_contract,
                                                       executor=user)

    make_deal_contract.save()

    models.EthInvitation.objects.filter(contract=make_deal_contract).delete()

    return redirect('eth-execution-contract-info', contract.pk)


def __save_signed_judgment_contract(request):
    tx_hash = request.POST.get("tx_hash").replace('"', "")
    tx_receipt = get_tx_receipt(tx_hash)

    contract_address = ExecutionContractInterface.get_judgment_contract_address(tx_receipt)
    execution_contract = models.ExecutionContract.objects.get(contract_address=tx_receipt.to)
    execution_contract.is_closed = True

    contract = models.JudgmentContract.objects.create(contract_address=contract_address,
                                                      execution_contract=execution_contract)
    execution_contract.save()
    return redirect('eth-judgment-contract-info', contract.pk)


def __approving_transaction_process(request):
    tx_hash = request.POST.get("tx_hash").replace('"', "")
    get_tx_receipt(tx_hash)  # waiting for when tx will be mined

    redirect_to = request.POST.get("redirect_to")
    if redirect_to is None:
        raise PermissionDenied()
    return redirect(redirect_to)


def __accept_solution_process(request):
    tx_hash = request.POST.get("tx_hash").replace('"', "")
    tx_receipt = get_tx_receipt(tx_hash)

    contract_obj = get_object_or_404(models.ExecutionContract, contract_address=tx_receipt.to)
    contract_obj.is_closed = True

    contract_obj.save()

    return redirect('eth-execution-contract-info', pk=contract_obj.pk)


def _get_sign_tx_url(sign_type, tx, redirect_to=None) -> str:
    tx_storage = get_tx_storage()
    tx_hash = tx_storage.save_tx(tx)
    request_args = {
        "sign_type": sign_type,
        "tx": tx_hash,
        "redirect_to": redirect_to,
    }
    return f"/eth/signtx/?{urlencode(request_args)}"


@login_required()
@csrf_exempt
@__error_decorator
def new_make_deal_contract(request):
    if request.method == "GET":
        return __new_make_deal_contract_GET(request)
    return __new_make_deal_contract_POST(request)


def __new_make_deal_contract_GET(request):
    form = forms.NewMakeDealContractForm()
    ctx = {
        "form": form,
    }
    return render(request, "eth/new_make_deal_contract.html", context=ctx)


def __new_make_deal_contract_POST(request):
    user = get_object_or_404(models.MarketplaceUser, user=request.user)
    sender = user.eth_address
    form = forms.NewMakeDealContractForm(request.POST)
    if not form.is_valid():
        return redirect("eth-new-make-deal-contract")
    form_data_kwargs = form.get_data()
    form_data_kwargs["user_address"] = sender
    url = f"/eth/contract/make_deal/new/preview?{urlencode(form_data_kwargs)}"
    return redirect(url)


@login_required()
@__error_decorator
def new_make_deal_contract_preview(request):
    user = models.MarketplaceUser.objects.get(user=request.user)
    form = forms.NewMakeDealContractPreviewForm(request.GET)
    if not form.is_valid():
        return redirect('eth-new-make-deal-contract')
    if request.method == "GET":
        return __new_make_deal_contract_preview_GET(request, form, user)
    return __new_make_deal_contract_preview_POST(request, form, user)


def __new_make_deal_contract_preview_GET(request, form, user):
    form_kwargs = form.get_data()
    new_make_deal_contract_tx = MakeDealContractInterface.new_contract_tx(
        form_kwargs["token_address"],
        1,
        hash_text(form_kwargs["task_text"]),
        form.get_timedelta(),
        form_kwargs["price"],
        form_kwargs["security_deposit_percent"],
        user.eth_address,
    )
    token = ERC20ContractInterface(form_kwargs["token_address"])
    gas_price = to_eth(get_gas_price())
    estimated_gas_amount = new_make_deal_contract_tx["gas"]
    tx_gas_price = round(float(gas_price * estimated_gas_amount), 5)
    ctx = {
        "user_address": user.eth_address,
        "task_execution_time_format_for_human": TIME_CONSTANTS[form_kwargs["task_execution_time_format"]],
        "gas_price": gas_price,
        "estimated_gas_amount": estimated_gas_amount,
        "tx_gas_price": tx_gas_price,
        "TOKEN_NAME": token.name(user.eth_address),
    }
    ctx.update(form_kwargs)
    return render(request, "eth/confirm_make_deal_contract.html", context=ctx)


def __new_make_deal_contract_preview_POST(request, form, user):
    form_kwargs = form.get_data()
    token = ERC20ContractInterface(form_kwargs["token_address"])
    task_id = _save_task(form_kwargs["task_text"])
    task_hash = hash_text(form_kwargs["task_text"])
    new_make_deal_contract_tx = MakeDealContractInterface.new_contract_tx(
        form_kwargs["token_address"],
        task_id,
        task_hash,
        form.get_timedelta(),
        token.to_minimal_units(form_kwargs["price"]),
        form_kwargs["security_deposit_percent"],
        user.eth_address,
    )
    new_make_deal_contract_tx["to"] = str()
    url = _get_sign_tx_url(MAKE_DEAL_CONTRACT_SIGN_TYPE, new_make_deal_contract_tx)
    return redirect(url)


def _save_task(task_text) -> int:
    # Возвращает id задачи
    task = models.Task.objects.create(text=task_text)
    return task.pk


@login_required()
@__error_decorator
def make_deal_contract_info(request, pk: int):
    if request.method == "GET":
        return __make_deal_contract_info_GET(request, pk)
    return __make_deal_contract_info_POST(request, pk)


def __make_deal_contract_info_GET(request, pk: int):
    user = models.MarketplaceUser.objects.get(user=request.user)
    sender = user.eth_address

    contract_obj = get_object_or_404(models.MakeDealContract, pk=pk)
    contract_address = contract_obj.contract_address

    ctx = _get_task_info_contract_data_view(contract_obj.task_info_contract_address, sender)
    merge_dicts(ctx, pk=contract_obj.pk,
                created_at=contract_obj.created,
                is_closed=contract_obj.is_closed,
                customer=contract_obj.customer,
                user=user)

    make_deal_smart_contract = MakeDealContractInterface(contract_address)
    make_deal_contract_ctx = make_deal_smart_contract.get_data_view(sender)
    _process_make_deal_contract_data_view(make_deal_contract_ctx)
    merge_dicts(ctx, make_deal_contract_ctx)

    is_activated = ctx["activated"]

    security_deposit_percent = int(ctx["security_deposit"] / ctx["price"] * 100)
    merge_dicts(ctx, security_deposit_percent=security_deposit_percent)

    execution_contract_pk = None
    if contract_obj.is_closed:
        execution_contract_pk = models.ExecutionContract.objects.get(make_deal_contract=contract_obj).pk
    merge_dicts(ctx, execution_contract_pk=execution_contract_pk)

    executor_choices_form = None
    responded_executors = None
    chosen_executors = None
    if not contract_obj.is_closed and is_activated and ctx["executors"]:
        responded_executors = list()
        chosen_executors = list()
        for executor, was_chosen in ctx["executors"]:
            if was_chosen:
                chosen_executors.append(executor)
            else:
                responded_executors.append(executor)
        if user == ctx["customer"] and responded_executors is not None and responded_executors:
            executor_choices_form = forms.MakeDealContractExecutorsChoiceForm(responded_executors)

    merge_dicts(ctx, executor_choices_form=executor_choices_form,
                responded_executors=responded_executors,
                chosen_executors=chosen_executors)

    show_respond_button = False
    show_accept_invitation_button = False
    if user != ctx["customer"]:
        show_respond_button = True if not contract_obj.is_closed and \
                                      (responded_executors is None or
                                       chosen_executors is None or
                                       user not in responded_executors + chosen_executors) else False
        show_accept_invitation_button = True if chosen_executors is not None and \
                                                user in chosen_executors else False

    merge_dicts(ctx, show_respond_button=show_respond_button,
                show_accept_invitation_button=show_accept_invitation_button)

    return render(request, "eth/make_deal_contract_view.html", context=ctx)


def _get_task_info_contract_data_view(address, sender):
    smart_contract = TaskInfoContractInterface(address)
    data = smart_contract.get_data_view(sender)
    _process_task_info_contract_data_view(data)
    return data


def _process_task_info_contract_data_view(data):
    token = get_token_from_symbol(data["token_name"])
    data["task_data_text"] = models.Task.objects.get(pk=data["task_data"].id).text
    data["price"] = token.to_decimal(data["price"])
    data["security_deposit"] = token.to_decimal(data["security_deposit"])
    data["solution_text"] = models.Solution.objects.filter(
        pk__in=[solution.id for solution in data["solution"]]).values_list("text", flat=True) \
        if data["solution"] is not None else None
    data["solution_data"] = list(zip(data["solution_text"], data["solution"])) \
        if data["solution_text"] is not None else None
    data.pop("solution")
    data.pop("solution_text")


def _process_make_deal_contract_data_view(data):
    executors = models.MarketplaceUser.objects.filter(
        eth_address__in=[executor.address for executor in data["executors"]])
    data["executors"] = [(user, executor.was_chosen) for user, executor in zip(executors, data["executors"])]


def __make_deal_contract_info_POST(request, pk: int):
    return _add_chosen_executors(request, pk)


def _add_chosen_executors(request, pk):
    user = models.MarketplaceUser.objects.get(user=request.user)
    sender = user.eth_address

    contract_obj = models.MakeDealContract.objects.get(pk=pk)
    smart_contract = MakeDealContractInterface(contract_obj.contract_address)

    chosen_executors = _extract_chosen_executors(request)
    if not chosen_executors:
        return

    eth_addresses = [executor.eth_address for executor in chosen_executors]
    tx = smart_contract.choose_executors_tx(eth_addresses, sender)
    _save_chosen_executors(chosen_executors, contract_obj)

    redirect_to = f"/eth/contract/make_deal/info/{pk}"
    url = _get_sign_tx_url(DEFAULT_TRANSACTION_SIGN_TYPE, tx, redirect_to)

    return redirect(url)


def _extract_chosen_executors(request):
    chosen = map(int, request.POST.getlist("executors"))
    if not chosen:
        return list()
    return models.MarketplaceUser.objects.filter(pk__in=chosen)


def _save_chosen_executors(chosen_executors, contract_obj):
    for executor in chosen_executors:
        models.EthInvitation.objects.create(contract=contract_obj, executor=executor)


# def _get_task_text(task_id: int) -> str:
#     task_obj = models.Task.objects.get(pk=task_id)
#     return task_obj.text


@login_required()
@__error_decorator
def make_deal_contract_activate(request, pk: int, step: int):
    user = get_object_or_404(models.MarketplaceUser, user=request.user)
    sender = user.eth_address

    contract_obj = get_object_or_404(models.MakeDealContract, pk=pk)
    smart_contract = MakeDealContractInterface(contract_obj.contract_address)

    is_activated = smart_contract.is_activated(sender)

    if is_activated:
        raise Http404("Contract already activated")

    if not step:
        return __make_deal_contract_activate_step_0(smart_contract, sender, pk)
    return __make_deal_contract_activate_step_1(smart_contract, sender, pk)


def __make_deal_contract_activate_step_0(smart_contract, sender, pk):
    money_distribution = smart_contract.count_money_distribution(sender)
    allowance = money_distribution.price + money_distribution.marketplace_fee

    token = TaskInfoContractInterface(smart_contract.get_task_info_contract_address(sender)).get_token(sender)

    approving_tx = token.approve_tx(
        smart_contract.address,
        allowance,
        sender
    )

    activation_url = f"/eth/contract/make_deal/activate/{pk}&1"
    url = _get_sign_tx_url(DEFAULT_TRANSACTION_SIGN_TYPE, approving_tx, activation_url)
    return redirect(url)


def __make_deal_contract_activate_step_1(smart_contract, sender, pk):
    activation_tx = smart_contract.activate_tx(sender)

    activation_redirect_to = f"/eth/contract/make_deal/info/{pk}"
    url = _get_sign_tx_url(DEFAULT_TRANSACTION_SIGN_TYPE, activation_tx, activation_redirect_to)
    return redirect(url)


@login_required()
@__error_decorator
def respond_to_make_deal_contract(request, pk: int, step: int):
    user = get_object_or_404(models.MarketplaceUser, user=request.user)
    sender = user.eth_address

    contract_obj = models.MakeDealContract.objects.get(pk=pk)
    smart_contract = MakeDealContractInterface(contract_obj.contract_address)

    if not step:
        return __respond_to_make_deal_contract_step_0(smart_contract, sender, pk)
    return __respond_to_make_deal_contract_step_1(smart_contract, sender, pk)


def __respond_to_make_deal_contract_step_0(smart_contract, sender, pk):
    money_distribution = smart_contract.count_money_distribution(sender)
    allowance = money_distribution.security_deposit

    token = TaskInfoContractInterface(smart_contract.get_task_info_contract_address(sender)).get_token(sender)

    approving_tx = token.approve_tx(
        smart_contract.address,
        allowance,
        sender
    )

    redirect_to = f"/eth/contract/make_deal/respond/{pk}&1"
    url = _get_sign_tx_url(DEFAULT_TRANSACTION_SIGN_TYPE, approving_tx, redirect_to)
    return redirect(url)


def __respond_to_make_deal_contract_step_1(smart_contract, sender, pk):
    tx = smart_contract.respond_tx(sender)

    redirect_to = f"/eth/contract/make_deal/info/{pk}"
    url = _get_sign_tx_url(DEFAULT_TRANSACTION_SIGN_TYPE, tx, redirect_to)
    return redirect(url)


@login_required()
@__error_decorator
def accept_invitation(request, pk: int):
    user = get_object_or_404(models.MarketplaceUser, user=request.user)
    sender = user.eth_address

    contract_obj = models.MakeDealContract.objects.get(pk=pk)
    smart_contract = MakeDealContractInterface(contract_obj.contract_address)

    tx = smart_contract.accept_invitation_tx(sender)

    redirect_to = f"/eth/contract/make_deal/info/{pk}"
    url = _get_sign_tx_url(EXECUTION_CONTRACT_SIGN_TYPE, tx, redirect_to)

    return redirect(url)


@login_required()
@__error_decorator
def execution_contract_info(request, pk: int):
    user = models.MarketplaceUser.objects.get(user=request.user)
    sender = user.eth_address

    contract_obj = get_object_or_404(models.ExecutionContract, pk=pk)
    customer = contract_obj.make_deal_contract.customer
    executor = contract_obj.executor

    if user != customer and user != executor:
        raise PermissionDenied()

    smart_contract = ExecutionContractInterface(contract_obj.contract_address)
    closed_status = smart_contract.close()
    if closed_status:
        contract_obj.is_closed = True
        contract_obj.save()

    task_info_contract_address = smart_contract.get_task_info_contract_address(sender)
    ctx = _get_task_info_contract_data_view(task_info_contract_address, sender)

    merge_dicts(ctx, pk=pk,
                customer=customer,
                executor=executor,
                created_at=contract_obj.created,
                is_closed=contract_obj.is_closed)

    contract_ctx = smart_contract.get_data_view(sender)
    _process_execution_contract_data_view(contract_ctx)
    merge_dicts(ctx, contract_ctx)

    add_execution_time_form = None
    add_execution_time_operation_gas = None
    if user == customer and not contract_obj.is_closed:
        add_execution_time_form = forms.AddExecutionTimeForm()
        tx = smart_contract.add_execution_time_tx(
            datetime.timedelta(days=1),
            sender
        )
        add_execution_time_operation_gas = to_eth(tx["gas"])
    merge_dicts(ctx, add_execution_time_form=add_execution_time_form,
                add_execution_time_operation_gas=add_execution_time_operation_gas)

    time_left = ctx["execution_time_left"]

    show_finish_execution_button = False
    finish_execution_operation_gas = None
    if user == executor and not contract_obj.is_closed and \
            time_left is not None and to_seconds(time_left) != 0 and \
            ctx["solution_data"]:
        show_finish_execution_button = True
        tx = smart_contract.finish_execution_tx(sender)
        finish_execution_operation_gas = to_eth(tx["gas"])
    merge_dicts(ctx, show_finish_execution_button=show_finish_execution_button,
                finish_execution_operation_gas=finish_execution_operation_gas)

    add_solution_form = None
    add_solution_operation_gas = None
    if user == executor and time_left is not None and to_seconds(time_left) != 0:
        add_solution_form = forms.AddSolutionForm()
        tx = smart_contract.add_solution_tx(
            SolutionData(
                1,
                hash_text("tx"),
                datetime.datetime.now()
            ),
            sender
        )
        add_solution_operation_gas = to_eth(tx["gas"])
    merge_dicts(ctx, add_solution_form=add_solution_form,
                add_solution_operation_gas=add_solution_operation_gas)

    try:
        judgment_pk = models.JudgmentContract.objects.get(execution_contract__pk=pk).pk
    except models.JudgmentContract.DoesNotExist:
        judgment_pk = None
    make_deal_pk = contract_obj.make_deal_contract.pk
    merge_dicts(ctx, make_deal_pk=make_deal_pk,
                judgment_pk=judgment_pk)

    show_accept_solution_button = False
    accept_solution_operation_gas = None
    show_deny_solution_button = False
    deny_solution_operation_gas = None
    if user == customer and not contract_obj.is_closed and to_seconds(time_left) == 0:
        show_accept_solution_button = True
        tx = smart_contract.accept_solution_tx(sender)
        accept_solution_operation_gas = to_eth(tx["gas"])

        show_deny_solution_button = True
        tx = smart_contract.deny_solution_tx(
            datetime.timedelta(weeks=2),
            sender
        )
        deny_solution_operation_gas = to_eth(tx["gas"])
    merge_dicts(ctx, show_accept_solution_button=show_accept_solution_button,
                accept_solution_operation_gas=accept_solution_operation_gas,
                show_deny_solution_button=show_deny_solution_button,
                deny_solution_operation_gas=deny_solution_operation_gas)
    return render(request, "eth/execution_contract_view.html", context=ctx)


def _process_execution_contract_data_view(data):
    now = datetime.datetime.now()
    time_end = data["execution_time_end"]
    if time_end is None:
        time_left = None
    elif now >= time_end:
        time_left = datetime.timedelta(seconds=0)
    else:
        time_left = time_end - now
    data.pop("execution_time_end")
    data["execution_time_left"] = time_left


@login_required()
@__error_decorator
def finish_execution(request, pk: int):
    user = models.MarketplaceUser.objects.get(user=request.user)
    sender = user.eth_address

    contract_obj = models.ExecutionContract.objects.get(pk=pk)
    if user != contract_obj.executor:
        raise PermissionDenied()

    smart_contract = ExecutionContractInterface(contract_obj.contract_address)
    tx = smart_contract.finish_execution_tx(sender)

    redirect_to = f"/eth/contract/execution/info/{pk}"
    url = _get_sign_tx_url(DEFAULT_TRANSACTION_SIGN_TYPE, tx, redirect_to)

    return redirect(url)


@login_required()
@__error_decorator
def add_solution(request, pk: int):
    user = models.MarketplaceUser.objects.get(user=request.user)
    sender = user.eth_address

    contract_obj = models.ExecutionContract.objects.get(pk=pk)
    if user != contract_obj.executor:
        raise PermissionDenied()

    smart_contract = ExecutionContractInterface(contract_obj.contract_address)
    solution_text = request.POST.get("solution_text")
    solution_id = _save_solution(solution_text)
    solution_data = SolutionData(
        solution_id,
        hash_text(solution_text),
        datetime.datetime.now()
    )

    tx = smart_contract.add_solution_tx(solution_data, sender)

    redirect_to = f"/eth/contract/execution/info/{pk}"
    url = _get_sign_tx_url(DEFAULT_TRANSACTION_SIGN_TYPE, tx, redirect_to)

    return redirect(url)


def _save_solution(text: str) -> int:
    # returns solution id
    solution = models.Solution.objects.create(text=text)
    return solution.pk


@login_required()
@__error_decorator
def add_execution_time(request, pk: int):
    user = models.MarketplaceUser.objects.get(user=request.user)
    sender = user.eth_address

    contract_obj = models.ExecutionContract.objects.get(pk=pk)
    smart_contract = ExecutionContractInterface(contract_obj.contract_address)
    task_execution_time = int(request.POST.get("task_execution_time"))
    task_execution_time_format = request.POST.get("task_execution_time_format")
    additional_time_in_seconds = task_execution_time * TIME_CONSTANT_TO_MULT[task_execution_time_format]
    timedelta = datetime.timedelta(seconds=additional_time_in_seconds)

    try:
        tx = smart_contract.add_execution_time_tx(timedelta, sender)
    except ContractLogicError as E:
        raise PermissionDenied()

    redirect_to = f"/eth/contract/execution/info/{pk}"
    url = _get_sign_tx_url(DEFAULT_TRANSACTION_SIGN_TYPE, tx, redirect_to)

    return redirect(url)


@login_required()
@__error_decorator
def accept_solution(request, pk: int):
    user = models.MarketplaceUser.objects.get(user=request.user)
    sender = user.eth_address

    contract_obj = models.ExecutionContract.objects.get(pk=pk)
    smart_contract = ExecutionContractInterface(contract_obj.contract_address)

    try:
        tx = smart_contract.accept_solution_tx(sender)
    except ContractLogicError as E:
        raise PermissionDenied()

    url = _get_sign_tx_url(ACCEPT_SOLUTION_SIGN_TYPE, tx)

    return redirect(url)


@login_required()
@__error_decorator
def deny_solution(request, pk: int):
    if request.method == "GET":
        return __deny_solution_GET(request)
    return __deny_solution_POST(request, pk)


def __deny_solution_GET(request):
    form = forms.DeclineSolutionForm()
    ctx = {
        "form": form,
    }
    return render(request, "eth/decline_solution.html", context=ctx)


def __deny_solution_POST(request, pk):
    user = models.MarketplaceUser.objects.get(user=request.user)
    sender = user.eth_address

    contract_obj = models.ExecutionContract.objects.get(pk=pk)
    smart_contract = ExecutionContractInterface(contract_obj.contract_address)

    form = forms.DeclineSolutionForm(request.POST)
    if not form.is_valid():
        return redirect("eth-deny-solution", pk)

    judgment_time = form.cleaned_data["judgment_time"]
    judgment_time_format = form.cleaned_data["judgment_time_format"]
    judgment_time_seconds = judgment_time * TIME_CONSTANT_TO_MULT[judgment_time_format]
    judgment_time_timedelta = datetime.timedelta(seconds=judgment_time_seconds)
    if judgment_time_timedelta < MINIMAL_JUDGMENT_TIME:
        judgment_time_timedelta = MINIMAL_JUDGMENT_TIME

    tx = smart_contract.deny_solution_tx(judgment_time_timedelta, sender)

    url = _get_sign_tx_url(JUDGMENT_CONTRACT_SIGN_TYPE, tx)

    return redirect(url)


@login_required()
@__error_decorator
def judgment_contract_info(request, pk: int):
    user = models.MarketplaceUser.objects.get(user=request.user)
    sender = user.eth_address

    contract_obj = get_object_or_404(models.JudgmentContract, pk=pk)
    customer = contract_obj.execution_contract.make_deal_contract.customer
    executor = contract_obj.execution_contract.executor

    smart_contract = JudgmentContractInterface(contract_obj.contract_address)
    closed_done = smart_contract.close()

    if closed_done:
        contract_obj.is_closed = True
        contract_obj.save()

    ctx = _get_task_info_contract_data_view(contract_obj.get_task_info_contract_address(), sender)
    merge_dicts(ctx, pk=pk,
                customer=customer,
                executor=executor,
                created_at=contract_obj.created,
                is_closed=contract_obj.is_closed)

    judgment_contract_ctx = smart_contract.get_data_view(sender)
    _process_judgment_contract_data_view(judgment_contract_ctx)
    merge_dicts(ctx, judgment_contract_ctx)

    time_left = ctx["judgment_time_left"]

    add_argument_form = None
    add_argument_operation_gas = None
    if user in (customer, executor) and time_left is not None:
        add_argument_form = forms.AddArgumentForm()
        tx = smart_contract.add_argument_tx(
            Argument(
                1,
                hash_text("tx"),
                datetime.datetime.now()
            ),
            sender
        )
        add_argument_operation_gas = to_eth(tx["gas"])
    merge_dicts(ctx, add_argument_form=add_argument_form,
                add_argument_operation_gas=add_argument_operation_gas)

    show_vote_button = False
    if user not in (customer, executor) and time_left is not None and \
            smart_contract.check_can_sender_vote(sender):
        show_vote_button = True

    merge_dicts(ctx, show_vote_button=show_vote_button,
                )

    execution_contract_pk = None
    if user in (customer, executor):
        execution_contract_pk = contract_obj.execution_contract.pk

    make_deal_contract_pk = contract_obj.execution_contract.make_deal_contract.pk

    alert_msg = request.GET.get("alert_msg", "")
    merge_dicts(ctx, make_deal_contract_pk=make_deal_contract_pk,
                execution_contract_pk=execution_contract_pk,
                alert_msg=alert_msg)

    return render(request, "eth/judgment_contract_view.html", context=ctx)


def _process_judgment_contract_data_view(data):
    data["customer_arguments"] = _process_arguments(data["customer_arguments"])
    data["executor_arguments"] = _process_arguments(data["executor_arguments"])
    _process_votes(data)
    data["judgment_time_left"] = _get_time_left(data["judgment_time_end"])


def _process_arguments(arguments):
    result = list()
    for argument in arguments:
        argument_text = models.Argument.objects.get(pk=argument.id).text
        result.append((argument_text, argument))
    return result


def _process_votes(data):
    votes = data["votes"]
    if votes is None:
        data["votes_for_customer"] = data["votes_for_executor"] = None
        return
    for_customer, for_executor = _split_votes(votes)
    data["votes_for_customer"] = for_customer
    data["votes_for_executor"] = for_executor


def _split_votes(votes):
    for_customer = list()
    for_executor = list()
    for vote in votes:
        vote_text = models.JudgeVote.objects.get(pk=vote.id).text
        judge = models.MarketplaceUser.objects.get(eth_address=vote.judge_address)
        data = (judge, vote_text, vote)
        if vote.verdict:
            for_customer.append(data)
        else:
            for_executor.append(data)
    return for_customer, for_executor


def _get_time_left(time_end):
    now = datetime.datetime.now()
    if now >= time_end:
        time_left = None
    else:
        time_left = time_end - now
    return time_left


@login_required()
@__error_decorator
def add_argument(request, pk: int):
    user = models.MarketplaceUser.objects.get(user=request.user)
    sender = user.eth_address

    contract_obj = models.JudgmentContract.objects.get(pk=pk)
    customer = contract_obj.execution_contract.make_deal_contract.customer
    executor = contract_obj.execution_contract.executor

    if user not in (customer, executor):
        raise PermissionDenied()

    form = forms.AddArgumentForm(request.POST)
    if form.is_valid():
        argument_text = form.cleaned_data["argument"]
        argument_id = _create_new_argument(argument_text)
        arg = Argument(
            argument_id,
            hash_text(argument_text),
            datetime.datetime.now()
        )

        smart_contract = JudgmentContractInterface(contract_obj.contract_address)
        tx = smart_contract.add_argument_tx(arg, sender)

        redirect_to = f"/eth/contract/judgment/info/{pk}"
        url = _get_sign_tx_url(DEFAULT_TRANSACTION_SIGN_TYPE, tx, redirect_to)

        return redirect(url)
    return redirect('eth-judgment-contact-info', pk, alert_msg="Error while adding argument")


def _create_new_argument(argument_text: str) -> int:
    # returns argument id
    argument_obj = models.Argument.objects.create(text=argument_text)
    return argument_obj.pk


@login_required()
@__error_decorator
def vote_for(request, pk: int, step: int):
    user = get_object_or_404(models.MarketplaceUser, user=request.user)
    sender = user.eth_address

    contract_obj = get_object_or_404(models.JudgmentContract, pk=pk)
    smart_contract = JudgmentContractInterface(contract_obj.contract_address)

    if not smart_contract.check_can_sender_vote(sender):
        return redirect('eth-judgment-contact-info', pk, alert_msg="You've already voted")

    if not step:
        return __vote_for_step_0(smart_contract, sender, pk)
    elif step == 1:
        return __vote_for_step_1(request, smart_contract, sender, pk)
    return __vote_for_step_2(request, smart_contract, sender, pk)


def __vote_for_step_0(smart_contract, sender, pk):
    task_info_contract_address = smart_contract.get_task_info_contract_address(sender)
    task_info_contract = TaskInfoContractInterface(task_info_contract_address)

    allowance = task_info_contract.get_security_deposit(sender)
    token = task_info_contract.get_token(sender)

    approving_tx = token.approve_tx(
        smart_contract.address,
        allowance,
        sender
    )

    activation_url = f"/eth/contract/judgment/votefor/{pk}&1"
    url = _get_sign_tx_url(DEFAULT_TRANSACTION_SIGN_TYPE, approving_tx, activation_url)
    return redirect(url)


def __vote_for_step_1(request, smart_contract, sender, pk):
    url = f"/eth/contract/judgment/votefor/{pk}&2"
    form = forms.VotingForm()

    task_info_contract_address = smart_contract.get_task_info_contract_address(sender)

    task_info_contract = TaskInfoContractInterface(task_info_contract_address)
    bid = task_info_contract.get_security_deposit(sender)
    token = task_info_contract.get_token(sender)

    ctx = {
        "url": url,
        "form": form,
        "bid": token.to_decimal(bid),
        "token_name": token.symbol(sender),
    }
    return render(request, "eth/vote_for.html", context=ctx)


def __vote_for_step_2(request, smart_contract, sender, pk):
    form = forms.VotingForm(request.POST)
    if not form.is_valid():
        return redirect("eth-judgment-contract-info", pk=pk)

    details = form.cleaned_data["details"]
    vote_id = _create_new_vote(details)
    verdict = form.cleaned_data["vote_for"] == forms.VotingForm.CHOICES[0][0]
    judge_vote = JudgeVote(
        vote_id,
        hash_text(details),
        datetime.datetime.now(),
        verdict,
        sender,
    )

    tx = smart_contract.vote_tx(judge_vote, sender)

    redirect_to = f"/eth/contract/judgment/info/{pk}"
    url = _get_sign_tx_url(DEFAULT_TRANSACTION_SIGN_TYPE, tx, redirect_to)
    return redirect(url)


def _create_new_vote(vote_details: str) -> int:
    # returns details id
    vote_obj = models.JudgeVote.objects.create(text=vote_details)
    return vote_obj.pk


@login_required()
@__error_decorator
def me(request):
    user = models.MarketplaceUser.objects.get(user=request.user)
    balance = W3.eth.get_balance(user.eth_address)
    ctx = {
        "eth_address": user.eth_address,
        "balance": to_eth(balance),
    }
    return render(request, "eth/me.html", context=ctx)


@login_required()
@__error_decorator
def owned_make_deal_contracts(request):
    user = models.MarketplaceUser.objects.get(user=request.user)
    contracts = models.MakeDealContract.objects.filter(customer=user).order_by("-created")
    contract_items = list()
    for contract in contracts:
        data = (
            contract.pk,
            contract.contract_address,
            contract.is_closed,
            contract.created
        )
        contract_items.append(data)
    ctx = {
        "contracts": contract_items,
        "url": "/eth/contract/make_deal/info/",
    }
    return render(request, "eth/my_contracts.html", context=ctx)


@login_required()
@__error_decorator
def owned_execution_contracts(request):
    user = models.MarketplaceUser.objects.get(user=request.user)
    contracts = models.ExecutionContract.objects.filter(
        make_deal_contract__customer=user.pk).order_by("-created")
    contract_items = list()
    for contract in contracts:
        data = (
            contract.pk,
            contract.contract_address,
            contract.is_closed,
            contract.created
        )
        contract_items.append(data)
    ctx = {
        "contracts": contract_items,
        "url": "/eth/contract/execution/info/",
    }
    return render(request, "eth/my_contracts.html", context=ctx)


@login_required()
@__error_decorator
def owned_judgment_contracts(request):
    user = models.MarketplaceUser.objects.get(user=request.user)
    contracts = models.JudgmentContract.objects.filter(
        execution_contract__make_deal_contract__customer__pk=user.pk).order_by("-created")
    contract_items = list()
    for contract in contracts:
        data = (
            contract.pk,
            contract.contract_address,
            contract.is_closed,
            contract.created
        )
        contract_items.append(data)
    ctx = {
        "contracts": contract_items,
        "url": "/eth/contract/judgment/info/"
    }
    return render(request, "eth/my_contracts.html", context=ctx)


@login_required()
@__error_decorator
def i_execute(request):
    user = models.MarketplaceUser.objects.get(user=request.user)
    contracts = models.ExecutionContract.objects.filter(executor=user, is_closed=False).order_by("-created")
    contract_items = list()
    for contract in contracts:
        data = (
            contract.pk,
            contract.contract_address,
            contract.is_closed,
            contract.created
        )
        contract_items.append(data)
    ctx = {
        "contracts": contract_items,
        "url": "/eth/contract/execution/info/",
    }
    return render(request, "eth/my_contracts.html", context=ctx)


@login_required()
@__error_decorator
def i_judge(request):
    user = models.MarketplaceUser.objects.get(user=request.user)
    votes = models.JudgeVote.objects.filter(judge=user).order_by("contract__created")
    contracts = list()
    for vote in votes:
        contract = vote.contract
        data = (
            contract.pk,
            contract.contract_address,
            contract.is_closed,
            contract.created
        )
        contracts.append(data)
    ctx = {
        "contracts": contracts,
        "url": "/eth/contract/judgment/info/",
    }
    return render(request, "eth/my_contracts.html", context=ctx)


# @login_required()
@__error_decorator
def actual_make_deal_contracts(request):
    contracts = models.MakeDealContract.objects.filter(is_closed=False).order_by("-created")
    contracts_data = list()
    for contract in contracts:
        data = (
            contract.pk,
            contract.contract_address,
            contract.is_closed,
            contract.created
        )
        contracts_data.append(data)
    ctx = {
        "contracts": contracts_data,
        "url": f"/eth/contract/make_deal/info/"
    }
    return render(request, "eth/actual_contracts.html", context=ctx)


# @login_required()
@__error_decorator
def actual_judgment_contracts(request):
    contracts = models.JudgmentContract.objects.filter(is_closed=False).order_by("-created")
    contracts_data = list()
    for contract in contracts:
        data = (
            contract.pk,
            contract.contract_address,
            contract.is_closed,
            contract.created
        )
        contracts_data.append(data)
    ctx = {
        "contracts": contracts_data,
        "url": "/eth/contract/judgment/info/",
    }
    return render(request, "eth/actual_contracts.html", context=ctx)
