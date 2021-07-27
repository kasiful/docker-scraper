import sqlite3

from datetime import datetime
from datetime import date
from datetime import timedelta

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import numpy as np
import pickle



def progressBar(current, total, barLength = 20):
    percent = float(current) * 100 / total
    arrow   = '=' * int(percent/100 * barLength - 1) + '>'
    spaces  = ' ' * (barLength - len(arrow))

    print('Progress: [%s%s] %d %%' % (arrow, spaces, percent), end='\r')
   




print("Mempersiapkan database")
sqliteConnection = sqlite3.connect('ais05.db')
sqlite_create_table_query = '''CREATE TABLE IF NOT EXISTS portCalls ( 
    event VARCHAR(20), 
    port_time VARCHAR(16), 
    port_id INT, 
    port_name VARCHAR(30), 
    vessel_name VARCHAR(30),
    vessel_mmsi VARCHAR(20),
    vessel_imo VARCHAR(20),
    vessel_url TEXT
    );'''

cursor = sqliteConnection.cursor()
cursor.execute(sqlite_create_table_query)

sqliteConnection.commit()
cursor.close()
sqliteConnection.close()


####### Menyusun tanggal untuk kemarin ###########

today = date.today()
today = datetime(today.year, today.month, today.day)

yesterday  = today - timedelta(1)
yesterday1 = today - timedelta(seconds=1)

currentDate = str(yesterday.timestamp())+"_"+str(yesterday1.timestamp())

print("tanggal",yesterday,"-",yesterday1)

currentDate = currentDate.replace(".0", "")

currentDate = "1621443600_1622221140"
currentUrl = "https://www.myshiptracking.com/ports-arrivals-departures/?pid=ID&type=0&pp=50&time="+currentDate

# currentUrl = "https://www.myshiptracking.com/ports-arrivals-departures/?pid=ID&type=0&pp=50&time=1619888400_1620061140"

######### Membuka Browser ###########

chrome_options = webdriver.chrome.options.Options()
chrome_options.add_argument("--headless")

print("membuka browser")
driver = webdriver.Chrome("./chromedriver", options = chrome_options)
driver.get(currentUrl)
driver.get(currentUrl)


######### Mengumpulkan Informasi ###########

last_page = int(driver.find_element_by_xpath("//div[@class='paging_column_center center']//li[position()=last()-1]").text)
nrecord = int(driver.find_element_by_xpath("//div[@class='paging_column_left left']//b").text)


dportCalls = []
list_vessel = []

print("terdapat",nrecord,"record")

i = 0
for page in range(1, last_page+1):
    
    driver.get(currentUrl + "&page=" + str(page))
    rows = driver.find_elements_by_class_name("table-row")
    
    for row in rows:
        
        progressBar(i, nrecord)
        
        col = row.find_elements_by_class_name("col")
        
        getEvent = col[1].text
        getTime = col[2].text
        getPort = col[3].text

        getPortId = col[3].find_element_by_tag_name("a").get_attribute("href")
        getPortId = int(getPortId.split("indonesia-id-")[1])

        getVessel = col[4].text

        getVesselMMSI = col[4].find_element_by_tag_name("a").get_attribute("href")
        getVesselMMSI = getVesselMMSI.split("-mmsi-")[1]
        
        temp = getVesselMMSI.split("-imo-")
        if temp[1] == "0":
            temp[1] = ""

        getVesselMMSI = temp[0]
        getVesselIMO = temp[1]
        
        getVesselUrl = col[4].find_element_by_tag_name("a").get_attribute("href")
        
        dportCalls.append((getEvent, getTime, getPort, getPortId, getVessel, getVesselMMSI, getVesselIMO, getVesselUrl))
        
        list_vessel.append(getVesselUrl)
    
        i=i+1
        progressBar(i, nrecord)
        
print("\n")


######### Url kapal banyak yg double, dibikin unique dulu ###########

list_vessel = np.asarray(list_vessel)
list_vessel = np.unique(list_vessel)


######### simpan variabel pakai pickle (untuk jaga2) ###########

print("simpan variabel pakai pickle (untuk jaga2)")

with open('list_vessel.pkl', 'wb') as f:  # Python 3: open(..., 'wb')
    pickle.dump(list_vessel, f)
    
with open('data_port_calls.pkl', 'wb') as f:  # Python 3: open(..., 'wb')
    pickle.dump(dportCalls, f)
    
    
########## Simpan ke database (portCalls) #############

print("simpan record portCalls ke database")

print("Store ke database tabel portCalls")

sqliteConnection = sqlite3.connect('ais05.db')
cursor = sqliteConnection.cursor()

cursor.execute("BEGIN TRANSACTION;")
try:
    cursor.executemany("INSERT INTO portCalls (event, port_time, port_name, port_id, vessel_name, vessel_mmsi, vessel_imo, vessel_url) VALUES (?,?,?,?,?,?,?,?)", dportCalls)
    cursor.execute("commit")
    print("store ke database berhasil")
except sqliteConnection.Error:
    print("gagal! roolback database")
    cursor.execute("rollback")
    
cursor.close()
sqliteConnection.close()


########### cek tabel vessels #############

print("cek tabel vessels")

sqliteConnection = sqlite3.connect('ais05.db')
sqlite_create_table_query = '''CREATE TABLE IF NOT EXISTS vessels ( 
    name VARCHAR(30), 
    flag VARCHAR(20), 
    mmsi VARCHAR(20), 
    imo VARCHAR(20), 
    call_sign VARCHAR(20),
    type VARCHAR(50),
    size VARCHAR(20),
    speed_avg_max VARCHAR(30),
    draught_avg VARCHAR(30),
    grt_ton INT,
    dwt_ton INT,
    owner VARCHAR(20),
    build_year INT,
    url TEXT
    );'''

cursor = sqliteConnection.cursor()
cursor.execute(sqlite_create_table_query)

sqliteConnection.commit()
cursor.close()
sqliteConnection.close()



######### ambil url yang pernah ada di database ###########

print("cek kapal yang belum pernah dimasukan ke database sebelumnya")

sqliteConnection = sqlite3.connect('ais05.db')

cursor = sqliteConnection.cursor()

temp = cursor.execute('select url from vessels')
temp = cursor.fetchall()

list_vessel_db = []
for t in temp:
    list_vessel_db.append((t[0]))

sqliteConnection.commit()
cursor.close()
sqliteConnection.close()


########### lalu disisakan url yang belum pernah tercatat dan dicatat ke list_vessel ###########

mask = np.in1d(list_vessel, list_vessel_db)
list_vessel = list_vessel[np.where(~mask)[0]]

print("terdapat",len(list_vessel),"yang belum tercatat di database")


############ print("mencari informasi kapal") ####################

print("mencari informasi kapal")

dvessel = []

i = 0
for lv in list_vessel:

    progressBar(i, len(list_vessel))
    
    driver.get(lv)
    vesselInfo = driver.find_elements_by_xpath("//table[@class='vessels_table']//tr//td[position()=last()]")
    dvessel.append((
        vesselInfo[0].text,
        vesselInfo[1].text,
        vesselInfo[2].text if vesselInfo[2].text != '---' else '',
        vesselInfo[3].text if vesselInfo[3].text != '---' else '',
        vesselInfo[4].text if vesselInfo[4].text != '---' else '',
        vesselInfo[5].text if vesselInfo[5].text != '---' else '',
        vesselInfo[6].text if vesselInfo[6].text != '---' else '',
        vesselInfo[7].text if vesselInfo[7].text != '---' else '',
        vesselInfo[8].text if vesselInfo[8].text != '---' else '',
        vesselInfo[9].text if vesselInfo[9].text != '---' else '',
        vesselInfo[10].text if vesselInfo[10].text != '---' else '',
        vesselInfo[11].text if vesselInfo[11].text != '---' else '',
        vesselInfo[12].text if vesselInfo[12].text != '---' else '',
        lv
    ))
    
    i=i+1
    progressBar(i, len(list_vessel))
   

######### Simpan ke database (vessels) ###########

print("Store ke database tabel vessels")

sqliteConnection = sqlite3.connect('ais05.db')
cursor = sqliteConnection.cursor()

cursor.execute("BEGIN TRANSACTION;")
try:
    cursor.executemany('''
    INSERT INTO vessels (
    name, flag, mmsi, imo, call_sign, 
    type, size, speed_avg_max, draught_avg, 
    grt_ton, dwt_ton, owner, build_year, url
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', dvessel)
    cursor.execute("commit")
    print("store ke database berhasil")
except sqliteConnection.Error:
    print("gagal! roolback database")
    cursor.execute("rollback")
    
cursor.close()
sqliteConnection.close()