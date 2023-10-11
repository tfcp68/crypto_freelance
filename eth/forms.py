from django import forms as djforms
from .constants import TIME_CONSTANTS
from .utility import *
from .allowed_tokens import ALLOWED_TOKENS, get_token_from_symbol

from api.contract_interfaces import ERC20ContractInterface

import typing
import datetime


class TimeChoiceForm(djforms.Form):
    task_execution_time = djforms.IntegerField(min_value=1, label="Task execution time")
    task_execution_time_format = djforms.ChoiceField(choices=tuple(TIME_CONSTANTS.items()), label="Time format")

    def get_data(self) -> typing.Dict:
        cd = self.cleaned_data
        return {
            "task_execution_time": int(cd["task_execution_time"]),
            "task_execution_time_format": cd["task_execution_time_format"],
        }

    def to_timedelta(self) -> datetime.timedelta:
        task_execution_time = int(self.cleaned_data["task_execution_time"])
        task_execution_time_format = self.cleaned_data["task_execution_time_format"]
        time_in_seconds = task_execution_time * TIME_CONSTANT_TO_MULT[task_execution_time_format]
        return datetime.timedelta(seconds=time_in_seconds)


class NewMakeDealContractForm(djforms.Form):
    token = djforms.ChoiceField(label="Token symbol", choices=ALLOWED_TOKENS)
    task_text = djforms.CharField(label="Task", widget=djforms.Textarea)
    price = djforms.FloatField(label=f"Task price")
    # , min_value=10 ** -TOKEN_DECIMALS, step_size=10 ** -TOKEN_DECIMALS)
    security_deposit_percent = djforms.IntegerField(min_value=1, max_value=99, label="Security deposit percent")
    task_execution_time = djforms.IntegerField(min_value=1, label="Task execution time")
    task_execution_time_format = djforms.ChoiceField(choices=tuple(TIME_CONSTANTS.items()), label="Time format")

    def get_data(self) -> typing.Dict:
        cd = self.cleaned_data
        # token = get_token_from_symbol(cd["token_symbol"])
        token = ERC20ContractInterface(cd["token"])
        data = {
            "token_symbol": token.symbol(),
            "task_text": cd["task_text"],
            "price": token.to_minimal_units(str_to_decimal_token_value(cd["price"])),
            "security_deposit_percent": int(cd["security_deposit_percent"]),
            "task_execution_time": int(cd["task_execution_time"]),
            "task_execution_time_format": cd["task_execution_time_format"],
        }
        return data


class NewMakeDealContractPreviewForm(djforms.Form):
    token_symbol = djforms.CharField(label="Token symbol")
    user_address = djforms.CharField(min_length=42, max_length=42)
    task_text = djforms.CharField(widget=djforms.Textarea)
    price = djforms.FloatField(label=f"Task price")
    security_deposit_percent = djforms.IntegerField(min_value=1, max_value=99, label="Security deposit percent")
    task_execution_time = djforms.IntegerField(min_value=1, label="Task execution time")
    task_execution_time_format = djforms.ChoiceField(choices=tuple(TIME_CONSTANTS.items()), label="Time format")

    def get_data(self) -> typing.Dict:
        cd = self.cleaned_data
        token = get_token_from_symbol(cd["token_symbol"])
        price = token.to_decimal(int(cd["price"]))
        price_in_minimal_units = token.to_minimal_units(price)
        security_deposit_percent = int(cd["security_deposit_percent"])
        marketplace_fee = token.to_decimal(eval_marketplace_fee(price_in_minimal_units))
        total_price = price + marketplace_fee
        return {
            "token_address": token.address,
            "user_address": cd["user_address"],
            "task_text": cd["task_text"],
            "price": price,
            "security_deposit_percent": security_deposit_percent,
            "security_deposit_value": token.to_decimal(eval_percent(price_in_minimal_units, security_deposit_percent)),
            "marketplace_fee": marketplace_fee,
            "total_price": total_price,
            "task_execution_time": int(cd["task_execution_time"]),
            "task_execution_time_format": cd["task_execution_time_format"],
        }

    def get_timedelta(self) -> datetime.timedelta:
        task_execution_time = int(self.cleaned_data["task_execution_time"])
        task_execution_time_format = self.cleaned_data["task_execution_time_format"]
        time_in_seconds = task_execution_time * TIME_CONSTANT_TO_MULT[task_execution_time_format]
        return datetime.timedelta(seconds=time_in_seconds)


class MakeDealContractExecutorsChoiceForm(djforms.Form):
    def __init__(self, executors, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["executors"] = djforms.MultipleChoiceField(label="Add executors",
                                                               choices=[(executor.pk, executor) for executor in
                                                                        executors])


class AddSolutionForm(djforms.Form):
    solution_text = djforms.CharField(widget=djforms.Textarea, label="Solution")


class AddExecutionTimeForm(djforms.Form):
    task_execution_time = djforms.IntegerField(min_value=1, label="Task execution time")
    task_execution_time_format = djforms.ChoiceField(choices=tuple(TIME_CONSTANTS.items()), label="Time format")


class DeclineSolutionForm(djforms.Form):
    judgment_time = djforms.IntegerField(min_value=1, label="Voting time")
    judgment_time_format = djforms.ChoiceField(choices=tuple(TIME_CONSTANTS.items())[1:], label="Time format")


class AddArgumentForm(djforms.Form):
    argument = djforms.CharField(label="Argument", widget=djforms.Textarea)


class VotingForm(djforms.Form):
    CHOICES = (
        ('c', 'For customer'),
        ('e', 'For executor')
    )

    details = djforms.CharField(label="Argument", widget=djforms.Textarea)
    vote_for = djforms.ChoiceField(label="Vote", choices=CHOICES)
