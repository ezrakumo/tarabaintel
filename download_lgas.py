import requests
import json

# A reliable open-source GeoJSON for Nigerian LGAs
url = "https://raw.githubusercontent.com/deldersveld/topojson/master/countries/nigeria/nigeria-lga.json"

# Note: Since this is a TopoJSON, we will use a simplified direct GeoJSON link instead for ease of use.
# Let's use a direct GeoJSON source for Nigerian LGAs.
url = "https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/nigeria-lgas.geojson"

print("Downloading Nigeria LGA GeoJSON...")
try:
    response = requests.get(url)
    response.raise_for_status()
    
    with open('nigeria_lgas.geojson', 'w', encoding='utf-8') as f:
        f.write(response.text)
        
    print("Success! Saved as 'nigeria_lgas.geojson'")
except Exception as e:
    print(f"Download failed: {e}")
    print("Please manually download the file from: https://github.com/codeforgermany/click_that_hood/blob/main/public/data/nigeria-lgas.geojson")