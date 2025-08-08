from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

import json


class Document:

    def __init__(self, tr: WebElement):
        # 主旨
        try:
            self.title = tr.find_element(By.XPATH, './/td[12]/p').get_attribute('title')
        except NoSuchElementException:
            self.title = tr.find_element(By.XPATH, './/td[12]').text

        # 文號
        doc_flow_obj = json.loads(tr.find_element(By.XPATH, './/*[@id="gbDocflowObj"]').get_attribute('value'))
        self.doc_id = doc_flow_obj['id']  # 公文系統內部識別號碼
        self.internal_doc_number = doc_flow_obj['doSno']  # 本局收文號

        # 線上/紙本文
        match doc_flow_obj['status4']:
            case '1':
                self.doc_type = '紙'
            case '2':
                self.doc_type = '線'
            case _:
                self.doc_type = "X"

        # 來文日期/字號
        td9 = tr.find_element(By.XPATH, './/td[9]/a').text.splitlines()
        if len(td9) == 1:
            self.issue_date = td9[0][0:10]
            self.external_doc_number = td9[10:]
        else:
            self.issue_date, self.external_doc_number = td9

        # 來文單位 //*[@id="listTBODY"]/tr[5]/td[10]/a //*[@id="listTBODY"]/tr[1]/td[10]/a/p
        try:
            self.issue_unit = tr.find_element(By.XPATH, './/td[10]/a/p').get_attribute('title')
        except NoSuchElementException:
            self.issue_unit = tr.find_element(By.XPATH, './/td[10]/a').text

        # 限辦期限
        self.deadline = tr.find_element(By.XPATH, './/td[15]').text
