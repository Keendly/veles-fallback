#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
import json
from random import choice
from string import ascii_uppercase


"""Lambda function entry point """
def handle(event, context):
    if event.get('items') is None:
        event['items'] = \
            json.loads(_fetch(event['s3Items']['bucket'], event['s3Items']['key']))

    articles = _to_extract_result(event['items'])
    return _store(articles)

def _fetch(bucket, key):
    file_name = _random_name()
    file_path = '/tmp/' + file_name
    s3 = boto3.resource('s3')
    s3.meta.client.download_file(bucket, key, file_path)
    f = open(file_path, "rb")
    msg = f.read()
    f.close()
    return msg

def _random_name():
    return ''.join(choice(ascii_uppercase) for i in range(12))

def _to_extract_result(items):
    articles = []
    for item in items:
        for article in item['articles']:
            try:
                articles.append({
                    'url': article['url'],
                    'text': article['content']
                })
            except Exception, e:
                print(e)
                print('Error transforming article: {}', article.get('url'))
    return articles

def _store(articles):
    s3 = boto3.resource('s3')
    key = 'messages/{}'.format(_random_name())
    s3.Bucket('keendly').put_object(Key=key, Body=json.dumps(articles))
    return key
