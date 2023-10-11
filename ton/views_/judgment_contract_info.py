from django.views.generic import View
from django.shortcuts import render, get_object_or_404
from ton import models
from python_contracts import ContractAPI, ContractStates
from ton.forms import AddArgumentForm
from ton.db_utils import get_text
import datetime
from ton.decorators import error_decorator


@error_decorator
def JudgmentContractInfoView(request, pk):
    return get(request, pk)


# class JudgmentContractInfoView(View):
#     @error_decorator
def get(request, pk):
    user = models.MarketplaceUser.objects.get(user=request.user)
    context = __get_base_context(pk)
    __update_context_by_button_states(context, user)
    return render(request, "ton/judgment_contract_info.html", context=context)


def __get_base_context(contract_pk):
    contract = get_object_or_404(models.Contract, pk=contract_pk)
    api = ContractAPI(contract.contract_address)
    context = __get_contract_data(api)
    task_text = models.Task.objects.get(pk=context["task_data"].id).text
    context.update(
        pk=contract_pk,
        address=contract.contract_address,
        created_at=contract.created,
        customer=contract.customer,
        task_text=task_text
    )
    __close_contract(api, context)
    __update_text_contents(context)
    return context


def __get_contract_data(api):
    state = api.get_state()
    price = api.get_price()
    security_deposit = api.get_security_deposit()
    judgment_time_end = api.get_judgment_time_end()
    now = datetime.datetime.now()
    data = {
        "state": state,
        "is_closed": state == ContractStates.CLOSED_AFTER_JUDGMENT,
        "task_data": api.get_task_data(),
        "price": price,
        "security_deposit": security_deposit,
        "solutions": api.get_solutions(),
        "executor": models.MarketplaceUser.objects.get(ton_address=api.get_executor()),
        # "judgment_time_left": datetime.timedelta(seconds=0) if now > judgment_time_end \
        #     else judgment_time_end - now,
        "customer_arguments": api.get_customer_arguments(),
        "executor_arguments": api.get_executor_arguments(),
        "num_votes": api.get_num_votes(),
        "votes": None if state == ContractStates.JUDGMENT else api.get_votes()
    }
    data["judgment_time_left"] = datetime.timedelta(seconds=0)
    if judgment_time_end is not None:
        if now < judgment_time_end:
            data["judgment_time_left"] = judgment_time_end - now
    return data


def __close_contract(api, context):
    if context["judgment_time_left"].total_seconds():
        return
    if context["state"] == ContractStates.CLOSED_AFTER_JUDGMENT:
        return
    api.close_judgment()
    context["state"] = ContractStates.CLOSED_AFTER_JUDGMENT


def __update_text_contents(context):
    __update_task_data_context(context)
    __update_solutions_context(context)
    __update_arguments_context(context, "customer_arguments")
    __update_arguments_context(context, "executor_arguments")
    __update_votes(context)


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


def __update_arguments_context(context, keyword):
    arguments = context[keyword]
    arguments_ids = [arg.id for arg in arguments]
    texts = models.Argument.objects.filter(pk__in=arguments_ids)
    result = list()
    for text, arg in zip(texts, arguments):
        result.append((text.text, arg.hash, arg.timestamp))
    context[keyword] = result


def __update_text_context(context, key, model):
    text_data = context[key]
    text_data_ids = [td.id for td in text_data]
    texts = model.objects.filter(pk__in=text_data_ids)
    result = list()
    for text, td in zip(texts, text_data):
        result.append((text.text, td.hash, td.timestamp))
    context[key] = result


def __update_votes(context):
    if context["votes"] is None:
        context["votes_for_customer"] = None
        context["votes_for_executor"] = None
        return
    votes_for_customer = list()
    votes_for_executor = list()
    for vote_data in context["votes"]:
        add_to = votes_for_customer if vote_data.vote else votes_for_executor
        text = get_text(vote_data.id, models.Vote)
        judge = get_object_or_404(models.MarketplaceUser, ton_address=vote_data.judge)
        add_to.append((
            judge, text,
            vote_data.hash, vote_data.timestamp
        ))
    context["votes_for_customer"] = votes_for_customer
    context["votes_for_executor"] = votes_for_executor


def __update_context_by_button_states(context, user):
    if context["is_closed"]:
        return
    __update_context_by_participant_button_states(context, user)
    __update_context_by_judge_button_states(context, user)


def __update_context_by_participant_button_states(context, user):
    if context["state"] == ContractStates.CLOSED_AFTER_JUDGMENT:
        return
    if user not in (context["customer"], context["executor"]):
        return
    if not context["judgment_time_left"].total_seconds():
        return
    context["add_argument_form"] = AddArgumentForm()


def __update_context_by_judge_button_states(context, user):
    if context["state"] == ContractStates.CLOSED_AFTER_JUDGMENT:
        return
    if user in (context["customer"], context["executor"]):
        return
    if not context["judgment_time_left"].total_seconds():
        return
    api = ContractAPI(context["address"])
    is_judge = api.is_judge(user.ton_address)
    context["show_vote_button"] = not is_judge
