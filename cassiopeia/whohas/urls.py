from django.urls import path, include
from .views import WhohasView, ItemsView
from .views.items import ItemDetailView, ItemCreateView, ItemDeleteView
from .views.loans import LoansView, LoanDetailView, OverdueLoansView
from .views.lists import ItemCategoriesView, ItemTypesView, LoanStatusesView


urlpatterns = [
    path ('', WhohasView.as_view(), name = 'whohas'),
    path('items', ItemsView.as_view(), name='items'),
    path('items/create', ItemCreateView.as_view(), name='itemcreate'),
    path('itemdetail/<int:itemid>', ItemDetailView.as_view(), name='itemdetail'),
    path('itemdetail/<int:itemid>/delete', ItemDeleteView.as_view(), name='itemdelete'),
    path('itemcategories', ItemCategoriesView.as_view(), name='itemcategories'),
    path('itemtypes', ItemTypesView.as_view(), name='itemtypes'),
    path('loanstatuses', LoanStatusesView.as_view(), name='loanstatuses'),
    path('loans', LoansView.as_view(), name='loans'),
    path('loans/overdue', OverdueLoansView.as_view(), name='overdue_loans'),
    path('loandetail/<int:loanid>', LoanDetailView.as_view(), name='loandetail'),
#    path('itemtype/create', ItemTypeCreateView.as_view(), name='itemtypecreate'),
#    path('itemtypedetail/<int:itemid>', ItemTypeDetailView.as_view(), name='itemtypedetail'),
#    path('itemtypedetail/<int:itemid>/delete', ItemTypeDeleteView.as_view(), name='itemtypedelete'),
]
