import django.forms as djforms
from .constants import TIME_CONSTANTS
from .money_utils import to_nano, from_nano, eval_fee
import typing
from decimal import Decimal


class NewMakeDealContractForm(djforms.Form):
    task_text = djforms.CharField(label="Task", widget=djforms.Textarea)
    price = djforms.FloatField(label=f"Task price", min_value=1, step_size=0.05)
    security_deposit_percent = djforms.IntegerField(min_value=1, max_value=99, label="Security deposit percent")
    task_execution_time = djforms.IntegerField(min_value=1, label="Task execution time")
    task_execution_time_format = djforms.ChoiceField(choices=tuple(TIME_CONSTANTS.items()), label="Time format")

    def get_data(self) -> typing.Dict:
        cd = self.cleaned_data
        data = {
            "task_text": cd["task_text"],
            "price": cd["price"],
            "security_deposit_percent": Decimal(cd["security_deposit_percent"]),
            "task_execution_time": int(cd["task_execution_time"]),
            "task_execution_time_format": cd["task_execution_time_format"],
        }
        return data


class NewMakeDealContractPreviewForm(djforms.Form):
    user_address = djforms.CharField(min_length=48, max_length=48)
    task_text = djforms.CharField(widget=djforms.Textarea)
    price = djforms.FloatField(label=f"Task price")
    security_deposit_percent = djforms.IntegerField(min_value=1, max_value=99, label="Security deposit percent")
    task_execution_time = djforms.IntegerField(min_value=1, label="Task execution time")
    task_execution_time_format = djforms.ChoiceField(choices=tuple(TIME_CONSTANTS.items()), label="Time format")

    def get_data(self) -> typing.Dict:
        cd = self.cleaned_data
        price = cd["price"]
        price_nano = to_nano(price)
        security_deposit_percent = cd["security_deposit_percent"]
        security_deposit_value_nano = price_nano * security_deposit_percent // 100
        marketplace_fee = from_nano(eval_fee(price_nano))
        total_price = price + marketplace_fee
        return {
            "user_address": cd["user_address"],
            "task_text": cd["task_text"],
            "price": f"{price:.2f}",
            "security_deposit_percent": security_deposit_percent,
            "security_deposit_value": from_nano(security_deposit_value_nano),
            "marketplace_fee": f"{marketplace_fee:.2f}",
            "total_price": f"{total_price:.2f}",
            "task_execution_time": int(cd["task_execution_time"]),
            "task_execution_time_format": cd["task_execution_time_format"],
        }


class MakeDealContractExecutorsChoiceForm(djforms.Form):
    def __init__(self, executors, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["executors"] = djforms.MultipleChoiceField(label="Add executors",
                                                               choices=[(executor.pk, executor) for executor in
                                                                        executors])


class AddExecutionTimeForm(djforms.Form):
    additional_time = djforms.IntegerField(min_value=1, label="Task execution time")
    additional_time_format = djforms.ChoiceField(choices=tuple(TIME_CONSTANTS.items()), label="Time format")


class AddSolutionForm(djforms.Form):
    solution_text = djforms.CharField(widget=djforms.Textarea, label="Solution")


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
