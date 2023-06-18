import json
import logging
import os
import pickle
from typing import Optional

import pandas as pd
import tensorflow_hub
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.tree import DecisionTreeClassifier

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Model:
    COLUMNS = None

    @classmethod
    def _load_data(cls, path_to_data: str, columns: list[str] = COLUMNS) -> pd.DataFrame:
        logger.info(f"Opening '{path_to_data}'")
        try:
            df = pd.read_csv(path_to_data, usecols=columns).dropna(subset=columns)
        except FileNotFoundError as err:
            logger.error("Can't find '%s' file", path_to_data)
            raise err
        except Exception as err:
            logger.error("Error opening '%s' file", path_to_data)
            raise err
        return df


class CategorizationModel(Model):
    """
    The basic model to categorize texts
    """
    COLUMNS = ["overview", "genres"]

    def __init__(self, model_dir: Optional[str] = None) -> None:
        """
        Init a model
        :param model_dir: a path to a saved model
        """
        self.embedder = tensorflow_hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")
        if model_dir is None:
            self.mlb = MultiLabelBinarizer()
            self.model = None
        else:
            with open(f"{model_dir}/mlb.pickle", "rb") as f:
                self.mlb = pickle.load(f)
            with open(f"{model_dir}/model.pickle", "rb") as f:
                self.model = pickle.load(f)

    def fit(self, path_to_data: str, train_test_split: float = 0.8) -> None:
        """
        Trains a model based on the data loaded from `path_to_data` location
        :param path_to_data: the path to a .csv file containing `overview` and `genres` columns (the latter should have specific format).
        :param train_test_split: train-test split ratio (`0.8` means 80% of rows are used for training and the rest for testing)
        """
        df = super()._load_data(path_to_data, self.COLUMNS)
        df["genres"] = df["genres"].apply(lambda x: [label["name"] for label in json.loads(x.replace("'", '"'))])
        labels = list(self.mlb.fit_transform(df["genres"]))
        embeddings = list(df["overview"].apply(self._embed))
        self.model = DecisionTreeClassifier()
        self.model.fit(embeddings, labels)

    def predict(self, overview_string: str) -> list[str]:
        """
        Predict a genre of a given movie overview
        :param overview_string: A movie overview
        :return: A list of genres
        """
        if self.model is None:
            raise RuntimeError("A model needs to be `fit()` first before making predictions")
        predictions = self.model.predict([self._embed(overview_string)])
        return [self.mlb.classes_[j] for j in [i for i, e in enumerate(predictions[0]) if e == 1]]

    def save(self, model_dir: str) -> None:
        os.mkdir(model_dir)
        with open(f"{model_dir}/mlb.pickle", "wb") as f:
            pickle.dump(self.mlb, f, pickle.HIGHEST_PROTOCOL)
        with open(f"{model_dir}/model.pickle", "wb") as f:
            pickle.dump(self.model, f, pickle.HIGHEST_PROTOCOL)

    def _embed(self, input_sent: str) -> list[float]:
        """
        Highly unoptimized embedding function :)
        :param input_sent: A sentence to compute embedding for
        :return: An embedding vector
        """
        return self.embedder([input_sent])[0].numpy()
