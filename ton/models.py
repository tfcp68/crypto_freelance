from django.db import models
from django.contrib.auth import models as auth_models
from utils import hash_text


# Create your models here.


class MarketplaceUser(models.Model):
    user = models.OneToOneField(
        auth_models.User,
        on_delete=models.CASCADE,
    )

    ton_address = models.CharField(
        max_length=48,
    )

    eth_address = models.CharField(
        max_length=42
    )

    def __str__(self):
        return f"{self.user}"

    def get_profile_url(self) -> str:
        return "#"


class Task(models.Model):
    text = models.TextField()

    def get_text_hash(self):
        return hash_text(self.text)


class Solution(models.Model):
    text = models.TextField()

    def get_text_hash(self):
        return hash_text(self.text)


class Argument(models.Model):
    text = models.TextField()

    def get_text_hash(self):
        return hash_text(self.text)


class Vote(models.Model):
    text = models.TextField()

    def get_text_hash(self):
        return hash_text(self.text)


class Contract(models.Model):
    contract_address = models.CharField(
        max_length=48,
    )

    state_init = models.TextField()

    created = models.DateTimeField(
        auto_now=True,
    )

    customer = models.ForeignKey(
        MarketplaceUser,
        on_delete=models.CASCADE,
    )


class Invitation(models.Model):
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
    )

    executor = models.ForeignKey(
        MarketplaceUser,
        on_delete=models.CASCADE,
    )


class TxData(models.Model):
    to = models.CharField(max_length=48)
    value = models.TextField()
    state_init = models.TextField()
    data = models.TextField()

    def to_dict(self):
        tx = {
            "to": self.to,
            "value": self.value,
            "stateInit": self.state_init,
        }
        if self.data:
            tx["data"] = self.data
        return tx
