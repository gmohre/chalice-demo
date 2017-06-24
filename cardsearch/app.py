import json
import urllib2
import base64
import boto3

from chalice import Chalice
from chalice import NotFoundError

app = Chalice(app_name='cardsearch')

REGION = 'us-east-2'
SCRYFALL_API_URL = 'https://api.scryfall.com/cards'

S3 = boto3.client('s3')

BUCKET_KEY =  'custom-cards'
CARD_KEY = 'my-card.json'
CARD_IMAGE = '{}.png'.format(CARD_KEY)
CARD_URL = 'https://s3.{}.amazonaws.com/{}/{}'.format(REGION, BUCKET_KEY, CARD_KEY)
IMAGE_URL = 'https://s3.{}.amazonaws.com/{}/{}'.format(REGION, BUCKET_KEY, CARD_IMAGE)

@app.route('/card', methods=['GET'])
def card_index():
    """
	Output:
		Dict containing a status message, current card json URL, and current card image URL
    """
    return {"status":"OK", "current_card":CARD_URL, "current_image":IMAGE_URL}


@app.route('/card/{key}', methods=['POST'])
def card_post(key):
    """
	Input: 
		raw payload of base64 encoded image
		key to query M:tG Database
	Output:
		Location of image
		Location of card JSON
    """
    body = app.current_request.raw_body if app.current_request._body else None
    image = base64.b64decode(body) if body else None
    

    filename = '{}.png'.format(CARD_KEY)
    card_query_url = '{}/search?q={}'.format(SCRYFALL_API_URL, key)

    try:
	card_query_resp = urllib2.urlopen(card_query_url)
    except:
	return {"status":"Error Card Not Found"}

    card_query_resp = card_query_resp.read()
    card_query_json = json.loads(card_query_resp)
    cards = card_query_json['data']
    card = cards.pop()

    card_data = {
	'name':card.get('name'),
	'card_type':card.get('type_line'),
	'oracle_text':card.get('oracle_text'),
	'power':card.get('power'),
	'toughness':card.get('toughness'),
	'image':IMAGE_URL}
    if image:
        image_s3 = S3.put_object(
       	    Bucket=BUCKET_KEY,
	    ACL='public-read',
	    Key=filename,
            Body=image, 
	    ContentType='image/png')

    card_s3 = S3.put_object(
	Bucket=BUCKET_KEY,
	ACL='public-read',
	Key=CARD_KEY,
	Body=json.dumps(card_data))

    return {'image':IMAGE_URL, 'card':CARD_URL}
