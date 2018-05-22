import boto3
import io
from PIL import Image
s3 = boto3.client('s3')

def getAllAlumnos(bucket):
    allObjects = s3.list_objects_v2(Bucket=bucket,Prefix='alumno_')
    listObjects = []
    key = ''

    for element in allObjects['Contents']:
        key = element['Key']
        listObjects.append(key)

    return listObjects


def conseguirNombre(tableName, key):
    response = s3.head_object(
        Bucket = tableName,
        Key = key
    )
    return response['Metadata']['fullname']

def agregarAlumnoS3(bucket, imagenEntrada):
    imagen = Image.open(imagenEntrada)
    stream = io.BytesIO()
    imagen.save(stream, format = 'JPEG')
    imagenCodificado = stream.getvalue()

    nombreCompleto = imagenEntrada[17:-4].replace('_',' ').title()
    print(nombreCompleto)

    s3.put_object(
        Body = imagenCodificado,
        Bucket = bucket,
        ContentType = 'image/jpeg',
        Key = imagenEntrada[10:],
        Metadata={
        'fullname': nombreCompleto
        }
    )
