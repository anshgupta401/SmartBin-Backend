


from fastapi import APIRouter, Depends, HTTPException, Query
from database import local_session
from sqlalchemy.orm import Session
import models
import crud,schemas
from datetime import datetime, timedelta
from typing import Optional
router = APIRouter()

def get_db():
    db = local_session()
    try:
        yield db
    finally:
        db.close()

@router.get("/get_bin_data")
def get_bin_info(db:Session = Depends(get_db)):
    data = db.query(models.Bin).all()
    total_bins = 0
    online_bins = 0
    offline_bins = 0
    bin_data = []
    current_time = datetime.now()
    for data in data:
        print(data.bin_id)
        print(data.distance)
        print(data.last_updated)
        print(data.lat)
        print(data.lon)
        print(data.temperature)
        total_bins = total_bins+1
        if current_time - data.last_updated <= timedelta(minutes=5):
            online_bins = online_bins+1
        else:
            offline_bins = offline_bins+1
        bin_data.append({
            "bin_id": data.bin_id,
            "fill_level": data.distance,
            "temperature": data.temperature,
            "lat": data.lat,
            "lon": data.lon,
            "last_updated": data.last_updated
        })
    return {
        "total_bins": total_bins,
        "online_bins": online_bins,
        "offline_bins": offline_bins,
        "bins": bin_data
    }
  
@router.get("/get_alerts")
def get_bin_alerts(db:Session = Depends(get_db)):
    data = db.query(models.Bin).filter(models.Bin.distance> 10).all()
    alerts_list = []
    for data in data:
        alerts_list.append(
            {
                "bin_id": data.bin_id,
                "location": f"Lat: {data.lat}, Lon: {data.lon}",
                "last_updated": data.last_updated
            }

        )
    return alerts_list

@router.get("/get_bins")
def fill_status(db:Session = Depends(get_db)):
    data = db.query(models.Bin).all()
    fill_list = []
    for data in data:
        fill_list.append(
            {
                "bin_id": data.bin_id,
                "status": "Full" if data.distance < 20 else "Empty" if data.distance >80 else "Half Full",
                "color": "red" if data.distance< 20 else "green" if data.distance >80 else "yellow",
                "location": f"Lat: {data.lat}, Lon: {data.lon}",
                "last_updated": data.last_updated
            }
        )
    return fill_list

@router.get("/api/reports")
def api_reports(from_date: Optional[str] = Query(None),
                to_date: Optional[str] = Query(None),
                time_range: Optional[str] = Query('7d'),
                location_filter: Optional[str] = Query('all'),
                bin_type_filter: Optional[str] = Query('all'),
                db: Session = Depends(get_db)):
    total_bins = 0
    avg_fill = 0
    full_bins = 0
    empty_bins = 0
    half_full = 0
    total_distance = 0
    data = db.query(models.Bin).all()
    bin_details = []
    locations = []
    for data in data:
        total_bins = total_bins+1
        total_distance = total_distance+data.distance
        if data.distance <20:
            full_bins = full_bins+1
        elif data.distance >80:
            empty_bins = empty_bins+1
        else:
            half_full = half_full +1
        bin_details.append(
            {
                "bin_id": data.bin_id,
                "location": f"{data.lat},{data.lon}",
                "type": "general",
                "current_fill": data.distance,
                "avg_daily_fill":"55.6",
                "peak_times": "10AM-2PM",
                "last_updated": data.last_updated
            }
        )
        locations.append([data.lat,data.lon])
    avg_fill = total_distance/total_bins
    if not from_date or not to_date:
        now = datetime.utcnow()
        end_date = now.strftime("%Y-%m-%d")
        if time_range == "7d":
            start_date = (now-timedelta(days=7)).strftime('%Y-%m-%d')
        elif time_range == "30d":
            start_date = (now-timedelta(days=30)).strftime('%Y-%m-%d')
        elif time_range == "90d":
            start_date = (now-timedelta(days=90)).strftime('%Y-%m-%d')
    history_data = db.query(models.BinHistory).filter(models.BinHistory.timestamp.between(start_date,end_date)).all()
    empty_dictionary = {}
    test_distance = 0
    trend_labels = []
    for i in history_data:
        date = i.timestamp.date()
        if date not in empty_dictionary:
            empty_dictionary[date] = {"total_fill":0,"total_temp":0,"count":0}
            trend_labels.append(date)
        empty_dictionary[date]["total_fill"] += i.distance
        empty_dictionary[date]["total_temp"] += i.temperature
        empty_dictionary[date]["count"] +=1
    avg_fill_level = []
    avg_temp_level = []
    for i in trend_labels:
        avg_fill = empty_dictionary[date]["total_fill"]/empty_dictionary[date]["count"]
        avg_fill_level.append(avg_fill)
        avg_temp = empty_dictionary[date]["total_temp"]/empty_dictionary[date]["count"]
        avg_temp_level.append(avg_temp)
 


    return {
        "total_bins": total_bins,
        "avg_fill": avg_fill,
        "full_bins": full_bins,
        "empty_bins": empty_bins,
        "moderate_bins": half_full,
        "trend_labels": trend_labels,
        "avg_fill_levels": avg_fill_level,
        "avg_temperature": avg_temp_level,
        "locations": locations,
        "location_fill_levels": "62.5",
        "location_bin_counts": 2,
        "bin_details": bin_details,
        "optimal_collections": [10, 12, 15, 10, 8, 5, 7],
        "actual_collections": [8, 10, 12, 9, 7, 4, 6],
        "fill_trend": 2.5

    }


@router.get("/test/date")
def data_by_date(db:Session = Depends(get_db)):
    empty_dictionary = {}
    current_date = 0
    empty_list = []
    data = db.query(models.BinHistory).all()
    for i in data:
        if not i.timestamp.date() == current_date:
            print("Date has changed")
            print(i.timestamp)
            empty_dictionary[i.timestamp.date()] = {"id":0,"bin_id":0,"temperature": 0}
        if i.timestamp.date() == current_date:
            empty_list.append({"id":i.id,"bin_id":i.bin_id, "temperature":i.temperature})
            empty_dictionary[i.timestamp.date()] = empty_list

        current_date = i.timestamp.date()

  
    data = empty_dictionary.values()
    count_dict = {}
    temp_count = {}
    print(empty_dictionary)

    for i in data:
        for j in i:
            if type(j) == str:
                print("Data is Str")
            else:
                if j["bin_id"] not in count_dict:
                    count_dict[j["bin_id"]] = 0
                count_dict[j["bin_id"]] +=1
                if j["bin_id"] not in temp_count:
                    temp_count[j["bin_id"]] = 0
                temp_count[j["bin_id"]] += j['temperature']
    print(count_dict)
    print(temp_count)
    # second_dict = {}
    average = {}
    second_dict = sorted(count_dict.keys())

    for i in second_dict:
        average[i] = temp_count[i]/count_dict[i]
    print(average)
    # print(second_dict)        
 


@router.get("/fill/level")
def data_by_fill_level(db:Session = Depends(get_db)):
    empty_dictionary = {}
    data = db.query(models.BinHistory).all()
    for i in data:
        if i.bin_id not in empty_dictionary:
            empty_dictionary[i.bin_id] = {"total_fill_level":0,"count":0,"time_stamp": 0}
        empty_dictionary[i.bin_id]["count"] += 1
        empty_dictionary[i.bin_id]["total_fill_level"] += i.distance
        if empty_dictionary[i.bin_id]["time_stamp"] not in empty_dictionary:
            empty_dictionary[i.bin_id]["time_stamp"] = i.timestamp.date()



    print(empty_dictionary)

    average = {}
    empty_list = []
    for i in empty_dictionary:
        print(empty_dictionary[i]["time_stamp"])
        if empty_dictionary[i]["time_stamp"] not in average:
            empty_list.append({"bin_id":i,"count":empty_dictionary[i]["count"],"total_fill_level":empty_dictionary[i]["total_fill_level"]})
            average[empty_dictionary[i]["time_stamp"]] = empty_list


    print(average)

# { 10-7-2025 : { "bin_id":101,"count":10 ,"total_fill_level":2000,}}


# { 10-7-2025 : [{ "bin_id":101,"count":10 ,"total_fill_level":2000},{ "bin_id":105"count":40 ,"total_fill_level":2000},{ "bin_id":102,"count":30 ,"total_fill_level":43000}]}



@router.get("/fill/levels")
def data_by_fill_levels(db:Session = Depends(get_db)):
    empty_dictionary = {}
    second_dictionary = {}
    empty_list = []
    data = db.query(models.BinHistory).all()
    for i in data:
        # if empty_dictionary[i.timestamp] not in empty_dictionary:
            # empty_dictionary[i.timestamp] = {}
        if i.bin_id not in second_dictionary:
            second_dictionary = {"total_fill_level":0, "count":0, "bin_id":0}
        second_dictionary["total_fill_level"] += i.distance
        second_dictionary["bin_id"] = i.bin_id
        second_dictionary["count"] +=1
    print(second_dictionary)






# just query the last 20 records

# What’s the total number of bins?

# Which bin is currently full?
#full bin is when distance is greater than 80

# Which bin hasn’t updated in > 5 minutes?

# Which location has the highest average fill?


@router.get("/practice/api")
def practice_function(db:Session = Depends(get_db)):
    total_bins = 0
    empty_list = []
    second_list = []
    third_list = []
    empty_dictionary = {}
    second_dictionary = {"lat":0,"lon":0}
    avg_fill = 0
    highest_average = 0
    current_time = datetime.now()
    data = db.query(models.BinHistory).limit(20)
    for i in data:
        if i.bin_id not in empty_list:
            empty_list.append(i.bin_id)
        if i.distance >80 and i.bin_id not in second_list:
            second_list.append(i.bin_id)
        if current_time - i.timestamp >= timedelta(minutes=5) and i.bin_id not in third_list:
            third_list.append(i.bin_id)
        if i.bin_id not in empty_dictionary:
            empty_dictionary[i.bin_id] = {"total_fill":0,"count":0,"lat":0,"lon":0}
        empty_dictionary[i.bin_id]["total_fill"] += i.distance
        empty_dictionary[i.bin_id]["count"] += 1
        empty_dictionary[i.bin_id]["lat"] = i.lat
        empty_dictionary[i.bin_id]["lon"] = i.lon
    for i in empty_dictionary:
        avg_fill = empty_dictionary[i]["total_fill"]/empty_dictionary[i]["count"]
        if avg_fill > highest_average:
            second_dictionary["lat"] = empty_dictionary[i]["lat"]
            second_dictionary["lon"] = empty_dictionary[i]["lon"]
            highest_average = avg_fill



    print(empty_list)
    print(second_list)
    print(third_list)
    print(empty_dictionary)
    print(second_dictionary)

#take timestamp input from user, retrieve the records 
#based on the timestamp retrive records and information user requires 
#store it in a csv file
import csv

@router.get("/retrieve/data")
def user_input_data(from_date: Optional[str] = Query(None),
                to_date: Optional[str] = Query(None),
                bin_id: Optional[bool] = Query(None),
                distance: Optional[bool] = Query(None),
                temperature: Optional[bool] = Query(None),
                db: Session = Depends(get_db)):
  
    second_list = []
    data = db.query(models.BinHistory).filter(models.BinHistory.timestamp.between(from_date,to_date)).all()
    for i in data:
        empty_list = [str(i.bin_id) if bin_id == True else None,str(i.distance) if distance == True else None,str(i.temperature) if temperature == True else None]
        print(" ".join(i for i in empty_list if i))
        second_list.append(empty_list)       
    with open("data.csv","w") as w:
        writer = csv.writer(w)
        writer.writerow(['Bin_Id', 'Distance', 'Temperature'])
        writer.writerows(second_list)