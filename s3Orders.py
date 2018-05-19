import boto3
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