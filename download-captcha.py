"""
    This script is to download captcha from ireserve.ntl.edu.tw
"""

import requests
import logging
import os
from datetime import datetime
import time
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)
session = boto3.Session()

def request_captcha(
    _base_url: str,
    _request_captcha_route: str,
    _request_payload: str
) -> str:
    """
        This function is to request captcha
    """
    try:
        headers = {
            'Content-Type': 'text/plain'
        }
        request_captcha_response = requests.post(
            f'{_base_url}{_request_captcha_route}',
            data = _request_payload,
            headers = headers
        )
        cpatcha_url_string = request_captcha_response.text.splitlines()[-2]
        return cpatcha_url_string
    except Exception as error:
        logger.error(error)
        raise ValueError('Error While Request Captcha.')

def format_cpatcha_url(
    _captcha_url_string: str
):
    """
        This function is to format captcha url
    """
    try:
        captcha_url = _captcha_url_string \
            .split(',')[-1][1:-3]
        return captcha_url
    except Exception as error:
        logger.error(error)
        raise ValueError('Error While Format Captcha Url.')

def download_captcha_image(
    _base_url: str,
    _captcha_url: str
):
    """
        This function is to download captcha image
    """
    try:
        captcha_response = requests.get(
            f'{_base_url}{_captcha_url}',
            allow_redirects = True
        )
        return captcha_response.content
    except Exception as error:
        logger.error(error)
        raise ValueError('Error While Download Captcha Image.')

def upload_image_to_s3(
    _captcha_response: str,
    _session: boto3.Session,
    _s3_bucket_name: str,
    _s3_prefix: str
):
    """
        This function is to upload image to s3
    """
    try:
        file_name = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')
        s3_client = _session.client('s3')
        s3_client.put_object(
            Body = _captcha_response,
            Bucket = _s3_bucket_name,
            Key = f'{_s3_prefix}/{file_name}.png'
        )
        print(f'{_s3_prefix}/{file_name}.png uploaded.')
    except Exception as error:
        logger.error(error)
        raise ValueError('Error While Upload Image To S3.')

def main(eveny, context):
    """
        This is main function
    """
    try:
        images_folder = 'images'
        s3_bucket_name = ''
        s3_prefix = ''
        base_url = 'http://ireserve.ntl.edu.tw'
        request_captcha_route = '/sm/dwr/call/plaincall/LoginWebController.loadCaptchaImage.dwr'
        request_payload = """
callCount=1\r\n
windowName=\r\n
nextReverseAjaxIndex=0\r\n
c0-scriptName=LoginWebController\r\n
c0-methodName=loadCaptchaImage\r\n
c0-id=0\r\n
batchId=29\r\n
instanceId=0\r\n
page=%2Fsm%2Fhome_web.do\r\n
scriptSessionId=GE44WuqiL92h6vJZNEg3rDMubxn/2h8vbxn-H$P4HI8Os
"""
        cpatcha_url_string = request_captcha(
            base_url,
            request_captcha_route,
            request_payload
        )
        cpatcha_url = format_cpatcha_url(
            cpatcha_url_string
        )
        captcha_response = download_captcha_image(
            base_url,
            cpatcha_url
        )
        upload_image_to_s3(
            captcha_response,
            session,
            s3_bucket_name,
            s3_prefix
        )
    except Exception as error:
        raise

if __name__ == '__main__':
    main()