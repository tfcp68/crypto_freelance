from django.contrib import admin

# Register your models here.

from . import models


@admin.register(models.MarketplaceUser)
class MarketplaceUserAdmin(admin.ModelAdmin):
    ...


@admin.register(models.Task)
class TaskAdmin(admin.ModelAdmin):
    ...


@admin.register(models.Solution)
class SolutionAdmin(admin.ModelAdmin):
    ...


@admin.register(models.Argument)
class ArgumentAdmin(admin.ModelAdmin):
    ...


@admin.register(models.JudgeVote)
class JudgeVoteAdmin(admin.ModelAdmin):
    ...


@admin.register(models.MakeDealContract)
class MakeDealContractAdmin(admin.ModelAdmin):
    ...


@admin.register(models.ExecutionContract)
class ExecutionContractAdmin(admin.ModelAdmin):
    ...


@admin.register(models.JudgmentContract)
class JudgmentContractAdmin(admin.ModelAdmin):
    ...


@admin.register(models.Invitation)
class InvitationAdmin(admin.ModelAdmin):
    ...


@admin.register(models.EthInvitation)
class EthInvitationAdmin(admin.ModelAdmin):
    ...
