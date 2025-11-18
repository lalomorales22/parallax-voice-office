"""
MCP HTTP Client Server
Provides HTTP request capabilities for API calls
"""

import logging
import requests
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MCPHTTPClient:
    """
    MCP server for HTTP requests
    Provides safe HTTP client functionality for API calls
    """

    def __init__(self, timeout: int = 30, max_retries: int = 3):
        """
        Initialize HTTP client

        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Parallax-Voice-Office/1.0'
        })
        logger.info(f"HTTP client initialized (timeout: {timeout}s, retries: {max_retries})")

    def get(self, url: str, params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Perform GET request

        Args:
            url: URL to request
            params: Query parameters
            headers: Additional headers

        Returns:
            Response data
        """
        return self._request('GET', url, params=params, headers=headers)

    def post(self, url: str, data: Optional[Dict[str, Any]] = None,
             json: Optional[Dict[str, Any]] = None,
             headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Perform POST request

        Args:
            url: URL to request
            data: Form data
            json: JSON data
            headers: Additional headers

        Returns:
            Response data
        """
        return self._request('POST', url, data=data, json=json, headers=headers)

    def put(self, url: str, data: Optional[Dict[str, Any]] = None,
            json: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Perform PUT request

        Args:
            url: URL to request
            data: Form data
            json: JSON data
            headers: Additional headers

        Returns:
            Response data
        """
        return self._request('PUT', url, data=data, json=json, headers=headers)

    def delete(self, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Perform DELETE request

        Args:
            url: URL to request
            headers: Additional headers

        Returns:
            Response data
        """
        return self._request('DELETE', url, headers=headers)

    def _request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """
        Perform HTTP request with retries

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            url: URL to request
            **kwargs: Additional request arguments

        Returns:
            Response data dictionary
        """
        try:
            # Validate URL
            if not url.startswith(('http://', 'https://')):
                return {
                    "status": "error",
                    "message": "URL must start with http:// or https://"
                }

            # Prepare request
            request_kwargs = {
                'timeout': self.timeout,
                **kwargs
            }

            # Perform request with retries
            last_error = None
            for attempt in range(self.max_retries):
                try:
                    response = self.session.request(method, url, **request_kwargs)

                    # Parse response
                    result = {
                        "status": "success",
                        "operation": "http_request",
                        "method": method,
                        "url": url,
                        "status_code": response.status_code,
                        "headers": dict(response.headers),
                        "requested_at": datetime.now().isoformat()
                    }

                    # Try to parse as JSON
                    try:
                        result['data'] = response.json()
                        result['content_type'] = 'json'
                    except:
                        result['data'] = response.text
                        result['content_type'] = 'text'

                    # Add success flag
                    result['success'] = response.status_code < 400

                    if not result['success']:
                        result['error'] = f"HTTP {response.status_code}: {response.reason}"

                    return result

                except requests.exceptions.Timeout:
                    last_error = f"Request timeout after {self.timeout}s (attempt {attempt + 1}/{self.max_retries})"
                    logger.warning(last_error)

                except requests.exceptions.ConnectionError as e:
                    last_error = f"Connection error: {str(e)} (attempt {attempt + 1}/{self.max_retries})"
                    logger.warning(last_error)

                except requests.exceptions.RequestException as e:
                    last_error = f"Request error: {str(e)}"
                    logger.error(last_error)
                    break  # Don't retry on general request errors

            # All retries failed
            return {
                "status": "error",
                "message": last_error or "Request failed after all retries"
            }

        except Exception as e:
            logger.error(f"HTTP client error: {e}")
            return {
                "status": "error",
                "message": f"HTTP client error: {str(e)}"
            }

    def download(self, url: str, filepath: str) -> Dict[str, Any]:
        """
        Download file from URL

        Args:
            url: URL to download from
            filepath: Local path to save file

        Returns:
            Download result
        """
        try:
            response = self.session.get(url, timeout=self.timeout, stream=True)
            response.raise_for_status()

            # Download in chunks
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            file_size = Path(filepath).stat().st_size

            return {
                "status": "success",
                "operation": "download",
                "url": url,
                "filepath": filepath,
                "size": file_size,
                "content_type": response.headers.get('content-type', 'unknown')
            }

        except Exception as e:
            logger.error(f"Download error: {e}")
            return {
                "status": "error",
                "message": f"Download failed: {str(e)}"
            }

    def get_headers(self, url: str) -> Dict[str, Any]:
        """
        Get headers from URL (HEAD request)

        Args:
            url: URL to check

        Returns:
            Headers information
        """
        try:
            response = self.session.head(url, timeout=self.timeout)

            return {
                "status": "success",
                "operation": "get_headers",
                "url": url,
                "status_code": response.status_code,
                "headers": dict(response.headers)
            }

        except Exception as e:
            logger.error(f"HEAD request error: {e}")
            return {
                "status": "error",
                "message": f"Failed to get headers: {str(e)}"
            }

    def shutdown(self):
        """Close the HTTP session"""
        self.session.close()


# Import Path for download method
from pathlib import Path
