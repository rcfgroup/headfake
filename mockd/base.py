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

        self.init_params()
        self.after_init_params()

    @property
    def names(self):
        return [self.name]

    def init_params(self):
        pass

    def after_init_params(self):
        [t.init_params(self) for t in self.transformers]

    def supplement_params(self, params):
        params["transformers"] = []
        return params
