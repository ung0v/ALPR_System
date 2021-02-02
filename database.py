import datetime
import pyodbc
import time
import os
server = 'DESKTOP-RM7E647\SQLEXPRESS' 
database = 'nhandien' 
username = 'sa' 
password = '1' 
cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
def insertDB(img1, img2, plate):
    # Some other example server values are
    # server = 'localhost\sqlexpress' # for a named instance
    # server = 'myserver,port' # to specify an alternate port
    date = datetime.date.today()
    cursor = cnxn.cursor()
    cursor.execute("""
    INSERT INTO bienso(Image, Image2, LicensePlate, CreatedDate) 
    VALUES ('%s', '%s', '%s', '%s')""" %(img1, img2, plate, date)) 
    cnxn.commit()

# insertDB('img1', 'img2', 'plate')
def getPlate():
    cursor = cnxn.cursor()
    cursor.execute("SELECT * FROM bienso order by ID desc")
    rows = cursor.fetchall()
    dataPlate = []
    for row in rows:
        data = []
        image = row[1].split("|")
        data.append(row[0])
        data.append(image[len(image) - 1])
        data.append(row[3])
        data.append(row[4].strftime("%m/%d/%Y %H:%M:%S"))
        dataPlate.append(data)
    return dataPlate[10]
print(getPlate())
directory = "Regcognized_Plates"
if not os.path.exists(directory):
    os.makedirs(directory)