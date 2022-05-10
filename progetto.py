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

df = pd.read_csv('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv')
regioni =  gpd.read_file('/workspace/Progetto_Info/Reg01012021_g_WGS84.zip')
province = gpd.read_file('/workspace/Progetto_Info/ProvCM01012021_g_WGS84.zip')



@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/regione/<nome_regione>', methods=['GET'])
def regione(nome_regione):
    global dati_regione,province_regione
    dati_regione = regioni[regioni["DEN_REG"] == nome_regione]
    confini_regione = regioni[regioni.touches(dati_regione.geometry.squeeze())]
    province_regione = province[province.within(dati_regione.geometry.squeeze())]

    return render_template('visualizza_regione.html',regione=nome_regione,confini=confini_regione.DEN_REG.to_list(),province_regione=province_regione.DEN_PROV.to_list())


@app.route('/mappa.png', methods=['GET'])
def regionepng():
    fig, ax = plt.subplots(figsize = (12,8))

   
    province_regione.to_crs(epsg=3857).plot(ax=ax,facecolor='none', edgecolor="r")
    dati_regione.to_crs(epsg=3857).plot(ax=ax,facecolor='none', edgecolor="k")
    contextily.add_basemap(ax=ax)  

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

@app.route('/info_regione', methods=['GET'])
def info():

    return render_template('info.html')

@app.route('/scelta', methods=['GET'])
def scelta():
    info = request.args['scelta']
    if info == "grafico":
        return redirect(url_for("grafico"))
    else:
        return redirect(url_for('info'))
'''df = df.filter(items=['denominazione_regione', 'periodo','totale_positivi_test_molecolare'])
df.dropna(subset = ["totale_positivi_test_molecolare"], inplace=True)
df[df['denominazione_regione'] == nome_regione].plot(figsize=(20,20) , x='periodo', y ='totale_positivi_test_molecolare')'''

@app.route("/grafico", methods=["GET"])

def grafico():
    
    df1 = df.filter(items=['denominazione_regione', 'periodo','totale_positivi_test_molecolare'])
    df1.dropna(subset = ["totale_positivi_test_molecolare"], inplace=True)
    grafico = df1[df1['denominazione_regione'] == 'nome_regione'].plot(figsize=(20,20) , x='periodo', y ='totale_positivi_test_molecolare')
    

    return render_template("grafico.html", tabella = grafico.to_html())




@app.route("/grafico.png", methods=["GET"])

def graficopng():

    fig, ax = plt.subplots(figsize = (12,8))




    




    output = io.BytesIO()

    FigureCanvas(fig).print_png(output)

    return Response(output.getvalue(), mimetype='image/png')




if __name__ == '__main__':
  app.run(host='0.0.0.0', port=3245, debug=True)