
import boto3
import json
from custom_encode import CustomEncoder
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodbTableName = 'product-inventory'
dynamodb = boto3.resource('dynamodb')
Table = dynamodb.Table(dynamodbTableName)


getMethod = 'GET'
postMethod = 'Post'
patchMethod = 'PATCH'
deleteMethod = 'DELETE'
healthPath = '/health'
productPath = '/product' 
productsPath = '/products'

def Lambda_handler(event, context):
    logger.info(event)
    httpMethod = event['httpMethod']
    path = event['path']

    if httpMethod == getMethod and path == healthPath:
        response = buildResponse(200)
    elif httpMethod == getMethod and path == productPath:
        response = getProduct(event['queryStringParameters']['productid'])
    elif httpMethod == getMethod and path == productsPath:
        response = getProducts()
    elif httpMethod == postMethod and path == productPath:
        response = saveProduct(json.loads(event['body'])),
    elif httpMethod == patchMethod and path == productPath:
        requestBody = json.loads(event['body']),
        response = modifyProduct(requestBody['productId'], requestBody['updatekey'], requestBody['updateValue']) 
    elif httpMethod == deleteMethod and path == productPath:
        requestBody = json.loads(event['body'])
        response = deleteProduct(requestBody['productId']), 
    else:
        response = buildResponse(404,'Not Found')
    return response


def getProduct(productId):
    try:
        response = table.get_item(
            Key={
                'productId': productId
                }
        )
        if 'Item' in response:
         return buildResponse (200, response['Item'])
        else:
         return buildResponse (404,{ 'Message': 'ProductId: %s not found' % productId})

    except:
             logger.exception('Do your custom error handling here. I am just gonna log it out here!!')



def getProducts():
    try:
       response = table.scan()
       result = response['Item']

       while 'LastEvaluateKey' in response:
        response = table.scan(ExclusiveStartKey=response[ 'LastEvaluatedkey']) 
        result.extend(response[ 'Item'])

       body = {
        'products': result

       }
       return buildResponse(200,body)
    except:
          logger.exception('Do your custom error handling here. I am just gonna log it out here!!')

def saveProduct():
    try:
        table.put_item(Item=requestBody)
        body = {
            'Operation': 'SAVE',
            'Message': 'SUCCESS',
            'Item' : requestBody
        }
        return buildResponse(200,body)
    except:
        logger.exception('Do your custom error handling here. I am just gonna log it out here!!')

def modifyProduct(productId,updateKey,updateValue):
   try:
    response = table.update_item(
        Key= {
          'productId': productId
       },
       ExpressionAttributeValue= {
        ':value' : updateValue
       },
       ReturnValues= 'UPDATED_NEW'
    )
    body = {
            'Operation': 'UPDATE',
            'Message': 'SUCCESS',
            'UpdatedAttributes' : response
        }
    return buildResponse(200,body)
   except:
        logger.exception('Do your custom error handling here. I am just gonna log it out here!!')
 

def deleteProduct(productId):
     try:
       response = table.delete_item(
        Key= {
          'productId': productId
          },
        ReturnValues= 'ALL_OLD'
         )
       body = {
            'Operation': 'DELETE',
            'Message': 'SUCCESS',
            'deleteItem' : response
        }
       return buildResponse(200,body)
     except:
        logger.exception('Do your custom error handling here. I am just gonna log it out here!!')
 

     

   



def buildResponse(statusCode,body=None):
    response = {
        'statusCode':statusCode,
          'header' : {
            'Content-type':'appliction/json',
            'Access-Control-Allow-Origin':'*'
        }

    }

    if body is not None:
        response['body'] = json.dumps(body,cls=CustomEncoder)
        return response











        