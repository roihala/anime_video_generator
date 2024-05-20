from datetime import datetime, timedelta
import re
from pathlib import Path

from config import logger


class CaptionsGenerator:
    ass_info = \
        """[Script Info]
; Script generated manually
Title: Awesome Voice
Original Script: Your Name
ScriptType: v4.00+
Collisions: Normal
PlayDepth: 0
Timer: 100.0000

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,24,&HFFFFFF,&H000000,&H000000,&H000000,0,0,0,0,100,100,0,0,1,1,0,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    @classmethod
    def generate_ass(cls, transcription):
        # Regular expression to capture SRT blocks
        re_srt_block = re.compile(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3})\n(.*)')

        blocks = re_srt_block.findall(transcription)
        output = []
        index = 1

        # Iterate in steps of three blocks
        for i in range(0, len(blocks), 3):
            if i + 2 < len(blocks):
                # Ensure there are at least three blocks to process
                block1 = blocks[i]
                block2 = blocks[i + 1]
                block3 = blocks[i + 2]

                # Create three new blocks, highlighting each word in turn
                text1 = f'{{\\\\c&H00FFFF&}}{block1[2]}{{\\\\c}} {block2[2]} {block3[2]}'
                text2 = f'{block1[2]} {{\\\\c&H00FFFF&}}{block2[2]}{{\\\\c}} {block3[2]}'
                text3 = f'{block1[2]} {block2[2]} {{\\\\c&H00FFFF&}}{block3[2]}{{\\\\c}}'

                for block, text in [(block1, text1), (block2, text2), (block3, text3)]:
                    start_time, end_time = block[1].split(' --> ')

                    # Append the new blocks to the output
                    # output.append(f"{index} {start_time} --> {end_time} {text}\n")
                    start_time = cls.format_time(start_time)
                    end_time = cls.format_time(end_time)
                    if not start_time and not end_time:
                        continue
                    elif not start_time:
                        start_time = end_time
                    elif not end_time:
                        end_time=start_time
                    output.append(f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{text}")
                    index += 1

        return cls.ass_info + '\n'.join(output)

    @classmethod
    def generate_srt(cls, transcription):
        # Regular expression to capture SRT blocks
        re_srt_block = re.compile(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3})\n(.*)')

        blocks = re_srt_block.findall(transcription)
        output = []
        index = 1

        # Iterate in steps of three blocks
        for i in range(0, len(blocks), 3):
            if i + 2 < len(blocks):
                # Ensure there are at least three blocks to process
                block1 = blocks[i]
                block2 = blocks[i + 1]
                block3 = blocks[i + 2]

                # Create three new blocks, highlighting each word in turn
                text1 = f'<font color="yellow">{block1[2]}</font> {block2[2]} {block3[2]}'
                text2 = f'{block1[2]} <font color="yellow">{block2[2]}</font> {block3[2]}'
                text3 = f'{block1[2]} {block2[2]} <font color="yellow">{block3[2]}</font>'

                for block, text in [(block1, text1), (block2, text2), (block3, text3)]:
                    start_time, end_time = block[1].split(' --> ')
                    # Decreasing -001 to fit captions subsequently
                    spet = end_time.split(",")
                    spet[-1] = str(int(spet[-1]) - 1)
                    end_time = ','.join(spet)

                    # Append the new blocks to the output
                    output.append(f"{index} {start_time} --> {end_time} {text}\n")
                    index += 1

        return '\n'.join(output)

    @classmethod
    def format_time(cls, time_from_srt):
        try:
            dt = datetime.strptime(time_from_srt, '%H:%M:%S,%f')
            # Decreasing -001 to fit captions subsequently
            dt -= timedelta(seconds=0.01)
            formatted_time = dt.strftime('%-H:%M:%S.%f')[:-4]  # Remove the last three digits to keep only two decimals

            return str(formatted_time)
        except Exception as e:
            logger.warning(f"Failed to format time on subscription file: {time_from_srt}")
            return ''
