from bazaar.goods.models import AbstractGood


class Good(AbstractGood):
    """
    Test class for goods
    """
    @property
    def cost(self):
        return 1
