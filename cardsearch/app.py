import json
import urllib2
import base64
import boto3

from botocore.exceptions import ClientError

from chalice import Chalice
from chalice import NotFoundError

app = Chalice(app_name='cardsearch')
app.debug = True

SCRYFALL_API_URL = 'https://api.scryfall.com/cards'
S3 = boto3.client('s3', region_name='us-east-2')
S3_RESOURCE = boto3.resource('s3', region_name='us-east-2')
BUCKET_KEY = 'custom-cards'
CARD_KEY = 'my-card'

#def _init_bucket():
#    try:
#	S3.meta.client.head_bucket(Bucket='mybucket')
#    except ClientError as e:
#        error_code = int(e.response['Error']['Code'])
#	if error_code == 404:
#            exists = False
#    return bucket, exists


@app.route('/cards', methods=['GET'])
def card_index():
#    bucket, exists = _init_bucket()
#    bucket_keys_json = {[k.key for k in bucket.objects.all()]}
#    if exists:
#	return json.load(bucket_keys_json)
    return "Nope"

@app.route('/cards/text/{query}', methods=['PUT'])
def card_put(query):
    request = app.current_request
    output = S3.put_object(Bucket=BUCKET_KEY, Key=CARD_KEY,
	Body=json.dumps(request.json_body))
    return "No Luck"

@app.route('/card/{key}', methods=['GET'])
def card_get(key):
    try:
	response = S3.get_object(Bucket=BUCKET_KEY, Key=key)
        return json.loads(response['Body'].read())
    except ClientError as e:
        raise NotFoundError(key)
    return "No Luck"

@app.route('/card/{key}', methods=['POST'])#, content_types=['application/octet-stream'])
def card_post(key):
    body = app.current_request.raw_body
    image = base64.b64decode(body)

    filename = '{}.png'.format(CARD_KEY)
    card_url = '{}/search?q={}'.format(SCRYFALL_API_URL, key)

    card_query_resp = urllib2.urlopen(card_url)
    card_query_resp = card_query_resp.read()

    card_query_json = json.loads(card_query_resp)
    cards = card_query_json['data']
    card = cards.pop()

    card_data = {'name':card.get('name'), 'oracle_text':card.get('oracle_text')} if card else {'name':key, 'oracle_text':key}
   

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
    return image_s3


