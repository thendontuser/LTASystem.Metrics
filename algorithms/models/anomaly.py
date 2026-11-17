from pyspark.sql.functions import col, count, avg, sum as _sum, when, round
from algorithms.utils.visualizer import plot_api_anomalies

class ApiAnomalyAnalyzer:
    def __init__(self, api_df):
        self.df = api_df

    def run(self):
        percentiles = self.df.approxQuantile("response_time_ms", [0.5, 0.95, 0.99], 0.01)
        p50, p95, p99 = percentiles
        print(f"[Аномалии] Медиана: {p50} мс, p95: {p95} мс, p99: {p99} мс")

        error_stats = self.df.groupBy("endpoint").agg(
            count("request_id").alias("total_calls"),
            _sum(when(col("response_status_code") == 500, 1).otherwise(0)).alias("errors_500"),
            round(avg("response_time_ms"), 2).alias("avg_response_time")
        ).withColumn("error_rate", round(col("errors_500") / col("total_calls") * 100, 2)).orderBy(col("error_rate").desc())
        
        print("[Аномалии] Доля ошибок 500 по эндпоинтам:")
        error_stats.show(truncate=False)

        pdf = self.df.select("response_time_ms", "response_status_code").toPandas()
        plot_api_anomalies(pdf, p99)
        return error_stats