"""
    this script is a POC for web scrapping of accounting invoices.
    we use selenium in python

"""




from selenium import webdriver;
from selenium.webdriver.common.keys import Keys;
from selenium.webdriver.common.by import By;
from selenium.webdriver import *;



def scrap_data_miner():

    driver = webdriver.Chrome('S:\ChangLiu\chromedriver\win32_232\chromedriver.exe');
    driver.get("https://dataminer.pjm.com/dataminerui/pages/public/lmp.jsf");

    first_date_picker = driver.find_element(By.XPATH, '//*[@id="frmCriteria:calStartDate_input"]');

    first_date_picker.send_keys(r"09/25/2017");

    second_date_picker = driver.find_element(By.XPATH, '//*[@id="frmCriteria:calStopDate_input"]');

    second_date_picker.send_keys(r"09/25/2017");



chrome_options = ChromeOptions();
# chrome_options.add_argument("--headless");


driver = webdriver.Chrome(executable_path = 'S:\ChangLiu\Github\pnl\input_data\chromedriver_win32\chromedriver.exe', chrome_options = chrome_options);
driver.get("https://dataminer.pjm.com/dataminerui/pages/public/lmp.jsf");



first_date_picker = driver.find_element(By.XPATH, '//*[@id="frmCriteria:calStartDate_input"]');

first_date_picker.send_keys(r"09/25/2017");

second_date_picker = driver.find_element(By.XPATH, '//*[@id="frmCriteria:calStopDate_input"]');

second_date_picker.send_keys(r"09/25/2017");
