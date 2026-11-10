import sys
import pandas as pd

from src.logger import logging
from src.exception import CustomException


class RouteAnalysis:
    """
    Performs business analytics on the processed dataset.
    """

    def __init__(self, processed_data_path):
        self.processed_data_path = processed_data_path

        logging.info("Loading processed dataset")

        self.df = pd.read_csv(processed_data_path)
    
    # KPI Summary

    def get_kpis(self):
        try:
            kpis = {
                "Total Sales": round(self.df["Sales"].sum(), 2),
                "Total Profit": round(self.df["Gross Profit"].sum(), 2),
                "Total Cost": round(self.df["Cost"].sum(), 2),
                "Total Units": int(self.df["Units"].sum()),
                "Average Shipping Days": round(self.df["Shipping Days"].mean(), 2),
                "Average Profit Margin": round(self.df["Profit Margin (%)"].mean(), 2),
            }
            return kpis

        except Exception as e:
            raise CustomException(e, sys)

    # Ship Mode Summary

    def ship_mode_summary(self, df=None):
        try:
            return (
                self.df.groupby("Ship Mode")
                .agg(
                    Average_Sales=("Sales", "mean"),
                    Average_Profit=("Gross Profit", "mean"),
                    Average_Shipping_Days=("Shipping Days", "mean"),
                    Total_Orders=("Order ID", "count"),
                ).round(2)
                .sort_values(by="Average_Sales",ascending=False)
            )

        except Exception as e:
            raise CustomException(e, sys)

    # Region Summary

    def region_summary(self, df=None):
        try:
            return (
                self.df.groupby("Region")
                .agg(
                    Average_Sales=("Sales", "mean"),
                    Average_Profit=("Gross Profit", "mean"),
                    Average_Shipping_Days=("Shipping Days", "mean"),
                    Total_Orders=("Order ID", "count"),
                ).round(2)
                .sort_values(
                    by="Average_Shipping_Days",ascending=False)
            )

        except Exception as e:
            raise CustomException(e, sys)

    # State Summary

    def state_summary(self, df=None):
        try:
            return (
                self.df.groupby("State/Province")
                .agg(
                    Average_Shipping_Days=("Shipping Days", "mean"),
                    Total_Orders=("Order ID", "count"),
                    Total_Sales=("Sales", "sum"),
                    Total_Profit=("Gross Profit", "sum"),
                ).round(2)
                .sort_values(by="Average_Shipping_Days",ascending=False)
            )

        except Exception as e:
            raise CustomException(e, sys)

    # City Summary

    def city_summary(self, df=None):
        try:
            city = (
                self.df.groupby("City")
                .agg(
                    Average_Shipping_Days=("Shipping Days", "mean"),
                    Total_Orders=("Order ID", "count"),
                    Total_Sales=("Sales", "sum"),
                    Total_Profit=("Gross Profit", "sum"),
                ).round(2)
            )

            city["Route Score"] = (
                city["Total_Profit"] / city["Average_Shipping_Days"]
            ).round(2)

            return city.sort_values(by="Average_Shipping_Days", ascending=False)

        except Exception as e:
            raise CustomException(e, sys)

    # Best Routes

    def best_routes(self, df=None, min_orders=10):
        try:
            city = self.city_summary(df)

            city = city[
                city["Total_Orders"] >= min_orders
            ]

            return city.sort_values(by="Route Score",ascending=False,).head(10)

        except Exception as e:
            raise CustomException(e, sys)

    # Worst Routes

    def worst_routes(self, df=None, min_orders=10):
        try:
            city = self.city_summary(df)

            city = city[
                city["Total_Orders"] >= min_orders
            ]

            return city.sort_values(by="Route Score",ascending=True).head(10)

        except Exception as e:
            raise CustomException(e, sys)