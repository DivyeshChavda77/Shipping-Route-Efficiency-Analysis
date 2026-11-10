from src.components.data_ingestion import DataIngestion
from src.components.data_transformation import DataTransformation
from src.components.route_analysis import RouteAnalysis


if __name__ == "__main__":

    # Step 1
    ingestion = DataIngestion()
    raw_path = ingestion.initiate_data_ingestion()

    # Step 2
    transformation = DataTransformation()
    processed_path = transformation.initiate_data_transformation(raw_path)

    # Step 3
    analysis = RouteAnalysis(processed_path)

    print("\n========== KPIs ==========")
    print(analysis.get_kpis())

    print("\n========== Ship Mode ==========")
    print(analysis.ship_mode_summary())

    print("\n========== Region ==========")
    print(analysis.region_summary())

    print("\n========== Best Routes ==========")
    print(analysis.best_routes())

    print("\n========== Worst Routes ==========")
    print(analysis.worst_routes())