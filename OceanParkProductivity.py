"""
Note that Google Sheet has cell limits
"""

from bluepy.btle import Scanner, DefaultDelegate
import datetime
import csv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# Variables
with open("/home/pi/Documents/Python/OceanParkProductivity/beaconReg.csv", "r") as fBeacon:  # Import registered beacons
    beaconListFull = list(csv.reader(fBeacon))
    beaconAddr = [item[1] for item in beaconListFull]

with open("/home/pi/Documents/Python/OceanParkProductivity/beaconThres.txt", "r") as fThres:
    beaconThres = int(fThres.readline())

with open("/home/pi/Documents/Python/OceanParkProductivity/scannerId.txt", "r") as fScanner:
    scannerId = fScanner.readline()


# gspread access spreadsheet
scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name('/home/pi/Documents/Python/OceanParkProductivity/drive_client_secret.json', scope)
gc = gspread.authorize(credentials)
googlesheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1RvO3S0LzEts_X72-xVm2_SvPcJBnQUsdhH1YoKSimNo").sheet1


# BLE Scan
class ScanDelegate(DefaultDelegate):
    """BLE Scan"""
    def __init__(self):
        DefaultDelegate.__init__(self)


# Check device proximity
while True:
    time = datetime.datetime.now()
    try:
        scanner = Scanner().withDelegate(ScanDelegate())
        devices = scanner.scan(10)  # Scans for n seconds, note that the Minew beacons broadcasts every 2 seconds
    except Exception:
        os.system("sudo reboot")
    scanSummary = []
    for dev in devices:
        if (dev.addr in beaconAddr) and (dev.rssi > beaconThres):
            scanAddr = list(item[0] for item in scanSummary)
            if dev.addr not in [item[0] for item in scanSummary]:
                scanSummary.append([dev.addr, dev.rssi])
            else:
                rownum = scanAddr.index(dev.addr)
                if dev.rssi > scanSummary[rownum][1]:
                    scanSummary[rownum][1] = dev.rssi
    if len(scanSummary) > 0:
        for eachRow in scanSummary:
            with open("/home/pi/Documents/Python/OceanParkProductivity/scanLog_oceanpark.csv", "a") as fscanlog:
                fscanlog.write("{},{},{},{}\n".format(scannerId,str(time),eachRow[0],eachRow[1]))
            try:
                gc.login()
                googlesheet.append_row([scannerId, str(time), eachRow[0], eachRow[1]])
            except Exception:
                os.system("sudo reboot")


