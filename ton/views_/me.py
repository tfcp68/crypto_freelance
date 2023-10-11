from django.views.generic import View
from django.shortcuts import get_object_or_404, render
from ton import models
from ton.decorators import error_decorator


@error_decorator
def MeView(request):
    return get(request)

# class MeView(View):
#     @error_decorator
def get(request):
    user = get_object_or_404(models.MarketplaceUser, user=request.user)
    context = {
        "ton_address": user.ton_address
    }
    return render(request, "ton/me.html", context=context)
