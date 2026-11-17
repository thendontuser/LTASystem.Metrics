import matplotlib.pyplot as plt

def plot_clusters(pdf):
    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(
        pdf['avg_time_on_page'], pdf['acceptance_rate'], 
        c=pdf['prediction'], s=pdf['total_api_requests']*2 + 20, 
        cmap='viridis', alpha=0.7
    )
    plt.colorbar(scatter, label='Кластер')
    plt.title('Кластеризация студентов (размер = API запросы)')
    plt.xlabel('Среднее время на странице (сек)')
    plt.ylabel('Доля принятых отчетов')
    plt.show()

def plot_api_anomalies(pdf, p99):
    plt.figure(figsize=(10, 6))
    colors = {200: 'green', 400: 'orange', 404: 'yellow', 500: 'red'}
    for status, color in colors.items():
        subset = pdf[pdf['response_status_code'] == status]
        if not subset.empty:
            plt.scatter(subset['response_time_ms'], subset['response_status_code'], 
                        c=color, label=f'HTTP {status}', alpha=0.5, s=10)
    plt.axvline(x=p99, color='red', linestyle='--', label=f'Аномалия (p99={p99:.0f} мс)')
    plt.title('Логи API: Время ответа vs Статус')
    plt.xlabel('Время ответа (мс)')
    plt.ylabel('HTTP Статус')
    plt.legend()
    plt.show()