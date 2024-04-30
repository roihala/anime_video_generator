#!/usr/bin/env ruby
require 'open3'
require 'fastimage'
require 'optparse'
require 'ostruct'
require 'open3'
require 'tempfile'

options = {
  file_list: 'file_list.txt',
  durations: [],
  background_music: nil,
  music_volume_adjustment: 0,
  narration_audio: nil,
  transition_sound_effect: nil,
  output_file: nil # Added output_file option
}

OptionParser.new do |opts|
  opts.banner = "Usage: ruby_script.rb [options]"

  opts.on("--file-list FILE", "Path to file list txt (default: file_list.txt)") do |file|
    options[:file_list] = file
  end

  opts.on("--durations DURATIONS", "List of durations matching the file list, separated by comma") do |durations|
    options[:durations] = durations.split(',').map(&:to_f)
  end

  opts.on("--background-music MUSIC", "Background music file") do |music|
    options[:background_music] = music
  end

  opts.on("--music-volume-adjustment VALUE", Float, "Music volume adjustment in decibels") do |value|
    options[:music_volume_adjustment] = value
  end

  opts.on("--narration-audio FILE", "Narration audio file") do |file|
    options[:narration_audio] = file
  end

  opts.on("--transition-sound-effect FILE", "Transition sound effect file") do |file|
    options[:transition_sound_effect] = file
  end

  opts.on("--output-file FILE", "Output file path") do |file| # Define output file option
    options[:output_file] = file
  end
end.parse!

# Load files from the file list
files = File.readlines(options[:file_list]).map(&:strip)
durations = options[:durations]

# Check for mismatch between number of files and durations
if files.size != durations.size
  puts "Warning: The number of files and durations does not match. Please ensure each file has a corresponding duration."
  exit
end

# Combine files with their durations
files_with_durations = files.zip(durations)

puts "Files with durations: #{files_with_durations.inspect}"
puts "Background Music: #{options[:background_music]}, Volume Adjustment: #{options[:music_volume_adjustment]} dB"
puts "Narration Audio: #{options[:narration_audio]}"
puts "Transition Sound Effect: #{options[:transition_sound_effect]}"
puts "Output File: #{options[:output_file]}" # Display the output file path

# #############################################################################
temp_file = Tempfile.new(['no_audio', '.mp4'])
begin
  # Concats all scenes without audio
  ffmpeg_command = [
    'ffmpeg',
    '-loglevel' ,
    'error',
    '-f', 'concat', # Specifies the input format as 'concat'
    '-safe', '0',
    '-i', "#{options[:file_list]}",
    '-c', 'copy', # Copy streams without reencoding
    '-y',
    temp_file.path
  ]
  puts "Executing command:#{ffmpeg_command.join(' ')}"
  system(*ffmpeg_command)

  ffmpeg_command = [
    'ffmpeg',
    '-loglevel' ,
    'error',
    '-i', temp_file.path,
    '-i', options[:background_music],
    '-i', options[:narration_audio],
    '-i', options[:transition_sound_effect],
    '-filter_complex', "[0:v]trim=duration=#{durations.sum},setpts=PTS-STARTPTS[v0]; [1:a]atrim=duration=#{durations.sum},asetpts=PTS-STARTPTS,volume=-#{options[:music_volume_adjustment]}dB:eval=frame[a1]; [2:a]atrim=duration=#{durations.sum},asetpts=PTS-STARTPTS,volume=1.0:eval=frame[a2]; [3:a]asplit=3[eff1][eff2][eff3]; [eff1]adelay=#{durations[0] * 1000}|#{durations[0] * 1000},volume=2.0:eval=frame[eff1out]; [eff2]adelay=#{durations.take(2 + 1).sum * 1000}|#{durations.take(2 + 1).sum * 1000},volume=2.0:eval=frame[eff2out]; [eff3]adelay=#{durations.take(4 + 1).sum * 1000}|#{durations.take(4 + 1).sum * 1000},volume=2.0:eval=frame[eff3out]; [a1][a2][eff1out][eff2out][eff3out]amix=inputs=5:duration=first:dropout_transition=2[a]",
    '-map', '[v0]',
    '-map', '[a]',
    '-y',
    '-c:v', 'libx264',
    options[:output_file]
  ]
  puts "Executing command:#{ffmpeg_command.join(' ')}"
  system(*ffmpeg_command)
ensure
  # Close and delete the temporary file
  temp_file.close!
  temp_file.unlink   # deletes the temp file
end
GC.start
