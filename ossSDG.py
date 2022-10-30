import overpy
import json
import requests
from shapely.geometry import Point
import geopandas as gpd
import webbrowser
import mapclassify
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import pandas as pd

# Source - https://villageinfo.in/maharashtra.html
mh2011Popln = [ { "#": 1, "district": "Ahmednagar", "area": "17,048 (km²)", "population": "45,43,159", "density": "266.5" }, 
{ "#": 2, "district": "Akola", "area": "5,673 (km²)", "population": "18,13,906", "density": "319.8" }, 
{ "#": 3, "district": "Amravati", "area": "12,210 (km²)", "population": "28,88,445", "density": "236.6" }, 
{ "#": 4, "district": "Aurangabad", "area": "10,131 (km²)", "population": "37,01,282", "density": "365.1" }, 
{ "#": 5, "district": "Bhandara", "area": "4,087 (km²)", "population": "12,00,334", "density": "293.7" }, 
{ "#": 6, "district": "Beed", "area": "10,693 (km²)", "population": "25,85,049", "density": "241.8" }, 
{ "#": 7, "district": "Buldhana", "area": "9,661 (km²)", "population": "25,86,258", "density": "267.7" }, 
{ "#": 8, "district": "Chandrapur", "area": "11,443 (km²)", "population": "22,04,307", "density": "192.6" }, 
{ "#": 9, "district": "Dhule", "area": "7,195 (km²)", "population": "20,50,862", "density": "285" }, 
{ "#": 10, "district": "Gadchiroli", "area": "14,412 (km²)", "population": "10,72,942", "density": "74.45" }, 
{ "#": 11, "district": "Gondiya", "area": "5,234 (km²)", "population": "13,22,507", "density": "252.7" }, 
{ "#": 12, "district": "Hingoli", "area": "4,827 (km²)", "population": "11,77,345", "density": "243.9" }, 
{ "#": 13, "district": "Jalgaon", "area": "11,765 (km²)", "population": "42,29,917", "density": "359.5" }, 
{ "#": 14, "district": "Jalna", "area": "7,694 (km²)", "population": "19,59,046", "density": "254.8" }, 
{ "#": 15, "district": "Kolhapur", "area": "7,685 (km²)", "population": "38,76,001", "density": "504.4" },
{ "#": 16, "district": "Latur", "area": "7,157 (km²)", "population": "24,54,196", "density": "342.9" }, 
{ "#": 17, "district": "Mumbai City", "area": "157 (km²)", "population": "30,85,411", "density": "19652" }, 
{ "#": 18, "district": "Mumbai Suburban", "area": "446 (km²)", "population": "93,56,962", "density": "20980" },
{ "#": 19, "district": "Nagpur", "area": "9,892 (km²)", "population": "46,53,570", "density": "470.4" }, 
{ "#": 20, "district": "Nanded", "area": "10,528 (km²)", "population": "33,61,292", "density": "319.3" }, 
{ "#": 21, "district": "Nandurbar", "area": "5,955 (km²)", "population": "16,48,295", "density": "276.8" }, 
{ "#": 22, "district": "Nashik", "area": "15,530 (km²)", "population": "61,07,187", "density": "393.3" }, 
{ "#": 23, "district": "Osmanabad", "area": "7,569 (km²)", "population": "16,57,576", "density": "219" }, 
{ "#": 24, "district": "Parbhani", "area": "6,214 (km²)", "population": "18,36,086", "density": "295.5" }, 
{ "#": 25, "district": "Pune", "area": "15,643 (km²)", "population": "94,29,408", "density": "602.8" }, 
{ "#": 26, "district": "Raigad", "area": "7,152 (km²)", "population": "26,34,200", "density": "368.3" }, 
{ "#": 27, "district": "Ratnagiri", "area": "8,208 (km²)", "population": "16,15,069", "density": "196.8" }, 
{ "#": 28, "district": "Sangli", "area": "8,572 (km²)", "population": "28,22,143", "density": "329.2" }, 
{ "#": 29, "district": "Satara", "area": "10,480 (km²)", "population": "30,03,741", "density": "286.6" }, 
{ "#": 30, "district": "Sindhudurg", "area": "5,207 (km²)", "population": "8,49,651", "density": "163.2" },
{ "#": 31, "district": "Solapur", "area": "14,895 (km²)", "population": "43,17,756", "density": "289.9" }, 
{ "#": 32, "district": "Thane", "area": "9,558 (km²)", "population": "1,10,60,148", "density": "1157" }, 
{ "#": 33, "district": "Wardha", "area": "6,309 (km²)", "population": "13,00,774", "density": "206.2" }, 
{ "#": 34, "district": "Washim", "area": "4,901 (km²)", "population": "11,97,160", "density": "244.3" }, 
{ "#": 35, "district": "Yavatmal", "area": "13,582 (km²)", "population": "27,72,348", "density": "204.1" } ]

columns = ['id', 'name','geo', 'admin_level','wikidata','government', 'wikidata','population']
api = overpy.Overpass()
in_admin_df = pd.read_csv('west_india_admin_boundaries.csv', usecols = columns)
in_admin_df = in_admin_df[in_admin_df.admin_level == 5]
in_admin_gdf = gpd.GeoDataFrame(in_admin_df.name, geometry=gpd.GeoSeries.from_wkt(in_admin_df.geo),crs=4326).rename(columns={"name": "district_name"})

def getPoplnForDistrict(districtName):
    for eachDist in mh2011Popln:
        if(eachDist["district"] == districtName):
            return eachDist["density"]
    return ""


def getOSMPOIs(query_result, htmlName):
    points_array = [ Point(x.lon, x.lat) for x in query_result.nodes]
    points_series = gpd.GeoSeries(points_array)
    pois_array = [ { "name": x.tags.get("name", "") } for x in query_result.nodes]
    pois_gdf = gpd.GeoDataFrame(pois_array, geometry=points_series, crs=4326)
    m = pois_gdf.explore(tooltip=["name"], highlight=True)
    m.save(htmlName)
    #webbrowser.open('gov_healthcare_map.html')
    return pois_gdf

def plot_district_counts(poiGDF, title):
    in_admin_poi_gdf = in_admin_gdf.sjoin(poiGDF)
    poi_count_df = in_admin_poi_gdf.groupby(by=["district_name"]).size().to_frame("count").reset_index()
    in_admin_total_counts = in_admin_gdf.merge(poi_count_df)
    ax = in_admin_total_counts.plot(column="count", cmap="summer", figsize=(15,10), legend=True)
    ax.set_title(title, fontsize=20)
    for idx, row in in_admin_total_counts.iterrows():
        lbl = str(row["count"])+ "-"+getPoplnForDistrict(row["district_name"])
        ax.annotate(text=lbl, xy=(row.geometry.centroid.x, row.geometry.centroid.y), horizontalalignment='center', path_effects=[pe.withStroke(linewidth=4, foreground="white")])
    #fig = plt.figure(figsize=(15, 10))
    ax.set_facecolor('#ccc')
    return ax


def mapHospitals():
    query_result = api.query("""
        area['is_in:country_code'='IN']['admin_level'='4']['name'='Maharashtra']->.place;
        (
            node["amenity"="hospital"]["name"~"^District"](area.place);
            node["healthcare"="hospital"]["name"~"^District"](area.place);
            node["amenity"="hospital"]["name"~"^Regional"](area.place);
            node["healthcare"="hospital"]["name"~"^Regional"](area.place);   
            node["amenity"="hospital"]["name"~"^Civil"](area.place);
            node["healthcare"="hospital"]["name"~"^Civil"](area.place);  
            node["amenity"="hospital"]["name"~"^General"](area.place);
            node["healthcare"="hospital"]["name"~"^General"](area.place);  
            node["amenity"="hospital"]["name"~"^National"](area.place);
            node["healthcare"="hospital"]["name"~"^National"](area.place);   
            node["amenity"="hospital"]["name"~"^AIIMS"](area.place);
            node["healthcare"="hospital"]["name"~"^AIIMS"](area.place);   
            node["amenity"="hospital"]["name"~"^Government"](area.place);
            node["healthcare"="hospital"]["name"~"^Government"](area.place);   
        );
        out body;
        """)
    poiGDF = getOSMPOIs(query_result, 'gov_hospital_map.html')
    # Merge Admin Map with POI Data
    fig = plt.figure(figsize=(15, 10))
    ax = plot_district_counts(poiGDF, "Medical Org in Maharashtra")
    in_admin_gdf.plot(ax=ax, alpha=.6, facecolor='white', edgecolor="#aaa", linewidth=1)
    poiGDF[poiGDF.name.str.match(".*District.*")].plot(ax=ax, facecolor='red', markersize=20, label="District", alpha=.4)
    poiGDF[poiGDF.name.str.match(".*Civil.*|.*Government.*")].plot(ax=ax, facecolor='blue', markersize=20, label="Civil", alpha=.4)
    poiGDF[poiGDF.name.str.match(".*National.*|.*AIIMS.*")].plot(ax=ax, facecolor='green', markersize=20, label="National", alpha=.4)
    poiGDF[poiGDF.name.str.match(".*Regional.*")].plot(ax=ax, facecolor='yellow', markersize=20, label="Regional", alpha=.4)
    ax.set_title("Medical Org in Maharashtra", fontsize=10)
    ax.legend()
    ax.set_facecolor('#ccc')
    plt.show()


def mapWomenAndChildHospitals():
    query_result = api.query("""
        area['is_in:country_code'='IN']['admin_level'='4']['name'='Maharashtra']->.place;
        (
            node["amenity"="hospital"]["name"~".*Woman.*|.*Women.*|.*Matern.*|.*Mother.*|.*Gynecolog.*"](area.place);
            node["healthcare"="hospital"]["name"~".*Child.*|.*Paediatr.*"](area.place);
        );
        out body;
        """)
    poiGDF = getOSMPOIs(query_result, 'women&Child_hospital_map.html')
    ax = plot_district_counts(poiGDF, "Women and Childrens Hospital")
    in_admin_gdf.plot(ax=ax, alpha=.6, facecolor='white', edgecolor="#aaa", linewidth=1)
    poiGDF[poiGDF.name.str.match(".*Child.*|.*Paediatr.*")].plot(ax=ax, facecolor='red', markersize=20, label="Childrens Hospital", alpha=.4)
    poiGDF[poiGDF.name.str.match(".*Woman.*|.*Women.*|.*Matern.*|.*Mother.*|.*Gynecolog.*")].plot(ax=ax, facecolor='blue', markersize=20, label="Womens Hospital", alpha=.4)
    ax.set_title("Womens and Childrens Hospitals", fontsize=10)
    ax.legend()
    ax.set_facecolor('#ccc')
    plt.show()


def mapMedicalColleges():
    query_result = api.query("""
    area['is_in:country_code'='IN']['admin_level'='4']['name'='Maharashtra']->.place;
    (
    node["amenity"="college"]["name"~"Medical"](area.place);
    node["amenity"="university"]["name"~"Medical"](area.place);
    node["amenity"="institute"]["name"~"Medical"](area.place); 
    node["amenity"="hospital"]["name"~"College"](area.place);  
    node["amenity"="hospital"]["name"~"Institute"](area.place);  
    );
    out body;
    """)
    poiGDF = getOSMPOIs(query_result, "Government Colleges")
    ax = plot_district_counts(poiGDF, "Medical Colleges in Maharashtra")
    plt.show()

mapWomenAndChildHospitals()

def get_input():
    print("\nHealth-e-quality, monitor SDG-3 Health Parameters >> ")
    print("\nEnter an option.(integer) :\n1. Hospitals Data\n2. Medical Colleges\n3. Women and Childrens Hospital")
    option = int(input("\n>>>"))
    while option not in [1,2,3]: 
        print("Invalid Option. Try Again \n>>")
        option = int(input())
    return option

if __name__ == '__main__':  #main function to act accordingly to the user's input.
    option=get_input()
    if(option==1):
        mapHospitals()
    elif(option==2):
        mapMedicalColleges()
    elif(option==3):
        mapWomenAndChildHospitals()
    print("Note: \n1. The coverage for Indian Healthcare data in OpenStreetMaps is not comprehensive and needs correction for accurate assessment.\n2. However, the current data gives reasonable amount of guidance in the right direction ")

