import os
from google.cloud import storage
from google.cloud import resourcemanager

from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv

import freesound

from config import LIB_DIRECTORY, BACKGROUND_MUSIC_BUCKET_NAME

# from src.video_maker import LIB_DIRECTORY

load_dotenv()  # This loads the variables from '.env' into the environment

AUDIO_DIRECTORY_PATH = LIB_DIRECTORY / 'background_music'


class GetBackgroundMusic:
    SEARCH_TERMS = [
        # "Cinematic orchestral music",
        "Epic adventure soundtrack",
        "Mysterious ambient tracks",
        "Upbeat electronic anime theme",
        "Dramatic suspense music",
        "Chill lo-fi hip hop",
        "Heroic battle music",
        "Fantasy world background",
        "Dark cyberpunk tracks",
        "Traditional Japanese instrumental",
        "Soothing nature soundscape",
        "Retro 80s synthwave",
        "Futuristic sci-fi ambience",
        "Intense action score",
        "Emotional piano melodies",
        "Quirky comedy tunes",
        "Romantic strings serenade",
        "Creepy horror music",
        "Medieval folk music",
        "Powerful rock anthem",
        "Mystical fairy tale music",
        "Space exploration theme",
        "Vintage jazz background",
        "Uplifting motivational tracks",
        "Sad, reflective acoustic",
        "Steampunk adventure soundtrack",
        "Underwater ambience music",
        "High energy dance beats",
        "Gentle, calming meditation music",
        "World music fusion"
    ]

    def __init__(self):
        client_id = os.getenv("FREESOUND_CLIENT_ID")
        client_secret = os.getenv("FREESOUND_API_KEY")
        #
        # # do the OAuth dance
        oauth = OAuth2Session(client_id)

        authorization_url, state = oauth.authorization_url(
            "https://freesound.org/apiv2/oauth2/authorize/"
        )
        print(f"Please go to {authorization_url} and authorize access.")

        authorization_code = input("Please enter the authorization code:")
        oauth_token = oauth.fetch_token(
            "https://freesound.org/apiv2/oauth2/access_token/",
            authorization_code,
            client_secret=client_secret,
        )

        self.client = freesound.FreesoundClient()
        self.client.set_token(oauth_token["access_token"], "oauth")

    def get(self):
        for term in self.SEARCH_TERMS:
            results = self.client.text_search(query=term, fields="id,name,previews")

            for sound in results:
                try:
                    sound.retrieve(str(AUDIO_DIRECTORY_PATH), sound.name + ".wav")
                    print('retrieved X')
                except Exception:
                    pass

    @staticmethod
    def upload_to_gcs():
        if os.path.exists(str(AUDIO_DIRECTORY_PATH)):
            storage_client = storage.Client()
            bucket = storage_client.bucket(BACKGROUND_MUSIC_BUCKET_NAME)
            audio_extensions = {'.mp3', '.wav', '.aac', '.m4a', '.flac', '.ogg', '.wma'}

            for filename in os.listdir(str(AUDIO_DIRECTORY_PATH)):
                local_path = os.path.join(str(AUDIO_DIRECTORY_PATH), filename)
                file_extension = os.path.splitext(filename)[1]

                # Make sure it's a file and not a directory
                if os.path.isfile(local_path) and file_extension in audio_extensions:
                    # Define the blob path in the bucket
                    blob = bucket.blob(filename)
                    # Upload the file
                    blob.upload_from_filename(local_path)
                    print(f"Uploaded {filename} to gcs")


if __name__ == '__main__':
    GetBackgroundMusic.upload_to_gcs()

