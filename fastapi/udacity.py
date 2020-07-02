"""
Scrape Udacity
"""

import logging
from time import sleep
from typing import List

import bs4

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tinydb import TinyDB


logger = logging.getLogger(__name__)

UDACITY_CATALOG_URL = "https://www.udacity.com/courses/all"
JSON_DB = "catalog-udacity.json"


def get_udacity_catalog_list() -> dict:
    """
    get udacity catalog list
    """
    logger.info("Getting Udacity catalog list...")
    browser = navigate_to_page()
    udacity_catalog = get_full_catalog_list(browser)
    save_to_local_database(udacity_catalog, table_name="udacity")
    browser.quit()
    logger.info(f"Completed getting {len(udacity_catalog)} Udacity catalog list")
    return {"udacity": udacity_catalog}


def save_to_local_database(catalog: List[dict], table_name: str):
    logger.info(f"Saving {len(catalog)} course infos to {JSON_DB} database...")
    db = TinyDB(JSON_DB)
    table = db.table(table_name)
    for course_info in catalog:
        table.insert(course_info)
    logger.info(f"Completed saving {len(catalog)} course infos to {JSON_DB} database!")


def get_full_catalog_list(browser: webdriver, use_mock: bool = False) -> list:
    """
    get full catalog list compromised of
        - Nanodegree Programs
        - Individual Courses
    """
    if use_mock:
        logger.info("Getting mock data products list...")
        return get_mock_data_products_list()

    logger.info("Getting full catalog list...")
    full_catalog_list = []

    soup = bs4.BeautifulSoup(browser.page_source, "html.parser")

    nanodegree_catalog_list = get_nanodegree_catalog_list(soup)
    full_catalog_list.extend(nanodegree_catalog_list)

    course_catalog_list = get_course_catalog_list(soup)
    full_catalog_list.extend(course_catalog_list)

    logger.info(f"Completed getting {len(full_catalog_list)} full catalog list")
    return full_catalog_list


def get_nanodegree_catalog_list(soup: BeautifulSoup) -> list:
    """
    get nanodegree catalog list
    """
    logger.info("Getting nanodegree catalog list...")
    nanodegree_cards = soup.find_all(
        "div",
        {
            "class": "course-summary-card row row-gap-medium catalog-card nanodegree-card ng-star-inserted"
        },
    )
    logger.info(f"Found {len(nanodegree_cards)} nanodegree cards on the Catalog web page")

    nanodegree_catalog_list = get_programs_details_list(nanodegree_cards)
    logger.info(f"Completed getting {len(nanodegree_catalog_list)} nanodegree catalog list")
    return nanodegree_catalog_list


def get_course_catalog_list(soup):
    """
    get course catalog list
    """
    logger.info("Getting course catalog list...")
    course_cards = soup.find_all(
        "div", {"class": "course-summary-card row row-gap-medium catalog-card ng-star-inserted"},
    )
    logger.info(f"Found {len(course_cards)} course cards on the Catalog web page")

    course_catalog_list = get_programs_details_list(course_cards)
    logger.info(f"Completed getting {len(course_catalog_list)} course catalog list")
    return course_catalog_list


def get_programs_details_list(course_cards: bs4.element.ResultSet) -> list:
    """
    returns list of lists containing info on programs
    Each program info list contains -
        - Name
        - Course Type
        - Relative URL Link
        - Category (if present)
        - Skills (if present)
        - Collaborators (if present)
        - Level: Beginner, Intermediate, Advanced (if present)
        - Details (if present)
    """
    logger.info("Getting program details list...")
    all_courses_info_list = []
    for i, course_card in enumerate(course_cards):
        course_info = {
            "course_name": "",
            "course_type": "",
            "course_link": "",
            "category": "",
            "skills": [],
            "collaborators": [],
            "course_level": "",
            "course_details": "",
        }

        # course name, type and link
        course_link = course_card.find("a", {"class": "capitalize"})
        course_name = course_link.text
        course_info["course_name"] = course_name

        course_link = course_link.get("href")

        if "--nd" in course_link.lower() or "nanodegree" in course_link.lower():
            course_type = "nanodegree"
        else:
            course_type = "course"

        course_info["course_type"] = course_type
        course_info["course_link"] = course_link

        # category
        category = course_card.find("h4", {"class": "category ng-star-inserted"})
        if category:
            category = category.text.strip()
            course_info["category"] = category

        # skills
        skills_section = course_card.find("div", {"class": "skills ng-star-inserted"})
        if skills_section:
            skills_list = skills_section.find_all("span", {"class": "ng-star-inserted"})
            skills = [skill.text.strip(" ").strip(",") for skill in skills_list]
            course_info["skills"] = skills

        # collaborators
        collaborators_section = course_card.find(
            "div", {"class": "hidden-sm-down ng-star-inserted"}
        )
        if collaborators_section:
            collaborators_list = collaborators_section.find_all(
                "span", {"class": "ng-star-inserted"}
            )
            collaborators = [collaborator.text for collaborator in collaborators_list]
            course_info["collaborators"] = collaborators

        # course level
        right_section = course_card.find("div", {"class": "right"})
        if right_section:
            course_level = right_section.text.capitalize()
            course_info["course_level"] = course_level

        # course details
        details_section = course_card.find("div", {"class": "card__expander"}).find(
            "span", {"class": "ng-star-inserted"}
        )
        if details_section:
            course_details = details_section.text
            course_info["course_details"] = course_details

        all_courses_info_list.append(course_info)

    logger.info("Completed getting program details list...")
    return all_courses_info_list


def navigate_to_page() -> webdriver:
    """
    navigate to the Udacity Catalog web page
    """
    logger.info("Navigating to the Udacity Catalog web page...")
    # chrome_driver = "/usr/bin/chromedriver" # linux
    chrome_driver = "/usr/local/bin/chromedriver"  # mac
    browser = webdriver.Chrome(executable_path=chrome_driver)
    browser.get(UDACITY_CATALOG_URL)

    pop_up_xml_path = (
        "/html/body/ir-root/ir-content/ir-autopopup-modal/ir-modal/div/div[2]/div/div[1]"
    )

    delay = 5  # seconds
    try:
        # logger.info(f"Sleeping for {delay} seconds")
        # sleep(delay)
        popup_close_button = WebDriverWait(browser, delay).until(
            EC.presence_of_element_located((By.XPATH, pop_up_xml_path))
        )
        logger.info("Course Catalog Page is ready!")

        logger.info("Closing pop up button")
        popup_close_button.click()

    except TimeoutException:
        logger.exception("Loading Course Catalog Page took too much time!")

    logger.info("Completed Navigating to the Udacity Catalog web page")
    return browser


def get_mock_data_products_list() -> list:
    """
    mock data products list
    """
    # TODO: Conver to List of dictionaries
    logger.info("Getting products test data...")
    mock_products_list = [
        [
            "Java Developer",
            "nanodegree",
            "/course/java-developer-nanodegree--nd035",
            "School of Programming",
            "Java, Spring Boot, Rest API, MySQL, MongoDB",
            "",
            "Intermediate",
            "Learn back-end development with the Java programming language",
        ],
        [
            "AI Product Manager",
            "nanodegree",
            "/course/ai-product-manager-nanodegree--nd088",
            "School of Artificial Intelligence",
            "AI Products, Training ML Models, Annotating Datasets, Prototyping a Product",
            "Figure Eight",
            "Beginner",
            "Learn to develop AI products that deliver business value. Build skills that help you compete in the new AI-powered world.",
        ],
        [
            "Self-Driving Fundamentals: Featuring Apollo ",
            "course",
            "/course/self-driving-car-fundamentals-featuring-apollo--ud0419",
            "School of Autonomous Systems",
            "Apollo HD Map, Localization, Perception, Prediction, Planning, Control",
            "Baidu",
            "Beginner",
            "Identify key parts of self-driving cars, utilize Apollo HD Map, localization, perception, prediction, planning and control, and start the learning path of building a self-driving car. ",
        ],
        [
            "Tales from the Genome",
            "course",
            "/course/tales-from-the-genome--bio110",
            "",
            "Genetics, DNA, Gene regulation",
            "23andMe",
            "Beginner",
            "Learn the basics of genetics, with a personal twist. This class is all about DNA and how it shapes who we are.",
        ],
    ]
    return mock_products_list
