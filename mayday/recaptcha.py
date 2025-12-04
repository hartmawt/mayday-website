import os
import json
from urllib.parse import urlencode
from urllib.request import urlopen, Request

from mayday.logger import logger

RECAPTCHA_SECRET_KEY = os.environ.get("RECAPTCHA_SECRET_KEY")
RECAPTCHA_SITE_KEY = os.environ.get("RECAPTCHA_SITE_KEY")


async def verify_recaptcha(token, remote_ip=None, expected_action=None, min_score=0.5):
    """Verify reCAPTCHA v3 token with Google's API"""
    if not RECAPTCHA_SECRET_KEY:
        logger.warning("RECAPTCHA_SECRET_KEY not configured, skipping verification")
        return False

    if not token:
        logger.warning("No reCAPTCHA token provided")
        return False

    data = {
        'secret': RECAPTCHA_SECRET_KEY,
        'response': token,
    }

    if remote_ip:
        data['remoteip'] = remote_ip

    try:
        url = 'https://www.google.com/recaptcha/api/siteverify'
        req_data = urlencode(data).encode('utf-8')
        request = Request(url, data=req_data)

        with urlopen(request) as response:
            result = json.loads(response.read().decode('utf-8'))

        success = result.get('success', False)
        score = result.get('score', 0.0)
        action = result.get('action', '')

        if not success:
            error_codes = result.get('error-codes', [])
            logger.warning(f"reCAPTCHA verification failed: {error_codes}")
            return False

        if expected_action and action != expected_action:
            logger.warning(f"reCAPTCHA action mismatch: expected '{expected_action}', got '{action}'")
            return False

        if score < min_score:
            logger.warning(f"reCAPTCHA score too low: {score} (minimum: {min_score})")
            return False

        logger.info(f"reCAPTCHA verification successful: score={score}, action={action}")
        return True

    except Exception as e:
        logger.error(f"reCAPTCHA verification error: {e}")
        return False


def get_recaptcha_site_key():
    """Get the reCAPTCHA site key for frontend use"""
    return RECAPTCHA_SITE_KEY