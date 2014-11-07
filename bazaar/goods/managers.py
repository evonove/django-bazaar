from model_utils.managers import InheritanceManagerMixin, PassThroughManager


class ProductsManager(InheritanceManagerMixin, PassThroughManager):
    pass
