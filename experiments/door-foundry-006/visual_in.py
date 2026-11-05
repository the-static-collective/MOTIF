"""MOTIF-006: real PNG image-in, exact small-palette raster observation.

A deliberately tiny visual instrument: recognize pixel cells only, not people,
objects in photographs, or meanings. Standard-library PNG 8-bit RGB/RGBA,
non-interlaced. Strict size, decompression, CRC, and palette limits.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import argparse
import json
import struct
import zlib

SIGN=b'\x89PNG\r\n\x1a\n'
PALETTE={
  '.':(255,255,255),
  'R':(220,40,50),
  '#':(35,60,160),
}
REVERSE={v:k for k,v in PALETTE.items()}

class HOLD(ValueError): pass

def digest(body):
    return sha256(json.dumps(body,separators=(',',':'),ensure_ascii=False,
                             allow_nan=False).encode()).hexdigest()

def png_chunk(kind,data):
    return struct.pack('>I',len(data))+kind+data+struct.pack(
        '>I',zlib.crc32(kind+data)&0xffffffff)

def encode_png(rows,scale=1):
    if (not rows or not 1<=scale<=16 or
        len(rows)*scale>256 or len(rows[0])*scale>2048 or
        any(not isinstance(r,str) or len(r)!=len(rows[0]) or
            any(x not in PALETTE for x in r) for r in rows)):
        raise HOLD('Invalid bounded visualization')
    width,height=len(rows[0])*scale,len(rows)*scale
    data=bytearray()
    for row in rows:
        line=bytes(v for c in row for _ in range(scale) for v in PALETTE[c])
        for _ in range(scale):data.extend(b'\0'+line)
    ihdr=struct.pack('>IIBBBBB',width,height,8,2,0,0,0)
    return SIGN+png_chunk(b'IHDR',ihdr)+png_chunk(
        b'IDAT',zlib.compress(bytes(data),level=9))+png_chunk(b'IEND',b'')

def _paeth(a,b,c):
    p=a+b-c
    pa,pb,pc=abs(p-a),abs(p-b),abs(p-c)
    return a if pa<=pb and pa<=pc else b if pb<=pc else c

def decode_png(raw,limit=16):
    if not isinstance(raw,bytes) or len(raw)>100000 or not raw.startswith(SIGN):
        raise HOLD('No valid bounded PNG image bytes')
    i=len(SIGN)
    chunks=[]
    idat=bytearray()
    ihdr=None
    finished=False
    while i<len(raw):
        if i+12>len(raw):raise HOLD('Truncated PNG chunk')
        n=struct.unpack('>I',raw[i:i+4])[0]
        kind=raw[i+4:i+8]
        if n>70000 or i+12+n>len(raw):
            raise HOLD('PNG chunk exceeds bounds')
        data=raw[i+8:i+8+n]
        crc=struct.unpack('>I',raw[i+8+n:i+12+n])[0]
        if zlib.crc32(kind+data)&0xffffffff!=crc:
            raise HOLD('Changed PNG bytes / CRC mismatch')
        i+=12+n
        if kind==b'IHDR':
            if ihdr is not None or chunks:raise HOLD('Reordered or repeated IHDR')
            ihdr=data
        elif kind==b'IDAT':
            if ihdr is None or finished:raise HOLD('Invalid image-data ordering')
            idat.extend(data)
            if len(idat)>70000:raise HOLD('Compressed PNG budget')
        elif kind==b'IEND':
            if len(data)!=0 or i!=len(raw):raise HOLD('Trailing PNG payload')
            finished=True
        else:
            if kind and kind[0]&32==0:
                raise HOLD('Unsupported critical PNG chunk')
            # Ignore metadata. Never run text profiles or external profiles.
        chunks.append(kind)
    if ihdr is None or not finished or not idat or len(ihdr)!=13:
        raise HOLD('Missing PNG header, pixels or terminator')
    width,height,depth,color,compression,filter_method,interlace=struct.unpack(
        '>IIBBBBB',ihdr)
    if (width<3 or height<3 or width>limit or height>limit or
        depth!=8 or color not in (2,6) or compression!=0 or
        filter_method!=0 or interlace!=0):
        raise HOLD('PNG must be tiny, 8-bit RGB/RGBA, non-interlaced')
    channels=3 if color==2 else 4
    scanbytes=width*channels
    total=(scanbytes+1)*height
    try:
        decomp=zlib.decompressobj()
        pixeldata=decomp.decompress(bytes(idat),total+1)
        if len(pixeldata)!=total or not decomp.eof or decomp.unused_data or decomp.unconsumed_tail:
            raise HOLD('Truncated, overlong or double-compressed PNG')
    except zlib.error as exc:raise HOLD('Invalid PNG compressed image data') from exc
    rows=[]
    offset=0
    prev=bytes(scanbytes)
    for y in range(height):
        filtercode=pixeldata[offset]
        offset+=1
        data=pixeldata[offset:offset+scanbytes]
        offset+=scanbytes
        out=bytearray()
        for k,v in enumerate(data):
            a=out[k-channels] if k>=channels else 0
            b=prev[k]
            c=prev[k-channels] if k>=channels else 0
            if filtercode==0:estimate=0
            elif filtercode==1:estimate=a
            elif filtercode==2:estimate=b
            elif filtercode==3:estimate=(a+b)//2
            elif filtercode==4:estimate=_paeth(a,b,c)
            else:raise HOLD('Unsupported PNG filter')
            out.append((v+estimate)&0xff)
        row=[]
        for x in range(width):
            rgb=tuple(out[x*channels:x*channels+3])
            if color==6 and out[x*channels+3]!=255:
                raise HOLD('Alpha blending not supported in image-in observations')
            if rgb not in REVERSE:
                raise HOLD('Pixel is outside the deliberately restricted palette')
            row.append(REVERSE[rgb])
        rows.append(''.join(row))
        prev=bytes(out)
    return tuple(rows)

def read_png(path):
    p=Path(path)
    if not p.is_file() or p.stat().st_size>100000:
        raise HOLD('Missing or oversized source PNG')
    return decode_png(p.read_bytes())

def coords(rows,letter):
    return {(x,y) for y,row in enumerate(rows) for x,c in enumerate(row) if c==letter}

def _one_red_block(rows):
    red=coords(rows,'R')
    if len(red)!=4:raise HOLD('Exactly one 2x2 red object required')
    left=min(x for x,_ in red)
    top=min(y for _,y in red)
    if red!={(left,top),(left+1,top),(left,top+1),(left+1,top+1)}:
        raise HOLD('The observed object must be one rigid 2x2 block')
    return red

def question(start_raw,goal_raw):
    a=decode_png(start_raw)
    b=decode_png(goal_raw)
    if len(a)!=len(b) or len(a[0])!=len(b[0]):
        raise HOLD('Start and imagined target must have equal dimensions')
    old=_one_red_block(a)
    target=_one_red_block(b)
    if old & target:raise HOLD('Use a separated relocation target for this invariant')
    if coords(a,'#')!=coords(b,'#'):
        raise HOLD('Stationary blue obstacles cannot be moved by this experiment')
    if any((x,y) in coords(a,'#') for x,y in target):
        raise HOLD('Target would overlap a blocked pixel')
    body={
      'schema':'motif.visual-gap.v0',
      'status':'PROVED_ADD_ONLY_GRAMMAR_CANNOT_RELOCATE',
      'scope':'SYNTHETIC_RASTER_ONLY',
      'start_png_sha256':sha256(start_raw).hexdigest(),
      'goal_png_sha256':sha256(goal_raw).hexdigest(),
      'start_rows':list(a),
      'goal_rows':list(b),
      'proof':{
         'invariant':'ADD_ONLY_CANNOT_REMOVE_OLD_RED_PIXELS',
         'old_red_pixels_must_be_cleared':len(old-target),
         'new_red_pixels_must_be_filled':len(target-old),
         'add_only_never_removes':True,
         'red_mass_conserved':len(old)==len(target),
         'fixed_graft029_add_only_insufficient':True,
      },
      'authority':{
        'produce_held_local_source':True,
        'deploy':False,
        'contact_people':False,
        'read_private_images':False,
      },
      'observational_limit':'PIXEL_PALETTE_ONLY_NOT_SEMANTIC_VISION',
      'user_image_transmitted_to_network':False,
    }
    return {**body,'content_sha256':digest(body)}

def verify_gap(gap,start_png,goal_png):
    if not isinstance(gap,dict):raise HOLD('Missing gap object')
    expected=question(start_png,goal_png)
    if expected!=gap:raise HOLD('Visual evidence does not replay from exact PNG bytes')
    return gap['content_sha256']

def demo_scene(x,y,blocks,width=9,height=8):
    if x<0 or y<0 or x+1>=width or y+1>=height:
        raise HOLD('Demo object exceeds raster')
    grid=[['.']*width for _ in range(height)]
    for bx,by in blocks:grid[by][bx]='#'
    for dx in (0,1):
        for dy in (0,1):
            if grid[y+dy][x+dx]!='.':raise HOLD('Demo object overlaps wall')
            grid[y+dy][x+dx]='R'
    return tuple(''.join(row) for row in grid)

def demo_pngs():
    blocks=[(4,y) for y in range(2,6)]
    return encode_png(demo_scene(1,3,blocks)),encode_png(demo_scene(6,3,blocks))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image',type=Path)
    parser.add_argument('--goal',type=Path)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--demo',action='store_true')
    args=parser.parse_args()
    try:
        if args.demo:
            a,b=demo_pngs()
            args.out.mkdir(parents=True,exist_ok=False)
            (args.out/'start.png').write_bytes(a)
            (args.out/'target.png').write_bytes(b)
            q=question(a,b)
            (args.out/'visual-gap.json').write_text(json.dumps(q,indent=2)+'\n')
        else:
            if not args.image or not args.goal or args.out.exists():
                raise HOLD('Supply existing --image and --goal PNG and new --out')
            q=question(args.image.read_bytes(),args.goal.read_bytes())
            args.out.write_text(json.dumps(q,indent=2)+'\n')
        print(json.dumps({'status':q['status'],
            'source_image_sha256':q['start_png_sha256'],
            'question_sha256':q['content_sha256'],
            'width':len(q['start_rows'][0]),
            'height':len(q['start_rows'])}))
    except (HOLD,FileExistsError) as exc:
        print(json.dumps({'stage':'HOLD','reason':str(exc)}))
        raise SystemExit(1)

if __name__=='__main__':main()
