import boto3
dynamodb = boto3.client('dynamodb')

def deleteTable(tableName):
    tableCheck = dynamodb.list_tables()
    print(tableCheck['TableNames'])

    if (len(tableCheck['TableNames']) != 0 and tableName in tableCheck['TableNames']):
        response = dynamodb.delete_table(TableName = tableName)
        print('La tabla ' + tableName + ' ha sido borrada!')
    else:
        print('La tabla ' + tableName + ' no existe!')


def updateIndex(tableName,faceID,fullname):
    response = dynamodb.put_item(
        TableName = tableName,
        Item = {
            'RekognitionId': {
                'S': faceID
            },
            'FullName': {
                'S': fullname
            }
        }
    )


def getName(tableName, faceID):
    response = dynamodb.get_item(
        TableName = tableName,
        Key = {
            'RekognitionId': {
                'S': faceID,
            }
        },
        ProjectionExpression = 'FullName'
    )

    return response['Item']['FullName']['S'].replace('_',' ')


def createDynamoTable(tableName):
    tableCheck = dynamodb.list_tables()
    print(tableName, tableCheck['TableNames'])

    if len(tableCheck['TableNames']) == 0 or tableName not in tableCheck['TableNames']:
        response = dynamodb.create_table(
            AttributeDefinitions=[
                {
                    'AttributeName': 'RekognitionId',
                    'AttributeType': 'S'
                }
            ],
            TableName=tableName,
            KeySchema = [
                {
                    'AttributeName': 'RekognitionId',
                    'KeyType': 'HASH'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print('Dynamo Table ' + tableName + ' fue creada exitosamente!')
    else:
        print('La Tabla ' + tableName + ' ya existe!')