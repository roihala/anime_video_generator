#!/usr/bin/env ruby

# MIT License - https://github.com/remko/kburns
require 'open3'
require 'stringio'
require 'fastimage'
require 'optparse'
require 'ostruct'
require 'open3'
require 'tempfile'

################################################################################
# Parse options
################################################################################

options = OpenStruct.new
options.slide_duration_s = 4
options.fade_duration_s = 1
options.fps = 60
options.zoom_rate = 0.1
options.zoom_direction = "random"
options.scale_mode = :pad

OptionParser.new do |opts|
  opts.banner = "Usage: #{$PROGRAM_NAME} [options] input1 [input2...] output"
  opts.on("-h", "--help", "Prints this help") do
    puts opts
    exit
  end
  opts.on("--slide-duration=[DURATION]", Float, "Slide duration (seconds) (default: #{options.slide_duration_s})") do |s|
    options.slide_duration_s = s
  end
  opts.on("--fade-duration=[DURATION]", Float, "Slide duration (seconds) (default: #{options.fade_duration_s})") do |s|
    options.fade_duration_s = s
  end
  opts.on("--fps=[FPS]", Integer, "Output framerate (frames per second) (default: #{options.fps})") do |n|
    options.fps = n
  end
  opts.on("--zoom-direction=[DIRECTION]", ["random"] + ["top", "bottom"].product(["left", "right"], ["in", "out"]).map {|m| m.join("-")}, "Zoom direction (default: #{options.zoom_direction})") do |t|
    options.zoom_direction = t
  end
  opts.on("--zoom-rate=[RATE]", Float, "Zoom rate (default: #{options.zoom_rate})") do |n|
    options.zoom_rate = n
  end
  opts.on("--scale-mode=[SCALE_MODE]", [:pad, :pan, :crop_center], "Scale mode (pad, crop_center, pan) (default: #{options.scale_mode})") do |n|
    options.scale_mode = n
  end
  opts.on("-y", "Overwrite output file without asking") do
    options.y = true
  end
end.parse!

if ARGV.length != 2
  puts "Need exactly one input file (scene) and 1 output file"
  exit 1
end

scene_image = ARGV[0]
output_file = ARGV[1]

################################################################################
# Constants
################################################################################
output_width =  1920
output_height = 1080

################################################################################

if options.zoom_direction == "random"
  x_directions = [:left, :right]
  y_directions = [:top, :bottom]
  z_directions = [:in, :out]
else
  x_directions = [options.zoom_direction.split("-")[1].to_sym]
  y_directions = [options.zoom_direction.split("-")[0].to_sym]
  z_directions = [options.zoom_direction.split("-")[2].to_sym]
end

output_ratio = output_height.to_f / output_width.to_f

ratio = output_height / output_width

img_file = Tempfile.new(['image', '.jpeg'])

cmd = ["ffmpeg",
  "-loglevel", "error",
  "-i", scene_image,
  "-vf", "scale=#{output_height}:#{output_width},format=yuv420p",
  "-y", img_file.path
]
puts cmd.join(" ")
system(*cmd)

# Create a single slide as a Hash instead of mapping over input_files
slide = {
  file: img_file.path,
  width: 1080,
  height: 1920,
  direction_x: x_directions.sample,
  direction_y: y_directions.sample,
  direction_z: z_directions.sample,
  scale: options.scale_mode == :auto ?
    ((ratio - output_ratio).abs > 0.5 ? :pad : :crop_center)
  :
    options.scale_mode
}

# Convert the single slide Hash into an Array containing that slide
slides = [slide]

# Base black image
filter_chains = [
  "color=c=black:r=#{options.fps}:size=#{output_height}x#{output_width}:d=#{(options.slide_duration_s-options.fade_duration_s)*slides.count+options.fade_duration_s}[black]"
]

# Slide filterchains
filter_chains += slides.each_with_index.map do |slide, i|
  filters = ["format=pix_fmts=yuva420p"]

  ratio = slide[:width].to_f/slide[:height].to_f

  # Crop to make video divisible
  filters << "crop=w=2*floor(iw/2):h=2*floor(ih/2)"

  # Pad filter
  if slide[:scale] == :pad or slide[:scale] == :pan
    width, height = ratio > output_ratio ?
      [slide[:width], (slide[:width]/output_ratio).to_i]
    :
      [(slide[:height]*output_ratio).to_i, slide[:height]]
    filters << "pad=w=#{width}:h=#{height}:x='(ow-iw)/2':y='(oh-ih)/2'"
  end

  # Zoom/pan filter
  z_step = options.zoom_rate.to_f/(options.fps*options.slide_duration_s)
  z_rate = options.zoom_rate.to_f
  z_initial = 1
  if slide[:scale] == :pan
    z_initial = ratio/output_ratio
    z_step = z_step*ratio/output_ratio
    z_rate = z_rate*ratio/output_ratio
    if ratio > output_ratio
      if (slide[:direction_x] == :left && slide[:direction_z] != :out) || (slide[:direction_x] == :right && slide[:direction_z] == :out)
        x = "(1-on/(#{options.fps}*#{options.slide_duration_s}))*(iw-iw/zoom)"
      elsif (slide[:direction_x] == :right && slide[:direction_z] != :out) || (slide[:direction_x] == :left && slide[:direction_z] == :out)
        x = "(on/(#{options.fps}*#{options.slide_duration_s}))*(iw-iw/zoom)"
      else
        x = "(iw-ow)/2"
      end
      y_offset = "(ih-iw/#{ratio})/2"
      y = case slide[:direction_y]
        when :top
          y_offset
        when :center
          "#{y_offset}+iw/#{ratio}/2-iw/#{output_ratio}/zoom/2"
        when :bottom
          "#{y_offset}+iw/#{ratio}-iw/#{output_ratio}/zoom"
      end
    else
      z_initial = output_ratio/ratio
      z_step = z_step*output_ratio/ratio
      z_rate = z_rate*output_ratio/ratio
      x_offset = "(iw-#{ratio}*ih)/2"
      x = case slide[:direction_x]
        when :left
          x_offset
        when :center
          "#{x_offset}+ih*#{ratio}/2-ih*#{output_ratio}/zoom/2"
        when :right
          "#{x_offset}+ih*#{ratio}-ih*#{output_ratio}/zoom"
      end
      if (slide[:direction_y] == :top && slide[:direction_z] != :out) || (slide[:direction_y] == :bottom && slide[:direction_z] == :out)
        y = "(1-on/(#{options.fps}*#{options.slide_duration_s}))*(ih-ih/zoom)"
      elsif (slide[:direction_y] == :bottom && slide[:direction_z] != :out) || (slide[:direction_y] == :top && slide[:direction_z] == :out)
        y = "(on/(#{options.fps}*#{options.slide_duration_s}))*(ih-ih/zoom)"
      else
        y = "(ih-oh)/2"
      end
    end
  else
    x = case slide[:direction_x]
      when :left
        "0"
      when :center
        "iw/2-(iw/zoom/2)"
      when :right
        "iw-iw/zoom"
    end
    y = case slide[:direction_y]
      when :top
        "0"
      when :center
        "ih/2-(ih/zoom/2)"
      when :bottom
        "ih-ih/zoom"
    end
  end
  z = case slide[:direction_z]
    when :in
      "if(eq(on,1),#{z_initial},zoom+#{z_step})"
    when :out
      "if(eq(on,1),#{z_initial+z_rate},zoom-#{z_step})"
  end
  width, height = case slide[:scale]
    when :crop_center
#       if output_ratio > ratio
      if output_ratio > ratio
        [output_width, (output_width/ratio).to_i]
      else
        [(output_height*ratio).to_i, output_height]
      end
    when :pan, :pad
      [output_height, output_width]
    end

  filters << "zoompan=z='#{z}':x='#{x}':y='#{y}':fps=#{options.fps}:d=#{options.fps}*#{options.slide_duration_s}:s=#{output_height}x#{output_width}"

  # Crop filter
  if slide[:scale] == :crop_center
    crop_x = "(iw-ow)/2"
    crop_y = "(ih-oh)/2"
    filters << "crop=w=#{output_width}:h=#{output_height}:x='#{crop_x}':y='#{crop_y}'"
  end

  # Time
  filters << "setpts=PTS-STARTPTS+#{i}*#{options.slide_duration_s}/TB"

  # All together now
  "[#{i}:v]" + filters.join(",") + "[v#{i}]"
end

# Overlays
filter_chains += slides.each_with_index.map do |slide, i|
  input_1 = i > 0 ? "ov#{i-1}" : "black"
  input_2 = "v#{i}"
  output = i == slides.count - 1 ? "out" : "ov#{i}"
  overlay_filter = "overlay" + (i == slides.count - 1 ? "=format=yuv420" : "")
  "[#{input_1}][#{input_2}]#{overlay_filter}[#{output}]"
end

# Start generating
scene_file = Tempfile.new(['scene', '.mp4'])
img_file = Tempfile.new(['image', '.mp4'])

begin
  # Run ffmpeg
  cmd = [
    "ffmpeg", "-loglevel", "error", "-hide_banner", *options.y ? ["-y"] : [],
    *slides.map { |s| ["-i", s[:file]] }.flatten,
    "-filter_complex", filter_chains.join(";"),
    "-t", (options.slide_duration_s).to_s,
    "-map", "[out]",
    "-c:v", "libx264", scene_file.path
  ]
  puts cmd.join(" ")
  system(*cmd)

  ffmpeg_command = [
  "ffmpeg",
  '-loglevel' ,
  'error',
  "-i", scene_file.path,
  "-vf", "select='gt(n,0)'",
  "-vsync", "vfr",
  "-c:a", "copy",
  '-y',
  output_file
]
  puts ffmpeg_command.join(" ")
  system(*ffmpeg_command)

ensure
  # Close and delete the temporary file
  scene_file.close!
  scene_file.unlink   # deletes the temp file
  img_file.close!
  img_file.unlink   # deletes the temp file

end
GC.start
