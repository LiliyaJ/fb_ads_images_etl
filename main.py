import os
from flask import make_response
import json
from datetime import datetime, timezone, timedelta
from helper import get_ads_images_and_ids
from helper import download_image
from helper import upload_to_gcs
from helper import insert_metadata_to_bigquery


AD_ACCOUNT_ID = os.environ.get('AD_ACCOUNT_ID')
GCS_BUCKET_NAME = os.environ.get('GCS_BUCKET_NAME')

def main(request):
    yesterday = datetime.now() - timedelta(days=1)
    since_date = yesterday.strftime('%Y-%m-%d')
    if not since_date:
        return make_response(json.dumps({'error': 'since_date parameter is required'}), 400)

    images_and_ids = get_ads_images_and_ids(AD_ACCOUNT_ID, since_date)

    for ad_id, creative_id, image_url in images_and_ids:
        # Download the image
        image_name = f"{ad_id}.jpg"  # Or extract the file name from the URL
        if download_image(image_url, image_name):
            # Upload the image to GCS
            gcs_path = f"ads_images/{image_name}"
            if upload_to_gcs(image_name, GCS_BUCKET_NAME, gcs_path):
                # Construct the GCS URL
                gcs_url = f"gs://{GCS_BUCKET_NAME}/{gcs_path}"
                # Insert metadata into BigQuery
                insert_metadata_to_bigquery(ad_id, creative_id, gcs_url)
            # Remove the local file after upload
            os.remove(image_name)

    return make_response(json.dumps({'result': 'Successfully uploaded the data'}))