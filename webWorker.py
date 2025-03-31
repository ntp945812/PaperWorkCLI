from selenium import webdriver

class WebWorker:

    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('headless')
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.get("https://odm.kcg.gov.tw")

    def __exit__(self):
        self.driver.quit()


if __name__ == "__main__":
    worker = WebWorker()
    print(worker.driver.title)