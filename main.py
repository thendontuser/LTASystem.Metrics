import config
from data.loader import DataLoader
from algorithms.features.engineer import FeatureEngineer
from algorithms.models.clustering import StudentBehaviorAnalyzer
from algorithms.models.anomaly import ApiAnomalyAnalyzer
from algorithms.models.rules import NavigationAnalyzer

def main():
    print("=== Запуск аналитического пайплайна QA Trainer ===")
    
    # 1. Загрузка
    loader = DataLoader(config.DATA_PATH)
    data = loader.load_all()

    # 2. Фичи
    fe = FeatureEngineer(data)
    features_df = fe.build_student_features()
    print(f"Признаки сконструированы для {features_df.count()} студентов.")

    # 3. Кластеризация
    print("\n--- Кластеризация студентов ---")
    cluster_model = StudentBehaviorAnalyzer(features_df, k=config.KMEANS_CLUSTERS)
    cluster_model.run()

    # 4. Аномалии API
    print("\n--- Анализ API-аномалий ---")
    api_model = ApiAnomalyAnalyzer(data["api"])
    api_model.run()

    # 5. Правила навигации
    print("\n--- Анализ навигационных паттернов ---")
    nav_model = NavigationAnalyzer(
        data["nav"], 
        min_support=config.FP_GROWTH_MIN_SUPPORT, 
        min_confidence=config.FP_GROWTH_MIN_CONFIDENCE
    )
    nav_model.run()

if __name__ == "__main__":
    main()