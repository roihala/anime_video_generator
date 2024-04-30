#!/usr/bin/env ruby
require 'open3'
require 'fastimage'
require 'optparse'
require 'ostruct'
require 'open3'
require 'tempfile'

options = {
  input_file: nil,
  output_file: nil,
  srt_file: nil
}

OptionParser.new do |opts|
  opts.banner = "Usage: ruby_script.rb [options]"

  opts.on("--output-file FILE", "Output file path") do |file| # Define output file option
    options[:output_file] = file
  end
  opts.on("--input-file FILE", "Input file path") do |file| # Define output file option
    options[:input_file] = file
  end
  opts.on("--srt-file FILE", "Srt file path") do |file| # Define output file option
    options[:srt_file] = file
  end
end.parse!

# #############################################################################
ffmpeg_command = [
  'ffmpeg',
  '-loglevel',
  'error',
  '-i', options[:input_file],
  '-vf', "subtitles=#{options[:srt_file]}:force_style='FontName=Arial,FontSize=24,PrimaryColour=&H00ff00'",
  '-codec:a', 'copy',
  '-y',
  options[:output_file]
]
puts "Executing command:#{ffmpeg_command.join(' ')}"
system(*ffmpeg_command)
GC.start
