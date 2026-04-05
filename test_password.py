"""
Запуск:
    1. Установить и активировать виртуальное окружение:
    python -m venv venv
    source venv/Scripts/activate

    2. Установить библиотеки `pip install -r requirements.txt`

    3. Запустить сервер из файл password_checker.py из IDE или командой `python password_checker.py`
        Убедиться что сервер запустился, по умолчанию стоит http://localhost:8080

    4. Запустить тесты командой `pytest test_password.py -v` или
        `pytest --html=report.html --self-contained-html` для генерации отчета в html

"""

import pytest
import time
from playwright.sync_api import sync_playwright

# Значения сервера по умолчанию
SERVER_PORT = 8080
BASE_URL = f"http://localhost:{SERVER_PORT}"

# Константа параметров тесткейса для ввода в тесте
TC01_SETTINGS = {
    "minLen": "8",
    "minDigits": "1",
    "minLetters": "0",
    "minUpper": "1",
    "minSpec": "1",
    "maxRepeat": "0",
    "blockAlpha": False,
    "blockYear": True,
    "blockKbd": False,
}

@pytest.fixture(scope="session")
def page():
    """Создание браузера"""
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False) # True, если не требуется запускать реальный браузер
        page = browser.new_page()
        yield page
        browser.close()

@pytest.fixture(scope="session")
def apply_settings(page):
    """Заполняет числовые поля и переключатели согласно словарю настроек."""
    print("Настройка проверяемых параметров")
    settings = TC01_SETTINGS
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")
    numeric_fields = ["minLen", "minDigits", "minLetters", "minUpper", "minSpec", "maxRepeat"]
    for field in numeric_fields:
        page.locator(f"#{field}").fill(settings[field])

    toggle_map = {
        "blockAlpha": settings["blockAlpha"],
        "blockYear": settings["blockYear"],
        "blockKbd": settings["blockKbd"],
    }
    for toggle_id, should_be_on in toggle_map.items():
        toggle = page.locator(f"#{toggle_id}")
        is_on = "on" in (toggle.get_attribute("class") or "")
        if is_on != should_be_on:
            toggle.locator("..").click()


def check_password(page, password: str) -> bool:
    """Вводит пароль, нажимает «Проверить», возвращает True или False"""
    print(f"Шаг теста: Ввод пароля: {password} ")
    page.locator("#pwd").clear()
    page.locator("#pwd").fill(password)
    page.locator("button.check-btn").click()
    time.sleep(0.5)
    page.wait_for_selector("#resultCard.visible")
    verdict_text = page.locator("#verdict").inner_text()
    return "Пароль подходит" in verdict_text


@pytest.mark.parametrize(
    "password, password_available, assert_text",
    [
        ("2B@vutxy", True, "Пароль '2B@vutxy' должен быть принят"),
        ("xxxxxxx", False, "Пароль 'xxxxxxx' должен быть отклонён"),
        ("abcdefgh", False, "Пароль 'abcdefgh' должен быть отклонён"),
        ("abcdef12", False, "Пароль 'abcdef12' должен быть отклонён"),
        ("abcdef12", True, "Пароль 'abcdef12' должен быть отклонён"), # Сломанный тест для демонстрации в отчете
    ],
    ids=["psw: 2B@vutxy", "psw: xxxxxxx", "psw: abcdefgh", "psw: 2abcdef12", "broken_test"]
)

def test_pass_valid_password(page, apply_settings, password, password_available, assert_text):
    """Тест по тесткейсу 01, проверка тестовых параметров для нескольких вариантов паролей"""

    result = check_password(page, password)
    print(f"Шаг теста: Проверка параметров для пароля: {password}")
    assert result is password_available, assert_text

