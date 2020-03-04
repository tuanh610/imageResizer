import json
import datetime
import boto3
import PIL
from PIL import Image
from io import BytesIO
import os

class URLIncorrect(Exception):
    pass

def call(event, context):
    try:
        print(event["pathParameters"])
        data = event["pathParameters"]["proxy"]
        #first: let remove "/" in the last place if any:
        if data[-1] == "/":
            data = data[:-1]
        #second: let seperate the name and the path:
        path = ""
        if "/" in data:
            idx = data.rfind("/")
            path = data[:idx]
            name = data[idx+1:]
        else:
            path = ""
            name = data
        #third: extract the size, original file name
        idx = name.find('_')
        if idx < 0 or (not name.endswith('jpg') and not name.endswith('png')):
            raise URLIncorrect
        size = name[:idx]
        key = name[idx+1:]

        #last: check valid size
        size_split = size.split('x')
        if len(size_split) != 2 or not size_split[0].isnumeric() or not size_split[1].isnumeric():
            raise URLIncorrect

        print("Key: {}".format(key))
        print("Size: {}".format(size))
        print("")
        width = int(size_split[0])
        height = int(size_split[1])
        result_url = resize_image(os.environ["BUCKET"], key, width, height, path)

        response = {
            "statusCode": 301,
            "body": "",
            "headers": {
                "location": result_url
            }
        }
    except:
        response = {
            "statusCode": 404,
            "body": "",
        }

    print(response)
    return response

def resize_image(bucket_name, key, width, height, path):
    s3 = boto3.resource('s3')
    original_key = path + "/" + key
    print("Original Path: {}".format(original_key))

    obj = s3.Object(
        bucket_name=bucket_name,
        key=original_key,
    )

    obj_body = obj.get()['Body'].read()
    img = Image.open(BytesIO(obj_body))
    img = img.resize( width, height, PIL.Image.ANTIALIAS)
    buffer = BytesIO()
    if key.endswith('jpg'):
        img.save(buffer, 'JPEG')
    else:
        img.save(buffer, 'PNG')
    buffer.seek(0)

    resize_key =  "{path}/{width}x{height}_{name}".format(path=path, name=key, width=width, height=height)

    obj = s3.Object(
        bucket_name=bucket_name,
        key=resize_key
    )
    if key.endswith('jpg'):
        obj.put(Body=buffer, ContentType='image/jpeg')
    else:
        obj.put(Body=buffer, ContentType='image/png')

    #Now make the object public
    object_acl = s3.ObjectAcl(bucket_name, resize_key)
    response = object_acl.put(ACL='public-read')
    print(response)
    print("Finish with resize image")
    link = resized_image_url(resize_key, bucket_name, os.environ["AWS_REGION"])
    print("Link: {}".format(link))
    return link

def resized_image_url(resized_key, bucket, region):
    return "https://s3-{region}.amazonaws.com/{bucket}/{resized_key}".format(bucket=bucket, region=region, resized_key=resized_key)




