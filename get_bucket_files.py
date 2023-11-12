import os
import boto3
import csv
import pandas as pd

def crear_cliente_s3_desde_csv(credenciales_csv):
    df = pd.read_csv(credenciales_csv)
    aws_access_key_id = df['Access key ID'][0]
    aws_secret_access_key = df['Secret access key'][0]
    # # Leer las credenciales del archivo CSV
    # with open(credenciales_csv, 'r') as csv_file:
    #     reader = csv.DictReader(csv_file)
    #     for row in reader:
    #         print(row)
    #         aws_access_key_id = row['Access key ID']
    #         aws_secret_access_key = row['Secret access key']
    
    # Crear el cliente de S3 utilizando las credenciales leídas
    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    s3 = session.client('s3')
    return s3

# Función para verificar si un archivo existe en la carpeta de salida
def archivo_existe(output_folder, objeto_nombre):
    ruta_salida = os.path.join(output_folder, objeto_nombre)
    return os.path.exists(ruta_salida)

# Resto del código sin cambios
def verificar_crear_carpeta(output_folder):
    # Verificar si la carpeta de salida existe, si no existe, crearla
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

def listar_archivos_en_bucket(s3, bucket_name):
    # Listar los objetos en el bucket
    response = s3.list_objects_v2(Bucket=bucket_name)
    return response.get('Contents', [])

def descargar_archivos_s3(s3, bucket_name, output_folder):
    objetos = listar_archivos_en_bucket(s3, bucket_name)
    
    for obj in objetos:
        # Obtener el nombre del objeto (archivo)
        objeto_nombre = obj['Key']
        
        # Verificar si el archivo ya existe en la carpeta de salida
        if not archivo_existe(output_folder, objeto_nombre):
            # Descargar el archivo desde S3 al directorio de salida
            ruta_salida = os.path.join(output_folder, objeto_nombre)
            s3.download_file(bucket_name, objeto_nombre, ruta_salida)
            print(f'Descargado: {objeto_nombre} -> {ruta_salida}')
        else:
            print(f'El archivo ya existe en la carpeta de salida: {objeto_nombre}')

if __name__ == "__main__":
    # Establecer la ruta del archivo CSV con las credenciales
    credenciales_csv = './credentials/voice_to_image_accessKeys.csv'
    
    # Establecer las variables de entrada
    bucket_name = 'stable-diffusion-city-images'
    output_folder = './data/output/images/'

    # Crear el cliente de S3 desde el archivo CSV
    s3 = crear_cliente_s3_desde_csv(credenciales_csv)

    # Verificar y crear la carpeta de salida
    verificar_crear_carpeta(output_folder)

    # Descargar archivos desde S3 (solo si no existen en la carpeta de salida)
    descargar_archivos_s3(s3, bucket_name, output_folder)
