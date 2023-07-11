import yfinance as yf
pfe=yf.Ticker("PFE")
import pandas as pd
import pg8000
from dotenv import load_dotenv
import os
from dotenv import load_dotenv
import os
import requests
# Cargo variables del archivo .env
load_dotenv()


db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_database = os.getenv("DB_DATABASE")

connection = pg8000.connect(
    user=db_user,
    password=db_password,
    host=db_host,
    port=db_port,
    database=db_database
)

#url = "https://api.teleport.org/api/urban_areas/slug:san-francisco-bay-area/scores/"
url = "https://api.teleport.org/api/urban_areas/"
# conexión a la API con get
response = requests.get(url)

# Consultar si lasolicitud fue exitosa (código de estado 200)
if response.status_code == 200:
    # Data en formato JSON
    data = response.json()

    # Mostrar los datos obtenidos
    print(data)
else:
    # Si la solicitud no fue exitosa, mostrar el código de estado
    print("Error al realizar la solicitud. Código de estado:", response.status_code)
    
#Creación de lista que incluye la dupla de nombre de ciudades y los links correspondientes que (incluyen luego los scores que nos interesan).
ciudades=data['_links']['ua:item']


schema = "bapintor_coderhouse"
table_name = "ciudades"

#Creación de tabla (ya la cree en mi esquema)
#city es la primary key porque en esta data no existen dos registros para la misma ciudad. 
create_table_query = f"""
CREATE TABLE IF NOT EXISTS {schema}.{table_name} (
    city VARCHAR PRIMARY KEY,
    "Housing" DECIMAL(10, 2),
    "Cost of Living" DECIMAL(10, 2),
    "Startups" DECIMAL(10, 2),
    "Venture Capital" DECIMAL(10, 2),
    "Travel Connectivity" DECIMAL(10, 2),
    "Commute" DECIMAL(10, 2),
    "Business Freedom" DECIMAL(10, 2),
    "Safety" DECIMAL(10, 2),
    "Healthcare" DECIMAL(10, 2),
    "Education" DECIMAL(10, 2),
    "Environmental Quality" DECIMAL(10, 2),
    "Economy" DECIMAL(10, 2),
    "Taxation" DECIMAL(10, 2),
    "Internet Access" DECIMAL(10, 2),
    "Leisure & Culture" DECIMAL(10, 2),
    "Tolerance" DECIMAL(10, 2),
    "Outdoors" DECIMAL(10, 2)
)
-- Aplicar la clave de ordenación a la nueva tabla
SORTKEY (city);
"""


# Ejecuta la consulta CREATE TABLE
cursor.execute(create_table_query)

# Confirma los cambios en la base de datos
connection.commit()


# Ejecuta la consulta CREATE TABLE

import requests


#Acá genero una lista con diccionarios sobre las categorias para cada ciudad para luego facilitar la carga de datos a la tabla creada. 
lista = []

# Iterar en cada ciudad
for ciudad in ciudades:
    ciudad_url = ciudad['href']+"scores/"
    ciudad_nombre = ciudad["name"]
    scores = []

    # Realiza la solicitud GET a la API para cada ciudad con los links anteriores
    response = requests.get(ciudad_url)

    # Comprueba si la solicitud fue exitosa (
    if response.status_code == 200:
        # Obtener los datos de respuesta en formato JSON
        ciudad_data = response.json()
        for categoria in ciudad_data['categories']:
            nombre = categoria["name"]
            score = categoria['score_out_of_10']
            scores.append({"nombre": nombre, "score": score})

        lista.append({"ciudad": ciudad_nombre, "puntajes": scores})
    else:
        # Si la solicitud no fue exitosa, mostrar el código de estado
        print("Error al realizar la solicitud. Código de estado:", response.status_code)

# lisa para ver los resultados
print(lista) 


#Para visuailizar y confirmar como se guarda el primero de los puntajes (housing)
for i in lista:
    print( i["ciudad"],i["puntajes"][0]["score"])
    

# Crear la consulta INSERT INTO
insert_query = f"""
INSERT INTO {schema}.{table_name} (
    city,
    "Housing",
    "Cost of Living",
    "Startups",
    "Venture Capital",
    "Travel Connectivity",
    "Commute",
    "Business Freedom",
    "Safety",
    "Healthcare",
    "Education",
    "Environmental Quality",
    "Economy",
    "Taxation",
    "Internet Access",
    "Leisure & Culture",
    "Tolerance",
    "Outdoors"
) VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
)
"""

#puntajes guarda del 0 al 16 cada una de las categorias para cada ciudad en el mismo orden que se creó la tabla
cursor = connection.cursor()
for i in lista:
        nombre = i["ciudad"]
        p_0=i["puntajes"][0]["score"]
        p_1=i["puntajes"][1]["score"]
        p_2=i["puntajes"][2]["score"]
        p_3=i["puntajes"][3]["score"]
        p_4=i["puntajes"][4]["score"]
        p_5=i["puntajes"][5]["score"]
        p_6=i["puntajes"][6]["score"]
        p_7=i["puntajes"][7]["score"]
        p_8=i["puntajes"][8]["score"]
        p_9=i["puntajes"][9]["score"]
        p_10=i["puntajes"][10]["score"]
        p_11=i["puntajes"][11]["score"]
        p_12=i["puntajes"][12]["score"]
        p_13=i["puntajes"][13]["score"]
        p_14=i["puntajes"][14]["score"]
        p_15=i["puntajes"][15]["score"]
        p_16=i["puntajes"][16]["score"]


        
        cursor.execute(insert_query, (nombre, p_0,p_1,p_2,p_3,p_4,p_5,p_6,p_7,p_8,p_9,p_10,p_11,p_12,p_13,p_14,p_15,p_16))

        try:
            connection.commit()  # Confirmar los cambios en la base de datos
        except Exception as e:
            connection.rollback()  # Revertir la transacción en caso de error
            print("Error:", str(e))
            
#drop_table_query = f"DROP TABLE IF EXISTS {schema}.{table_name}"
#cursor.execute(drop_table_query)
connection.commit()

connection.close()#cerrar conexión

