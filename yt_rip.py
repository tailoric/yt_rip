from youtube_dl import YoutubeDL
import argparse
import asyncio
import subprocess
from functools import partial

async def get_dl_url(url, opt):
    loop = asyncio.get_event_loop()
    with YoutubeDL(opt) as ydl:
        func = partial(ydl.extract_info, url, download=False)
        result = await loop.run_in_executor(None, func)
        return result.get('url')

async def download_and_launch_ffmpeg(args):
    ydl_opts_vid = {"skip-dash-manifest": True,
                'format': 'bestvideo'}
    
    ydl_opts_audio = {"skip-dash-manifest": True,
                'format': 'bestaudio'}
    results = await asyncio.gather(
        get_dl_url(args.url, ydl_opts_audio),
        get_dl_url(args.url, ydl_opts_vid)
        )
    arglist = ['ffmpeg']
    if bool(args._to):
        arglist.extend(['-to', str(args._to)])
    if bool(args._from):
        arglist.extend(['-ss', str(args._from)])
    arglist.extend(['-i', results[0]])
    if bool(args._to):
        arglist.extend(['-to', str(args._to)])
    if bool(args._from):
        arglist.extend(['-ss', str(args._from)])
    arglist.extend(['-i', results[1]])
    if bool(args.copy):
        arglist.extend(['-c', 'copy'])
    arglist.append('-y')
    if bool(args.output):
        arglist.append(args.output)
    else:
        arglist.append('output.mp4')
    p = subprocess.Popen(arglist)
    p.communicate()

parser = argparse.ArgumentParser(description="A python script wrapping ffmpeg and youtube_dl for downloading timestamps from youtube or other sources")
parser.add_argument('--from', dest='_from', help="start time of the video")
parser.add_argument('--to', dest='_to', help="end time of the clip")
parser.add_argument('-c', dest='copy', action='store_true', help="use the quick copy option")
parser.add_argument('--output', dest='output', help="set output file")
parser.add_argument('url')
args = parser.parse_args()
asyncio.run(download_and_launch_ffmpeg(args))


