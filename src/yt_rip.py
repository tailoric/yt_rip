from youtube_dl import YoutubeDL
import argparse
import asyncio
import subprocess
from functools import partial
import logging

async def get_dl_url(url, opt):
    loop = asyncio.get_event_loop()
    logging.debug(opt)
    with YoutubeDL(opt) as ydl:
        func = partial(ydl.extract_info, url, download=False)
        result = await loop.run_in_executor(None, func)
        return result.get('url')

async def download_and_launch_ffmpeg(args):

    ydl_opts_vid = {"skip-dash-manifest": True,
                'format': 'bestvideo'}
    
    ydl_opts_audio = {"skip-dash-manifest": True,
                'format': 'bestaudio'}
    if "ytdl_flags" in args.keys() and args['ytdl_flags']:
        flags = [f for f in args['ytdl_flags'].split(',')]
        opts = {k:v for k,v in (f.split('=') for f in flags)}
        ydl_opts_vid.update(opts)
        ydl_opts_audio.update(opts)
    results = await asyncio.gather(
        get_dl_url(args.get('url'), ydl_opts_audio),
        get_dl_url(args.get('url'), ydl_opts_vid)
        )
    arglist = ['ffmpeg']
    if args.get('_to'):
        arglist.extend(['-to', str(args.get('_to'))])
    if args.get('_from'):
        arglist.extend(['-ss', str(args.get('_from'))])
    if results[0]:
        arglist.extend(['-i', results[0]])
    if args.get('_to'):
        arglist.extend(['-to', str(args.get('_to'))])
    if args.get('_from'):
        arglist.extend(['-ss', str(args.get('_from'))])
    if results[1]:
        arglist.extend(['-i', results[1]])
    if args.get('copy'):
        arglist.extend(['-c', 'copy'])
    arglist.append('-y')
    if args.get('output'):
        arglist.append(args.get('output'))
    else:
        arglist.append('output.mp4')
    logging.debug(arglist)
    p = subprocess.Popen(arglist)
    p.communicate()

parser = argparse.ArgumentParser(description="A python script wrapping ffmpeg and youtube_dl for downloading timestamps from youtube or other sources")
parser.add_argument('--from', dest='_from', help="start time of the video")
parser.add_argument('--to', dest='_to', help="end time of the clip")
parser.add_argument('-c', dest='copy', action='store_true', help="use the quick copy option")
parser.add_argument('--output', dest='output', help="set output file")
parser.add_argument('--ytdl-flags', dest="ytdl_flags", help="Set some misc flags you want to pass to youtube_dl (comma separated) like --ytdl-flags=option1=value,option2=value", type=str)
parser.add_argument('-d', dest="debug", help="set to debug mode", action='store_true')
parser.add_argument('url')
args = parser.parse_args()
args = vars(args)
logging.basicConfig(level=logging.DEBUG if args.get('debug') else logging.INFO)
logging.debug(args)
asyncio.run(download_and_launch_ffmpeg(args))


