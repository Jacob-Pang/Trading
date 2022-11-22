import numpy as np

cdef class IndicatorBase:
    def __init__(self) -> None:
        self.current_observation = np.zeros(shape=(self.get_num_features(),), dtype=float)

    # Getters
    cpdef int get_num_features(self):
        # Number of features per observation.
        return 1

    cpdef double get_feature(self, int feature_index):
        return self.current_observation[feature_index]

    cpdef np.ndarray[double, ndim=1] get_observation(self):
        return np.asarray(self.current_observation, dtype=float)

    # Mutators
    cpdef void set(self, int feature_index, double feature_value):
        self.current_observation[feature_index] = feature_value
    
    cpdef void update(self):
        # Performs update to store current observation
        return


    def __reduce__(self):
        return (self.__class__, tuple())


cdef class FeaturesCompiler:
    def __init__(self, indicators: list[IndicatorBase]) -> None:
        self.indicators = indicators
        self.num_features = 0

        for indicator in self.indicators:
            self.num_features += indicator.get_num_features()

        self.features = np.zeros(shape=(self.num_features,), dtype=float)

    cpdef int get_num_features(self):
        return self.num_features

    cpdef np.ndarray[double, ndim=1] get(self):
        # Runs update and returns the features for the current observation.
        cdef int feature_index = 0
        cdef int sub_feature_index
        cdef int num_features

        for indicator in self.indicators:
            indicator.update()
            
            for sub_feature_index in range(indicator.get_num_features()):
                self.features[feature_index] = indicator.get_feature(sub_feature_index)
                feature_index += 1

        return np.asarray(self.features, dtype=float)

    def __reduce__(self) -> tuple:
        return (self.__class__, (self.indicators,))
