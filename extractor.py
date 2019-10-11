from bs4 import BeautifulSoup
import pandas as pd
import re
import requests

bus_stops_link = 'http://pis.bmtcits.com:8080/Trip_Planner/Busstoplist.jsp?routeid={}&busno=KIAS-{}'
table = BeautifulSoup(open("info.html"), "html.parser")
rows = table.find_all('tr')


def extract_bus_stops(route_id, bus_code):
  bus_stops_url = bus_stops_link.format(route_id, bus_code)
  print('fetching bus stops from', bus_stops_url)
  stops_page = requests.get(bus_stops_url)
  html = BeautifulSoup(stops_page.text, "html.parser")

  trs = html.find('tr').find('tbody').find('tbody').find_all('tr')
  stop_names = []
  for tr in trs:
    stop_names.append(tr.find_all('td')[0].text)
  
  stops_df = pd.DataFrame({ 'stop_names': stop_names })
  stops_df['stop_order'] = stops_df.index
  return stops_df


airport_departures_dfs = []
origin_departures_dfs = []
origin_dfs = []
bus_stop_dfs = []
for row in rows:
  tds = row.find_all('td')
  # departure_times = row.find('td', {'id': 'Departure_Start_time-int'})
  tds = row.find_all('td')

  if len(tds) >= 1:
    departure_times = tds[-4].text.split(',')
    arrival_at_airport = tds[-3].text.split(',')
    departure_from_airport = tds[-2].text.split(',')
    arrival_at_origin = tds[-1].text.split(',')

    routeno = tds[0].find('p', {'id': 'routeno'})
    origin = tds[0].find('p', {'id': 'origin'})
    stops = tds[0].find('p', {'id': 'viewbusstop'})

    if routeno:
      bus_no = re.search('KIAS-(.+)', routeno.text)
      
      if stops:
        bus_stops_details = eval(stops.find_all('a')[0].get('href').replace('javascript:child_open', ''))
        bus_stops_df = extract_bus_stops(bus_stops_details[0], bus_stops_details[1])
        bus_stops_df['bus_no'] = bus_no.group(1)



      origin = origin.text.replace('\n', '').replace('Origin :', '').lstrip().rstrip()
      origins_df = pd.DataFrame({ 'origin': [origin] })
      origins_df['bus_no'] = bus_no.group(1)
      origins_df['bus_code'] = bus_stops_details[1]
      origins_df['route_id'] = bus_stops_details[0]
      origin_departures = pd.DataFrame({
        'departure_times': departure_times,
        'arrival_times': arrival_at_airport
      })
      origin_departures['bus_no'] = bus_no.group(1)


      airtport_departures = pd.DataFrame({
        'departure_times': departure_from_airport,
        'arrival_times': arrival_at_origin
      })
      airtport_departures['bus_no'] = bus_no.group(1)
      
      bus_stop_dfs.append(bus_stops_df)
      origin_dfs.append(origins_df)
      origin_departures_dfs.append(origin_departures)
      airport_departures_dfs.append(airtport_departures)



departure_times = pd.concat(origin_departures_dfs, axis=0, ignore_index=True)
origins = pd.concat(origin_dfs, axis=0, ignore_index=True)
airport_departure_times = pd.concat(airport_departures_dfs, axis=0, ignore_index=True)
bus_stops = pd.concat(bus_stop_dfs, axis=0, ignore_index=True)

print('********************')
print(departure_times.head())              # origin -> airport
print('********************')
print(origins.head())
print('********************')
print(airport_departure_times.head())      # airport -> origin
print('********************')
print(bus_stops.head())                    # all stops



'''Save as csv files'''
# departure_times.to_csv('origin_to_airport_timings.csv', index=False)
# origins.to_csv('origins.csv', index=False)
# airport_departure_times.to_csv('airport_to_origin.csv', index=False)
# bus_stops.to_csv('bus_stops.csv', index=False)
