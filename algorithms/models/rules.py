# src/models/rules.py
from pyspark.ml.fpm import FPGrowth
from pyspark.sql.functions import split, col, array_distinct

class NavigationAnalyzer:
    def __init__(self, nav_df, min_support=0.05, min_confidence=0.6):
        self.df = nav_df
        self.min_support = min_support
        self.min_confidence = min_confidence

    def run(self):
        # 1. Разбиваем строку на массив
        # 2. array_distinct удаляет повторяющиеся страницы в рамках одной сессии
        transactions = self.df.select(
            array_distinct(split(col("sequence_of_pages"), "->")).alias("items")
        )
        
        # 3. Создаем модель
        fp = FPGrowth(itemsCol="items", minSupport=self.min_support, minConfidence=self.min_confidence)
        model = fp.fit(transactions)

        print("[Навигация] Топ-10 частых страниц:")
        model.freqItemsets.orderBy(col("freq").desc()).show(10, truncate=False)

        print("[Навигация] Ассоциативные правила:")
        rules = model.associationRules.orderBy(col("confidence").desc())
        rules.select("antecedent", "consequent", "confidence", "lift").show(10, truncate=False)
        return rules