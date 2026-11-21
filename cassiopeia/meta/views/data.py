from django.apps import apps
from .web import WebMainRender

class ModelDataGet(WebMainRender):
    def data_prepare(self):
        model = apps.get_model(
                        self.view_attributes["application"],
                        self.view_attributes["model"],
        )
        template_name = f"{model._meta.model_name}.html"
        records = list(model._default_manager.order_by("pk"))
        return self.view_attributes["application"], self.view_attributes["model"], template_name, records