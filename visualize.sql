-- to prepare a table for the visualisation 

CREATE OR REPLACE TABLE `YOUR_BIGQUERY_PROJECT.YOUR_DATASET.YOUR_CONSUMER_TABLE` AS(
SELECT 
DateStart date,
CampaignName,
AdSetName,
AdId,
AdName,
-- make the address readable from internet
REPLACE(gcs_url, 'gs://', 'https://storage.cloud.google.com/') Image,
Impressions,
Clicks,
OutboundClicks,
Spend
FROM `YOUR_BIGQUERY_PROJECT.YOUR_DATASET.YOUR_FB_DATA_TABLE` t1 join `YOUR_BIGQUERY_PROJECT.YOUR_DATASET.YOUR_FB_IMAGES_TABLE` t2 ON t1.AdId = t2.ad_id
)