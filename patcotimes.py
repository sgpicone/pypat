import sqlite3 as sql
from datetime import date
from datetime import timedelta
from datetime import datetime
import time



def openConnection():
    conn = sql.connect('patco.db')
    return conn

def getHelp():
    print "GetBestTimes(time, origin='248', dest='240', direction='E', express=False"

def getBestTimes(time, origin='248', destination='240', direction='E', day=None):
    conn = openConnection()
    cur = conn.cursor()
    serviceId = { 0: 2,
            1: 2,
            2: 2,
            3: 3,
            4: 4
        }.get(date.today().weekday() if day is None else day.weekday(), 2)
    
    if direction == 'W':
        headsign = 'PHILADELPHIA%'
    else:
        headsign = 'LINDENWOLD%'
    strtime = datetime.strptime(time,'%H:%M:%S')
    endtime = (strtime + timedelta(hours=1)).strftime('%H:%M:%S')
    query = """
    SELECT
        CASE WHEN (c.service_id = '4') then 'Friday'
            WHEN (c.service_id = '3') then 'Thursday'
            WHEN (c.service_id = '2') then 'Mon-Wed'
            WHEN (c.service_id = '1') then 'Sat-Sun'
        end as DAY,
        t.trip_headsign,
        orig.stop_name,
        origTime.departure_time,
        dest.stop_name,
        destTime.arrival_time,
        fas.price
    FROM stop_times origTime
        JOIN stop_times destTime ON origTime.trip_id = destTime.trip_id
        JOIN stops orig ON orig.stop_id = origTime.stop_id
        JOIN stops dest ON dest.stop_id = destTime.stop_id
        JOIN trips t ON t.trip_id = origTime.trip_id
        JOIN calendar c ON c.service_id = t.service_id
	JOIN fare_rules frs ON frs.origin_id = orig.stop_id 
	    AND frs.destination_id = dest.stop_id
        JOIN fare_attributes fas ON frs.fare_id = fas.fare_id
    WHERE
        t.service_id = '{servId}' AND
        destTime.stop_id = {dest} AND
        t.trip_headsign LIKE '{headsign}' AND
        origTime.arrival_time > '{starttime}' AND 
		origTime.arrival_time < '{endtime}' AND
        origTime.stop_id = '{origin}'"""
    mainQuery = query.format(
            servId=serviceId,
            dest=destination,
            headsign=headsign,
            starttime=time,
            endtime=endtime,
            origin=origin)
    res = cur.execute(mainQuery).fetchall()
    departQuery = None
    if res:
        firstArrival = datetime.strptime(res[0][5], '%H:%M:%S')
        optionalDepart = firstArrival + timedelta(hours=9, minutes=6)
        departQuery = query.format(
            servId=serviceId,
            dest=origin,
            headsign='PHILADELPHIA%' if direction=='E' else 'LINDENWOLD%',
            starttime=optionalDepart.strftime('%H:%M:%S'),
            endtime=(optionalDepart + timedelta(hours=1)).strftime('%H:%M:%S'),
            origin=destination)
        
    for row in res:
        for it in row:
            print it+"\t",
        print

    if departQuery is not None:
        res = cur.execute(departQuery).fetchall()
        for row in res:
            for it in row:
                print it+"\t",
            print
    return

def getDests():
    conn = openConnection()
    cur = conn.cursor()
    res = cur.execute("select stop_id, stop_name from stops;")
    for r in res.fetchall():
        for it in r:
            print it,
        print

def isCurrentSchedule():
    conn = openConnection()
    cur = conn.cursor()
    serviceId = { 0: 2,
            1: 2,
            2: 2,
            3: 3,
            4: 4
        }.get(date.today().weekday(), 2)
    query ="""select
        (date(start_date) < date('now') AND
        date(end_date) > date('now'))
        from calendar where service_id = {servId};""".format(servId=serviceId)
    res = cur.execute(query)
    return res.fetchone()[0]

def constantCheck():
    prevRes = []
    conn = openConnection()
    cur = conn.cursor()
    serviceId = { 0: 2,
            1: 2,
            2: 2,
            3: 3,
            4: 4
        }.get(date.today().weekday(), 2)
    leavetime = datetime.now() + timedelta(minutes=12)
    deptTime = datetime.strftime(leavetime, "%H:%M:%S")
    arrTime = leavetime + timedelta(hours=1)
    endTime = datetime.strftime(arrTime, "%H:%M:%S")
    
    query = """
    SELECT
        CASE WHEN (c.service_id = '4') then 'Friday'
            WHEN (c.service_id = '3') then 'Thursday'
            WHEN (c.service_id = '2') then 'Mon-Wed'
            WHEN (c.service_id = '1') then 'Sat-Sun'
        end as DAY,
        t.trip_headsign,
        orig.stop_name,
        origTime.departure_time,
        dest.stop_name,
        destTime.arrival_time,
        fas.price
    FROM stop_times origTime
        JOIN stop_times destTime ON origTime.trip_id = destTime.trip_id
        JOIN stops orig ON orig.stop_id = origTime.stop_id
        JOIN stops dest ON dest.stop_id = destTime.stop_id
        JOIN trips t ON t.trip_id = origTime.trip_id
        JOIN calendar c ON c.service_id = t.service_id
        JOIN fare_rules frs ON frs.origin_id = orig.stop_id 
            AND frs.destination_id = dest.stop_id
        JOIN fare_attributes fas ON frs.fare_id = fas.fare_id
    WHERE
        t.service_id = '{servId}' AND
        destTime.stop_id = {dest} AND
        t.trip_headsign LIKE '{headsign}' AND
        origTime.arrival_time > '{starttime}' AND 
                origTime.arrival_time < '{endtime}' AND
        origTime.stop_id = '{origin}'"""
    query = query.format(
            servId=serviceId,
            dest='240',
            headsign="LINDENWOLD%",
            starttime=deptTime,
            endtime=endTime,
            origin='248')
    res = cur.execute(query).fetchall()
    thisTrain = res[0]
    print "Next train: Dept: ",thisTrain[3], " Arr: ", thisTrain[5]
    while True:
        leavetime = datetime.now() + timedelta(minutes=12)
        if leavetime > datetime.combine(date.today(), datetime.strptime(thisTrain[3],"%H:%M:%S").time()):
            print "Missed the ", thisTrain[3], " train..."
            deptTime = datetime.strftime(leavetime, "%H:%M:%S")
            print deptTime
            arrTime = leavetime + timedelta(hours=1)
            print arrTime
            endTime = datetime.strftime(arrTime, "%H:%M:%S")
            print endTime
            query = query.format(
                servId=serviceId,
                dest='240',
                headsign="LINDENWOLD%",
                starttime=deptTime,
                endtime=endTime,
                origin='248')
            print query
            res = cur.execute(query).fetchall()
            thisTrain = res[0]
            print thisTrain
            print "Next train: Dept: ", thisTrain[3], " Arr: ", thisTrain[5]
    conn.close()

def run():
    if not True:
        print "This schedule is invalid! Update the database ASAP!"
        raw_input("Press any key...")
    else:    
        time = raw_input("What time do you plan to leave? (HH:MM:SS)\n")
        origin = raw_input("Your point of origin? (16L,12L,9L,8M,CH,BR,FA,CW,WM,HF,WC,AL,LW)\n").upper()
        dest = raw_input("Your destination? (16L,12L,9L,8M,CH,BR,FA,CW,WM,HF,WC,AL,LW)\n").upper()
        today = int(raw_input("Today? (1=Y,0=N)\n"))
        if not today:
            day = raw_input("What date? (YYYY-MM-DD)\n")
            day = datetime.strptime(day,'%Y-%M-%d')
        stops = {"16L":252,
                 "12L":251,
                 "9L":250,
                 "8M":249,
                 "CH":248,
                 "BR":247,
                 "FA":246,
                 "CW":245,
                 "WM":244,
                 "HF":243,
                 "WC":242,
                 "AL":241,
                 "LW":240
                }
        start = stops.get(origin,'248')
        stop = stops.get(dest,'240')
        heading = "W" if start-stop < 0 else "E"
        print "Getting best times for " + heading + " from " + origin + " to " + dest + " at " + time
        getBestTimes(time, start, stop, heading, day if not today else None)


