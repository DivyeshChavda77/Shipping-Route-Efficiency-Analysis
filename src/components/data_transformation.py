import os
import sys

import pandas as pd

from dataclasses import dataclass

from src.exception import CustomException
from src.logger import logging


@dataclass
class DataTransformationConfig:
      processed_data_path = os.path.join("artifacts","processed_data.csv")

class DataTransformation:
    def __init__(self):
        self.transformation_config = DataTransformationConfig()

    def initiate_data_transformation(self, raw_data_path):

        logging.info("Starting Data Transformation")

        try:

            # Read raw dataset
            df = pd.read_csv(raw_data_path)

            logging.info("Raw dataset loaded successfully")

            # Convert Date Columns
            df["Order Date"] = pd.to_datetime(df["Order Date"],format="mixed")
            df["Ship Date"] = pd.to_datetime(df["Ship Date"],format="mixed" )

            logging.info("Date columns converted")

            # Feature Engineering
            
            # Shipping Days
            df["Shipping Days"] = (
                df["Ship Date"] - df["Order Date"]
            ).dt.days

            # Profit Margin (%)
            df["Profit Margin (%)"] = (
                df["Gross Profit"] / df["Sales"]
            ) * 100

            logging.info("Feature Engineering Completed")

            
            # Validation
            if df["Shipping Days"].isnull().sum() > 0:
                raise Exception(
                    "Shipping Days contains missing values."
                )

            if (df["Shipping Days"] < 0).any():
                raise Exception(
                    "Negative Shipping Days found."
                )

            logging.info("Validation Completed")

            
            # Save Processed Dataset

            os.makedirs(
                os.path.dirname(
                    self.transformation_config.processed_data_path
                ),
                exist_ok=True
            )

            df.to_csv(
                self.transformation_config.processed_data_path,
                index=False
            )

            logging.info("Processed dataset saved successfully")

            logging.info("Data Transformation Completed")

            return (
                self.transformation_config.processed_data_path
            )

        except Exception as e:
            raise CustomException(e, sys)