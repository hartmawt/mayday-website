"""
Google My Business API integration for fetching reviews and ratings
Replaces Playwright-based scraping with official API calls
"""
import os
import aiohttp
import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class GoogleBusinessAPI:
    """
    Handles Google My Business API authentication and data fetching
    """

    def __init__(self):
        self.client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        self.refresh_token = os.getenv('GOOGLE_REFRESH_TOKEN')

        # Validate required environment variables
        if not all([self.client_id, self.client_secret, self.refresh_token]):
            raise ValueError(
                "Missing required environment variables: "
                "GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN"
            )

    async def get_access_token(self) -> str:
        """
        Get a new access token using the refresh token
        """
        url = 'https://oauth2.googleapis.com/token'
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token'
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, data=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Failed to get access token: {response.status} - {error_text}")
                        raise Exception(f"Token refresh failed: {response.status}")

                    data = await response.json()
                    access_token = data.get('access_token')

                    if not access_token:
                        logger.error(f"No access token in response: {data}")
                        raise Exception("No access token received")

                    logger.info("Successfully obtained access token")
                    return access_token

            except Exception as e:
                logger.error(f"Error getting access token: {e}")
                raise

    async def get_account_and_location_ids(self, token: str) -> tuple[str, str]:
        """
        Get account and location IDs automatically
        Returns (account_id, location_id) tuple
        """
        headers = {'Authorization': f'Bearer {token}'}

        async with aiohttp.ClientSession() as session:
            try:
                # Get Account
                acc_url = "https://mybusinessaccountmanagement.googleapis.com/v1/accounts"
                async with session.get(acc_url, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Failed to get accounts: {response.status} - {error_text}")
                        raise Exception(f"Failed to get accounts: {response.status}")

                    acc_data = await response.json()
                    if not acc_data.get('accounts'):
                        raise Exception("No accounts found")

                    account_name = acc_data['accounts'][0]['name']
                    account_id = account_name.split('/')[-1]
                    logger.info(f"Found account: {account_id}")

                # Get Location
                loc_url = f"https://mybusinessbusinessinformation.googleapis.com/v1/{account_name}/locations?readMask=name,title"
                async with session.get(loc_url, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Failed to get locations: {response.status} - {error_text}")
                        raise Exception(f"Failed to get locations: {response.status}")

                    loc_data = await response.json()
                    if not loc_data.get('locations'):
                        raise Exception("No locations found")

                    location_name = loc_data['locations'][0]['name']
                    location_id = location_name.split('/')[-1]
                    logger.info(f"Found location: {location_id}")

                return account_id, location_id

            except Exception as e:
                logger.error(f"Error getting account/location IDs: {e}")
                raise

    async def fetch_all_reviews(self) -> dict[str, Any]:
        """
        Fetch all reviews using the Google My Business API
        Returns data in format compatible with existing website code
        """
        try:
            # Get access token
            token = await self.get_access_token()

            # Get account and location IDs
            acc_id, loc_id = await self.get_account_and_location_ids(token)

            all_reviews = []
            next_page_token = None
            headers = {'Authorization': f'Bearer {token}'}

            logger.info(f"Starting review fetch for Account {acc_id}, Location {loc_id}")

            async with aiohttp.ClientSession() as session:
                while True:
                    # Construct the URL with the pageToken if we have one
                    url = f"https://mybusiness.googleapis.com/v4/accounts/{acc_id}/locations/{loc_id}/reviews"
                    params = {'pageSize': 50}  # Max allowed per request
                    if next_page_token:
                        params['pageToken'] = next_page_token

                    async with session.get(url, headers=headers, params=params) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            logger.error(f"Failed to fetch reviews: {response.status} - {error_text}")
                            raise Exception(f"Failed to fetch reviews: {response.status}")

                        response_data = await response.json()

                    # Add the reviews from this page to our main list
                    current_page_reviews = response_data.get('reviews', [])
                    all_reviews.extend(current_page_reviews)

                    logger.info(f"Collected {len(all_reviews)} reviews so far...")

                    # Check if there is another page to fetch
                    next_page_token = response_data.get('nextPageToken')
                    if not next_page_token:
                        break  # No more pages left!

            logger.info(f"Successfully fetched {len(all_reviews)} reviews from API")

            # Transform data to match website expectations
            all_transformed_reviews = []
            filtered_reviews = []  # For display (5-star only)
            total_rating = 0
            rating_count = 0

            # Map star rating strings to numbers
            rating_map = {
                'ONE': 1,
                'TWO': 2,
                'THREE': 3,
                'FOUR': 4,
                'FIVE': 5
            }

            for review in all_reviews:
                # Extract relevant data from API response
                rating_str = review.get('starRating', 'NOT_SPECIFIED')
                rating = rating_map.get(rating_str, 0)

                if rating > 0:
                    total_rating += rating
                    rating_count += 1

                # Format date for display
                create_time = review.get('createTime', '')
                formatted_date = ''
                create_datetime = None

                if create_time:
                    try:
                        # Convert ISO timestamp to readable format and keep datetime for sorting
                        create_datetime = datetime.fromisoformat(create_time.replace('Z', '+00:00'))
                        formatted_date = create_datetime.strftime('%B %d, %Y')
                    except Exception:
                        formatted_date = create_time

                review_text = review.get('comment', '').strip()

                transformed_review = {
                    'author': review.get('reviewer', {}).get('displayName', 'Anonymous'),
                    'rating': rating,
                    'text': review_text,
                    'date': formatted_date,
                    'relative_time': formatted_date,  # Some parts of the site may expect this
                    'source': 'google_business_api',
                    'create_datetime': create_datetime  # For sorting
                }
                all_transformed_reviews.append(transformed_review)

                # Filter for display: only 5-star reviews with substantial text (like the old scraping logic)
                if rating == 5 and review_text and len(review_text) > 20:
                    filtered_reviews.append(transformed_review)

            # Sort filtered reviews by date (most recent first)
            filtered_reviews.sort(key=lambda x: x.get('create_datetime') or datetime.min, reverse=True)

            # Limit to top 10 recent 5-star reviews
            display_reviews = filtered_reviews[:10]

            # Remove the datetime field from display reviews (not needed in final output)
            for review in display_reviews:
                review.pop('create_datetime', None)

            # Calculate average rating from all reviews
            avg_rating = (total_rating / rating_count) if rating_count > 0 else None

            logger.info(f"Filtered {len(filtered_reviews)} five-star reviews from {len(all_reviews)} total reviews, showing top 10")

            return {
                "reviews": display_reviews,  # Only recent 5-star reviews for display
                "total_found": len(all_reviews),  # Total reviews from API
                "filtered_count": len(filtered_reviews),  # Total 5-star reviews with text
                "displayed_count": len(display_reviews),  # Actually returned (max 10)
                "rating": avg_rating,  # Average of all reviews
                "review_count": len(all_reviews),  # Total review count
                "source": "google_business_api",
                "fetched_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error fetching reviews from Business API: {e}")
            return {
                "reviews": [],
                "total_found": 0,
                "rating": None,
                "review_count": None,
                "source": "api_error",
                "error": str(e)
            }

    async def get_rating_summary(self) -> dict[str, Any]:
        """
        Get just the rating summary (faster than fetching all reviews)
        This can be used for the rating API endpoint
        """
        try:
            # For now, we'll get this from the full review fetch
            # In the future, this could be optimized to use a different endpoint
            # if Google provides one specifically for ratings
            review_data = await self.fetch_all_reviews()

            return {
                "rating": review_data.get("rating"),
                "review_count": review_data.get("review_count"),
                "source": review_data.get("source"),
                "fetched_at": review_data.get("fetched_at")
            }

        except Exception as e:
            logger.error(f"Error getting rating summary from Business API: {e}")
            return {
                "rating": None,
                "review_count": None,
                "source": "api_error",
                "error": str(e)
            }