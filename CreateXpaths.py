import os
import json
import hashlib
import validators
from bs4 import BeautifulSoup
from selenium import webdriver
from collections import OrderedDict
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

tags = ["a", "button", "div", "input", "span"]

def open_url(url):
    html_doc = None
    # Path of ChromeDriver executable
    chrome_driver_path = "chromedriver.exe"
    
    # Use Selenium to load the page with JavaScript execution
    chrome_options = Options()

    # Set the ChromeDriver executable path directly in the constructor
    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url)
    driver.maximize_window()

    WebDriverWait(driver, 60).until(
        lambda driver: driver.execute_script("return document.readyState") == "complete"
    )

    html_doc = driver.page_source
    driver.quit()
	
    return html_doc


def create_xpaths_from_page_source(html_doc, tags):
    soup = BeautifulSoup(html_doc, "html.parser")

    # create an empty dictionary to store xpaths
    xpath_dictionary = {}

    for tag in tags:
        all_elements = soup.find_all(tag)
        index = 1  # xpath index starts from 1

        for element in all_elements:
            xpath = select_xpath_attribute(element)
            node = key_name(element, index)
            xpath_dictionary[node] = xpath

            index += 1

    return xpath_dictionary


def select_xpath_attribute(element):
    tag = element.name
    
    if element.get("id"):
        attr_value = element.get("id")
        xpath = f"//{tag}[@id = '{attr_value}']"
    elif element.get("href"):
        attr_value = element.get("href")
        xpath = f"//{tag}[@href = '{attr_value}']"
    elif element.get("src"):
        attr_value = element.get("src")
        xpath = f"//{tag}[@src = '{attr_value}']"
    elif element.get("class"):
        attr_value = " ".join(element.get("class"))
        xpath = f"//{tag}[@class = '{attr_value}']"
    elif element.get("aria-label"):
        attr_value = element.get("aria-label")
        xpath = f"//{tag}[@aria-label = '{attr_value}']"
    elif element.get("title"):
        attr_value = element.get("title")
        xpath = f"//{tag}[@title = '{attr_value}']"
    elif element.string and str(element.string).strip():
        xpath = f"//{tag}[contains(text(), '{str(element.string).strip()}')]"
    elif element.get("name"):
        attr_value = element.get("name")
        xpath = f"//{tag}[(@name = '{attr_value}')]"
    elif element.get("value"):
        attr_value = element.get("value")
        xpath = f"//{tag}[(@value = '{attr_value}')]"
    else:
        xpath = f"//{tag}"

    return xpath


def key_name(element, index):
    key = None
    if element.name == "a":
        if element.string and str(element.string).strip():
            key = snake_case_convertor(element.string)
        elif element.get("aria-label"):
            key = snake_case_convertor(element.get("aria-label"))

        if key:
            key += "_link"
        else:
            key = "link_" + str(index)
    else:
        if element.string and str(element.string).strip():
            key = snake_case_convertor(element.string)
        elif element.get("aria-label"):
            key = snake_case_convertor(element.get("aria-label"))

        if key:
            key += "_" + element.name
        else:
            key = element.name + "_" + str(index)

    return key

def snake_case_convertor(raw_string):
    """
    This function converts a string to a valid variable name in snake case format

    This function may result in empty string when a string only contains special symbols
    """

    if not isinstance(raw_string, str):
        raw_string = str(raw_string)

    words = "".join(
        char.lower()
        for char in raw_string.strip()
        if (char.isalnum() or char == "_" or char == " ")
    )

    return words.replace(" ", "_")


#################################### Code execution starts here #############################
url = input("Enter the URL: ")
if not url.endswith("/"):
    url += "/"
if not validators.url(url):
    raise ValueError(
        "Passed URL is invalid. Include 'http' or 'https' protocol in the url to make it valid"
    )

html_doc = open_url(url)

# pass HTML doc
xpath_dictionary = create_xpaths_from_page_source(html_doc, tags)

for key, value in xpath_dictionary.items():
	print(f"{key} = {value}\n")
