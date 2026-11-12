import csv
import random
import uuid
from datetime import datetime, timedelta
import os

# --- НАСТРОЙКИ ОБЪЕМА (МЕНЯЙТЕ ЗДЕСЬ) ---
NUM_USERS = 300              # Количество студентов
NUM_SESSIONS = 5000          # Количество сессий
ROWS_PAGE_VIEWS = 20000      # ~20k строк
ROWS_CLICKS = 15000          # ~15k строк
ROWS_API = 10000             # ~10k строк
ROWS_REPORTS = 5000          # ~5k строк

START_DATE = datetime(2026, 1, 1, 8, 0, 0)
END_DATE = datetime(2026, 3, 1, 23, 59, 59)

PAGES = [
    ("/home", "Главная"), ("/catalog", "Каталог"), ("/item/1", "Карточка товара 1"),
    ("/item/2", "Карточка товара 2"), ("/cart", "Корзина"), ("/checkout", "Оформление заказа"),
    ("/profile", "Личный кабинет"), ("/search", "Поиск")
]
ENDPOINTS = [
    ("GET", "/api/products"), ("GET", "/api/products/1"), ("POST", "/api/cart/add"),
    ("POST", "/api/orders"), ("GET", "/api/user/profile"), ("DELETE", "/api/cart/item/1")
]
BUG_IDS = [f"BUG-{i:03d}" for i in range(1, 51)] # 50 багов в системе

def generate_uuid():
    return str(uuid.uuid4())[:8]

def random_date(start, end):
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def main():
    out_dir = "big_dataset"
    ensure_dir(out_dir)

    # Базовые списки для связности
    students = [f"student_{i:04d}" for i in range(1, NUM_USERS + 1)]
    teachers = ["teacher_01", "teacher_02", "teacher_03"]
    
    # Создаем пул сессий, чтобы использовать их в разных файлах
    sessions = []
    for _ in range(NUM_SESSIONS):
        sessions.append({
            "session_id": generate_uuid(),
            "user_id": random.choice(students),
            "start": random_date(START_DATE, END_DATE)
        })

    # 1. page_views.csv
    print("Генерация page_views.csv...")
    with open(f"{out_dir}/page_views.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["event_id", "timestamp", "user_id", "session_id", "page_url", "page_title", "time_on_page_sec", "scroll_depth_percent"])
        for _ in range(ROWS_PAGE_VIEWS):
            sess = random.choice(sessions)
            page = random.choice(PAGES)
            # Время проведенное на странице: от 5 сек до 5 минут. Иногда "зависают" на 10+ минут (выбросы)
            time_spent = random.randint(5, 300) if random.random() > 0.05 else random.randint(600, 1200)
            scroll = random.randint(10, 100) if page[0] != "/home" else 100
            writer.writerow([generate_uuid(), sess["start"].strftime("%Y-%m-%d %H:%M:%S"), sess["user_id"], sess["session_id"], page[0], page[1], time_spent, scroll])

    # 2. ui_clicks.csv
    print("Генерация ui_clicks.csv...")
    with open(f"{out_dir}/ui_clicks.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["click_id", "timestamp", "user_id", "element_id", "element_text", "coordinates_x", "coordinates_y", "is_error_click"])
        elements = [("btn_buy", "Купить"), ("btn_add_cart", "В корзину"), ("filter_sort", "Сортировка"), ("btn_submit", "Оформить"), ("btn_apply_promo", "Применить промокод")]
        for _ in range(ROWS_CLICKS):
            sess = random.choice(sessions)
            el = random.choice(elements)
            is_error = random.random() < 0.05 # 5% кликов по сломанным элементам
            writer.writerow([generate_uuid(), sess["start"].strftime("%Y-%m-%d %H:%M:%S"), sess["user_id"], el[0], el[1], random.randint(0, 1920), random.randint(0, 1080), is_error])

    # 3. form_inputs.csv
    print("Генерация form_inputs.csv...")
    with open(f"{out_dir}/form_inputs.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["input_id", "timestamp", "user_id", "field_name", "input_value", "was_validation_error", "attempt_number"])
        for _ in range(8000):
            sess = random.choice(sessions)
            field = random.choice(["Количество", "Промокод", "Email", "Телефон"])
            val = random.choice(["-5", "abc", "999999999", "0", "test@mail.ru", "123", "10000000000000000000"])
            err = val in ["-5", "abc", "10000000000000000000"] 
            writer.writerow([generate_uuid(), sess["start"].strftime("%Y-%m-%d %H:%M:%S"), sess["user_id"], field, val, err, random.randint(1, 5)])

    # 4. navigation_paths.csv
    print("Генерация navigation_paths.csv...")
    with open(f"{out_dir}/navigation_paths.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["path_id", "user_id", "start_time", "end_time", "sequence_of_pages", "is_successful"])
        for _ in range(4000):
            sess = random.choice(sessions)
            path = "->".join(random.choices([p[0] for p in PAGES], k=random.randint(3, 8)))
            end_t = sess["start"] + timedelta(minutes=random.randint(5, 60))
            writer.writerow([generate_uuid(), sess["user_id"], sess["start"].strftime("%Y-%m-%d %H:%M:%S"), end_t.strftime("%Y-%m-%d %H:%M:%S"), path, random.random() < 0.4])

    # 5. api_requests.csv
    print("Генерация api_requests.csv...")
    with open(f"{out_dir}/api_requests.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["request_id", "timestamp", "user_id", "method", "endpoint", "request_payload", "response_status_code", "response_time_ms", "is_intentional_error"])
        for _ in range(ROWS_API):
            req = random.choice(ENDPOINTS)
            # Распределение кодов: 80% успешных, 15% клиентские ошибки, 5% серверные
            rand_val = random.random()
            if rand_val < 0.80: status = 200
            elif rand_val < 0.95: status = random.choice([400, 404])
            else: status = 500
            
            payload = '{"id": 1, "qty": ' + str(random.randint(-10, 999999)) + '}' if req[0] == "POST" else ""
            # Время ответа: обычно быстрое, но иногда аномально долгое (для поиска аномалий)
            resp_time = random.randint(50, 500) if random.random() > 0.02 else random.randint(3000, 10000)
            
            writer.writerow([generate_uuid(), random_date(START_DATE, END_DATE).strftime("%Y-%m-%d %H:%M:%S"), random.choice(students), req[0], req[1], payload, status, resp_time, status != 200])

    # 6. boundary_testing.csv
    print("Генерация boundary_testing.csv...")
    with open(f"{out_dir}/boundary_testing.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["test_id", "user_id", "field_name", "value_tested", "expected_code", "actual_code", "is_bug_found"])
        for _ in range(3000):
            val = random.choice(["-1", "0", "999999999", "abc", "", "1.5", "-999"])
            # В 20% случаев находим баг (ожидали 400, получили 200 или 500)
            actual = random.choice([400, 200, 500]) if random.random() > 0.2 else 400
            writer.writerow([generate_uuid(), random.choice(students), "qty", val, 400, actual, actual != 400])

    # 7. swagger_usage.csv
    print("Генерация swagger_usage.csv...")
    with open(f"{out_dir}/swagger_usage.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["action_id", "user_id", "endpoint_viewed", "time_spent_reading_sec"])
        for _ in range(5000):
            req = random.choice(ENDPOINTS)
            writer.writerow([generate_uuid(), random.choice(students), req[1], random.randint(5, 200)])

    # 8. bug_reports.csv
    print("Генерация bug_reports.csv...")
    bug_reports = []
    with open(f"{out_dir}/bug_reports.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["report_id", "timestamp", "user_id", "target_bug_id", "report_type", "status", "time_to_create_sec", "rework_count"])
        for _ in range(ROWS_REPORTS):
            rep_id = generate_uuid()
            status = random.choices(["Draft", "OnReview", "Rework", "Accepted"], weights=[0.1, 0.3, 0.2, 0.4])[0]
            bug_reports.append(rep_id)
            writer.writerow([rep_id, random_date(START_DATE, END_DATE).strftime("%Y-%m-%d %H:%M:%S"), random.choice(students), random.choice(BUG_IDS), random.choice(["UI", "API"]), status, random.randint(60, 3600), random.randint(0, 4)])

    # 9. ai_feedback.csv
    print("Генерация ai_feedback.csv...")
    with open(f"{out_dir}/ai_feedback.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["feedback_id", "report_id", "ai_score", "ai_recommendations_count", "did_student_edit_after_ai", "time_spent_editing_sec"])
        for rep_id in bug_reports:
            if random.random() < 0.8: # ИИ проверял 80% отчетов
                writer.writerow([generate_uuid(), rep_id, random.randint(10, 100), random.randint(0, 8), random.random() < 0.5, random.randint(30, 900)])

    # 10. teacher_reviews.csv
    print("Генерация teacher_reviews.csv...")
    with open(f"{out_dir}/teacher_reviews.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["review_id", "report_id", "teacher_id", "decision", "comment_length", "time_to_review_sec"])
        for rep_id in bug_reports:
            if random.random() < 0.9: # Препод проверил 90% отчетов
                writer.writerow([generate_uuid(), rep_id, random.choice(teachers), random.choices(["Accept", "Return"], weights=[0.7, 0.3])[0], random.randint(10, 500), random.randint(60, 7200)])

    print("Успех! Большой датасет сгенерирован в папке 'big_dataset'.")

if __name__ == "__main__":
    main()