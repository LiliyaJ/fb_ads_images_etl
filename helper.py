import os
import requests
import json
from datetime import datetime, timezone, timedelta
from flask import make_response
from google.cloud import storage, bigquery
from google.oauth2 import service_account
import google.auth
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adcreative import AdCreative


# ---------------------- APP TOKEN --------------------------

ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN') #given as a function run variable
APP_ID = os.environ.get('APP_ID') #given as a function run variable
APP_SECRET = os.environ.get('APP_SECRET') #given as a function run variable


# ---------------------- SET UP VERAIBALES --------------------------

# Google Cloud Storage and BigQuery credentials
BIGQUERY_PROJECT = os.environ.get('BIGQUERY_PROJECT')
BIGQUERY_DATASET = os.environ.get('BIGQUERY_DATASET')
BIGQUERY_TABLE = os.environ.get('BIGQUERY_TABLE')
project_id = f'{BIGQUERY_PROJECT}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}'

# ---------------------- INITIALIZING --------------------------

# Initialize Facebook API
FacebookAdsApi.init(APP_ID, APP_SECRET, ACCESS_TOKEN)

### for local debugging
# credentials = service_account.Credentials.from_service_account_file(
#       'fb_image_service_account.json', scopes=[
#           "https://www.googleapis.com/auth/drive",
#           "https://www.googleapis.com/auth/cloud-platform"],
#   )
###
### for cloud functions or cloud run deployment
#Authentication with service account for bigquery
scopes=[
           "https://www.googleapis.com/auth/cloud-platform"]
credentials, _ = google.auth.default(scopes = scopes)

# Initialize Google Cloud Storage client
storage_client = storage.Client(credentials=credentials, project=BIGQUERY_PROJECT)

# Initialize BigQuery client
bigquery_client = bigquery.Client(credentials=credentials, project=BIGQUERY_PROJECT)

def get_creative_details(creative_id):
    try:
        creative = AdCreative(creative_id).api_get(fields=[
            AdCreative.Field.id,
            AdCreative.Field.name,
            AdCreative.Field.object_story_spec,
            AdCreative.Field.image_url,
            AdCreative.Field.image_hash,
            AdCreative.Field.thumbnail_url,
        ])
        return creative
    except Exception as e:
        print(f"Error fetching creative details for ID {creative_id}: {e}")
        return None

def get_ads_images_and_ids(ad_account_id, since_date):
    ad_account = AdAccount(ad_account_id)
    since_datetime = datetime.strptime(since_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)

    try:
        ads = ad_account.get_ads(fields=[
            Ad.Field.id,
            Ad.Field.creative,
            Ad.Field.created_time
        ])
    except Exception as e:
        print(f"Error fetching ads: {e}")
        return []

    images_and_ids = []

    for ad in ads:
        ad_id = ad.get(Ad.Field.id)
        creative_id = ad.get(Ad.Field.creative, {}).get('id')
        created_time = datetime.strptime(ad.get(Ad.Field.created_time), '%Y-%m-%dT%H:%M:%S%z')

        if created_time >= since_datetime and creative_id:
            creative = get_creative_details(creative_id)
            if creative:
                image_url = None
                # Check for direct image URL
                if 'image_url' in creative:
                    image_url = creative['image_url']
                # Check for image URL in object_story_spec -> link_data
                elif ('object_story_spec' in creative and
                      'link_data' in creative['object_story_spec'] and
                      'image_url' in creative['object_story_spec']['link_data']):
                    image_url = creative['object_story_spec']['link_data']['image_url']
                # Check for thumbnail URL
                elif 'thumbnail_url' in creative:
                    image_url = creative['thumbnail_url']

                if image_url:
                    images_and_ids.append((ad_id, creative_id, image_url))
                else:
                    print(f"No image URL found for ad ID: {ad_id}, creative ID: {creative_id}")
            else:
                print(f"Failed to fetch creative details for ad ID: {ad_id}")
        else:
            print(f"No creative ID found for ad ID: {ad_id} for time since {since_datetime}")
    
    return images_and_ids

def download_image(image_url, save_path):
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
        else:
            print(f"Failed to download image from {image_url}")
            return False
    except Exception as e:
        print(f"Error downloading image from {image_url}: {e}")
        return False

def upload_to_gcs(file_path, bucket_name, gcs_path):
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(gcs_path)
        blob.upload_from_filename(file_path)
        print(f"Uploaded {file_path} to gs://{bucket_name}/{gcs_path}")
        return True
    except Exception as e:
        print(f"Error uploading {file_path} to GCS: {e}")
        return False

def insert_metadata_to_bigquery(ad_id, creative_id, gcs_url):
    table_id = f"{BIGQUERY_PROJECT}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}"
    rows_to_insert = [
        {
            u"ad_id": ad_id,
            u"creative_id": creative_id,
            u"gcs_url": gcs_url
        }
    ]

    errors = bigquery_client.insert_rows_json(table_id, rows_to_insert)
    if errors == []:
        print(
            "Loaded {} rows and {} columns to {}".format(
                rows_to_insert.num_rows, len(rows_to_insert.schema), table_id
            ))
    else:
        print(f"Encountered errors while inserting rows: {errors}")