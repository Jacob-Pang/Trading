import os
import pickle
import sys
import numpy as np
import tensorflow as tf

from sklearn.preprocessing import StandardScaler
from tensorflow.python import keras
from tensorflow.python.keras.layers import Input, Dense
from tensorflow.python.keras.initializers import Constant
from config import *

ROOT_DPATH = os.path.dirname(os.path.dirname(__file__))
DATA_DPATH = os.path.join(os.path.dirname(__file__), "data")
MODELS_DPATH = os.path.join(os.path.dirname(__file__), "models")

sys.path.insert(0, ROOT_DPATH)

METRICS = [
    keras.metrics.BinaryAccuracy(
        name='accuracy', threshold=CLASSIFICATION_THRESHOLD
    ),
    keras.metrics.Precision(
        name="precision", thresholds=CLASSIFICATION_THRESHOLD,
    )
]

class BatchGenerator:
    def __init__(self, x: np.ndarray, y: np.ndarray, batch_size):
        self.x = x
        self.y = y
        self.batch_size = batch_size
        self.index = 0

        self.num_batches = (self.y.shape[0] // self.batch_size + 1) \
            if (self.y.shape[0] % self.batch_size) else \
            self.y.shape[0] // self.batch_size

    def get_steps_per_epoch(self) -> int:
        # Number of batches per epoch
        return self.num_batches

    def __iter__(self):
        # Not called from fit()
        return self

    def __next__(self) -> tuple[np.ndarray, np.ndarray]:
        if self.index >= self.num_batches:
            # Reset
            self.index = 0
            shuffling = np.random.permutation(self.x.shape[0])
            self.x = self.x[shuffling]
            self.y = self.y[shuffling]

        x_batch = self.x[self.index * self.batch_size:min((self.index + 1) * self.batch_size, self.y.shape[0])]
        y_batch = self.y[self.index * self.batch_size:min((self.index + 1) * self.batch_size, self.y.shape[0])]
        self.index += 1

        return x_batch, y_batch

def make_classifier(num_features: int, outputs: np.ndarray, metrics: list = METRICS):
    positives = np.sum(outputs)
    negatives = outputs.shape[0] - positives
    bias_initializer = Constant(np.log([positives/ negatives]))

    # Layers
    input_layer = Input(shape=(num_features))
    dense_layer = Dense(units=512, activation="relu")(input_layer)
    dense_layer = Dense(units=256, activation="relu")(input_layer)
    output_layer = Dense(units=1, activation="sigmoid", bias_initializer=bias_initializer) \
            (dense_layer) # Binary output

    model = keras.Model(input_layer, output_layer)
    model.compile(optimizer="adam", loss='binary_crossentropy', metrics=metrics)

    return model

def main():
    # TODO: add summary of performance
    # Load datasets
    with open(os.path.join(DATA_DPATH, "data_pipeline.pickle"), "rb") as file:
        data_pipeline = pickle.load(file)

    features_compiler = data_pipeline.get("features_compiler")

    observations = np.load(os.path.join(DATA_DPATH, "observations.npy"))
    long_signals = np.load(os.path.join(DATA_DPATH, "long_signals.npy"))
    short_signals = np.load(os.path.join(DATA_DPATH, "short_signals.npy"))

    # Creating scalers and dataset generators
    long_scaler = StandardScaler()
    long_observations = observations[:long_signals.shape[0]]
    long_scaler.fit(long_observations[-2000000:])

    long_generator = BatchGenerator(
        x=long_scaler.transform(long_observations[-2000000:]),
        y=long_signals[-2000000:],
        batch_size=BATCH_SIZE
    )

    short_scaler = StandardScaler()
    short_observations = observations[:short_signals.shape[0]]
    short_scaler.fit(short_observations[-2000000:])

    short_generator = BatchGenerator(
        x=short_scaler.transform(short_observations[-2000000:]),
        y=short_signals[-2000000:],
        batch_size=BATCH_SIZE
    )

    # Creating tensorflow models
    long_classifier = make_classifier(features_compiler.get_num_features(), long_signals)
    short_classifier = make_classifier(features_compiler.get_num_features(), short_signals)

    long_classifier.fit(
        long_generator,
        steps_per_epoch=long_generator.get_steps_per_epoch(),
        epochs=EPOCHS,
        verbose=True
    )

    long_classifier.save(os.path.join(MODELS_DPATH, "training", "long_trading_engine"))
    
    with open(os.path.join(MODELS_DPATH, "training", "long_scaler.pickle"), "wb") as file:
        pickle.dump(long_scaler, file)

    short_classifier.fit(
        short_generator,
        steps_per_epoch=short_generator.get_steps_per_epoch(),
        epochs=EPOCHS,
        verbose=True
    )

    short_classifier.save(os.path.join(MODELS_DPATH, "training", "short_trading_engine"))

    with open(os.path.join(MODELS_DPATH, "training", "short_scaler.pickle"), "wb") as file:
        pickle.dump(short_scaler, file)
    
if __name__ == "__main__":
    main()
