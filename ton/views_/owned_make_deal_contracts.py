from django.views.generic import View
from django.shortcuts import render
from ton import models
from python_contracts import ContractAPI, ContractStates
from ton.decorators import error_decorator


@error_decorator
def OwnedMakeDealContractsView(request):
    return get(request)


# class OwnedMakeDealContractsView(View):
#     @error_decorator
def get(request):
    user = models.MarketplaceUser.objects.get(user=request.user)
    contracts = models.Contract.objects.filter(customer=user).order_by("-created")
    contract_items = list()
    for contract in contracts:
        api = ContractAPI(contract.contract_address)
        state = api.get_state()
        if state is None or state < ContractStates.MAKE_DEAL:
            continue
        data = (
            contract.pk,
            contract.contract_address,
            state > ContractStates.MAKE_DEAL,
            contract.created
        )
        contract_items.append(data)
    ctx = {
        "contracts": contract_items,
        "url": "/ton/contract/make_deal/info/",
    }
    return render(request, "ton/my_contracts.html", context=ctx)
