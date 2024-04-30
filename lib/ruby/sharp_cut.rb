#!/usr/bin/env ruby
require 'open3'
require 'fastimage'
require 'optparse'
require 'ostruct'
require 'open3'
require 'tempfile'

# Assuming ARGV[0], ARGV[1], and ARGV[2] are provided correctly

first_image = ARGV[0]
second_image = ARGV[1]
output_file = ARGV[2]

temp_file = Tempfile.new(['long_transition', '.mp4'])

begin
  # This command generates a long video with a sharp cut, which will be trimmed next
  ffmpeg_command = [
    'ffmpeg',
    '-loglevel' ,
    'error',
    '-loop', '1',
    '-t', '5',
    '-i', first_image,
    '-loop', '1',
    '-t', '5',
    '-i', second_image,
    '-filter_complex', "[0:v]format=yuv420p,scale=1080:1920,fps=60[v0];[1:v]format=yuv420p,scale=1080:1920,fps=60[v1];[v0][v1]overlay=x='if(lte(t,2),W,if(lte(t,3),max(W-(t-2)*W*5,0),0))':y=0",
    '-c:v', 'libx264',
    '-preset', 'fast',
    '-t', '5',
    '-r', '60',
    '-y',
    temp_file.path
  ]

  # Debugging: Print the command to be executed
  puts "Executing command:#{ffmpeg_command.join(' ')}"

  # Execute the command
  system(*ffmpeg_command)

  ffmpeg_trim = [
  'ffmpeg',
  '-loglevel' ,
  'error',
  '-i',
  temp_file.path,
  '-ss',
  '00:00:02.000',
  '-frames:v',
  '13',
  '-y',
  output_file
]

  # Debugging: Print the command to be executed
  puts "Executing command:#{ffmpeg_trim.join(' ')}"

  # Execute the command
  system(*ffmpeg_trim)
ensure
  # Close and delete the temporary file
  temp_file.close!
  temp_file.unlink   # deletes the temp file
end
GC.start
