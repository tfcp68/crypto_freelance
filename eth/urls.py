from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="eth-index"),
    path('__defaultaccounts/', views.default_accounts, name="eth-default-accounts"),
    path('somethingwentwrong/', views.something_went_wrong, name="eth-something-went-wrong"),
    path('signtx/', views.sign_tx, name="eth-sign-tx"),

    path('contract/make_deal/new', views.new_make_deal_contract, name="eth-new-make-deal-contract"),
    path('contract/make_deal/new/preview', views.new_make_deal_contract_preview,
         name="eth-new-make-deal-contract-preview"),
    path('contract/make_deal/info/<int:pk>', views.make_deal_contract_info, name="eth-make-deal-contract-info"),
    path('contract/make_deal/activate/<int:pk>&<int:step>', views.make_deal_contract_activate,
         name="eth-make-deal-contract-activate"),
    path('contract/make_deal/respond/<int:pk>&<int:step>/', views.respond_to_make_deal_contract,
         name="eth-respond-to-make-deal-contract"),
    path('contract/make_deal/acceptinvitation/<int:pk>', views.accept_invitation, name="eth-accept-invitation"),

    path('contract/execution/info/<int:pk>', views.execution_contract_info, name="eth-execution-contract-info"),
    path('contract/execution/finishexecution/<int:pk>', views.finish_execution, name="eth-finish-execution"),
    path('contract/execution/addsolution/<int:pk>', views.add_solution, name="eth-add-solution"),
    path('contract/execution/addexecutiontime/<int:pk>', views.add_execution_time, name="eth-add-execution-time"),
    path('contract/execution/acceptsolution/<int:pk>', views.accept_solution, name="eth-accept-solution"),
    path('contract/execution/denysolution/<int:pk>', views.deny_solution, name="eth-deny-solution"),

    path('contract/judgment/info/<int:pk>', views.judgment_contract_info, name="eth-judgment-contract-info"),
    path('contract/judgment/addargument/<int:pk>', views.add_argument, name="eth-add-argument"),
    path('contract/judgment/votefor/<int:pk>&<int:step>', views.vote_for, name="eth-vote-for"),

    path('me', views.me, name="eth-me"),
    path('me/ownedmakedealcontracts', views.owned_make_deal_contracts, name="eth-owned-make-deal-contracts"),
    path('me/ownewexecutioncontracts', views.owned_execution_contracts, name="eth-owned-execution-contracts"),
    path('me/ownedjudgmentcontracts', views.owned_judgment_contracts, name="eth-owned-judgment-contracts"),
    path('me/iexecute', views.i_execute, name="eth-i-execute"),
    path('me/ijudge', views.i_judge, name="eth-i-judge"),

    path('actual/makedeal', views.actual_make_deal_contracts, name="eth-actual-make-deal-contracts"),
    path('actual/judgment', views.actual_judgment_contracts, name="eth-actual-judgment-contracts"),
]
