from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import random

# Function to initialize WebDriver
def init_driver():
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("user-agent=danielgeorge922@gmail.com")  # Set a custom user-agent
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        print(f"Error initializing WebDriver: {e}")
        return None

# Function to log in to the UF site
def login(driver, username, password):
    try:
        login_url = "https://login.ufl.edu/idp/profile/SAML2/Redirect/SSO?execution=e3s1"
        driver.get(login_url)

        # Wait for the username field to be present
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        password_field = driver.find_element(By.ID, "password")
        submit_button = driver.find_element(By.ID, "submit")

        # Enter username and password
        username_field.send_keys(username)
        password_field.send_keys(password)

        # Submit the form
        submit_button.click()

        # Wait for login to complete by checking for a known element on the post-login page
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "search-bar"))  # Replace with a known element ID after login
        )
    except Exception as e:
        print(f"Error during login: {e}")

# Function to search for a course
def search_course(driver, course_id):
    try:
        search_url = "https://one.uf.edu/soc/registration-search/2248"
        driver.get(search_url)

        # Wait for the search input field to be present
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "course-number"))
        )

        search_box.send_keys(course_id)
        search_box.send_keys(Keys.RETURN)

        # Wait for search results to load
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "course-card")))

        # Give time for the page to fully load
        time.sleep(3)
        page_source = driver.page_source
        return page_source
    except Exception as e:
        print(f"Error during course search: {e}")
        return None

# Function to parse course details from the page source
def parse_course_details(page_source):
    try:
        soup = BeautifulSoup(page_source, 'html.parser')
        course_cards = soup.find_all('div', class_='course-card')

        courses = []
        for card in course_cards:
            course = {}
            course['course_id'] = card.find('h2', class_='course-id').text.strip()
            course['course_title'] = card.find('h3', class_='course-title').text.strip()
            course['instructor'] = card.find('p', class_='instructor-name').text.strip()
            course['times'] = card.find('p', class_='class-times').text.strip()
            course['days'] = card.find('p', class_='class-days').text.strip()
            courses.append(course)

        return courses
    except Exception as e:
        print(f"Error parsing course details: {e}")
        return []

# Function to introduce a random delay to avoid overloading the server
def delay():
    time.sleep(random.uniform(1, 3))  # Random delay between 1 and 3 seconds

# Main function
def main(course_id, username, password):
    driver = init_driver()
    if driver is None:
        print("WebDriver initialization failed.")
        return

    try:
        login(driver, username, password)
        page_source = search_course(driver, course_id)
        if page_source is None:
            print("Failed to retrieve page source.")
            return

        delay()
        course_details = parse_course_details(page_source)

        for course in course_details:
            print(course)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        driver.quit()

# Run the script with a specific course ID and login credentials
if __name__ == "__main__":
    course_id = 'COP3530'  # Replace with the course ID you want to search for
    username = 'danielgeorge'  # Replace with your UF username
    password = 'Dg092204-'  # Replace with your UF password
    main(course_id, username, password)
