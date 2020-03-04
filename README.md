This is image resizing project which do resize image on the go with:
Python3.8
AWS lambda 
AWS S3
AWS API Gateway
Deployed with serverless 

The endpoint to consume this is: https://XXXXXX.execute-api.ap-southeast-1.amazonaws.com/dev/{proxy+}

XXXXX: is the API endpoint you have

{proxy+}: path/to/image/[size]_[imagename]

size: wxh such as "250x350" 

imagename: should be fullname like "cat.jpg"

This currently will only works with jpeg and png file.