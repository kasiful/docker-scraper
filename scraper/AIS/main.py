import os
from time import sleep
from datetime import date
from datetime import datetime
from datetime import timedelta
# wd = os.path.abspath(os.getcwd())

import numpy as np

from selenium import webdriver
from selenium.webdriver.common.keys import Keys



def comtrade(date_from, date_to):
    
    url = "https://comtrade.un.org/data/ais"

    ###### FORM ISIAN ######

    # isian reporter, ketik nama negara (bisa isi lebih dari satu, default = World)
    reporter = ["Indonesia"]

    # isian vessel type, 
    # All, Bulk, Container_gcargo, Foodstuff, LPG/LNG, Oil/chemicals, Total, Vehicles 
    # (bisa isi lebih dari satu, default = Total)
    vessel = ["All"]

    # isian flows, 
    # All, Exports, Imports
    # (bisa isi lebih dari satu, default = All)
    flows = ["All"]

    print("Scraping mulai tgl",str(date_from),"sampai",str(date_to))

    # from selenium.webdriver.chrome.options import Options
    # options = Options()
    # options.binary_location = wd + "/chromeDriver/GoogleChromePortable/App/Chrome-bin/chrome.exe"

    # driver = webdriver.Chrome(wd+"/chromeDriver/chromedriver.exe", options=options)
    # driver.close()

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('window-size=1200x600')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)

    driver.get(url)
    while True:
        elem = driver.find_element_by_id("wrap").find_element_by_class_name("ct-form")
        temp = elem.find_elements_by_xpath("//li[@class='select2-search-choice']/a")
        if len(temp) == 3:
            break

    for t in temp:
        t.click()
        sleep(0.1)



    ####### REPORTER #######

    # dapatkan elemen reporters
    elem_reporters = elem.find_elements_by_class_name("row")[1].find_elements_by_class_name("col-md-3")[0].find_element_by_class_name("select2-choices")

    # isian reporter ganti dengan isian yang sudah ditentukan
    elem_reporters.click()
    for rep in reporter:
        elem_reporters.find_element_by_class_name("select2-search-field").find_element_by_tag_name("input").send_keys(rep)
        elem_reporters.find_element_by_class_name("select2-search-field").find_element_by_tag_name("input").send_keys(Keys.ENTER)
        sleep(0.1)

    ####### VESSEL TYPE #######

    # dapatkan elemen reporters
    elem_vessel = elem.find_elements_by_class_name("row")[1].find_elements_by_class_name("col-md-3")[1].find_element_by_class_name("select2-choices")

    # isian reporter ganti dengan isian yang sudah ditentukan
    elem_vessel.click()
    for rep in vessel:
        elem_vessel.find_element_by_class_name("select2-search-field").find_element_by_tag_name("input").send_keys(rep)
        elem_vessel.find_element_by_class_name("select2-search-field").find_element_by_tag_name("input").send_keys(Keys.ENTER)
        sleep(0.1)

    ####### FLOWS ########

    # dapatkan elemen reporters
    elem_flows = elem.find_elements_by_class_name("row")[1].find_elements_by_class_name("col-md-3")[2].find_element_by_class_name("select2-choices")

    # isian reporter ganti dengan isian yang sudah ditentukan
    elem_flows.click()
    for rep in flows:
        elem_flows.find_element_by_class_name("select2-search-field").find_element_by_tag_name("input").send_keys(rep)
        elem_flows.find_element_by_class_name("select2-search-field").find_element_by_tag_name("input").send_keys(Keys.ENTER)
        sleep(0.1)

    ###### DATE ######
    # dapatkan elemen reporters
    elem_date = elem.find_elements_by_class_name("row")[1].find_elements_by_class_name("col-md-3")[3]
    elem_date.find_element_by_id("dateFrom").clear()
    elem_date.find_element_by_id("dateFrom").send_keys(date_from)
    sleep(0.1)

    elem_date.find_element_by_id("dateTo").clear()
    elem_date.find_element_by_id("dateTo").send_keys(date_to)
    sleep(0.1)

    elem.click()



    # ###### PREVIEW DATA ######
    elem.find_element_by_id("preview").click()

    # pastikan loadingnya selesai
    while True:
        sleep(1)
        temp = driver.find_element_by_id("ct-waiting")
        if (temp.get_attribute("style") == "display: none;"):
            print("load data selesai")
            break



    ###### CONNECT KE DATABASE ######
    import sqlite3

    sqliteConnection = sqlite3.connect('/home/scraper/AIS/ais03.db')
    sqlite_create_table_query = '''CREATE TABLE IF NOT EXISTS aistrade ( 
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        vessel_type VARCHAR(20), 
        flow VARCHAR(10), 
        dates date, 
        num_pc REAL, 
        mtc REAL, 
        dwt REAL, 
        num_pc_ma REAL, 
        mtc_ma REAL, 
        dwt_ma REAL );'''

    cursor = sqliteConnection.cursor()
    cursor.execute(sqlite_create_table_query)

    sqliteConnection.commit()

    cursor.close()

    sqliteConnection.close()










    ###### MEMBACA ISI TABEL ######
    # algoritma: 
    # pilih dulu tab tabel
    # cari dulu tabny ada berapa banyak
    # lalu balik ke first
    # perulangan klik next sebanyak (jumlah tab)-1

    # 1. pilih tab tabel
    table_container = driver.find_element_by_id("preview-table-container")

    # 2. cari jumlah tab
    table_container.find_element_by_id("preview-table_last").click()
    tag_a = table_container.find_element_by_id("preview-table_paginate").find_element_by_tag_name("span").find_elements_by_tag_name("a")

    if len(tag_a) == 0: # jumlah tab 0 atau tidak ada row data
        print("data belum tersedia")
        print("###################################\n\n")
        driver.close()


    else:

        jumlah_tab = int(tag_a[-1].text)

        # 3. balik ke first tab
        table_container.find_element_by_id("preview-table_first").click()

        dlist = []
        tanggal = []

        # 4. perulangan baca tab
        for tab in range(0, jumlah_tab):
        # 5. membaca tiap baris dari setiap tab, lalu colom dari setiap baris
            table_rows = table_container.find_element_by_id("preview-table").find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")
            for row in table_rows:
                temp = []
                cols = row.find_elements_by_tag_name("td")
                for col in cols:
                    temp.append(col.text)
                # utk tanggal diambil tanggalnya saja
                temp[3] = temp[3].split("T")[0]

                # hapus array awal karena negaranya pasti Indonesia
                temp.pop(0)

                temp = (temp[0], temp[1], temp[2], temp[3], temp[4], temp[5], temp[6], temp[7], temp[8])

                dlist.append((temp))

                tanggal.append(temp[2])

                # masukkan ke database
        #         sql = '''
        #         INSERT INTO aistrade
        #         (vessel_type, flow, dates, num_pc, mtc, dwt, num_pc_ma, mtc_ma, dwt_ma)
        #         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        #         cursor.execute(sql, temp)
        #         sqliteConnection.commit()

            table_container.find_element_by_id("preview-table_next").click()

        driver.close()

        # Update isi
        print("Update isian yang ada di database")

        sqliteConnection = sqlite3.connect('/home/scraper/AIS/ais03.db')
        cursor = sqliteConnection.cursor()

        cursor.execute("BEGIN TRANSACTION;")
        try:
        #     cursor.execute("delete from ports")
        #     cursor.execute("VACUUM")

            cursor.execute("DELETE FROM aistrade WHERE  dates>='"+min(tanggal)+"' AND dates<='"+max(tanggal)+"';")

            cursor.executemany('''INSERT INTO aistrade
                (vessel_type, flow, dates, num_pc, mtc, dwt, num_pc_ma, mtc_ma, dwt_ma)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', dlist)
            cursor.execute("commit")
            print("store ke database berhasil")

        except sqliteConnection.Error as e:
            print("gagal! roolback database:", e)
            cursor.execute("rollback")

        cursor.close()
        sqliteConnection.close()

        print("Update ports berhasil")
        print("###################################\n\n")
        
        
        
        
        
        
        
        
        
###### CONNECT KE DATABASE DAN CEK TANGGAL TERAKHIR ######

last_date = ""

import sqlite3

sqliteConnection = sqlite3.connect('/home/scraper/AIS/ais03.db')
cursor = sqliteConnection.cursor()

try:

    cursor.execute("SELECT dates FROM aistrade order by dates DESC limit 1")

    rows = cursor.fetchone()
    
    last_date = rows[0]
    
    print("data terakhir tanggal", last_date)

except sqliteConnection.Error as e:
    print("gagal baca database", e)

cursor.close()
sqliteConnection.close()


date_first = datetime.strptime(last_date, "%Y-%m-%d") 
date_last  = datetime.today()
n_days = abs((date_last - date_first).days)


loop = np.arange(0,n_days,7).tolist()

loop.append(n_days)




for iterasi in range(0, len(loop)-1):
    date_from = date_first + timedelta(loop[iterasi]+1)
    date_to   = date_first + timedelta(loop[iterasi+1])
    comtrade(date_from.strftime("%Y-%m-%d"), date_to.strftime("%Y-%m-%d"))
