from flask import Flask, render_template, send_file, make_response, url_for, Response,request,redirect
app = Flask(__name__)
# pip install flask pandas contextily geopandas matplotlib folium
import folium
import io
import geopandas as gpd
import contextily
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

covid = pd.read_csv('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv')
regioni =  gpd.read_file('/workspace/Progetto_Info/Reg01012021_g_WGS84.zip')
province = gpd.read_file('/workspace/Progetto_Info/ProvCM01012021_g_WGS84.zip')
print(regioni)
@app.route('/', methods=['GET'])
def home():
    map = folium.Map(location= [43,12],zoom_start= 5)
#map.save('prova.html')
#marker
#folium.Marker(location= [])
map

    return render_template('prova.html',map=map)



   



if __name__ == '__main__':
  app.run(host='0.0.0.0', port=3245, debug=True)