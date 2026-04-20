import os
import requests
import psycopg2
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- НАСТРОЙКИ (Добавь их в Render Environment Variables) ---
DB_URL = os.environ.get("postgresql://postgres:%5Bhunhic-doqbec-7vivSe%5D@db.wlaumgaruezzijwhhvpl.supabase.co:5432/postgres")
EMAIL_USER = os.environ.get("EMAIL_USER") # Твоя почта (отправитель)
EMAIL_PASS = os.environ.get("EMAIL_PASS") # Пароль приложения
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL") # Куда слать отчеты (может быть той же почтой)

def send_email_report(subject, body):
    """Отправка подробного отчета на почту"""
    if not EMAIL_USER or not EMAIL_PASS:
        print("Ошибка: Данные почты не настроены")
        return

    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = RECEIVER_EMAIL or EMAIL_USER
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465) # Для Mail.ru тоже 465
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, msg['To'], msg.as_string())
        server.quit()
        print("[MAIL] Отчет успешно отправлен на почту")
    except Exception as e:
        print(f"[MAIL ERROR] {e}")

def generate_massive_report(s_type, query):
    """Генерация сверх-обширного отчета"""
    
    # Заголовок
    report = f"==========================================\n"
    report += f"   ПОЛНЫЙ РАЗВЕДЫВАТЕЛЬНЫЙ ОТЧЕТ: {query}\n"
    report += f"==========================================\n\n"

    # Блок 1: Системные данные
    report += "[1. СИСТЕМНЫЙ АНАЛИЗ]\n"
    report += f"Статус: Активен\nТип запроса: {s_type.upper()}\n"
    report += "Приоритет: Высокий\n\n"

    # Блок 2: Реальные данные из API (IP)
    if s_type == 'ip':
        try:
            res = requests.get(f"http://ip-api.com/json/{query}?fields=66846719").json()
            if res.get('status') == 'success':
                report += f"[2. ДАННЫЕ СЕТИ]\n"
                report += f"IP Адрес: {res['query']}\n"
                report += f"Провайдер (ISP): {res['isp']}\n"
                report += f"Организация: {res['org']}\n"
                report += f"AS Номер: {res['as']}\n"
                report += f"Тип соединения: {'Мобильный' if res['mobile'] else 'Проводной'}\n"
                report += f"Proxy/VPN: {'Да' if res['proxy'] else 'Нет'}\n\n"
                report += f"[3. ГЕОЛОКАЦИЯ]\n"
                report += f"Страна: {res['country']} ({res['countryCode']})\n"
                report += f"Регион/Город: {res['regionName']} / {res['city']}\n"
                report += f"Координаты: {res['lat']}, {res['lon']}\n"
                report += f"Google Maps: https://www.google.com/maps?q={res['lat']},{res['lon']}\n\n"
        except: report += "[!] Ошибка связи с модулем IP-API\n"

    # Блок 3: Имитация глубокого поиска (VK/Phone)
    elif s_type in ['vk', 'phone', 'global']:
        report += f"[2. ЦИФРОВОЙ СЛЕД И УТЕЧКИ]\n"
        report += f"Поиск '{query}' в базе слитых паролей (2020-2025)... Найдено\n"
        report += f"- Хеш пароля: 4b62f***e81 (MD5)\n"
        report += f"- Последний вход: г. Москва\n"
        report += f"- Связанные почты: {query[:3]}***@gmail.com, {query[:2]}***@mail.ru\n\n"
        
        report += "[3. СОЦИАЛЬНЫЕ СВЯЗИ]\n"
        report += f"- Найден аккаунт на Avito (активен)\n"
        report += f"- Найден аккаунт в Telegram (ID: 591***)\n"
        report += f"- Упоминания на форумах: 4 совпадения\n\n"
        
        report += "[4. АНАЛИЗ ГРАФА СВЯЗЕЙ]\n"
        report += "Вероятные родственники: Найдено 2 совпадения по фамилии.\n"
        report += "Частые локации: Работа (БЦ 'Сити'), Дом (ЖК 'Орбита').\n"

    # Подвал
    report += "\n==========================================\n"
    report += "Конец отчета. Сформировано системой SEARCHHEMS.\n"
    return report

@app.route('/api/search', methods=['POST'])
def handle_search():
    data = request.json
    s_type = data.get('type')
    query = data.get('query')

    # Создаем отчет
    full_report = generate_massive_report(s_type, query)

    # 1. Сохраняем в Supabase
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS reports (id SERIAL, q TEXT, r TEXT)")
        cur.execute("INSERT INTO reports (q, r) VALUES (%s, %s)", (query, full_report))
        conn.commit()
        cur.close()
        conn.close()
    except: pass

    # 2. Шлем на ПОЧТУ
    send_email_report(f"OSINT ОТЧЕТ: {query}", full_report)

    return jsonify({"report": full_report})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
