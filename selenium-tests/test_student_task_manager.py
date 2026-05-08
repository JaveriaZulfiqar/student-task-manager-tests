"""
Student Task Manager – Selenium Test Suite
==========================================
15 automated test cases using headless Chrome.

Requirements:
  pip install selenium pytest

Run locally:
  pytest test_student_task_manager.py -v

Environment variable:
  BASE_URL  – defaults to http://localhost:5000
"""

import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")
HEADLESS = os.environ.get("HEADLESS", "true").lower() != "false"

TEST_USER = {
    "name": "Selenium Test User",
    "email": f"selenium_{int(time.time())}@test.com",
    "password": "TestPassword123",
}


@pytest.fixture(scope="module")
def driver():
    """Headless Chrome WebDriver shared across all tests."""
    options = Options()
    if HEADLESS:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,800")
    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(5)
    yield drv
    drv.quit()


def wait_for(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )


def navigate(driver, path=""):
    driver.get(BASE_URL + path)


def login(driver):
    navigate(driver, "/login")
    wait_for(driver, By.ID, "email")
    driver.find_element(By.ID, "email").clear()
    driver.find_element(By.ID, "email").send_keys(TEST_USER["email"])
    driver.find_element(By.ID, "password").clear()
    driver.find_element(By.ID, "password").send_keys(TEST_USER["password"])
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    WebDriverWait(driver, 10).until(EC.url_contains("/dashboard"))


# ==================== TEST CASES ====================


def test_01_home_redirects_to_login(driver):
    """TC-01: Unauthenticated visit to / must redirect to /login."""
    navigate(driver)
    time.sleep(1)
    assert "/login" in driver.current_url, \
        f"Expected redirect to /login, got: {driver.current_url}"


def test_02_page_title_is_correct(driver):
    """TC-02: Browser tab title must read 'Student Task Manager'."""
    navigate(driver, "/login")
    assert "Student Task Manager" in driver.title, \
        f"Unexpected title: {driver.title}"


def test_03_login_page_has_register_link(driver):
    """TC-03: Login page must contain a link to /register."""
    navigate(driver, "/login")
    link = driver.find_element(By.CSS_SELECTOR, "a[href='/register']")
    assert link.is_displayed(), "Register link not visible on login page"


def test_04_register_page_password_mismatch_shows_error(driver):
    """TC-04: Submitting mismatched passwords on register shows an error message."""
    navigate(driver, "/register")
    wait_for(driver, By.ID, "name")
    driver.find_element(By.ID, "name").send_keys("Test User")
    driver.find_element(By.ID, "email").send_keys("mismatch@test.com")
    driver.find_element(By.ID, "password").send_keys("Password123")
    driver.find_element(By.ID, "confirm").send_keys("WrongPassword")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(1)
    assert "passwords do not match" in driver.page_source.lower(), \
        "Password mismatch error not displayed"


def test_05_register_new_user_redirects_to_dashboard(driver):
    """TC-05: Registering with valid unique credentials redirects to /dashboard."""
    navigate(driver, "/register")
    wait_for(driver, By.ID, "name")
    driver.find_element(By.ID, "name").send_keys(TEST_USER["name"])
    driver.find_element(By.ID, "email").send_keys(TEST_USER["email"])
    driver.find_element(By.ID, "password").send_keys(TEST_USER["password"])
    driver.find_element(By.ID, "confirm").send_keys(TEST_USER["password"])
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    WebDriverWait(driver, 10).until(EC.url_contains("/dashboard"))
    assert "/dashboard" in driver.current_url, \
        f"Expected /dashboard after registration, got: {driver.current_url}"


def test_06_dashboard_shows_three_stat_cards(driver):
    """TC-06: Dashboard must display Total Tasks, Completed, and Pending stat cards."""
    navigate(driver, "/dashboard")
    source = driver.page_source.lower()
    assert "total tasks" in source, "Total Tasks card missing"
    assert "completed" in source, "Completed card missing"
    assert "pending" in source, "Pending card missing"


def test_07_dashboard_welcome_contains_user_name(driver):
    """TC-07: Dashboard welcome heading must include the registered user's name."""
    navigate(driver, "/dashboard")
    wait_for(driver, By.TAG_NAME, "h1")
    h1 = driver.find_element(By.TAG_NAME, "h1").text
    assert TEST_USER["name"].split()[0] in h1, \
        f"User name not found in welcome heading: '{h1}'"


def test_08_logout_clears_session_and_redirects(driver):
    """TC-08: Clicking Logout must redirect to /login and block access to /dashboard."""
    navigate(driver, "/dashboard")
    wait_for(driver, By.TAG_NAME, "button")
    buttons = driver.find_elements(By.TAG_NAME, "button")
    for btn in buttons:
        if "logout" in btn.text.lower():
            btn.click()
            break
    WebDriverWait(driver, 10).until(EC.url_contains("/login"))
    # Confirm session is gone — visiting /dashboard should redirect back to /login
    navigate(driver, "/dashboard")
    time.sleep(1)
    assert "/login" in driver.current_url, \
        "Session not cleared — /dashboard still accessible after logout"


def test_09_invalid_login_shows_error(driver):
    """TC-09: Submitting wrong credentials must display a login error message."""
    navigate(driver, "/login")
    wait_for(driver, By.ID, "email")
    driver.find_element(By.ID, "email").send_keys("wrong@test.com")
    driver.find_element(By.ID, "password").send_keys("WrongPassword")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(2)
    assert "/login" in driver.current_url, \
        "Invalid login should stay on /login"
    assert "login failed" in driver.page_source.lower() or \
           "invalid" in driver.page_source.lower() or \
           "error" in driver.page_source.lower(), \
        "No error message shown for invalid credentials"


def test_10_add_task_form_has_correct_fields(driver):
    """TC-10: Add Task form must render title, description, dueDate, and file fields."""
    login(driver)
    navigate(driver, "/tasks/add")
    wait_for(driver, By.ID, "title")
    assert driver.find_element(By.ID, "title").is_displayed(),       "Title field missing"
    assert driver.find_element(By.ID, "description").is_displayed(), "Description field missing"
    assert driver.find_element(By.ID, "dueDate").is_displayed(),     "Due date field missing"
    assert driver.find_element(By.ID, "file") is not None,           "File input missing"


def test_11_create_task_redirects_to_tasks_list(driver):
    """TC-11: Submitting a valid new task must redirect to /tasks."""
    navigate(driver, "/tasks/add")
    wait_for(driver, By.ID, "title")
    driver.find_element(By.ID, "title").send_keys("Selenium Test Task")
    driver.find_element(By.ID, "description").send_keys("Created by Selenium")
    driver.find_element(By.ID, "dueDate").send_keys("2025-12-31")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    WebDriverWait(driver, 10).until(EC.url_contains("/tasks"))
    assert "/tasks" in driver.current_url, \
        "Task creation did not redirect to /tasks"


def test_12_created_task_appears_in_task_list(driver):
    """TC-12: The newly created task title must be visible in the /tasks card grid."""
    navigate(driver, "/tasks")
    time.sleep(1)
    assert "Selenium Test Task" in driver.page_source, \
        "Created task not found in task list"


def test_13_task_card_shows_pending_status_and_due_date(driver):
    """TC-13: Task cards must display a status badge and a due date."""
    navigate(driver, "/tasks")
    time.sleep(1)
    source = driver.page_source.lower()
    assert "pending" in source or "done" in source, \
        "No status badge found on task cards"
    assert "due:" in source, \
        "Due date label not found on task cards"


def test_14_edit_task_form_is_prefilled(driver):
    """TC-14: Opening Edit Task must pre-fill the title field with existing task data."""
    navigate(driver, "/tasks")
    time.sleep(1)
    buttons = driver.find_elements(By.TAG_NAME, "button")
    for btn in buttons:
        if "edit" in btn.text.lower():
            btn.click()
            break
    WebDriverWait(driver, 10).until(EC.url_contains("/tasks/edit/"))
    wait_for(driver, By.ID, "title")
    title_value = driver.find_element(By.ID, "title").get_attribute("value")
    assert title_value != "", \
        "Title field is empty — task data not pre-filled on edit page"


def test_15_delete_task_removes_it_from_list(driver):
    """TC-15: Clicking the delete button on a task must remove it from the task list."""
    navigate(driver, "/tasks")
    time.sleep(1)
    source_before = driver.page_source
    # Find the delete button (Trash2 icon button — no text, last button in each card)
    delete_buttons = driver.find_elements(
        By.CSS_SELECTOR, "button.text-destructive, button[class*='destructive']"
    )
    assert len(delete_buttons) > 0, "No delete buttons found on tasks page"
    delete_buttons[0].click()
    time.sleep(2)
    source_after = driver.page_source
    assert source_after != source_before, \
        "Page source unchanged after delete — task may not have been removed"
