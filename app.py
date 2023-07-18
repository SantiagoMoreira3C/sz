from flask import Flask, render_template
from pymongo import MongoClient
import matplotlib.pyplot as plt
import pandas as pd
import io
import base64
from sklearn.linear_model import LinearRegression
from datetime import datetime





 

client = MongoClient('mongodb+srv://admin:admin@cluster0.hrgaavf.mongodb.net/')
#client = MongoClient('mongodb://localhost:27017')
db = client.ritmo
collection = db.datos

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/sensor')
def sensor():
    # Obtener datos de MongoDB
    data = collection.find({'$and': [{'frecuencia': {'$ne': 0}}, {'saturacion': {'$ne': 0}}]})
    df = pd.DataFrame(data)

    df['TIME'] = df['TIME'].apply(lambda x: sum(int(t) * 60**(2-i) for i, t in enumerate(x.split(':'))))


    # Realizar regresión lineal para la frecuencia cardíaca
    model_frecuencia = LinearRegression()
    model_frecuencia.fit(df[['TIME']], df['frecuencia'])
    pred_frecuencia = model_frecuencia.predict(df[['TIME']])

    # Realizar regresión lineal para la saturación de oxígeno
    model_saturacion = LinearRegression()
    model_saturacion.fit(df[['TIME']], df['saturacion'])
    pred_saturacion = model_saturacion.predict(df[['TIME']])

      # Calcular resumen de frecuencia cardíaca
    resumen_frecuencia = {
        'Máximo': df['frecuencia'].max(),
        'Promedio': df['frecuencia'].mean(),
        'Mínimo': df['frecuencia'].min()
    }

    # Calcular resumen de saturación de oxígeno
    resumen_saturacion = {
        'Máximo': df['saturacion'].max(),
        'Promedio': df['saturacion'].mean(),
        'Mínimo': df['saturacion'].min()
    }


    # Crear gráficos
    plt.figure(figsize=(10, 5))
    plt.plot(df['TIME'], df['frecuencia'], label='Frecuencia cardíaca')
    plt.plot(df['TIME'], pred_frecuencia, label='Predicción de frecuencia cardíaca')
    plt.xlabel('Tiempo(Segundos)')
    plt.ylabel('Frecuencia')
    plt.title('Gráfico de Frecuencia Cardiaca')
    plt.legend()

    img1 = io.BytesIO()
    plt.savefig(img1, format='png')
    img1.seek(0)
    plot_url1 = base64.b64encode(img1.getvalue()).decode()

    plt.figure(figsize=(10, 5))
    plt.plot(df['TIME'], df['saturacion'], label='Saturación de oxígeno')
    plt.plot(df['TIME'], pred_saturacion, label='Predicción de saturación de oxígeno')
    plt.xlabel('Tiempo(Segundos)')
    plt.ylabel('Saturación')
    plt.title('Gráfico de Saturación de Oxígeno')
    plt.legend()

    img2 = io.BytesIO()
    plt.savefig(img2, format='png')
    img2.seek(0)
    plot_url2 = base64.b64encode(img2.getvalue()).decode()

    # Generar recomendaciones
    recomendaciones = []
    if pred_frecuencia[-1] > 80:
        recomendaciones.append('Consulte a un médico, la frecuencia cardíaca está alta.')
    if pred_saturacion[-1] < 95:
        recomendaciones.append('Mantenga un monitoreo de la saturación de oxígeno.')

    return render_template('sensor.html', plot_url1=plot_url1, plot_url2=plot_url2,
                           table_data=df.to_dict('records'), recomendaciones=recomendaciones,
                           resumen_frecuencia=resumen_frecuencia, resumen_saturacion=resumen_saturacion)


if __name__ == '__main__':
    app.run(debug=True)
