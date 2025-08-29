import subprocess

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoAlertPresentException, StaleElementReferenceException

import time
from pathlib import Path
import base64
import os

from document import Document

import tempfile

DOWNLOAD_DIR = "C:\\Users\\hsiegw\\Desktop\\unzip_and_merge"
TEMP_DIR = tempfile.gettempdir()
CAPTCHA_IMG_PATH = Path(TEMP_DIR).joinpath('captcha_login.png')

class WebWorker:

    def __init__(self):
        self.officer_doc_trs = []
        self.table_doc_trs = []
        self.documents = []
        self.is_login = False
        self.current_role = None
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('headless')
        service = webdriver.ChromeService(service_args=['--log-level=OFF'], log_output=subprocess.DEVNULL)
        self.options.add_experimental_option("prefs", {
            "download.default_directory": DOWNLOAD_DIR,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True,
            "profile.content_settings.exceptions.automatic_downloads.*.setting": 1,
            "profile.default_content_setting_values.automatic_downloads": 1,
        })
        self.driver = webdriver.Chrome(options=self.options, service=service)
        self.go_to_login_page()

    def __exit__(self):
        self.driver.quit()

    def go_to_login_page(self):
        self.driver.get("https://odm.kcg.gov.tw")
        WebDriverWait(self.driver, 5).until(EC.title_is("高雄市政府第二代公文整合系統-登入畫面"))

    def download_user_rnd_img(self):
        img_xpath = "/html/body/form/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table/tbody/tr[1]/td/div/table/tbody/tr[3]/td[3]/img"
        img_base64 = self.driver.execute_script("""
            var ele = arguments[0];
            var cnv = document.createElement('canvas');
            cnv.width = ele.width; cnv.height = ele.height;
            cnv.getContext('2d').drawImage(ele, 0, 0);
            return cnv.toDataURL('image/jpeg').substring(22);    
            """, self.driver.find_element(By.XPATH, img_xpath))

        with open(CAPTCHA_IMG_PATH, 'wb') as image:
            image.write(base64.b64decode(img_base64))

    def login(self, user_id, user_pwd, user_rnd):
        user_id_input = self.driver.find_element(By.XPATH, '//*[@id="userID"]')
        user_pwd_input = self.driver.find_element(By.XPATH, '//*[@id="userPWD"]')
        user_rnd_input = self.driver.find_element(By.XPATH, '//*[@id="userRnd"]')
        login_btn = self.driver.find_element(By.XPATH,
                                             '/html/body/form/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table/tbody/tr[2]/td/table/tbody/tr/td[2]/input')
        user_id_input.send_keys(user_id)
        user_pwd_input.send_keys(user_pwd)
        user_rnd_input.send_keys(user_rnd)

        try:
            login_btn.click()
            WebDriverWait(self.driver, 3).until(EC.title_is("公文管理系統"))
            self.is_login = True
            self.current_role = "承辦人"
            self.driver.switch_to.frame(self.driver.find_element(By.ID, "title"))
            # 切換到承辦人頁面
            self.driver.find_element(By.XPATH,
                                     '//*[@id="form1"]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[3]/a').click()

        except TimeoutException as timeout:
            msg = self.driver.find_element(By.TAG_NAME, 'body').text
            self.go_to_login_page()
            raise TimeoutException(msg, timeout.screen, timeout.stacktrace)

    def switch_to_checkin_table(self):
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame(self.driver.find_element(By.ID, "title"))
        role_select_element = self.driver.find_element(By.XPATH, '//*[@id="form1"]/table/tbody/tr[1]/td/table/tbody/tr[2]/td/font/select[2]')
        role_select = Select(role_select_element)
        role_select.select_by_visible_text("登記桌人員")
        self.current_role = "登記桌人員"
        time.sleep(0.5)


    def switch_to_officer(self):
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame(self.driver.find_element(By.ID, "title"))
        role_select_element = self.driver.find_element(By.XPATH, '//*[@id="form1"]/table/tbody/tr[1]/td/table/tbody/tr[2]/td/font/select[2]')
        role_select = Select(role_select_element)
        role_select.select_by_visible_text("承辦人")
        self.current_role = "承辦人"
        time.sleep(0.5)

    def toggle_std1_page(self):
        """切換到待簽收頁面"""
        if self.is_login:
            self.driver.switch_to.default_content()
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "fbody")))
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "memu")))

            sdt1_a = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="sdt1"]')))
            sdt1_a.click()

    def toggle_std2_page(self):
        """切換到承辦中頁面"""
        if self.is_login:

            self.driver.switch_to.default_content()
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "fbody")))
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "memu")))
            sdt2_a = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="sdt2"]')))
            sdt2_a.click()

    def toggle_mainframe(self):
        """切換到公文列表所在的frame"""
        if self.is_login:
            self.driver.switch_to.default_content()
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//*[@id="fbody"]')))
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//*[@id="mainframe"]')))

    def windows_cleanup(self,original_window):

        for window in self.driver.window_handles:
            if window != original_window:
                self.driver.switch_to.window(window)
                self.driver.close()

        wait = WebDriverWait(self.driver, 3)
        wait.until(EC.number_of_windows_to_be(1))
        self.driver.switch_to.window(original_window)

    def get_officer_all_docs(self):

        if self.current_role != "承辦人":
            raise RuntimeError("Role missmatch.")

        self.toggle_std2_page()

        self.officer_doc_trs = self.get_document_tr()

        docs = []

        for tr in self.officer_doc_trs:
            d = Document(tr)
            docs.append(d)

        self.documents = docs

        return docs

    def get_table_all_docs(self):
        if self.current_role != "登記桌人員":
            raise RuntimeError("Role missmatch.")

        self.toggle_std1_page()

        self.table_doc_trs = self.get_document_tr()

        docs = []

        for tr in self.table_doc_trs:
            d = Document(tr)
            docs.append(d)

        return docs

    def get_document_tr(self):
        self.toggle_mainframe()
        # 文件數 <=10 的時候 不會出現input
        try:
            page_size_input = self.driver.find_element(By.XPATH,
                                                       '//*[@id="form1"]/div[2]/table[2]/tbody/tr/td/table/tbody/tr/td[1]/span/input')
            page_size_input.send_keys("100")

            page_size_text = self.driver.find_element(By.XPATH,
                                                      '//*[@id="form1"]/div[2]/table[2]/tbody/tr/td/table/tbody/tr/td/span')
            page_size_text.click()

            time.sleep(1)

        except NoSuchElementException:
            pass

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="listTBODY"]')))

        docs_table = self.driver.find_element(By.XPATH, '//*[@id="listTBODY"]')

        tr = docs_table.find_elements(By.TAG_NAME, 'tr')

        return tr


    def download_document(self, row_index, doc_id):
        """:param doc_id: pass any string other than empty can do the job.
        :param row_index: row index of document wants to download.
        """
        self.toggle_mainframe()
        original_window = self.driver.current_window_handle
        self.driver.execute_script(f"queryOne('{doc_id}',3,{row_index})")
        wait = WebDriverWait(self.driver, 15)
        wait.until(EC.number_of_windows_to_be(2))
        self.driver.switch_to.window(self.driver.window_handles[-1])

        try:
            download_all_link = self.driver.find_element(By.XPATH, '//*[@id="listTHEAD"]/tr[1]/th[3]/a[2]')
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="listTHEAD"]/tr[1]/th[3]/a[2]')))
            download_main_doc_link = self.driver.find_element(By.XPATH, '//*[@id="listTHEAD"]/tr[2]/td[3]/input[3]')
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="listTHEAD"]/tr[2]/td[3]/input[3]')))

            document_name = \
                self.driver.find_element(By.XPATH, '//*[@id="listTHEAD"]/tr[2]/td[3]/input[1]').get_attribute(
                    'value').split(
                    '.')[0]

            download_path = Path(DOWNLOAD_DIR)

            download_all_link.click()
            wait.until(lambda _: download_path.joinpath(f'{document_name}.zip').exists())
            download_main_doc_link.click()
            wait.until(lambda _: download_path.joinpath(f'{document_name}.pdf').exists())
        except NoSuchElementException:
            pass
        finally:
        # download will open another window
            self.windows_cleanup(original_window)

    def preview_document(self, row_index, doc_id):
        """:param doc_id: pass any string other than empty can do the job.
        :param row_index: row index of document wants to download.
        """
        self.toggle_mainframe()
        original_window = self.driver.current_window_handle
        self.driver.execute_script(f"queryOne('{doc_id}',3,{row_index})")
        wait = WebDriverWait(self.driver, 15)
        wait.until(EC.number_of_windows_to_be(2))
        self.driver.switch_to.window(self.driver.window_handles[-1])

        try:
            download_main_doc_link = self.driver.find_element(By.XPATH, '//*[@id="listTHEAD"]/tr[2]/td[3]/input[3]')
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="listTHEAD"]/tr[2]/td[3]/input[3]')))

            document_name = \
                self.driver.find_element(By.XPATH, '//*[@id="listTHEAD"]/tr[2]/td[3]/input[1]').get_attribute(
                    'value').split(
                    '.')[0]

            temp_filename = Path(TEMP_DIR).joinpath(f'{document_name}.pdf')

            if not temp_filename.exists():
                download_dir_path = Path(DOWNLOAD_DIR)
                download_file_path = download_dir_path.joinpath(f'{document_name}.pdf')

                download_main_doc_link.click()
                wait.until(lambda _: download_file_path.exists())

                download_file_path.rename(temp_filename)


            os.startfile(temp_filename)

        except NoSuchElementException:
            pass
        finally:
        # download will open another window
            self.windows_cleanup(original_window)

    def transfer_document_to_paper(self, row_index, doc_id):

        if self.documents[row_index].doc_type != "線":
            return
        
        # 轉紙本之前需要重新取得最新的文件列表
        self.get_officer_all_docs()

        wait = WebDriverWait(self.driver, timeout=3)
        
        original_window = self.driver.current_window_handle
        
        wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="functionMenuContainer"]/span[2]/input')))
        to_paper_input = self.driver.find_element(By.XPATH,'//*[@id="functionMenuContainer"]/span[2]/input')
        
        target_tr = self.officer_doc_trs[row_index]
        target_tr_checkbox = target_tr.find_element(By.XPATH,'.//*[@id="ids"]')

        if doc_id == target_tr_checkbox.get_attribute('value'):
            target_tr_checkbox.click()
            to_paper_input.click()
            # 確認要轉紙本
            alert = wait.until(lambda d: d.switch_to.alert)
            alert.accept()

            # 確認請印出紙本公文 有時候會出現 有時候又不會出現
            try:
                alert2 = wait.until(EC.alert_is_present())
                alert2.accept()
            except TimeoutException:
                print("請印出紙本公文 alert not present.")

            self.windows_cleanup(original_window)

        else:
            raise RuntimeError("row_index and doc_id missmatch in transfer_document_to_paper")

    def receipt_document_from_table(self, doc_ids):
        self.get_table_all_docs()

        for doc_id in doc_ids:
            for tr in self.table_doc_trs:
                tr_checkbox = tr.find_element(By.XPATH,'.//*[@id="ids"]')
                if doc_id == tr_checkbox.get_attribute('value'):
                    tr_checkbox.click()
                    break

        self.driver.find_element(By.XPATH,'//*[@id="functionMenuContainer"]/span[1]/input').click()

    def distribute_document(self, doc_ids , officer="謝冠緯(系統科-副工程司)"):

        if self.current_role != "登記桌人員":
            raise RuntimeError("Role missmatch.")

        self.toggle_std2_page()

        distribute_document_tr = self.get_document_tr()

        for doc_id in doc_ids:
            for tr in distribute_document_tr:
                tr_checkbox = tr.find_element(By.XPATH,'.//*[@id="ids"]')
                if doc_id == tr_checkbox.get_attribute('value'):
                    tr_checkbox.click()
                    break
        # 分文按鈕
        self.driver.find_element(By.XPATH, '//*[@id="functionMenuContainer"]/span[1]/input').click()

        time.sleep(0.5)

        # 選要分給誰
        officer_select_element = self.driver.find_element(By.XPATH, '//*[@id="form1"]/table[3]/tbody/tr[2]/td/div/table/tbody/tr[1]/td[4]/select[1]')
        officer_select = Select(officer_select_element)
        officer_select.select_by_visible_text(officer)

        self.driver.find_element(By.XPATH, '//*[@id="form1"]/table[2]/tbody/tr/td/span/input[1]').click()

        # 切換回承辦人
        self.switch_to_officer()
        # 切換到簽收頁面
        self.toggle_std1_page()
        self.toggle_mainframe()
        time.sleep(0.5)

        # 讓所有公文在同一頁
        try:
            page_size_input = self.driver.find_element(By.XPATH,
                                                       '//*[@id="form1"]/div[2]/table[2]/tbody/tr/td/table/tbody/tr/td[1]/span/input')
            page_size_input.send_keys("100")

            page_size_text = self.driver.find_element(By.XPATH,
                                                      '//*[@id="form1"]/div[2]/table[2]/tbody/tr/td/table/tbody/tr/td[1]/span')
            page_size_text.click()

            time.sleep(1)

        except NoSuchElementException:
            pass

        # 按全選按鈕
        self.driver.find_element(By.XPATH,'//*[@id="cbAll"]').click()
        time.sleep(0.5)

        self.driver.find_element(By.XPATH,'//*[@id="functionMenuContainer"]/span[1]/input').click()
        self.switch_to_checkin_table()

    # 待測試
    def return_document(self, row_index, doc_id, reason):

        doc_trs = self.get_document_tr()

        for tr in doc_trs:
            tr_checkbox = tr.find_element(By.XPATH, './/*[@id="ids"]')
            if doc_id == tr_checkbox.get_attribute('value'):
                tr_checkbox.click()
                break
        if self.current_role == "登記桌人員":
            self.driver.find_element(By.XPATH, '//*[@id="functionMenuContainer"]/span[2]/input').click()
        elif self.current_role == "承辦人":
            self.driver.find_element(By.XPATH, '//*[@id="functionMenuContainer"]/span[12]/input').click()

        time.sleep(0.5)

        wait = WebDriverWait(self.driver, 3)
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//*[@id="batchFrame"]')))

        self.driver.find_element(By.XPATH,'//*[@id="form1"]/table[3]/tbody/tr[2]/td/div/table/tbody/tr[1]/td[4]/textarea').send_keys(reason)
        self.driver.find_element(By.XPATH,'//*[@id="form1"]/table[2]/tbody/tr/td/span/input[1]').click()

if __name__ == "__main__":
    worker = WebWorker()
    print(worker.driver.title)

    worker.download_user_rnd_img()
    rnd = input("請輸入驗證碼:")
    worker.login("", "", rnd)  # MARK :- 帳號 密碼使用 env
    r_idx = 0
    doc = worker.get_officer_all_docs()[r_idx]
    worker.download_document(doc.doc_id, r_idx)

    # with open(f"{worker.driver.title}.txt", "w") as source_file:
    #     print(worker.driver.page_source, file=source_file)
