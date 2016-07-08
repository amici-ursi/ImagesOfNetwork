from .hooks import Registry, EXPERIMENT_HOOKS, FEATURE_HOOKS
from random import randint
_FEATURES = {}
_EXPERIMENTS = {}
_EXPERIMENT_CONF = {}
LOG_NAME = "experiments.json"


class FeatureException(Exception):
    pass

class ExperimentException(Exception):
    pass

def feature(name, **passeddata):
    if name not in _FEATURES:
        raise FeatureException('Nonexistent feature')
    return _FEATURES[name].state(**passeddata)

def experiment(name, **passeddata):
    if name not in _EXPERIMENTS:
        raise ExperimentException('Nonexistent experiment')
    return _EXPERIMENTS[name].state(**passeddata)

def load_features_scope(conf):
    experiments = conf.get('experiment', [])
    features = conf.get('features', [])
    for experiment_name, experiment_data in experiments.items():
        if experiment_data['experiment_randomization'] == 'onread':
            _EXPERIMENT_CONF[experiment_name] = randint(0,
                experiment_data['experiment_range'])
        elif experiment_data['experiment_randomization'] == 'onload':
            pass
        else:
            raise ExperimentException(
                'experiment_randomization of {0} must be "onload" or "onread"'.format(
                    experiment_name)
            )
        Experiment(experiment_name, experiment_data)
    for feature_name, feature_data in experiments.items():
        Feature(feature_name, feature_data)
        
        
class Feature(object):
    def __init__(self, name, data):
        self.name = name
        self.data = data
        
    def state(self, **passeddata):
        return State(self, passeddata)

class Experiment(Feature):
    def __init__(self, name, data):
        self.randomization = data.pop('experiment_randomization')
        self.range = data.pop('experiment_range')
        super(Experiment, self).__init__(name, data)

class State(object):
    def __init__(self, feature, testdata):
        self.feature = feature
        self.testdata = testdata
        self._int = 0
        def checkvals(expectedval, testval):
            if isinstance(testval, list):
                return expectedval in testval
            return expectedval == testval
        for datakey, dataval in testdata.iteritems():
            if checkvals(feature.data.get(datakey, object()), dataval):
                if isinstance(self.feature, Feature):
                    self._int = 1
                    break
                elif isinstance(self.feature, Experiment):
                    if self.feature.randomization == 'onload':
                        self._int = random.randint(0, randomization)
                    else:
                        self._int = _EXPERIMENT_CONF[self.feature.name]
                    break
        
    def __enter__(self):
        self.current_data = {}
        {Feature: _FEATURE_HOOKS,
         Experiment: _EXPERIMENT_HOOKS}.get(type(self.feature)).get(
             self.feature.name, Registry())(self.feature)
        
    def __exit__(self, *_):
        self.logdata()
        
    def __int__(self):
        return self._int
        
    def __bool__(self):
        return bool(self._int)
