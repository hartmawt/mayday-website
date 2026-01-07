import os
import requests
import json

def get_new_access_token():
    url = 'https://oauth2.googleapis.com/token'
    payload = {
        'client_id': os.getenv('CLIENT_ID'),
        'client_secret': os.getenv('CLIENT_SECRET'),
        'refresh_token': os.getenv('REFRESH_TOKEN'),
        'grant_type': 'refresh_token'
    }
    response = requests.post(url, data=payload)
    return response.json().get('access_token')

def get_auto_ids(token):
    headers = {'Authorization': f'Bearer {token}'}
    # 1. Get Account
    acc_url = "https://mybusinessaccountmanagement.googleapis.com/v1/accounts"
    acc_data = requests.get(acc_url, headers=headers).json()
    account_name = acc_data['accounts'][0]['name']
    
    # 2. Get Location
    loc_url = f"https://mybusinessbusinessinformation.googleapis.com/v1/{account_name}/locations?readMask=name,title"
    loc_data = requests.get(loc_url, headers=headers).json()
    location_name = loc_data['locations'][0]['name']
    
    return account_name.split('/')[-1], location_name.split('/')[-1]

def fetch_all_reviews():
    token = get_new_access_token()
    acc_id, loc_id = get_auto_ids(token)
    
    all_reviews = []
    next_page_token = None
    
    print(f"🔄 Starting full download for Account {acc_id}...")

    while True:
        # Construct the URL with the pageToken if we have one
        url = f"https://mybusiness.googleapis.com/v4/accounts/{acc_id}/locations/{loc_id}/reviews"
        params = {'pageSize': 50} # Max allowed per request
        if next_page_token:
            params['pageToken'] = next_page_token
            
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(url, headers=headers, params=params).json()
        
        # Add the reviews from this page to our main list
        current_page_reviews = response.get('reviews', [])
        all_reviews.extend(current_page_reviews)
        
        print(f"   Collected {len(all_reviews)} reviews so far...")

        # Check if there is another page to fetch
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break # No more pages left!

    print(f"\n✅ SUCCESS: Total of {len(all_reviews)} reviews retrieved.")
    
    # Optional: Save them all to a JSON file for your website
    with open('all_reviews.json', 'w') as f:
        json.dump(all_reviews, f, indent=4)
    print("💾 Saved all reviews to all_reviews.json")

if __name__ == "__main__":
    fetch_all_reviews()