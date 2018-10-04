from flask import Flask, render_template, request, redirect, send_file, url_for
from werkzeug import secure_filename
from geopy.geocoders import Nominatim
import pandas
import folium
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/success", methods=['POST'])

def success():
    global file

    if request.method == 'POST': # 'POST' БЕЗ СКОБОК!
        # check the file_extension
        # read the file
        file = request.files["file"]
        file.save(secure_filename("uploaded_"+file.filename))
        # check the Name just like try
        try:
            # create df
            df = pandas.read_csv("uploaded_"+file.filename, encoding='latin-1')

            if 'address' in df.columns:
                tr_name= 'address'
            elif 'Address' in df.columns:
                tr_name = 'Address'

            nom = Nominatim()
            df["Coordinates"] = df[tr_name].apply(nom.geocode)
            df["Latitude"] = df["Coordinates"].apply(lambda x: x.latitude if x!=None else None)
            df["Longitude"] = df["Coordinates"].apply(lambda x: x.longitude if x!=None else None)

            # save the file
            if not os.path.isfile("saved_"+file.filename):
                df.to_csv("saved_"+file.filename, header='column_names')
            else:
                df.to_csv("saved_"+file.filename, mode='a', header=None)

            # create the table
            df_table = df.to_html()

            # передадим таблицу в html и отрендерим страничку с таблицей и кнопкой
            return render_template("success.html", table = df_table, btn="download.html")
        except:
            return render_template("index.html", text = "I can't find address or Address column in your file. Please, check it!")
    else:
        return  render_template("index.html", text="Something went wrong")

@app.route("/download")
def download():
    return send_file("saved_"+file.filename, attachment_filename="your_file.csv", as_attachment=True)
    pass

@app.route("/map", methods=['GET','POST'])
def map():
    df = pandas.read_csv("saved_"+file.filename, encoding='latin-1')
    # add the data for markers
    lat = list(df["Latitude"])
    lon = list(df["Longitude"])
    name = list(df["Address"])

    # create the map
    map = folium.Map(location=None, zoom_start=9)
    # add markers to the map
    fgv = folium.FeatureGroup(name="Places")

    for lt, ln, nm in zip(lat, lon, name):
        fgv.add_child(folium.CircleMarker(location=[lt,ln], radius=10, popup=nm, fill = True, fill_color='blue', color='white', fill_opacity=0.7))

    map.add_child(fgv)
    map.save("./templates/map.html")

    # show the map
    return render_template("map.html")

if __name__ == '__main__':
    app.debug = True
    app.run()
