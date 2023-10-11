from django.views.generic import TemplateView


class SomethingWentWrongView(TemplateView):
    template_name = "ton/something_went_wrong.html"
