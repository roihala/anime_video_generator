#!/usr/bin/env ruby
require 'open3'
require 'fastimage'
require 'optparse'
require 'ostruct'
require 'open3'
require 'tempfile'
require 'shellwords'


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
    options[:file_list] = Shellwords.escape(File.expand_path(file))
  end

  opts.on("--durations DURATIONS", "List of durations matching the file list, separated by comma") do |durations|
    options[:durations] = durations.split(',').map do |dur|
      dur.to_f
    end
  end

  opts.on("--background-music FILE", "Background music file") do |file|
    options[:background_music] = Shellwords.escape(File.expand_path(file))
  end

  opts.on("--music-volume-adjustment VALUE", Float, "Music volume adjustment in decibels") do |value|
    options[:music_volume_adjustment] = value
  end

  opts.on("--narration-audio FILE", "Narration audio file") do |file|
    options[:narration_audio] = Shellwords.escape(File.expand_path(file))
  end

  opts.on("--transition-sound-effect FILE", "Transition sound effect file") do |file|
    options[:transition_sound_effect] = Shellwords.escape(File.expand_path(file))
  end

  opts.on("--output-file FILE", "Output file path") do |file| # Define output file option
    options[:output_file] = Shellwords.escape(File.expand_path(file))
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

# TODO: -1 only if even?
num_transitions = durations.size / 2 - (durations.size.even? ? 1 : 0)
transition_effects = []
transition_outputs = []
first_line = []

# transition_durations.each_with_index do |duration, i|
(1..num_transitions).step(1) do |i|
  # Calculate the delay based on the cumulative duration up to this point
  delay_time = durations.take(i * 2 - 1).sum * 1000 - 300  # adjust formula as needed

  first_line << "[eff#{i}]"
  transition_effects << "[eff#{i}]adelay=#{delay_time}|#{delay_time},volume=2.0:eval=frame[eff#{i}out]"
  transition_outputs << "[eff#{i}out]"
end

first_line_str = first_line.join('')
transition_effects_str = transition_effects.join('; ')
transition_outputs_str = transition_outputs.join('')


# Combine files with their durations
files_with_durations = files.zip(durations)

puts "Files with durations: #{files_with_durations.inspect}"
puts "Background Music: #{options[:background_music]}, Volume Adjustment: #{options[:music_volume_adjustment]} dB"
puts "Narration Audio: #{options[:narration_audio]}"
puts "Transition Sound Effect: #{options[:transition_sound_effect]}"
puts "Output File: #{options[:output_file]}" # Display the output file path

# #############################################################################
no_audio_file = Tempfile.new(['no_audio', '.mp4'])
with_music_file = Tempfile.new(['with_music', '.mp4'])

begin
  # Concats all scenes without audio
  ffmpeg_command = [
    'ffmpeg',
    '-loglevel' ,
    'error',
    '-f', 'concat', # Specifies the input format as 'concat'
    '-safe', '0',
    '-i', options[:file_list],
    '-c', 'copy', # Copy streams without reencoding
    '-y',
    no_audio_file.path
  ]
  puts "Executing command:#{ffmpeg_command.join(' ')}"
  system(*ffmpeg_command)

  ffmpeg_command = [
    'ffmpeg',
    '-loglevel' ,
    'error',
    '-i', no_audio_file.path,
    '-i', options[:background_music],
    '-i', options[:narration_audio],
    # origianl
#     '-filter_complex', "[0:v]trim=duration=#{durations.sum},setpts=PTS-STARTPTS[v0]; [1:a]atrim=duration=#{durations.sum},asetpts=PTS-STARTPTS,volume=-#{options[:music_volume_adjustment]}dB:eval=frame[a1]; [2:a]atrim=duration=#{durations.sum},asetpts=PTS-STARTPTS,volume=1.0:eval=frame[a2]; [3:a]asplit=3[eff1][eff2][eff3]; [eff1]adelay=#{(durations[0] * 1000 - 300)}|#{(durations[0] * 1000 - 300)},volume=2.0:eval=frame[eff1out]; [eff2]adelay=#{(durations.take(2 + 1).sum * 1000 - 300)}|#{(durations.take(2 + 1).sum * 1000 - 300)},volume=2.0:eval=frame[eff2out]; [eff3]adelay=#{(durations.take(4 + 1).sum * 1000 - 300)}|#{(durations.take(4 + 1).sum * 1000 - 300)},volume=2.0:eval=frame[eff3out]; [a1][a2][eff1out][eff2out][eff3out]amix=inputs=5:duration=first:dropout_transition=2[a]",

    '-filter_complex', "[0:v]trim=duration=#{durations.sum},setpts=PTS-STARTPTS[v0]; [1:a]atrim=duration=#{durations.sum},asetpts=PTS-STARTPTS,volume=-#{options[:music_volume_adjustment]}dB:eval=frame[a1]; [2:a]atrim=duration=#{durations.sum},asetpts=PTS-STARTPTS,volume=1.0:eval=frame[a2]; [a1][a2]amix=inputs=2:duration=first:dropout_transition=2[a]",
    # Staged
#     '-filter_complex', "[0:v]trim=duration=#{durations.sum},setpts=PTS-STARTPTS[v0]; [1:a]atrim=duration=#{durations.sum},asetpts=PTS-STARTPTS,volume=-#{options[:music_volume_adjustment]}dB:eval=frame[a1]; [2:a]atrim=duration=#{durations.sum},asetpts=PTS-STARTPTS,volume=1.0:eval=frame[a2]; [3:a]asplit=#{num_transitions}#{first_line_str}; #{transition_effects_str}; [a1][a2]#{transition_outputs_str}amix=inputs=#{2 + num_transitions}:duration=first:dropout_transition=2[a]",

    '-map', '[v0]',
    '-map', '[a]',
    '-y',
    '-c:v', 'libx264',
    with_music_file.path
  ]
  puts "Executing command:\n#{ffmpeg_command.join(' ')}"
  system(*ffmpeg_command)

  ffmpeg_command = [
    'ffmpeg',
    '-loglevel' ,
    'error',
    '-i', with_music_file.path,
    '-i', options[:transition_sound_effect],
    '-filter_complex', "[0:v]trim=duration=#{durations.sum},setpts=PTS-STARTPTS[v0]; [0:a]atrim=duration=#{durations.sum},asetpts=PTS-STARTPTS[orig_audio]; [1:a]asplit=#{num_transitions}#{first_line_str};#{transition_effects_str}; [orig_audio]#{transition_outputs_str}amix=inputs=#{num_transitions + 1}:duration=first:dropout_transition=2[a]",
    '-map', '[v0]',
    '-map', '[a]',
    '-y',
    '-c:v', 'libx264',
    options[:output_file]
  ]
  puts "Executing command:\n#{ffmpeg_command.join(' ')}"
  system(*ffmpeg_command)
ensure
  # Close and delete the temporary file
  with_music_file.close!
  with_music_file.unlink   # deletes the temp file
  no_audio_file.close!
  no_audio_file.unlink   # deletes the temp file
end
GC.start
