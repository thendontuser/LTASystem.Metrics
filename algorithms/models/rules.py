from pyspark.ml.fpm import FPGrowth
from pyspark.sql.functions import split, col, array_distinct

class NavigationAnalyzer:
    """
    Ищет ассоциативные правила (паттерны) в путях перемещения студентов по сайту.
    Использует алгоритм FP-Growth (более эффективный аналог Apriori для Big Data).
    """
    def __init__(self, nav_df, min_support=0.05, min_confidence=0.6):
        self.df = nav_df
        self.min_support = min_support
        self.min_confidence = min_confidence

    def run(self):
        # 1. Разбиваем строку на массив и удаляем дубликаты (FP-Growth требует уникальности элементов в транзакции)
        transactions = self.df.select(
            array_distinct(split(col("sequence_of_pages"), "->")).alias("items")
        )
        
        # 2. Обучаем модель поиска частых наборов и ассоциативных правил
        fp = FPGrowth(itemsCol="items", minSupport=self.min_support, minConfidence=self.min_confidence)
        model = fp.fit(transactions)

        # 3. Выводим самые частые страницы
        print("[Навигация] Топ-10 частых страниц:")
        model.freqItemsets.orderBy(col("freq").desc()).show(10, truncate=False)

        # 4. Выводим правила (Антецедент -> Консеквент) и метрики уверенности (Confidence, Lift)
        print("[Навигация] Ассоциативные правила:")
        rules = model.associationRules.orderBy(col("confidence").desc())
        rules.select("antecedent", "consequent", "confidence", "lift").show(10, truncate=False)
        return rules