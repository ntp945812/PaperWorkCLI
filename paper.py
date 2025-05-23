from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

import json

class Paper:

    def __init__(self,tr: WebElement):
        # 主旨
        try:
            self.subject = tr.find_element(By.XPATH, './/td[12]/p').get_attribute('title')
        except NoSuchElementException:
            self.subject = tr.find_element(By.XPATH, './/td[12]').text

        # 文號
        doc_flow_obj = json.loads(tr.find_element(By.XPATH, './/*[@id="gbDocflowObj"]').get_attribute('value'))
        self.doc_id = doc_flow_obj['id'] # 公文系統內部識別號碼
        self.serial_no = doc_flow_obj['doSno'] # 本局收文號

        # 線上/紙本文
        match doc_flow_obj['status4']:
            case '1':
                self.status = '紙'
            case '2':
                self.status = '線'
            case _:
                self.status = "X"

        # 來文日期/字號

        self.send_date ,self.send_no = tr.find_element(By.XPATH,'.//td[9]/a').text.splitlines()

        # 來文單位 //*[@id="listTBODY"]/tr[5]/td[10]/a //*[@id="listTBODY"]/tr[1]/td[10]/a/p
        try:
            self.send_depart = tr.find_element(By.XPATH, './/td[10]/a/p').get_attribute('title')
        except NoSuchElementException:
            self.send_depart = tr.find_element(By.XPATH, './/td[10]/a').text

        # 限辦期限
        self.deadline = tr.find_element(By.XPATH, './/td[15]').text
