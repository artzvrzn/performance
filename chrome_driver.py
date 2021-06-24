from pathlib import Path
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from datetime import date, timedelta
from glob import glob
import os
from time import sleep
from getpass import getuser
from logger import logger

BASE_PATH = Path(__file__).parent.resolve()
chrome_path = BASE_PATH / 'chromedriver.exe'

LT22_URL = 'https://cuvl0301.eur.cchbc.com:8204/sap/bc/ui2/flp#LT22-display'

WAREHOUSE_NUMBER = 'M0:46:::0:34'
STORAGE_TYPE = 'M0:46:::1:34'
CONFIRMED_TO = 'M0:46:::6:2'
SOURCE = 'M0:46:::10:2'
DESTINATION = 'M0:46:::11:2'
TO_DATE_FROM = 'M0:46:::15:34'
TO_DATE_TO = 'M0:46:::15:59'
EXECUTE_BTN = 'M0:50::btn[8]'
CONTINUE_BTN = 'M1:50::btn[0]'

DATE_BEFORE = (date.today() - timedelta(days=1)).strftime('%d.%m.%Y')
DATE_TODAY = date.today().strftime('%d.%m.%Y')

options = webdriver.ChromeOptions()
options.add_argument('--lang=en')


def get_last_file_path():
    try:
        last_file = max(glob(f'C:\\Users\\{getuser()}\\Downloads\\*.xlsx'), key=os.path.getctime)
    except ValueError:
        last_file = 'No file'
        logger.debug(last_file)
    return last_file


class LT22Run:

    def __init__(self):
        self._remove_old_file()
        self.driver = None
        self.fill_parameters = {WAREHOUSE_NUMBER: '270',
                                STORAGE_TYPE: '200',
                                CONFIRMED_TO: '',
                                SOURCE: '',
                                DESTINATION: '',
                                TO_DATE_FROM: DATE_BEFORE,
                                TO_DATE_TO: DATE_TODAY,
                                EXECUTE_BTN: ''}
        self.file_name = get_last_file_path()

    def _start_application(self):
        self.driver = webdriver.Chrome(chrome_path, chrome_options=options)
        logger.info(f'Chrome version {self.driver.capabilities["browserVersion"]}')
        self.driver.implicitly_wait(10)
        self.driver.get(LT22_URL)
        self.driver.switch_to.frame('application-LT22-display')

    def _get_file_path(self):
        while self.file_name == get_last_file_path():
            sleep(0.5)
        self.file_name = get_last_file_path()
        logger.info(f'lt22.xlsx: {self.file_name}')
        self.driver.quit()
        with open(file='lt22_old.txt', mode='w', encoding='utf8') as legacy:
            legacy.write(os.path.normpath(self.file_name))
        return self.file_name

    def _run_application(self):
        self._start_application()
        for id_elem, value in self.fill_parameters.items():
            element = self.driver.find_element_by_id(id_elem)
            if id_elem in (CONFIRMED_TO, SOURCE, DESTINATION, EXECUTE_BTN):
                element.click()
            else:
                element.clear()
                element.send_keys(value)

        body = WebDriverWait(driver=self.driver, timeout=300).until(lambda d: d.find_element_by_id('M0:46:::3:2_l'))
        body.send_keys(Keys.SHIFT + Keys.F4)
        self.driver.find_element_by_id(CONTINUE_BTN).click()

    def _remove_old_file(self):
        try:
            with open(file=Path(__file__).parent.resolve() / 'lt22_old.txt', mode='r', encoding='utf8') as legacy:
                for line in legacy.readlines():
                    Path.unlink(Path(line))
        except Exception as exc:
            print(exc)

    def execute(self):
        self._run_application()
        self._get_file_path()
