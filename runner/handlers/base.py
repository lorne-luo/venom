class BaseHandler():
    subscribes = ()

    def __init__(self, context):
        self._context = context

    def set_context(self, context):
        if not self._context:
            self._context = context

    def put(self, event):
        return self._context.put(event)

    def get(self):
        return self._context.get()

    def process(self, event):
        raise NotImplementedError
