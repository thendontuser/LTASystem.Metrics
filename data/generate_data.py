import csv
import random
import uuid
from datetime import datetime, timedelta
import os

# Настройки генерации
NUM_STUDENTS = 50
NUM_SESSIONS = 200
START_DATE = datetime(2026, 2, 1, 9, 0, 0)

# Справочники для реалистичности
PAGES = [
    ("/home", "Главная"), ("/catalog", "Каталог"), ("/item/1", "Карточка товара 1"),
    ("/item/2", "Карточка товара 2"), ("/cart", "Корзина"), ("/checkout", "Оформление заказа"),
    ("/profile", "Личный кабинет")
]
ENDPOINTS = [
    ("GET", "/api/products"), ("GET", "/api/products/1"), ("POST", "/api/cart/add"),
    ("POST", "/api/orders"), ("GET", "/api/user/profile")
]
BUG_IDS = [f"BUG-{i:03d}" for i in range(1, 16)] # 15 багов в системе

def generate_uuid():
    return str(uuid.uuid4())[:8]

def random_date(start, end):
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def main():
    out_dir = "dataset"
    ensure_dir(out_dir)

    # --- Готовим базовые данные (списки студентов и сессий) ---
    students = [f"student_{i:02d}" for i in range(1, NUM_STUDENTS + 1)]
    teachers = ["teacher_01", "teacher_02"]
    
    sessions = []
    for _ in range(NUM_SESSIONS):
        sessions.append({
            "session_id": generate_uuid(),
            "user_id": random.choice(students),
            "start": random_date(START_DATE, START_DATE + timedelta(days=30))
        })

    # --- 1. page_views.csv ---
    with open(f"{out_dir}/page_views.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["event_id", "timestamp", "user_id", "session_id", "page_url", "page_title", "time_on_page_sec", "scroll_depth_percent"])
        for sess in sessions:
            current_time = sess["start"]
            for _ in range(random.randint(3, 10)): # 3-10 просмотров за сессию
                page = random.choice(PAGES)
                time_spent = random.randint(5, 300)
                scroll = random.randint(10, 100) if page[0] != "/home" else 100
                writer.writerow([generate_uuid(), current_time.strftime("%Y-%m-%d %H:%M:%S"), sess["user_id"], sess["session_id"], page[0], page[1], time_spent, scroll])
                current_time += timedelta(seconds=time_spent + random.randint(2, 30))

    # --- 2. ui_clicks.csv ---
    with open(f"{out_dir}/ui_clicks.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["click_id", "timestamp", "user_id", "element_id", "element_text", "coordinates_x", "coordinates_y", "is_error_click"])
        elements = [("btn_buy", "Купить"), ("btn_add_cart", "В корзину"), ("filter_sort", "Сортировка"), ("btn_submit", "Оформить")]
        for sess in sessions:
            current_time = sess["start"]
            for _ in range(random.randint(5, 20)):
                el = random.choice(elements)
                is_error = random.random() < 0.1 # 10% кликов по сломанным элементам
                writer.writerow([generate_uuid(), current_time.strftime("%Y-%m-%d %H:%M:%S"), sess["user_id"], el[0], el[1], random.randint(0, 1920), random.randint(0, 1080), is_error])
                current_time += timedelta(seconds=random.randint(1, 60))

    # --- 3. form_inputs.csv ---
    with open(f"{out_dir}/form_inputs.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["input_id", "timestamp", "user_id", "field_name", "input_value", "was_validation_error", "attempt_number"])
        for sess in sessions:
            for _ in range(random.randint(1, 5)):
                field = random.choice(["Количество", "Промокод", "Email", "Телефон"])
                val = random.choice(["-5", "abc", "999999999", "0", "test@mail.ru", "123"])
                err = val in ["-5", "abc"] # Имитация ошибки валидации
                writer.writerow([generate_uuid(), sess["start"].strftime("%Y-%m-%d %H:%M:%S"), sess["user_id"], field, val, err, random.randint(1, 3)])

    # --- 4. navigation_paths.csv ---
    with open(f"{out_dir}/navigation_paths.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["path_id", "user_id", "start_time", "end_time", "sequence_of_pages", "is_successful"])
        for sess in sessions:
            path = "->".join(random.choices([p[0] for p in PAGES], k=random.randint(3, 6)))
            end_t = sess["start"] + timedelta(minutes=random.randint(5, 40))
            writer.writerow([generate_uuid(), sess["user_id"], sess["start"].strftime("%Y-%m-%d %H:%M:%S"), end_t.strftime("%Y-%m-%d %H:%M:%S"), path, random.random() < 0.6])

    # --- 5. api_requests.csv ---
    with open(f"{out_dir}/api_requests.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["request_id", "timestamp", "user_id", "method", "endpoint", "request_payload", "response_status_code", "response_time_ms", "is_intentional_error"])
        for _ in range(500): # 500 запросов
            req = random.choice(ENDPOINTS)
            status = random.choice([200, 200, 200, 400, 404, 500]) # Больше успешных
            payload = '{"id": 1, "qty": ' + str(random.randint(-10, 999)) + '}' if req[0] == "POST" else ""
            writer.writerow([generate_uuid(), random_date(START_DATE, START_DATE + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S"), random.choice(students), req[0], req[1], payload, status, random.randint(50, 2000), status != 200])

    # --- 6. boundary_testing.csv ---
    with open(f"{out_dir}/boundary_testing.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["test_id", "user_id", "field_name", "value_tested", "expected_code", "actual_code", "is_bug_found"])
        for _ in range(200):
            val = random.choice(["-1", "0", "999999999", "abc", ""])
            writer.writerow([generate_uuid(), random.choice(students), "qty", val, 400, random.choice([400, 200, 500]), random.random() < 0.3])

    # --- 7. swagger_usage.csv ---
    with open(f"{out_dir}/swagger_usage.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["action_id", "user_id", "endpoint_viewed", "time_spent_reading_sec"])
        for _ in range(150):
            req = random.choice(ENDPOINTS)
            writer.writerow([generate_uuid(), random.choice(students), req[1], random.randint(5, 120)])

    # --- 8. bug_reports.csv ---
    bug_reports = []
    with open(f"{out_dir}/bug_reports.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["report_id", "timestamp", "user_id", "target_bug_id", "report_type", "status", "time_to_create_sec", "rework_count"])
        for _ in range(100):
            rep_id = generate_uuid()
            status = random.choice(["Draft", "OnReview", "Rework", "Accepted"])
            bug_reports.append(rep_id)
            writer.writerow([rep_id, random_date(START_DATE, START_DATE + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S"), random.choice(students), random.choice(BUG_IDS), random.choice(["UI", "API"]), status, random.randint(60, 1800), random.randint(0, 3)])

    # --- 9. ai_feedback.csv ---
    with open(f"{out_dir}/ai_feedback.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["feedback_id", "report_id", "ai_score", "ai_recommendations_count", "did_student_edit_after_ai", "time_spent_editing_sec"])
        for rep_id in bug_reports:
            if random.random() < 0.7: # ИИ проверял не все отчеты
                writer.writerow([generate_uuid(), rep_id, random.randint(40, 100), random.randint(0, 5), random.random() < 0.6, random.randint(30, 600)])

    # --- 10. teacher_reviews.csv ---
    with open(f"{out_dir}/teacher_reviews.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["review_id", "report_id", "teacher_id", "decision", "comment_length", "time_to_review_sec"])
        for rep_id in bug_reports:
            if random.random() < 0.8: # Препод проверил 80% отчетов
                writer.writerow([generate_uuid(), rep_id, random.choice(teachers), random.choice(["Accept", "Return"]), random.randint(10, 300), random.randint(60, 3600)])

    print("Успех! 10 CSV файлов сгенерированы в папке 'dataset'.")

if __name__ == "__main__":
    main()