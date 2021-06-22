from pathlib import Path
from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from datetime import date, timedelta
from logger import logger

try:
    chrome_driver = Path(__file__).parent.resolve() / 'chromedriver_92.exe'
    driver = webdriver.Chrome(chrome_driver)
except SessionNotCreatedException:
    chrome_driver = Path(__file__).parent.resolve() / 'chromedriver_91.exe'
    driver = webdriver.Chrome(chrome_driver)
    logger.info('Хром версии 91')

LT22_URL = 'https://cuvl0301.eur.cchbc.com:8204/sap/bc/ui2/flp#LT22-display'

driver.implicitly_wait(10)
driver.get(LT22_URL)
driver.switch_to.frame('application-LT22-display')

WAREHOUSE_NUMBER = 'M0:46:::0:34'
STORAGE_TYPE = 'M0:46:::1:34'
CONFIRMED_TO = 'M0:46:::6:2'
SOURCE = 'M0:46:::10:2'
DESTINATION = 'M0:46:::11:2'
TO_DATE_FROM = 'M0:46:::15:34'
TO_DATE_TO = 'M0:46:::15:59'
EXECUTE_BTN = 'M0:50::btn[8]'
CONTINUE_BTN = 'M1:50::btn[0]'

date_before = (date.today() - timedelta(days=1)).strftime('%d.%m.%Y')

fill_parameters = {WAREHOUSE_NUMBER: '270',
                   STORAGE_TYPE: '200',
                   CONFIRMED_TO: '',
                   SOURCE: '',
                   DESTINATION: '',
                   TO_DATE_FROM: date_before,
                   TO_DATE_TO: date.today().strftime('%d.%m.%Y'),
                   EXECUTE_BTN: ''}

for id_elem, value in fill_parameters.items():
    element = driver.find_element_by_id(id_elem)
    if id_elem in (CONFIRMED_TO, SOURCE, DESTINATION, EXECUTE_BTN):
        element.click()
    else:
        element.clear()
        element.send_keys(value)

body = WebDriverWait(driver=driver, timeout=10).until(lambda d: d.find_element_by_id('M0:46:::26:1_l'))
body.send_keys(Keys.SHIFT + Keys.F4)

driver.find_element_by_id(CONTINUE_BTN).click()
