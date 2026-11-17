from pyspark.sql import SparkSession

class DataLoader:
    def __init__(self, base_path):
        self.base_path = base_path
        self.spark = SparkSession.builder \
            .master("local[*]") \
            .appName("QA_Trainer_Analysis") \
            .getOrCreate()

    def load_csv(self, filename):
        df = self.spark.read.csv(
            f"{self.base_path}/{filename}", 
            header=True, 
            inferSchema=True,
            escape='"'  # <--- добавьте это
        )
        return df.dropna(how="all")

    def load_all(self):
        return {
            "views": self.load_csv("page_views.csv"),
            "reports": self.load_csv("bug_reports.csv"),
            "api": self.load_csv("api_requests.csv"),
            "nav": self.load_csv("navigation_paths.csv")
        }