# Facebook Ads Image Processing and Visualization Project

This project processes Facebook Ads images, uploads them to Google Cloud Storage, and stores metadata in BigQuery. It also includes a SQL script for creating a consumer table in Looker Studio and instructions for preparing a dashboard.

## Project Structure

- **`main.py`**: Contains the `main(request)` function optimized for use in Google Cloud Functions. This function is responsible for the daily update of Facebook Ads images and their associated metadata.
- **`helper.py`**: Includes all the helper functions needed to:

  - Fetch ads data from Facebook.
  - Download ad images.
  - Upload images to Google Cloud Storage.
  - Insert metadata into BigQuery.

- **`requirements.txt`**: Lists all the Python libraries needed for running this project.

- **`visualize.sql`**: A SQL script to prepare a consumer table in BigQuery. This table joins the native Facebook data with the table created by this project on the `AdId` field. It also converts `gs://` URLs to `https://storage.cloud.google.com/...` for easier access in Looker Studio.

- **`lookerstudio.txt`**: Instructions on how to prepare a dashboard in Looker Studio, using the data from BigQuery.

## Setup Guide

### 1. Google Cloud Setup

#### Google Cloud Functions

1. **Create a Google Cloud Function**:

   - Go to the Google Cloud Console and navigate to **Cloud Functions**.
   - Click **Create Function**.
   - Use the `main.py` file as the entry point by setting the function to use `main` as the function name.
   - Upload the `helper.py` and `requirements.txt` files.
   - Set your environment variables (like `ACCESS_TOKEN`, `APP_ID`, and `APP_SECRET`) in the **Environment variables** section.

2. **Deploy the Function**:
   - Review and deploy the function. The function will run daily, processing and uploading Facebook Ads images.

#### Google Cloud Storage

1. **Create a Google Cloud Storage Bucket**:
   - In the Google Cloud Console, go to **Storage**.
   - Click **Create Bucket**.
   - Name your bucket and choose your desired settings (location, storage class, etc.).

#### BigQuery

1. **Create a BigQuery Dataset**:

   - Go to the BigQuery section in the Google Cloud Console.
   - Click **Create Dataset** and name it appropriately (e.g., `meta_integration`).

2. **Create a BigQuery Table**:
   - Within your dataset, create a table where the metadata will be stored (e.g., `ads_ids_images_urls`).
   - Define the schema to match the structure of the data being inserted by the Cloud Function.

### 2. Data Visualization in Looker Studio

#### SQL Script Execution

1. **Run the `visualize.sql` Script**:
   - In BigQuery, navigate to your dataset.
   - Open the SQL workspace and schedule the SQL script from `visualize.sql` to create and update the consumer table.

#### Looker Studio Dashboard

1. **Set Up Looker Studio**:
   - Open Looker Studio (formerly Data Studio).
   - Create a new data source linked to your BigQuery dataset.
   - Follow the instructions in `lookerstudio.txt` to set up your dashboard, making use of the data from your consumer table.

## Usage

Once everything is set up, the Google Cloud Function will run daily, processing new Facebook Ads images, storing them in Google Cloud Storage, and updating the metadata in BigQuery. The Looker Studio dashboard will automatically reflect these updates, providing an up-to-date visualization of your Facebook Ads data.
