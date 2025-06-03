from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import time
from pathlib import Path
import base64

from document import Document

download_dir = "C:\\Users\\hsiegw\\Desktop\\unzip_and_merge"


class WebWorker:

    def __init__(self):
        self.is_login = False
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('headless')
        self.options.add_experimental_option("prefs", {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True,
            "profile.content_settings.exceptions.automatic_downloads.*.setting": 1,
            "profile.default_content_setting_values.automatic_downloads": 1,
        })
        self.driver = webdriver.Chrome(options=self.options)
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

        with open("captcha_login.png", 'wb') as image:
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

            self.driver.switch_to.frame(self.driver.find_element(By.ID, "title"))
            # 切換到承辦人頁面
            self.driver.find_element(By.XPATH,
                                     '//*[@id="form1"]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[3]/a').click()
            # 切換到承辦中頁面
            self.toggle_std2_page()

        except TimeoutException as timeout:
            msg = self.driver.find_element(By.TAG_NAME, 'body').text
            self.go_to_login_page()
            raise TimeoutException(msg, timeout.screen, timeout.stacktrace)

    def toggle_std2_page(self):
        """切換到承辦中頁面"""
        if self.is_login:
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame(self.driver.find_element(By.ID, "fbody"))
            self.driver.switch_to.frame(self.driver.find_element(By.ID, "memu"))
            self.driver.find_element(By.XPATH, '//*[@id="sdt2"]').click()

    def toggle_mainframe(self):
        """切換到公文列表所在的frame"""
        if self.is_login:
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame(self.driver.find_element(By.ID, "fbody"))
            self.driver.switch_to.frame(self.driver.find_element(By.ID, "mainframe"))

    def get_all_docs(self):

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

        WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, '//*[@id="listTBODY"]')))

        docs_table = self.driver.find_element(By.XPATH, '//*[@id="listTBODY"]')

        doc_trs = docs_table.find_elements(By.TAG_NAME, 'tr')

        docs = []

        for tr in doc_trs:
            d = Document(tr)
            docs.append(d)

        return docs

    def download_document(self, row_index, doc_id):
        """:param doc_id: pass any string other than empty can do the job.
        :param row_index: row index of document wants to download.
        """
        self.toggle_mainframe()
        original_window = self.driver.current_window_handle
        self.driver.execute_script(f"queryOne('{doc_id}',3,{row_index})")
        wait = WebDriverWait(self.driver, 5)
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

            download_path = Path(download_dir)

            download_all_link.click()
            wait.until(lambda _: download_path.joinpath(f'{document_name}.zip').exists())
            download_main_doc_link.click()
            wait.until(lambda _: download_path.joinpath(f'{document_name}.pdf').exists())
        except NoSuchElementException:
            pass
        finally:
        # download will open another window
            for window in self.driver.window_handles:
                if window != original_window:
                    self.driver.switch_to.window(window)
                    self.driver.close()

            wait.until(EC.number_of_windows_to_be(1))
            self.driver.switch_to.window(original_window)


if __name__ == "__main__":
    worker = WebWorker()
    print(worker.driver.title)

    worker.download_user_rnd_img()
    rnd = input("請輸入驗證碼:")
    worker.login("", "", rnd)  # MARK :- 帳號 密碼使用 env
    r_idx = 0
    doc = worker.get_all_docs()[r_idx]
    worker.download_document(doc.doc_id, r_idx)

    # with open(f"{worker.driver.title}.txt", "w") as source_file:
    #     print(worker.driver.page_source, file=source_file)
