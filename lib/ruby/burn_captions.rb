#!/usr/bin/env ruby
require 'open3'
require 'fastimage'
require 'optparse'
require 'ostruct'
require 'open3'
require 'tempfile'
require 'shellwords'


options = {
  input_file: nil,
  output_file: nil,
  srt_file: nil
}

OptionParser.new do |opts|
  opts.banner = "Usage: ruby_script.rb [options]"

  opts.on("--output-file FILE", "Output file path") do |file| # Define output file option
    options[:output_file] = Shellwords.escape(File.expand_path(file))
  end
  opts.on("--input-file FILE", "Input file path") do |file| # Define output file option
    options[:input_file] = Shellwords.escape(File.expand_path(file))
  end
  opts.on("--srt-file FILE", "Srt file path") do |file| # Define output file option
    options[:srt_file] = Shellwords.escape(File.expand_path(file))
  end
end.parse!

# #############################################################################
ffmpeg_command = [
  'ffmpeg',
  '-loglevel',
  'error',
  '-i', options[:input_file],
  '-vf', "ass=#{options[:srt_file]}",
  '-codec:a', 'copy',
  '-y',
  options[:output_file]
]
puts "Executing command:#{ffmpeg_command.join(' ')}"
system(*ffmpeg_command)
GC.start
