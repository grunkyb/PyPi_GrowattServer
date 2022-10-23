import numpy as np
import growattServer
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

date = datetime.strptime('2022-10-22', '%Y-%m-%d')

api = growattServer.GrowattApi()
login_response = api.login('USERNAME_EMAIL',
                           'PASSWORD')
# print(login_response)
if login_response['success']:
    # Get a list of growatt plants.
    plant_list = api.plant_list(login_response['user']['id'])
    plant = plant_list['data'][0]
    plant_id = plant['plantId']
    plant_info = api.plant_info(plant_id)
    device = plant_info['deviceList'][0]
    device_sn = device['deviceSn']
    
data = api.get_ac_production_consumption(device_sn, plant_id, date=date)

# date = datetime.now().replace(hour = 0, minute = 0)

 # Set up storage array
 # hour, minute, ['pacToUser', 'sysOut', 'pdischarge', 'pacToGrid', 'ppv']
summary = np.zeros((24,12,5))
times = np.arange('2022-10-18T00:00','2022-10-19T00:00', 5, dtype='datetime64')

for h in range(0,24):
    for m in range(0,60,5):
        key = '{:02d}:{:02d}'.format(h,m)
        try:
            summary[h,m//5,:] = np.array([float(data['obj']['chartData'][key]['pacToUser']),
                                          float(data['obj']['chartData'][key]['sysOut']), 
                                          float(data['obj']['chartData'][key]['pdischarge']),
                                          float(data['obj']['chartData'][key]['pacToGrid']),
                                          float(data['obj']['chartData'][key]['ppv'])])
        except:
            summary[h,m//5,:] = np.array([None, None, None, None, None])

summary = summary.reshape((24*12,5))
summaryMask = np.isfinite(summary[:,0]).flatten()

fig, ax  = plt.subplots(1, 1, sharex=True, figsize=(6, 4))
myFmt = mdates.DateFormatter('%H:%M')
ax.xaxis.set_major_formatter(myFmt)
plt.fill_between(times[summaryMask], summary[summaryMask,4], 
                  edgecolor=(0,0.6,0,1), facecolor=(0,0.6,0,0.2),
                  label='PV inverter')
plt.fill_between(times[summaryMask], summary[summaryMask,1], 
                  edgecolor=(0,0.9,0.7,1), facecolor=(0,0.9,0.7,0.2),
                  label='load consumption')
plt.fill_between(times[summaryMask], summary[summaryMask,3], 
                  edgecolor=(0.4,0,1,1), facecolor=(0.4,0,1,0.2),
                  label='exported to grid')
plt.fill_between(times[summaryMask], summary[summaryMask,0], 
                  edgecolor=(0.5,0,0,1), facecolor=(0.5,0,0,0.2),
                  label='import from grid')
plt.fill_between(times[summaryMask], summary[summaryMask,2], 
                  edgecolor=(0,0.4,1,1), facecolor=(0,0.4,1,0.2),
                  label='from battery')
plt.tick_params(labelsize=9, direction='inout')
plt.xlabel('Time (hh:mm)', fontsize=10)
plt.ylabel('Energy (kWh)', fontsize=10)
plt.title('Growatt', fontsize=12, fontweight='bold')
plt.legend(fontsize=9, edgecolor='1')
plt.show()
