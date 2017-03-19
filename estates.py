#!/usr/bin/python

import json
import urllib2
import re
import os
from subprocess import Popen, PIPE, STDOUT
district_no = 9 # Prague 9
price_m2_max = 160000
price_m2_min = 45000
price_max = 40000000
if os.environ.get("ESTATES_PRICE_MAX") is not None:
   price_max = int(os.environ.get("ESTATES_PRICE_MAX"))
min_area = 10
if os.environ.get("ESTATES_MIN_AREA") is not None:
   min_area = int(os.environ.get("ESTATES_MIN_AREA"))
image_viewer = 'imgcat' # for Linux use terminology, aview or fim
ads_no = 5
ad_no = 0
out_of_price_per_m2_filter = 0
filtered = 0

is_display_image = os.environ.get("ESTATES_IMAGES") is not None and os.environ.get("ESTATES_IMAGES") == "YES"
is_full_detail = is_display_image
district = 5000 + district_no

pattern=re.compile(r"(\d+)")
count_url = 'https://www.sreality.cz/api/cs/v2/estates/count?category_main_cb=1&category_type_cb=1&czk_price_summary_order2=0%7C'+str(price_max)+'&no_auction=1&locality_district_id='+str(district)+'&locality_region_id=10&usable_area='+str(min_area)+'%7C10000000000&ownership=1&per_page=60&building_type_search=2|3'
search_url = 'https://www.sreality.cz/api/cs/v2/estates?category_main_cb=1&category_type_cb=1&czk_price_summary_order2=0%7C'+str(price_max)+'&no_auction=1&locality_district_id='+str(district)+'&locality_region_id=10&usable_area='+str(min_area)+'%7C10000000000&ownership=1&per_page=60&building_type_search=2|3'

average_price_m2 = 0
all_m2_prices = []

f = open("stats.dat", "w")
f.write('title,price,area,price_m2,lon,lat')

def read_url(url):
  req = urllib2.Request(url)
  response = urllib2.urlopen(req)
  return response.read()

def get_page(url):
  page = read_url(url)
  #print page
  return json.loads(page)

def display_image(url):
  if is_display_image:
    bytes = read_url(url)
    p = Popen([image_viewer], stdout=None, stdin=PIPE, stderr=STDOUT)    
    p.communicate(input=bytes)
  

def display_estate(x):
    global ad_no
    global average_price_m2
    global out_of_price_per_m2_filter
    global filtered
    global f
    locality = x["locality"].encode('utf-8')
    name = x["name"].encode('utf-8')
    price = x["price"]
    images = x["_links"]["images"]
    img = images[0]
    self_link = "https://www.sreality.cz/api" + x["_links"]["self"]["href"]
    detailed_info = get_page(self_link)
    main_info = [o for o in detailed_info["items"] if o["type"] == "price_czk"][0]
    state = [o["value"].encode('utf-8') for o in detailed_info["items"] if o["name"] == "Stav"]
    state_str = state[0] if len(state)>0 else "" 
    phones = ", ".join([ o["number"].encode('utf-8') for o in detailed_info["_embedded"]["seller"]["phones"]])
    area = max([int(o["value"]) for o in detailed_info["items"] if o["type"] == "area"])
    updates = ", ".join([o["value"].encode('utf-8') for o in detailed_info["items"] if o["type"] == "edited"])
    is_topped = detailed_info["is_topped"]
    lon = detailed_info["map"]["lon"]
    lat = detailed_info["map"]["lat"]
    top_str = "topped" if is_topped else "not topped" 
    negotiation = main_info["negotiation"]
    full_text = detailed_info["text"]["value"].encode('utf-8') if is_full_detail else ""
    m2_price = price / int(area)
    if m2_price <= price_m2_max and m2_price >= price_m2_min:
       average_price_m2 += m2_price;
       all_m2_prices.append(m2_price)
       filtered += 1
       ad_no += 1
       print "----------------------------------------------------------------------------------------------------"
       print locality+ " " + name + " " + str(price) + " "+  str(area) + "m2 " + str(m2_price) + "Kc/m2 "  + state_str +" "  +top_str +" negotiation: "+str(negotiation)+" phones:"+phones
       print "Updates:", updates
       f.write("\n" + name + " ," + str(price) + ", " + str(area) + ", " + str(m2_price) + ", " + str(lon) + ", " + str(lat))
       print full_text
       display_image(img["href"])
    else:
       out_of_price_per_m2_filter += 1
 

count = get_page(count_url) ["result_size"]
pages = 1 + count / 60



for page in xrange(1,1+pages):
  sreality_page = get_page(search_url+'&page='+str(page))
  estates = sreality_page["_embedded"]["estates"]
  
  for x in estates:
    try:
      display_estate(x)
      if is_full_detail and (ad_no % ads_no == 0):
        ad_no += 1
        raw_input('------ Load more --------')

    except KeyError:
      pass
  
average_price_m2 /= filtered
all_m2_prices.sort()
median = all_m2_prices[len(all_m2_prices)/2]

print "Average price m2:" + str(average_price_m2) + "Kc/m2"
print "Median  price m2:" + str(median) + "Kc/m2"
print "Total Count     :" + str(count)
print "Filtered        :" + str(filtered)
print "Out of filter   :" + str(out_of_price_per_m2_filter)

f.close()
