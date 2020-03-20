class ParamList:
    default_params = {}

    def __init__(self, **kwargs):
        params = self.default_params
        params = self.supplement_params(params)
        for k, v in params.items():
            if k not in kwargs:
                kwargs[k] = v

        for k, v in kwargs.items():
            setattr(self, k, v)

        self.init()


    @property
    def names(self):
        return [self.name]

    def init(self):
        pass

    def supplement_params(self, params):
        return params
