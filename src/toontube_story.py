import re
import requests

from config import logger


class ToonTubeStory:
    def __init__(self, url):
        self.url = url

    def get_pages_from_reader(self):
        try:
            # Make the HTTP GET request
            response = requests.get(self.url)
            response.raise_for_status()  # Raises an exception for HTTP errors

            # Get the response text
            text = response.text

            # Define the base pattern to search for
            base_pattern = 'https://toontube.imgix.net/PAGE'

            # Create a regex pattern to capture the entire URL
            # This pattern captures the URL starting with the base pattern and ending at a standard URL boundary
            url_pattern = re.escape(base_pattern) + r'[^\s\'"<>]*'

            # Find all occurrences of the complete URL
            matches = re.findall(url_pattern, text)

            # Process each match to remove the part after '&'
            processed_matches = []
            for match in matches:
                # Split the URL at '&' and take the first part
                processed_url = match.split('&')[0]
                processed_matches.append(processed_url)

            return list(set(processed_matches))
        except Exception:
            raise RuntimeError(f"Couldn't get pages from toontube reader: {self.url}")
