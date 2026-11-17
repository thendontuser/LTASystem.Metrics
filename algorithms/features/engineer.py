from pyspark.sql.functions import col, count, avg, sum as _sum, when, stddev
from pyspark.sql.types import IntegerType

class FeatureEngineer:
    def __init__(self, dataframes):
        self.views = dataframes["views"]
        self.reports = dataframes["reports"]
        self.api = dataframes["api"]

    def build_student_features(self):
        ui_features = self.views.groupBy("user_id").agg(
            count("event_id").alias("total_page_views"),
            avg("time_on_page_sec").alias("avg_time_on_page"),
            avg("scroll_depth_percent").alias("avg_scroll_depth"),
            stddev("time_on_page_sec").alias("std_time_on_page")
        )
        api_df_clean = self.api.withColumn(
            "response_status_code", col("response_status_code").cast(IntegerType())
        )
        api_features = api_df_clean.groupBy("user_id").agg(
            count("request_id").alias("total_api_requests"),
            avg("response_time_ms").alias("avg_api_response_time"),
            _sum(when(col("response_status_code") == 500, 1).otherwise(0)).alias("api_errors_500")
        )
        report_features = self.reports.groupBy("user_id").agg(
            count("report_id").alias("total_reports"),
            _sum(when(col("status") == "Accepted", 1).otherwise(0)).alias("accepted_reports"),
            _sum(when(col("status") == "Rework", 1).otherwise(0)).alias("rework_reports"),
            avg("time_to_create_sec").alias("avg_report_creation_time")
        )
        df = ui_features.join(api_features, on="user_id", how="outer") \
                        .join(report_features, on="user_id", how="outer").fillna(0)
        df = df.withColumn("acceptance_rate", when(col("total_reports") > 0, col("accepted_reports") / col("total_reports")).otherwise(0.0))
        df = df.withColumn("api_error_rate", when(col("total_api_requests") > 0, col("api_errors_500") / col("total_api_requests")).otherwise(0.0))
        return df