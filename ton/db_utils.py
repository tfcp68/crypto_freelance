from . import models


def save_text(text, model) -> int:
    # returns pk
    return model.objects.create(text=text).pk


def get_text(pk, model) -> str:
    return model.objects.get(pk=pk).text


def save_transaction(transaction) -> int:
    # returns pk
    return models.TxData.objects.create(
        to=transaction["to"],
        value=str(transaction["value"]),
        state_init=transaction["stateInit"],
        data=str() if "data" not in transaction else transaction["data"]
    ).pk
