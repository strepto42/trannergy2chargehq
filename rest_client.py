"""
REST client for sending inverter data to external APIs
Handles rate limiting and error handling for REST endpoints

        This program is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import time
import threading
import requests
import config as cfg

# Logging
import __main__
import logging
import os
try:
    script = os.path.basename(__main__.__file__)
    script = os.path.splitext(script)[0]
except AttributeError:
    script = "rest_client"
logger = logging.getLogger(script + "." + __name__)


class ChargeHQClient:
    """
    REST client for ChargeHQ API
    Handles rate limiting to prevent sending data more than once per minute
    """

    def __init__(self):
        """
        Initialize the ChargeHQ client
        """
        logger.debug(">>")
        self._last_send_time = 0
        self._send_interval = cfg.REST_MAX_FREQUENCY_SECONDS  # Use configurable frequency
        self._lock = threading.Lock()
        self._api_url = "https://api.chargehq.net/api/public/push-solar-data"
        logger.debug("<<")

    def should_send_data(self):
        """
        Check if enough time has passed since last send

        Returns:
            bool: True if data should be sent, False otherwise
        """
        with self._lock:
            current_time = time.time()
            time_since_last_send = current_time - self._last_send_time
            return time_since_last_send >= self._send_interval

    def send_solar_data(self, production_kw, consumption_kw=1.0):
        """
        Send solar data to ChargeHQ API

        Args:
            production_kw (float): Solar production in kW
            consumption_kw (float): Energy consumption in kW (defaults to 1.0)

        Returns:
            bool: True if data was sent successfully, False otherwise
        """
        logger.debug(">>")

        if not self.should_send_data():
            logger.debug(f"Rate limiting: skipping send (last send was {time.time() - self._last_send_time:.1f}s ago)")
            return False

        if not cfg.CHARGEHQ_APIKEY:
            logger.warning("ChargeHQ API key not configured, skipping REST send")
            return False

        # Calculate net import (negative means exporting)
        net_import_kw = consumption_kw - production_kw

        # Prepare the data payload
        payload = {
            "apiKey": cfg.CHARGEHQ_APIKEY,
            "siteMeters": {
                "consumption_kw": consumption_kw,
                "net_import_kw": net_import_kw,
                "production_kw": production_kw
            }
        }

        try:
            logger.info(f"Sending solar data to ChargeHQ: production={production_kw}kW, consumption={consumption_kw}kW, net_import={net_import_kw}kW")

            response = requests.post(
                self._api_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10  # 10 second timeout
            )

            if response.status_code == 200:
                logger.info("Successfully sent data to ChargeHQ")
                with self._lock:
                    self._last_send_time = time.time()
                return True
            else:
                logger.error(f"ChargeHQ API error: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.Timeout:
            logger.error("Timeout sending data to ChargeHQ API")
            return False
        except requests.exceptions.ConnectionError:
            logger.error("Connection error sending data to ChargeHQ API")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error sending data to ChargeHQ API: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending data to ChargeHQ API: {e}")
            return False
        finally:
            logger.debug("<<")

    def __del__(self):
        logger.debug("ChargeHQ client destroyed")
