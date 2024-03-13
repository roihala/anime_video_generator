ffmpeg_command = [
  "ffmpeg",
  "-i", "video1.mp4",
  "-i", "video2.mp4",
  *slides.map { |s| ["-i", s[:file]] }.flatten,
  "-i", "C:\Users\RoiHa\PycharmProjects\anime_video_generator\lib\sound FX\Whoosh 08.wav",
  "-hide_banner",
  "-y",
  "-filter_complex", "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[video][audio]; [2:a]adelay=2s:all=1[adjusted_audio]; [audio][adjusted_audio]amix=inputs=2:duration=first[aout]",
  "-map", "[video]",
  "-map", "[aout]",
  "output.mp4"
]
