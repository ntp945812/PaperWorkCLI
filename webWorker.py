from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import base64
from paper import Paper


class WebWorker:

    def __init__(self):
        self.is_login = False
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('headless')
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.get("https://odm.kcg.gov.tw")
        self.driver.implicitly_wait(5)

    def __exit__(self):
        self.driver.quit()

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

        login_btn.click()
        WebDriverWait(self.driver, 5).until(EC.title_is("公文管理系統"))

        if self.driver.title == "公文管理系統":
            self.is_login = True

            self.driver.switch_to.frame(self.driver.find_element(By.ID, "title"))
            # 切換到承辦人頁面
            self.driver.find_element(By.XPATH,
                                     '//*[@id="form1"]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[3]/a').click()
            # 切換到承辦中頁面
            self.toggle_std2_page()

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
        page_size_input = self.driver.find_element(By.XPATH,
                                                   '//*[@id="form1"]/div[2]/table[2]/tbody/tr/td/table/tbody/tr/td[1]/span/input')
        page_size_input.send_keys("100")

        page_size_text = self.driver.find_element(By.XPATH,
                                                  '//*[@id="form1"]/div[2]/table[2]/tbody/tr/td/table/tbody/tr/td/span')
        page_size_text.click()

        time.sleep(0.7)

        docs_table = self.driver.find_element(By.XPATH, '//*[@id="listTBODY"]')

        doc_trs = docs_table.find_elements(By.TAG_NAME, 'tr')

        docs = []

        for tr in doc_trs:
            paper = Paper(tr)
            docs.append(paper)
            print(paper.status)

        return docs

if __name__ == "__main__":
    worker = WebWorker()
    print(worker.driver.title)

    worker.download_user_rnd_img()
    rnd = input("請輸入驗證碼:")
    worker.login("", "", rnd) # MARK :- 帳號 密碼使用 env
    worker.get_all_docs()

    # with open(f"{worker.driver.title}.txt", "w") as source_file:
    #     print(worker.driver.page_source, file=source_file)
