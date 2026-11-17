from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator
from pyspark.sql.functions import col, avg, count
from algorithms.utils.visualizer import plot_clusters

class StudentBehaviorAnalyzer:
    def __init__(self, features_df, k=4):
        self.df = features_df
        self.k = k

    def run(self):
        feature_cols = ["avg_time_on_page", "avg_scroll_depth", "total_api_requests", "acceptance_rate", "api_error_rate"]
        assembler = VectorAssembler(inputCols=feature_cols, outputCol="raw_features")
        df_vec = assembler.transform(self.df).na.drop(subset=feature_cols)
        
        scaler = StandardScaler(inputCol="raw_features", outputCol="features")
        df_scaled = scaler.fit(df_vec).transform(df_vec)

        kmeans = KMeans(featuresCol="features", k=self.k, seed=42)
        predictions = kmeans.fit(df_scaled).transform(df_scaled)

        evaluator = ClusteringEvaluator(featuresCol="features")
        silhouette = evaluator.evaluate(predictions)
        print(f"[K-Means] Silhouette Score: {silhouette:.3f}")

        predictions.groupBy("prediction").agg(
            avg("acceptance_rate").alias("avg_acceptance_rate"),
            avg("avg_time_on_page").alias("avg_time_on_page"),
            avg("total_api_requests").alias("avg_api_requests"),
            count("user_id").alias("students_in_cluster")
        ).orderBy("prediction").show()

        pdf = predictions.select("avg_time_on_page", "acceptance_rate", "total_api_requests", "prediction").toPandas()
        plot_clusters(pdf)
        return predictions