from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

import csv
from tqdm import tqdm

CHROMEDRIVER_PATH = "/usr/bin/chromedriver"
CHROME_PATH = "/usr/bin/chromium-browser"
WINDOW_SIZE = "1920,1080"

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
chrome_options.binary_location = CHROME_PATH
prefs = {'profile.managed_default_content_settings.images':2}
chrome_options.add_experimental_option("prefs", prefs)

url = "https://www.quora.com/search?q=iiit%20hyderabad&type=question"
# url = "https://www.quora.com/search?q=ugee&type=question"
# url = "https://www.quora.com/search?q=rashbehari&type=question"

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.implicitly_wait(5)
driver.get(url)

counter = int(input("Press counter count and then Enter: "))

prev_qlen = 0
file = open('iiithyderabad-output.csv','w')
writer = csv.writer(file)
writer.writerow(['Question','Answer','Author','Author Info','Upvote count','Comment count','Share count'])

for count in tqdm(range(counter),desc="Scrolling"):
    html = driver.find_element(By.TAG_NAME, 'html')
    html.send_keys(Keys.END)
    wait = WebDriverWait(driver, 100)

    if count%500 != 0 and count != counter-1:
        continue

    html = driver.find_element(By.TAG_NAME, 'html')

    question_list = driver.find_elements(By.XPATH, '//*[@id="mainContent"]/div/div/div[2]/div/span/a/div/div/div/div/span')
    q_len = len(question_list)
    if prev_qlen < q_len and count != counter-1:
        prev_qlen = q_len
        continue

    # Write into csv 200 lines at a time
    curr_question = 0
    more_list = driver.find_elements(By.XPATH, '//*[@id="mainContent"]/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div[2]/div')

    curr_increment = 1

    for btn in tqdm(more_list,"Pressing (more)"):
        driver.execute_script("arguments[0].click();", btn)
        curr_question += 1

        if curr_question != len(more_list):
            if curr_question%200 != 0:
                continue

        writer_list = driver.find_elements(By.XPATH, '//*[@id="mainContent"]/div/div/div[2]/div/div/div[1]/div/div[1]/div/div/div/div/div[2]/div[1]/span[1]/span/div/div/div/div/div/a/div/span/span')
        writer_info_list = driver.find_elements(By.XPATH, '//*[@id="mainContent"]/div/div/div[2]/div/div/div[1]/div/div[1]/div/div/div/div/div[2]/div[2]/span')
        comment_list = driver.find_elements(By.XPATH, '//*[@id="mainContent"]/div/div/div[2]/div/div/div[1]/div/div/div/div/div[1]/div[2]/div/div/div/button/div')
        share_list = driver.find_elements(By.XPATH, '//*[@id="mainContent"]/div/div/div[2]/div/div/div[1]/div/div/div/div/div[1]/div[3]/div/div/button/div')

        # Scrape next 200 and write to 
        if len(question_list) > 200:
            questions = [x.text for x in question_list[:200]]
            del question_list[:200]
            writers = [x.text for x in writer_list[:200]]
            del writer_list[:200]
            writer_infos = [x.text for x in writer_info_list[:200]]
            del writer_info_list[:200]
            comments = [x.text for x in comment_list[:200]]
            del comment_list[:200]
            shares = [x.text for x in share_list[:200]]
            del share_list[:200]

        else:
            questions = [x.text for x in question_list]
            del question_list
            writers = [x.text for x in writer_list]
            writer_infos = [x.text for x in writer_info_list]
            comments = [x.text for x in comment_list]
            shares = [x.text for x in share_list]
            del writer_list
            del writer_info_list
            del comment_list
            del share_list

        # answers = driver.find_elements(By.XPATH, f'//*[@id="mainContent"]/div/div/div[2]/div/div/div[1]/div/div/div/div[1]/span/span')
        # upvotes = driver.find_elements(By.XPATH, f'//*[@id="mainContent"]/div/div/div[2]/div/div/div[1]/div/div/div/div/div[1]/div[1]/div/div/div/button/div[2]')

        answers = []
        upvote_list = []
            
        for i in tqdm(range(len(questions)), desc="Scraping answers"):
            temp = 0
            while(True):
                temp += 1
                try:
                    try:
                        answer = driver.find_element(By.XPATH, f'//*[@id="mainContent"]/div/div/div[2]/div[{i+curr_increment}]/div/div[1]/div/div[2]/div/div[1]/span/span')
                        upvote = driver.find_element(By.XPATH, f'//*[@id="mainContent"]/div/div/div[2]/div[{i+curr_increment}]/div/div[1]/div/div[4]/div/div/div[1]/div[1]/div/div/div/button/div[2]')
                    except:
                        answer = driver.find_element(By.XPATH, f'//*[@id="mainContent"]/div/div/div[2]/div[{i+curr_increment}]/div/div[1]/div/div[3]/div/div[1]/span/span')
                        upvote = driver.find_element(By.XPATH, f'//*[@id="mainContent"]/div/div/div[2]/div[{i+curr_increment}]/div/div[1]/div/div[5]/div/div/div[1]/div[1]/div/div/div/button/div[2]')
                    answers.append(answer)
                    upvote_list.append(upvote)
                    break
                except:
                    curr_increment += 1
                    if temp > 10:
                        print(f"Program stuck at {i}th answer")
                        break
        curr_increment += len(questions)

        answer_texts = [x.text for x in answers]
        upvotes = [x.text for x in upvote_list]
        del answers

        min_len = min(len(questions),len(answer_texts),len(writers),len(writer_infos),len(upvotes),len(comments),len(shares))
        for i in tqdm(range(min_len), "Writing into csv"):
            curr_row = []   
            curr_row.append(questions[i])
            curr_row.append(answer_texts[i])
            curr_row.append(writers[i])
            curr_row.append(writer_infos[i])
            curr_row.append(upvotes[i])
            curr_row.append(comments[i])
            curr_row.append(shares[i])
            writer.writerow(curr_row)

        file.close()
    
    break
