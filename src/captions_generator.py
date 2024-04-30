import re
from pathlib import Path


class CaptionsGenerator:
    @classmethod
    def generate_highlighted_captions(cls, transcription):
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
                    output.append(f"{index}\n{start_time} --> {end_time}\n{text}\n")
                    index += 1

        return '\n'.join(output)


if __name__ == '__main__':
    srt_content = "0\n00:00:00,000 --> 00:00:00,340\nWatch\n\n1\n00:00:00,340 --> 00:00:01,160\nout.\n\n2\n00:00:01,640 --> 00:00:01,660\nThe\n\n3\n00:00:01,660 --> 00:00:02,300\nvigilante\n\n4\n00:00:02,300 --> 00:00:02,620\nhero\n\n5\n00:00:02,620 --> 00:00:03,280\nDRAM\n\n6\n00:00:03,280 --> 00:00:03,660\nis\n\n7\n00:00:03,660 --> 00:00:03,860\nabout\n\n8\n00:00:03,900 --> 00:00:04,000\nto\n\n9\n00:00:04,000 --> 00:00:04,240\nunleash\n\n10\n00:00:04,260 --> 00:00:04,480\nhis\n\n11\n00:00:04,600 --> 00:00:04,880\nfury\n\n12\n00:00:04,880 --> 00:00:05,080\non\n\n13\n00:00:05,080 --> 00:00:05,140\nthe\n\n14\n00:00:05,160 --> 00:00:05,440\ncriminal\n\n15\n00:00:05,440 --> 00:00:06,000\nunderworld.\n\n16\n00:00:06,560 --> 00:00:06,860\nJustice\n\n17\n00:00:06,860 --> 00:00:07,040\nhas\n\n18\n00:00:07,040 --> 00:00:07,180\na\n\n19\n00:00:07,180 --> 00:00:07,420\nnew\n\n20\n00:00:07,420 --> 00:00:07,760\nname,\n\n21\n00:00:08,320 --> 00:00:08,440\nand it's\n\n22\n00:00:08,460 --> 00:00:08,660\nabout\n\n23\n00:00:08,660 --> 00:00:09,020\nto\n\n24\n00:00:09,020 --> 00:00:09,420\nkick some\n\n25\n00:00:09,420 --> 00:00:09,960\nserious\n\n26\n00:00:10,000 --> 00:00:10,480\nbutt."

    x = CaptionsGenerator.generate_highlighted_captions(srt_content)
    with open('/Users/roihala/PycharmProjects/anime_video_generator/resources/temp.srt', 'w') as f:
        f.write(x)

