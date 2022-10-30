import osmium
import shapely.wkb
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def merge_two_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z

class AdminAreaHandler(osmium.SimpleHandler):
    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.areas = []
        self.wkbfab = osmium.geom.WKBFactory()

    def area(self, a):
        if  "admin_level" in a.tags:
            if(a.id != 14239925 and a.id != 15770795 and a.id != 15770787 and a.id != 15770773 and a.id != 15777929 and a.id != 23933273 and a.id != 23933347 and a.id != 23933269 and a.id != 23933275 and a.id != 23933205 and a.id != 23933203 and a.id != 23933221 and a.id != 23933201 and a.id != 23933199 and a.id != 23933207 and a.id != 23933349 and a.id != 28313747 and a.id != 28316191 and a.id != 27527337):
                wkbshape = self.wkbfab.create_multipolygon(a)
                shapely_obj = shapely.wkb.loads(wkbshape, hex=True)
                area = { "id": a.id, "geo": shapely_obj }
                area = merge_two_dicts(area, a.tags)
                self.areas.append(area)

handler = AdminAreaHandler()
osm_file = "western-zone-latest.osm.pbf"
handler.apply_file(osm_file, locations=True, idx='flex_mem')
df = pd.DataFrame(handler.areas)
gdf = gpd.GeoDataFrame(df, geometry="geo")
in_india = gdf.within(gdf[gdf.admin_level == "4"].geo.iloc[0])

fig = plt.figure(figsize=(15, 15))
ax = plt.axes()
# state boundary
gdf[(gdf.admin_level == "4")].set_crs(crs=4326).plot(ax=ax, alpha=1, edgecolor="#000", linewidth=2, facecolor='none')
# admin level 6 boundaries
admin_level_5_gdf = gdf[(in_india & (gdf.admin_level=="5") & (~gdf["ISO3166-2"].isna()))].set_crs(crs=4326)
admin_level_5_gdf.plot(ax=ax, alpha=.1, facecolor='b', edgecolor="#000", linewidth=1)

# add labels
for idx, row in admin_level_5_gdf.iterrows():
    ax.annotate(text=row["name:en"], xy=(row.geo.centroid.x, row.geo.centroid.y), horizontalalignment='center')
gdf.to_csv("west_india_admin_boundaries.csv")

