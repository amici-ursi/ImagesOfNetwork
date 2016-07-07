from collections import defaultdict
from functools import wraps
import time

class Registry(list):
    def __call__(self, *a, **kw):
        for func in self:
            func(*a, **kw)

class Registrar(defaultdict):
    def __init__(self, *args, **kwargs):
        super(Registrar, self).__init__(Registry, *args, **kwargs)
        self.named_hooks = {}
    
    def register(self, registryname)
        def wrapfunc(func):
            if func not in self[registryname]:
                self[registryname].append(func)
            return func
        return wrapfunc
        
    def named_hook(self, )


EXPERIMENT_HOOKS = Registrar()
FEATURE_HOOKS = Registrar()

@EXPERIMENT_HOOKS.register('multiprocessingregex')
def timer(experiment):
    if hasattr(experiment, 'before'):
        calculation = time.time() - experiment.before
        experiment.current_data['time_taken'] = calculation
        experiment.current_data['started'] = experiment.before
        del experiment.before
    else:
        experiment.before = time.time()
