class OrderGrabber(object):
    model = None
    processor_class = None

    def __init__(self):
        self._processor = self.processor_class()

    def process(self, order):
        self._processor.process(order)

    def grab_orders(self):
        """
        This method should yield a dict for each retrieved order
        """
        raise NotImplementedError

    def run(self):
        for order in self.grab_orders():
            pass
