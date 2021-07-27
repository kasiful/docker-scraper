import sqlite3

# membuat fungsi catat progress
def progressBar(current, total, barLength = 20):
    percent = float(current) * 100 / total
    arrow   = '=' * int(percent/100 * barLength - 1) + '>'
    spaces  = ' ' * (barLength - len(arrow))

    print('Progress: [%s%s] %d %%' % (arrow, spaces, percent), end='\r')
    
# cek database

print("Update ports, mempersiapkan database")

sqliteConnection = sqlite3.connect('ais05.db')
sqlite_create_table_query = '''CREATE TABLE IF NOT EXISTS ports ( 
    id INTEGER PRIMARY KEY, 
    name VARCHAR(20), 
    type VARCHAR(20), 
    longitude REAL, 
    latitude REAL, 
    area_size VARCHAR(10),
    local_time VARCHAR(10),
    timezone VARCHAR(30),
    url TEXT
    );'''

cursor = sqliteConnection.cursor()
cursor.execute(sqlite_create_table_query)

sqliteConnection.commit()

cursor.close()

sqliteConnection.close()



print("Mempersiapkan Webdriver")

# persiapan webdriver
# https://www.google.com/travel/things-to-do

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
import numpy as np




print("Mempersiapkan Pickle (untuk simpan variabel sebagai antisipasi)")
import pickle

# membuka website
print("Membuka website")

chrome_options = webdriver.chrome.options.Options()
chrome_options.add_argument("--headless")

# driver = webdriver.Chrome("./chromedriver")
# driver.get("https://www.myshiptracking.com/ports&pp=50") # pp=50 artinya per page dimunculin 50 row

driver = webdriver.Chrome("./chromedriver", options = chrome_options)
driver.get("https://www.myshiptracking.com/ports&pp=50") # pp=50 artinya per page dimunculin 50 row





# ambil nilai pagination terakhirnya berapa
last_page = driver.find_element_by_xpath("//div[@class='table_footer']/div[@class='table_paging_results']/div[@class='paging_column_center center']/nav/ul/li[position()=last()-1]/a")
last_page = int(last_page.get_attribute("href").split("&page=")[1])





# lakukan perulangan untuk setiap page, lalu di cek yang mana punya Indonesia dari benderanya

dlist = []

# ini nanti perulangan page dari 1 sampai last_page
for page in range(1,last_page+1):

    driver.get("https://www.myshiptracking.com/ports&pp=50&page="+str(page))
    rows = driver.find_elements_by_xpath("//table[@class='table_main']/tbody/tr")   
    
    for row in rows:
        flag = row.find_element_by_tag_name("td").find_element_by_tag_name("img").get_attribute("src")
        if ("ID.png" in flag):
            url = row.find_elements_by_tag_name("td")[1].find_element_by_tag_name("a").get_attribute("href")
            dlist.append(url)
            
    progressBar(page, last_page)
                
print("\n")



# Saving the objects:
with open('list_port.pkl', 'wb') as f:  # Python 3: open(..., 'wb')
    pickle.dump(dlist, f)

dports = []


# ambil url yang pernah ada di database

print("cek port yang belum pernah dimasukan ke database sebelumnya")

sqliteConnection = sqlite3.connect('ais05.db')

cursor = sqliteConnection.cursor()

temp = cursor.execute('select url from ports')
temp = cursor.fetchall()

list_port_db = []
for t in temp:
    list_port_db.append((t[0]))

sqliteConnection.commit()
cursor.close()
sqliteConnection.close()

dlist = np.asarray(dlist[0:50])
list_port_db = np.asarray(list_port_db)


# lalu disisakan url yang belum pernah tercatat dan dicatat ke list_port

print("melakukan seleksi url yang belum pernah tercatat di database")

mask = np.in1d(dlist, list_port_db)
dlist = dlist[np.where(~mask)[0]]

print("terdapat",len(dlist),"yang belum tercatat di database")


dports = []

# saatnya mengumpulkan variabel yang dibutuhkan
# buka masing-masing link lalu simpan ke database

print("Mengambil informasi dari masing2 id pelabuhan")

i = 0
for url in dlist:

    driver.get(url)
    temp = driver.find_elements_by_xpath("//table[@class='vessels_table']/tbody/tr")

    getId        = int(url.split("indonesia-id-")[1])
    getName      = temp[0].find_elements_by_tag_name("td")[1].text
    getType      = temp[2].find_elements_by_tag_name("td")[1].text
    getLongitude = float(temp[4].find_elements_by_tag_name("td")[1].text[0:-1])
    getLatitude  = float(temp[5].find_elements_by_tag_name("td")[1].text[0:-1])
    getAreaSize  = temp[6].find_elements_by_tag_name("td")[1].text

    getLocalTime = temp[11].find_elements_by_tag_name("td")[1].text
    getLocalTime = getLocalTime.split("(")[1][0:-1]

    getTimeZone  = temp[12].find_elements_by_tag_name("td")[1].text

    dports.append((
    getId, getName, getType, getLongitude, getLatitude, getAreaSize, getLocalTime, getTimeZone, url
    ))
    
    progressBar(i, len(dlist)-1)
    i=i+1

print("\n")


# Simpan ke database (Paling penting)
print("Store ke database tabel ports")

sqliteConnection = sqlite3.connect('ais05.db')
cursor = sqliteConnection.cursor()

cursor.execute("BEGIN TRANSACTION;")
try:
#     cursor.execute("delete from ports")
#     cursor.execute("VACUUM")
    cursor.executemany("insert into ports(id, name, type, longitude, latitude, area_size, local_time, timezone, url) values (?,?,?,?,?,?,?,?,?)", dports)
    cursor.execute("commit")
    print("store ke database berhasil")
except sqliteConnection.Error as e:
    print("gagal! roolback database:", e)
    cursor.execute("rollback")
    
cursor.close()
sqliteConnection.close()

print("Update ports berhasil")