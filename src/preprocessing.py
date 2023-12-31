from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder, OrdinalEncoder


def preprocess_data(
    train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Pre processes data for modeling. Receives train, val and test dataframes
    and returns numpy ndarrays of cleaned up dataframes with feature engineering
    already performed.

    Arguments:
        train_df : pd.DataFrame
        val_df : pd.DataFrame
        test_df : pd.DataFrame

    Returns:
        train : np.ndarray
        val : np.ndarrary
        test : np.ndarray
    """
    # Print shape of input data
    print("Input train data shape: ", train_df.shape)
    print("Input val data shape: ", val_df.shape)
    print("Input test data shape: ", test_df.shape, "\n")

    # Make a copy of the dataframes
    working_train_df = train_df.copy()
    working_val_df = val_df.copy()
    working_test_df = test_df.copy()

    # Correct outliers/anomalous values in numerical
    # columns (`DAYS_EMPLOYED` column).
    working_train_df["DAYS_EMPLOYED"].replace({365243: np.nan}, inplace=True)
    working_val_df["DAYS_EMPLOYED"].replace({365243: np.nan}, inplace=True)
    working_test_df["DAYS_EMPLOYED"].replace({365243: np.nan}, inplace=True)

    # Encoding for features with 2 categories.

    ordinal_encoder = OrdinalEncoder()
    ordinal_features = working_train_df.select_dtypes(include=["object"]).nunique()==2

    ordinal_columns = ordinal_features[ordinal_features].index.tolist()
    ordinal_encoder.fit(working_train_df[ordinal_columns])

    ordinal_train_df = ordinal_encoder.transform(working_train_df[ordinal_columns])
    ordinal_val_df = ordinal_encoder.transform(working_val_df[ordinal_columns])
    ordinal_test_df = ordinal_encoder.transform(working_test_df[ordinal_columns])

    # Encoding for features with more than 2 categories.

    onehot_encoder = OneHotEncoder(sparse_output=False)
    onehot_features = working_train_df.select_dtypes(include=["object"]).nunique() > 2
    onehot_columns = onehot_features[onehot_features].index.tolist()
    onehot_encoder.fit(working_train_df[onehot_columns])

    onehot_train_df = onehot_encoder.transform(working_train_df[onehot_columns])
    onehot_val_df = onehot_encoder.transform(working_val_df[onehot_columns])
    onehot_test_df = onehot_encoder.transform(working_test_df[onehot_columns])

    # Concatenate Ordinal and OneHot Encoded
    t_train_df = np.concatenate((ordinal_train_df, onehot_train_df) , axis=1)
    t_val_df = np.concatenate((ordinal_val_df, onehot_val_df), axis=1)
    t_test_df = np.concatenate((ordinal_test_df, onehot_test_df), axis=1)

    # Get The Numeric Numpy

    # Names
    numeric_features = working_train_df.select_dtypes(include=np.number).columns.to_list()

    n_train_df = working_train_df[numeric_features]
    n_val_df = working_val_df[numeric_features]
    n_test_df = working_test_df[numeric_features]

    # Concatenate The Already Encoded with Numerical
    working_train_df = np.concatenate((n_train_df, t_train_df) , axis=1)
    working_val_df = np.concatenate((n_val_df, t_val_df), axis=1)
    working_test_df = np.concatenate((n_test_df, t_test_df), axis=1)

    # Impute values for all columns with missing data or, just all the columns.
    imp_mean = SimpleImputer(missing_values=np.nan, strategy='mean')
    imp_mean.fit(working_train_df)

    t_train_df = imp_mean.transform(working_train_df)
    t_val_df = imp_mean.transform(working_val_df)
    t_test_df = imp_mean.transform(working_test_df)

    scaler = MinMaxScaler()
    scaler = scaler.fit(t_train_df)

    t_train_df = scaler.transform(t_train_df)
    t_val_df = scaler.transform(t_val_df)
    t_test_df = scaler.transform(t_test_df)

    return t_train_df, t_val_df, t_test_df
