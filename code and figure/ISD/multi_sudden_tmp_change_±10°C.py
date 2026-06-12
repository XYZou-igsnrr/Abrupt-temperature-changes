#Temperature data is measured in degrees Fahrenheit, 1°F=1.8°C+32 or 1°C=5/9(1°F-32)

import os
import sys
import csv
import pandas as pd
import multiprocessing
from datetime import datetime

#df = pd.read_csv("/data1/zxy/sudden_temp_change/ISD-global-daily/unzip/2023/01001099999.csv")
#filePath ="/data1/zxy/sudden_temp_change/ISD-global-daily/unzip/2022/"
#print(df.iloc[0:3,list(range(7)) + [20, 22]])

#for year in range(1929, 2023):
T_change_threshold=10*1.8

def count_sudden_T_change(year):
    filePath = "/data1/zxy/sudden_temp_change/ISD-global-daily/unzip/"+str(year)

    obs_count=0
    ATCc_count=0
    ATCw_count=0
   
    obs_count_Southern=0
    ATCw_Southern=0
    ATCc_Southern=0
    
    obs_count_Northern=0
    ATCw_Northern=0
    ATCc_Northern=0
    for station_file in os.listdir(filePath):
        df = pd.read_csv(filePath+"/"+station_file)
        if len(df) > 200 and df.iloc[-1, 2]>-60:
            #print(df.iloc[-1, 2])
            #file_count+=1
            #print(file_count)
            for i in range(2,len(df)):
                if df.iloc[i-1, 20]==9999.9 or df.iloc[i-1, 22]==9999.9 or df.iloc[i, 20]==9999.9 or df.iloc[i, 22]==9999.9:
                    continue
                
                obs_count+=1
                mean_T_diff=df.iloc[i, 6] - df.iloc[i-1, 6]

                date_difference = datetime.strptime(df.iloc[i,1], "%Y-%m-%d").date()-datetime.strptime(df.iloc[i-1,1], "%Y-%m-%d").date()

                ATCc_count+=1 if mean_T_diff < (-T_change_threshold) and date_difference.days ==1 else 0
                ATCw_count+=1 if mean_T_diff > T_change_threshold and date_difference.days ==1 else 0

                
                #South_0-60E    
                if  -60 <= df.iloc[i, 2] < 0:              
                    obs_count_Southern+=1
                    ATCw_Southern+=1 if mean_T_diff > T_change_threshold and date_difference.days ==1 else 0 
                    ATCc_Southern+=1 if mean_T_diff < (-T_change_threshold) and date_difference.days ==1 else 0 
                #Northern
                elif df.iloc[i, 2] > 0:
                    obs_count_Northern+=1
                    ATCw_Northern+=1 if mean_T_diff > T_change_threshold and date_difference.days ==1 else 0 
                    ATCc_Northern+=1 if mean_T_diff < (-T_change_threshold) and date_difference.days ==1 else 0 
             

        #filename, extension = os.path.splitext(station_file)
        #stations.append(filename)
    print(year)
    sys.stdout.flush()
    return [year,obs_count,ATCw_count,ATCc_count,obs_count_Northern,ATCw_Northern,ATCc_Northern,obs_count_Southern,ATCw_Southern,ATCc_Southern]
    #csv.writer(csv_file).writerow([year,obs_count,mean_T_count,max_T_count,min_T_count])

if __name__ == "__main__":

    year = list(range(1973,2024))

    #Number of processes
    num_processes=10
    pool = multiprocessing.Pool(processes=num_processes)

    result=pool.map(count_sudden_T_change, year)

    pool.close()
    pool.join()

    current_directory = os.path.dirname(os.path.abspath(__file__))
    #csv
    csv_file = open(str(current_directory)+'/multi_sudden_tmp_change_±'+str(int(T_change_threshold/1.8))+'°C.csv', 'w', newline='', encoding='utf-8')
    header=['year','obs_count','ATCw_count','ATCc_count','obs_count_Northern','ATCw_Northern','ATCc_Northern','obs_count_Southern','ATCw_Southern','ATCc_Southern',]
    csv.writer(csv_file).writerow(header)
    csv.writer(csv_file).writerows(result)



