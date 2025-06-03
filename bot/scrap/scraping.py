import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
# Menggunakan 3 web browser yang berbeda
from selenium.webdriver.chrome.options import Options

def scrape_data(url):
    try:
        # Configurasi webdriver dengan 3 web browser
        options = Options()
        options.add_argument('-headless')
        # Chrome
        driver = webdriver.Chrome(options=options)
        # Getting URL yang diberikan nantinya
        driver.get(url)

        try:
            wait = WebDriverWait(driver, timeout=5)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'css-1otdiuc')))
        except:
            raise LookupError("There is no element specified")
        
        # Parsing With Beautifulsoup
        content = driver.page_source
        soup = BeautifulSoup(content, 'html.parser')
        # Mengambil Data Magang
        interns = []

        for info in soup.find_all('div', class_='css-1otdiuc'):
            # Getting data there
            try:
                name = info.find('h2', class_='css-1gzvnis').text.strip()
                company = info.find('a', class_='k-text-subdued k-font-bold').text.strip()
                address = info.find('span', class_="k-text-gray-500 k-block k-pointer-events-none").text.strip()
                salary = info.find('p', class_="k-text-gray-500").text.strip()
                date_limit = info.find('span', class_='k-text-xs k-font-bold k-text-gray-600').text.strip()

                interns.append(
                    {
                        'Intern Name': name,
                        "Intern Company" : company,
                        "Intern Address" : address,
                        "Intern Salary" : salary,
                        "Intern Limit Time" : date_limit

                    }
                )
            except AttributeError:
                continue

        return interns

    except Exception as e:
        print('An Error Ocurred: ', e)
        return []
    
    finally:
        driver.quit()

