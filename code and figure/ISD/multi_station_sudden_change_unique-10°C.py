#Temperature data is measured in degrees Fahrenheit, 1°F=1.8°C+32 or 1°C=5/9(1°F-32)

import os
import sys
import csv
from collections import Counter
import pandas as pd
import multiprocessing
from datetime import datetime

#for s in range(0,len(station_csv)-1):
def count_sudden_T_change(stations):
    #index,station=stations
    station,index=stations
    print(station)
    sys.stdout.flush()

    station=station.replace('\t', '')
    station_file=station+".csv"
    T_change_threshold=-18
    obs_count=0
    mean_T_count=0
    max_T_count=0
    min_T_count=0
    DTR_T_count=0
    lat=0
    lon=0
    #file_count=0
    for year in range(1973, 1994):
        filePath = "/data1/zxy/sudden_temp_change/ISD-global-daily/unzip/"+str(year)


        if station_file in os.listdir(filePath):
            df = pd.read_csv(filePath+"/"+station_file)
            obs_count+=len(df)-1
            if len(df)-1>1:
                lat=df.iloc[1, 2]
                lon=df.iloc[1, 3]
            for i in range(2,len(df)):
                if df.iloc[i-1, 20]==9999.9 or df.iloc[i-1, 22]==9999.9 or df.iloc[i, 20]==9999.9 or df.iloc[i, 22]==9999.9:
                    continue

                mean_T_diff=df.iloc[i, 6] - df.iloc[i-1, 6]
                max_T_diff =df.iloc[i, 20] - df.iloc[i-1, 20]
                min_T_diff =df.iloc[i, 22] - df.iloc[i-1, 22]
                DTR_T_diff=(df.iloc[i, 20]-df.iloc[i, 22])-(df.iloc[i-1, 20]-df.iloc[i-1, 22])
    
                date_difference = datetime.strptime(df.iloc[i,1], "%Y-%m-%d").date()-datetime.strptime(df.iloc[i-1,1], "%Y-%m-%d").date()
    
                mean_T_count+=1 if mean_T_diff < T_change_threshold and date_difference.days ==1 else 0
                max_T_count +=1 if max_T_diff  < T_change_threshold and date_difference.days ==1 else 0
                min_T_count +=1 if min_T_diff  < T_change_threshold and date_difference.days ==1 else 0
                DTR_T_count +=1 if DTR_T_diff  < T_change_threshold and date_difference.days ==1 else 0
                

    #print(station_file)
    print(index)
    sys.stdout.flush()
    return[station,lat,lon,obs_count,mean_T_count,max_T_count,min_T_count,DTR_T_count]


if __name__ == "__main__":

    station_csv=pd.read_csv("/data1/zxy/sudden_temp_change/ISD-global-daily/station_unique_1973-1993.csv")
    #stations=station_csv.iloc[:, [0,2]].tolist()
    stations=station_csv.iloc[:, [0,2]].values.tolist()
    #year = list(range(1929,2024))

    #Number of processes
    num_processes=400
    pool = multiprocessing.Pool(processes=num_processes)

    #result=pool.map(count_sudden_T_change, enumerate(stations))
    result=pool.map(count_sudden_T_change, stations)

    pool.close()
    pool.join()

    current_directory = os.path.dirname(os.path.abspath(__file__))
    #csv
    csv_file = open(str(current_directory)+'/station_sudden_change_-10°C_after_1973-1993.csv', 'w', newline='', encoding='utf-8')
    header=['station','lat','lon','obs_count','mean_T_count','max_T_count','min_T_count','DTR_T_count']
    csv.writer(csv_file).writerow(header)
    csv.writer(csv_file).writerows(result)






    