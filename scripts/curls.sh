# From server
curl -X 'POST' \
  'http://127.0.0.1:8000/transcription_webhook' \
  -H 'content-type: application/json' \
  -H 'accept: */*' \
  -H 'accept-encoding: gzip, deflate, br' \
  -d $'{"data": {"job_id": "CeWwTCuzeqUA4ZM2g3", "input": {"filename": "CeWwTCuzeqUA4ZM2g3.mp3", "url": "https://peregrine-results.s3.amazonaws.com/CeWwTCuzeqUA4ZM2g3.mp3"}, "results": {"format": "SRT", "word_level": true, "segment_level": false, "webhook_url": "https://webhook.site/f3fcb54c-24ce-47e6-9a65-663770829de1", "status": "complete", "started": "2024-04-10 09:39:32.374730", "completed_at": "2024-04-10 09:39:33.328290", "_links": [{"href": "http://127.0.0.1:8080/transcribe/result/CeWwTCuzeqUA4ZM2g3", "method": "GET", "contentType": "application/json", "rel": "self", "description": "Collect transcription JSON payload results"}], "transcription": "0\n00:00:00,040 --> 00:00:00,360\nHello\n\n1\n00:00:00,360 --> 00:00:00,680\nfrom\n\n2\n00:00:00,680 --> 00:00:00,900\na\n\n3\n00:00:00,900 --> 00:00:01,440\nrealistic\n\n4\n00:00:01,440 --> 00:00:01,960\nvoice."}}}'

curl -X 'POST' \
  'http:/127.0.0.1:8000/story_to_video' \
  -H 'Content-Type: application/json' \
  -d '{
        "story_images": [
            "https://storage.googleapis.com/public_stories/abc/007.jpg",
            "https://storage.googleapis.com/public_stories/abc/011.jpg",
            "https://storage.googleapis.com/public_stories/abc/018.jpg",
            "https://storage.googleapis.com/public_stories/abc/028.jpg"
        ]
      }'
#




curl -X 'POST' \
  'http:/34.68.162.217/story_to_video' \
  -H 'Content-Type: application/json' \
  -d '{
        "story_images": [
            "https://storage.googleapis.com/public_stories/abc/007.jpg",
            "https://storage.googleapis.com/public_stories/abc/011.jpg",
            "https://storage.googleapis.com/public_stories/abc/018.jpg",
            "https://storage.googleapis.com/public_stories/abc/028.jpg"
        ]
      }'
#




#curl -X 'POST' \
#  'http://127.0.0.1:8000/story_to_video' \
#  -H 'Content-Type: application/json' \
#  -d '{
#        "story_images": [
#            "https://storage.googleapis.com/public_stories/abc/007.jpg",
#            "https://storage.googleapis.com/public_stories/abc/011.jpg",
#            "https://storage.googleapis.com/public_stories/abc/018.jpg",
#            "https://storage.googleapis.com/public_stories/abc/028.jpg"
#        ],
#        "script": "This is the script of the story.",
#        "webhook_url": "https://example.com/webhook",
#        "voice": "male"
#      }'
