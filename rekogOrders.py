import boto3
import io
from PIL import Image

from s3Orders import conseguirNombre
from dynamoDBOrders import updateIndex, getName
rekognition = boto3.client('rekognition','us-west-2')


def crearCurso(curso):
    collectionsCheck = rekognition.list_collections()
    print(collectionsCheck['CollectionIds'])

    if (len(collectionsCheck['CollectionIds']) == 0 or curso not in collectionsCheck['CollectionIds']):
        response = rekognition.create_collection(CollectionId=curso)
        print('Curso ' + curso + ' creado.')
    else:
        print('Curso ' + curso + ' ya existe de antemano.')
    
    return


def retornarCurso(curso, tableName ='testtic3v2'):
    response = rekognition.list_faces(CollectionId=curso)
    allFaceIds = []

    for element in response['Faces']:
        allFaceIds.append(getName(tableName, element['FaceId']))
    
    return allFaceIds


def borrarCurso(curso):
    collectionsCheck = rekognition.list_collections()
    #print(collectionsCheck['CollectionIds'])

    if (len(collectionsCheck['CollectionIds']) != 0 and curso in collectionsCheck['CollectionIds']):
        response = rekognition.delete_collection(CollectionId=curso)
        print('Curso ' + curso + ' eliminado!')
    else:
        print('La tabla ' + curso + ' no existe!')


def agregarAlumno(tableName, curso, alumno):
    response = rekognition.index_faces(
        CollectionId=curso,
        Image={
            'S3Object': {
                'Bucket': tableName,
                'Name': alumno
            }
        }
    )
    
    faceID = response['FaceRecords'][0]['Face']['FaceId']
    personFullName = conseguirNombre(tableName, alumno)
    #print(faceID, alumno, personFullName)

    updateIndex(tableName,faceID,personFullName)
    print('Alumno ' + personFullName.replace('_', ' ') + ' agregado al curso ' + curso)
    return


def comprarConColleccion(curso, imageFile):
    # Pasar imagen a blob
    image = Image.open(imageFile)
    stream = io.BytesIO()
    image.save(stream, format = 'JPEG')
    encodedimg = stream.getvalue()

    # Conseguir las cajas envolvientes de cada cara detectada
    response = rekognition.detect_faces(Image={'Bytes': encodedimg})
    allFaces = response['FaceDetails']
    allFaceIds = {} # Crea un diccionario {FaceId: Similarity}

    # Consigue proporciones del imagen entregado
    image_width = image.size[0]
    image_height = image.size[1]

    # Por cada cara detectada...
    for face in allFaces:
        # Crea un imagen temporal, que solo consiste en el area de la Caja Envolviente
        boundingBox = face['BoundingBox']
        x1 = int(boundingBox['Left'] * image_width) * 0.9
        y1 = int(boundingBox['Top'] * image_height) * 0.9
        x2 = int(boundingBox['Left'] * image_width + boundingBox['Width'] * image_width) * 1.1
        y2 = int(boundingBox['Top'] * image_height + boundingBox['Height'] * image_height) * 1.1

        croppredImage = image.crop((x1,y1,x2,y2))

        # Pasa este imagen temporal a un blob...
        stream = io.BytesIO()
        croppredImage.save(stream, format = 'JPEG')
        binary = stream.getvalue()

        # Para luego pasar este imagen singular por Search Faces by Image
        response = rekognition.search_faces_by_image(
            CollectionId = curso,
            Image = {'Bytes': binary},
            FaceMatchThreshold=70 # minimo nivel de aceptacion
        )
        if len(response['FaceMatches']) == 0:
            print('Alumno no del Curso Detectado')
        else:
            # Agrega FaceId y Similarity del sujeto encontrado al diccionario
            allFaceIds[response['FaceMatches'][0]['Face']['FaceId']] = response['FaceMatches'][0]['Similarity']
    
    return allFaceIds # Entrega diccionario de caras con su similitud


''' Vieja version de Compare, solo revisaba una cara en la imagen
def compare2Collection(curso,encodedimg):
    response = rekognition.search_faces_by_image(
        CollectionId=curso, # nombre del curso
        Image={'Bytes': encodedimg}, # imagen por analizar
        FaceMatchThreshold=10 # minimo nivel de aceptacion
    )

    outputIDs = {}
    for element in response['FaceMatches']:
        outputIDs[element['Face']['FaceId']] = element['Similarity']

    print(response)

    if len(response['FaceMatches']) != 0:
        return outputIDs
        #return response['FaceMatches'][0]['Face']['FaceId'], response['FaceMatches'][0]['Similarity']
    else:
        return {}
'''