from ._util import FrameworkManager, _split_dataset
import pandas as pd

def dataset(train_valid_test=(0.6, 0.2, 0.2)):
    train_amnt, valid_amnt, test_amnt = train_valid_test

    assert train_amnt + valid_amnt + test_amnt == 1, "the train_valid_test splits should all add up to 1.0"

    FrameworkManager.train_valid_test_splits = train_valid_test

    def dataset_decorator(func):
        # Get the dataset from the user-provided function
        X, y = func()

        FrameworkManager.all_X = X
        FrameworkManager.all_y = y

        FrameworkManager.features = pd.DataFrame(index=X.index.copy())

        _split_dataset()

        return X

    return dataset_decorator

def preprocess(func):
    FrameworkManager.preprocess_func = func

    X = func(FrameworkManager.all_X)

    FrameworkManager.all_X = X

    FrameworkManager.features = pd.DataFrame(index=X.index.copy())

    _split_dataset() # resplit dataset

    return X

def feature(name):
    def feature_decorator(func):
        FrameworkManager.feature_funcs.append(func)

        # The function is explicitly called with the keyword argument for end-user consistancy (note: is this a good thing? yes? no?)
        feature_output = pd.DataFrame(func(X=FrameworkManager.all_X.copy()), index=FrameworkManager.features.index)

        FrameworkManager.features = FrameworkManager.features.join(feature_output)

        return feature_output

    return feature_decorator

def model(name):
    def model_decorator(func):
        define_func, train_func, predict_func = func()

        FrameworkManager.models[name] = {}
        FrameworkManager.models[name]['define'] = define_func
        FrameworkManager.models[name]['train'] = train_func
        FrameworkManager.models[name]['predict'] = predict_func

        num_columns = len(FrameworkManager.all_X.columns)
        num_columns += len(FrameworkManager.features.columns)

        FrameworkManager.models[name]['model'] = define_func(num_columns)

    return model_decorator
