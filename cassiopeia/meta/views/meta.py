from .data import ModelDataGet

class MetaView(ModelDataGet):
    permission_required = "meta.view_meta"
    view_attributes = {"application": "meta", "model": "Meta"}

class DatabasesView(ModelDataGet):
    permission_required = "meta.view_databases"
    view_attributes = {"application": "meta", "model": "Databases"}
