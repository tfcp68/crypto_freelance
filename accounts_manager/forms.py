from django import forms as djforms


class AddressForm(djforms.Form):
    eth_address = djforms.CharField(
        label="ETH Address",
        min_length=42,
        max_length=42
    )

    ton_address = djforms.CharField(
        label="TON Address",
        min_length=48,
        max_length=48,
    )

    def clean_ton_address(self):
        return self.cleaned_data["ton_address"]

    def clean_eth_address(self):
        return self.cleaned_data["eth_address"]
