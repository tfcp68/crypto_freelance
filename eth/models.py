from django.db import models
from django.contrib.auth import models as auth_models

from api.utility import hash_text
from ton.models import MarketplaceUser, Task, Solution, Argument, Vote, Invitation


# Create your models here.
JudgeVote = Vote


# class Task(models.Model):
#     text = models.TextField()
#
#     def get_text_hash(self):
#         return hash_text(self.text)
#
#
# class Solution(models.Model):
#     text = models.TextField()
#
#     def get_text_hash(self):
#         return hash_text(self.text)
#
#
# class Argument(models.Model):
#     text = models.TextField()
#
#     def get_text_hash(self):
#         return hash_text(self.text)
#
#
# class JudgeVote(models.Model):
#     text = models.TextField()
#
#     def get_text_hash(self):
#         return hash_text(self.text)


# class TaskInfoContract(models.Model):
#     contract_address = models.CharField(
#         max_length=42,
#     )


class MakeDealContract(models.Model):
    contract_address = models.CharField(
        max_length=42,
    )

    task_info_contract_address = models.CharField(
        max_length=42,
    )

    created = models.DateTimeField(
        auto_now=True,
    )

    customer = models.ForeignKey(
        MarketplaceUser,
        on_delete=models.CASCADE,
    )

    is_closed = models.BooleanField(
        default=False,
    )

    def get_task_info_contract_address(self) -> str:
        return self.task_info_contract_address


class ExecutionContract(models.Model):
    contract_address = models.CharField(
        max_length=42,
    )

    make_deal_contract = models.ForeignKey(
        MakeDealContract,
        on_delete=models.CASCADE,
    )

    created = models.DateTimeField(
        auto_now=True,
    )

    is_closed = models.BooleanField(
        default=False,
    )

    executor = models.ForeignKey(
        MarketplaceUser,
        on_delete=models.CASCADE,
    )

    def get_task_info_contract_address(self) -> str:
        return self.make_deal_contract.get_task_info_contract_address()


class JudgmentContract(models.Model):
    contract_address = models.CharField(
        max_length=42,
    )

    execution_contract = models.ForeignKey(
        ExecutionContract,
        on_delete=models.CASCADE,
    )

    created = models.DateTimeField(
        auto_now=True,
    )

    is_closed = models.BooleanField(
        default=False,
    )

    def get_task_info_contract_address(self) -> str:
        return self.execution_contract.get_task_info_contract_address()


class EthInvitation(models.Model):
    contract = models.ForeignKey(
        MakeDealContract,
        on_delete=models.CASCADE,
    )

    executor = models.ForeignKey(
        MarketplaceUser,
        on_delete=models.CASCADE,
    )
