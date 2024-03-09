ffmpeg -hide_banner -y ^
-i ./demo_output/images\007.jpg ^
-i ./demo_output/images\011.jpg ^
-i ./demo_output/images\018.jpg ^
-i ./demo_output/awesome_voice.mp3 ^
-i "C:\Users\RoiHa\PycharmProjects\anime_video_generator\lib\background_music\B5 Dubstep Loops 2.wav.mp3" ^
-filter_complex "[3:a][4:a]amix=inputs=2:duration=longest[aout];color=c=black:r=120:size=1080x1920:d=11.146921768707484[black];[0:v]format=pix_fmts=yuva420p,crop=w=2*floor(iw/2):h=2*floor(ih/2),pad=w=1949:h=3464:x='(ow-iw)/2':y='(oh-ih)/2',zoompan=z='if(eq(on,1),1.2,zoom-0.0003803171638170907)':x='iw-iw/zoom':y='ih-ih/zoom':fps=120:d=120*4.382307256235828:s=1080x1920,fade=t=in:st=0:d=1.0:alpha=0,fade=t=out:st=3.382307256235828:d=1.0:alpha=1,setpts=PTS-STARTPTS+0*4.382307256235828/TB[v0];[1:v]format=pix_fmts=yuva420p,crop=w=2*floor(iw/2):h=2*floor(ih/2),pad=w=4677:h=8314:x='(ow-iw)/2':y='(oh-ih)/2',zoompan=z='if(eq(on,1),1,zoom+0.0003803171638170907)':x='0':y='ih-ih/zoom':fps=120:d=120*4.382307256235828:s=1080x1920,fade=t=in:st=0:d=1.0:alpha=1,fade=t=out:st=3.382307256235828:d=1.0:alpha=1,setpts=PTS-STARTPTS+1*4.382307256235828/TB[v1];[2:v]format=pix_fmts=yuva420p,crop=w=2*floor(iw/2):h=2*floor(ih/2),pad=w=4677:h=8314:x='(ow-iw)/2':y='(oh-ih)/2',zoompan=z='if(eq(on,1),1,zoom+0.0003803171638170907)':x='iw-iw/zoom':y='0':fps=120:d=120*4.382307256235828:s=1080x1920,fade=t=in:st=0:d=1.0:alpha=1,fade=t=out:st=3.382307256235828:d=1.0:alpha=0,setpts=PTS-STARTPTS+2*4.382307256235828/TB[v2];[black][v0]overlay[ov0];[ov0][v1]overlay[ov1];[ov1][v2]overlay=format=yuv420[out]" ^
-t 14.146921768707484 ^
-map [out] ^
-map [aout] ^
-c:v libx264 ^
./demo_output/video\video1.mp4
