ffmpeg -i video.mp4 -filter_complex "[0:v]drawbox=x=400:y=400:w=1080:h=1960:color=yellow@0.5:t=fill:enable='between(t,1,2)'[highlighted];[highlighted]subtitles=/Users/roihala/PycharmProjects/anime_video_generator/general.ass" -c:a copy x.mp4


sudo ffmpeg -i video.mp4 -vf "ass=/Users/roihala/PycharmProjects/anime_video_generator/general.ass" -c:v libx264 -c:a copy  x.mp4
