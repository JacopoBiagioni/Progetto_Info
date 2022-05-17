from flask import Flask, render_template, send_file, make_response, url_for, Response,request,redirect
app = Flask(__name__)
# pip install flask pandas contextily geopandas matplotlib folium lxml
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
#pd.plotting.register_matplotlib_converters()
df = pd.read_csv('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv')
Regioni =  gpd.read_file('/workspace/Progetto_Info/Reg01012021_g_WGS84.zip')
province = gpd.read_file('/workspace/Progetto_Info/ProvCM01012021_g_WGS84.zip')
prov = pd.read_html('https://www.tuttitalia.it/province/')[0]
prov.filter(items=['Provincia/Città Metropolitana', 'Popolazioneresidenti	','Superficiekm²','Densitàabitanti/km²','NumeroComuni',]).reset_index(drop=True)
prov['SIGLA']=prov['Provincia/Città Metropolitana'].str[:2]
info_prov = pd.merge(prov,province,how='inner',on ='SIGLA')
info_prov.filter(items=['DEN_PROV','SIGLA','Popolazioneresidenti','Superficiekm²','Densitàabitanti/km²','NumeroComuni','geometry'])
info_prov = info_prov.set_geometry("geometry")
regioni = pd.read_html('https://www.tuttitalia.it/regioni/popolazione/')[0]
regioni = regioni.filter(items=['Regione', 'Popolazioneresidenti','Superficiekm²','Densitàabitanti/km²','NumeroComuni','NumeroProvince']).reset_index(drop=True)

@app.route('/', methods=['GET'])
def home():
    
    return render_template('home.html',regioni = regioni.to_html())

@app.route('/regione/<nome_regione>', methods=['GET'])
def regione(nome_regione):
    global dati_regione, nome_reg,confini_regione,province_regione
    nome_reg = nome_regione
    dati_regione = Regioni[Regioni["DEN_REG"] == nome_regione]
    confini_regione = Regioni[Regioni.touches(dati_regione.geometry.squeeze())]
    province_regione = province[province.within(dati_regione.geometry.squeeze())]
    province_regione1 = info_prov[info_prov.within(dati_regione.geometry.squeeze())][['DEN_UTS','SIGLA','Popolazioneresidenti','Superficiekm²','Densitàabitanti/km²']]
    
    return render_template('visualizza_regione.html',regione=nome_regione,info=province_regione1.to_html())


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
        return redirect(url_for('informazioni'))

@app.route('/informazioni', methods=['GET'])
def informazioni():
    
    province_regione = province[province.within(dati_regione.geometry.squeeze())]
    confini_regione = Regioni[Regioni.touches(dati_regione.geometry.squeeze())]
    lst = province_regione.DEN_PROV.to_list()
    lst1 = confini_regione.DEN_REG.to_list()
    regioni["province_regione"] = ""
    regioni["regioni_confinanti"] = ""
    for i in range(0, len(regioni)):
        regioni.at[i, 'province_regione'] = lst
        regioni.at[i, 'regioni_confinanti'] = lst1
    informazioni_regione_selezionata =  regioni[regioni["Regione"] == nome_reg]
    regioni['province_regione'].astype(str)
    regioni['regioni_confinanti'].astype(str)

    return render_template('informazioni.html', regione = nome_reg, tabella =informazioni_regione_selezionata.to_html())



@app.route("/grafico", methods=["GET"])

def grafico():
    global df, df1,df3
    df3 = df
    df3['data'] = pd.to_datetime(df['data'])
    df['periodo']= df3['data'] #.dt.to_period('D')
    df1 = df.filter(items=['denominazione_regione', 'periodo','totale_positivi_test_molecolare'])
    df1.dropna(subset = ["totale_positivi_test_molecolare"], inplace=True)
    df = df[~df.denominazione_regione.str.contains("P.A.")]
    

    return render_template("grafico.html" )



@app.route("/grafico.png", methods=["GET"])
def graficopng():
    fig, ax = plt.subplots(figsize = (12,8))
    
    dfrisultato = df1[df1['denominazione_regione'] == nome_reg]
   
    # print(dfrisultato.dtypes)

    # dfrisultato["periodo"] = dfrisultato["periodo"].astype(str)
    ax.plot(dfrisultato.periodo, dfrisultato.totale_positivi_test_molecolare)
  
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=3245, debug=True)