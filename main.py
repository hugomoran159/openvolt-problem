import requests
import json
import pandas as pd 

# Problem 1
url1 = "https://api.openvolt.com/v1/interval-data?meter_id=6514153c23e3d1424bf82738&granularity=month&start_date=2023-01-01&end_date=2023-02-01"

headers = {
    "accept": "application/json",
    "x-api-key": "test-Z9EB05N-07FMA5B-PYFEE46-X4ECYAR"
}

def get_response(url):
    return requests.get(url, headers=headers)

consumption_data = get_response(url1).json()

consumption = consumption_data['data'][0]['consumption']

print(consumption)

# Problem 2
url2 = "https://api.openvolt.com/v1/interval-data?meter_id=6514167223e3d1424bf82742&granularity=hh&start_date=2023-01-01&end_date=2023-02-01"

half_hourly_consumption = pd.DataFrame(get_response(url2).json()['data'])

half_hourly_consumption.drop(half_hourly_consumption.index[-1], inplace=True)

total_consumption_half_hourly = half_hourly_consumption['consumption'].astype(float).sum()
print(total_consumption_half_hourly)
# 14 day limit is not enforced 
carbon_request = requests.get('https://api.carbonintensity.org.uk/intensity/2023-01-01T00:30Z/2023-02-01T00:00Z')

carbon_data = carbon_request.json()

half_hourly_carbon = pd.DataFrame(carbon_data['data'])
half_hourly_carbon = pd.json_normalize(half_hourly_carbon['intensity'])



half_hourly_consumption['consumption'] = half_hourly_consumption['consumption'].astype(int)
half_hourly_carbon['building_emissions'] = half_hourly_consumption['consumption'] * half_hourly_carbon['actual']
total_carbon_emissions = half_hourly_carbon['building_emissions'].sum() / 1000

print(total_carbon_emissions)

# Problem 3

generation_mix_request = requests.get('https://api.carbonintensity.org.uk/generation/2023-01-01T00:30Z/2023-02-01T00:00Z')

generation_data = generation_mix_request.json()['data']
processed_data = []

for entry in generation_data:
    row = {
        'from': entry['from'],
        'to': entry['to']
    }
    for mix in entry['generationmix']:
        row[mix['fuel']] = mix['perc']
    processed_data.append(row)

hourly_generation_data = pd.DataFrame(processed_data)

hourly_generation_data.fillna(0, inplace=True)
num_half_hours = 1487

generation_mix = pd.DataFrame()

biomas = hourly_generation_data['biomass'].sum() / num_half_hours 
coal = hourly_generation_data['coal'].sum() / num_half_hours
imports = hourly_generation_data['imports'].sum() / num_half_hours 
gas = hourly_generation_data['gas'].sum() /num_half_hours
nuclear = hourly_generation_data['nuclear'].sum() / num_half_hours
other = hourly_generation_data['other'].sum() / num_half_hours
hydro = hourly_generation_data['hydro'].sum() / num_half_hours
solar = hourly_generation_data['solar'].sum() / num_half_hours
wind = hourly_generation_data['wind'].sum() / num_half_hours

print("biomas: " + str(biomas))
print("coal: " + str(coal))
print("imports: " + str(imports))
print("gas: " + str(gas))
print("nuclear: " + str(nuclear))
print("other: " + str(other))
print("hydro: " + str(hydro))
print("solar: " + str(solar))
print("wind: " + str(wind))