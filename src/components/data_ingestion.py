import os
import sys

import pandas as pd

from dataclasses import dataclass

from src.exception import CustomException
from src.logger import logging


@dataclass
class DataIngestionConfig:
    raw_data_path = os.path.join("artifacts", "raw_data.csv")

class DataIngestion:
    def __init__(self):
        self.ingestion_config = DataIngestionConfig()

    def initiate_data_ingestion(self):

        logging.info("Started Data Ingestion")

        try:
            # Read Dataset
            df = pd.read_csv("data/Nassau-Candy-Distributor.csv")

            logging.info("Dataset loaded successfully")

            # Create artifacts folder
            os.makedirs(
                os.path.dirname(
                    self.ingestion_config.raw_data_path
                ),
                exist_ok=True,
            )

            # Save Raw Dataset
            df.to_csv(
                self.ingestion_config.raw_data_path,
                index=False,
                header=True,
            )

            logging.info("Raw dataset saved successfully")

            logging.info("Data Ingestion Completed")

            return self.ingestion_config.raw_data_path

        except Exception as e:
            raise CustomException(e, sys)