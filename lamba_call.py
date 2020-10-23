import sys
from pip._internal import main

main(['install', '-I', '-q', 'boto3', '--target', '/tmp/', '--no-cache-dir', '--disable-pip-version-check'])
sys.path.insert(0,'/tmp/')

import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    s3 = boto3.resource('s3')
    comprehend = boto3.client('comprehend')
    obj = s3.Object('emails-unredacted', 'email.txt')
    text = obj.get()['Body'].read().decode("utf-8")

    print(boto3.__version__)

    response = comprehend.detect_pii_entities(Text=text,LanguageCode='en')
    
    char_offsets_begin = []
    char_offsets_end = []


    for i in range(len(response['Entities'])):
        if response['Entities'][i]['Type'] == 'CREDIT_DEBIT_NUMBER':
            char_offsets_begin.append(response['Entities'][i]['BeginOffset'])
            char_offsets_end.append(response['Entities'][i]['EndOffset'])
    
    text_redact = (text[:char_offsets_begin[0]] + '#'*(char_offsets_end[0]-char_offsets_begin[0]) + text[char_offsets_end[0]:])
    print(text_redact)
    
    
    s3.Bucket('emails-redacted').put_object(Key='email.txt', Body=text_redact)

    
  
