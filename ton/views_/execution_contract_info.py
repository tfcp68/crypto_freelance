from django.views.generic import View
from django.shortcuts import render, get_object_or_404
from ton import models
from python_contracts import ContractAPI, ContractStates
from ton.forms import AddExecutionTimeForm, AddSolutionForm
import datetime
from ton.decorators import error_decorator
from ton.money_utils import from_nano


@error_decorator
def ExecutionContractInfoView(request, pk):
    return get(request, pk)


# class ExecutionContractInfoView(View):
#     @error_decorator
def get(request, pk):
    user = models.MarketplaceUser.objects.get(user=request.user)
    context = __get_base_context(pk)
    __update_context_by_button_states(context, user)
    return render(request, "ton/execution_contract_info.html", context=context)


def __get_base_context(contract_pk):
    contract = get_object_or_404(models.Contract, pk=contract_pk)
    api = ContractAPI(contract.contract_address)
    context = __get_contract_data(api)
    task_text = models.Task.objects.get(pk=context["task_data"].id)
    context.update(
        pk=contract_pk,
        address=contract.contract_address,
        created_at=contract.created,
        customer=contract.customer,
        task_text=task_text
    )
    __update_text_contents(context)
    return context


def __get_contract_data(api):
    state = api.get_state()
    price = api.get_price()
    security_deposit = api.get_security_deposit()
    execution_time_end = api.get_execution_time_end()
    security_deposit_percent = int(security_deposit / price * 100)
    now = datetime.datetime.now()
    data = {
        "state": state,
        "is_closed": state > ContractStates.EXECUTION,
        "task_data": api.get_task_data(),
        "price": f"{from_nano(price):.2f}",
        "security_deposit": f"{from_nano(security_deposit):.2f}",
        "security_deposit_percent": security_deposit_percent,
        "solutions": api.get_solutions(),
        "executor": models.MarketplaceUser.objects.get(ton_address=api.get_executor()),
        # "execution_time_left": datetime.timedelta(seconds=0) \
        #     if execution_time_end is not None and now > execution_time_end \
        #     else execution_time_end - now
    }
    execution_time_left = datetime.timedelta(seconds=0)
    if execution_time_end is not None:
        if now < execution_time_end:
            execution_time_left = execution_time_end - now
    data["execution_time_left"] = execution_time_left
    return data


def __update_text_contents(context):
    __update_task_data_context(context)
    __update_solutions_context(context)


def __update_task_data_context(context):
    task_data = context["task_data"]
    context["task_text"] = models.Task.objects.get(pk=task_data.id).text


def __update_solutions_context(context):
    solutions = context["solutions"]
    solutions_ids = [sol.id for sol in solutions]
    texts = models.Solution.objects.filter(pk__in=solutions_ids)
    result = list()
    for text, td in zip(texts, solutions):
        result.append((text.text, td.hash, td.timestamp))
    context["solutions"] = result


def __update_context_by_button_states(context, user):
    context["show_judgment_contract_button"] = context["is_closed"] and context["state"] > ContractStates.CLOSED
    if context["is_closed"]:
        return
    __update_context_by_customer_button_states(context, user)
    __update_context_by_executor_button_states(context, user)


def __update_context_by_customer_button_states(context, user):
    context["add_execution_time_form"] = None
    context["show_solution_manage_button"] = False
    if user == context["customer"]:
        context["add_execution_time_form"] = AddExecutionTimeForm()
        if context["execution_time_left"].total_seconds() == 0:
            context["show_solution_manage_button"] = True


def __update_context_by_executor_button_states(context, user):
    context["add_solution_form"] = None
    context["show_finish_execution_button"] = False
    if user == context["executor"] and context["execution_time_left"].total_seconds():
        context["add_solution_form"] = AddSolutionForm()
        if context["solutions"]:
            context["show_finish_execution_button"] = True
