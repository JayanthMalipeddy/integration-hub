"""Build an adaptive palette and assemble native Windows GIF frames. No downloads."""
from pathlib import Path
import argparse, struct
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
WORK=ROOT/'runtime/architecture-animation'
OUT=Path(__file__).resolve().parent/'integration-hub-architecture-animated.gif'

def palette():
    rgb=np.fromfile(WORK/'sample.bgr',dtype=np.uint8).reshape(-1,3)[:,::-1]
    q=rgb.astype(np.int32)>>2
    ids=(q[:,0]<<12)|(q[:,1]<<6)|q[:,2]
    counts=np.bincount(ids,minlength=262144)
    keys=np.flatnonzero(counts)
    colors=np.column_stack(((keys>>12)*4+2,((keys>>6)&63)*4+2,(keys&63)*4+2)).astype(np.float64)
    weights=counts[keys]
    boxes=[np.arange(len(keys))]
    while len(boxes)<255:
        scores=[np.ptp(colors[b],axis=0).max()*np.sqrt(weights[b].sum()) if len(b)>1 else -1 for b in boxes]
        pos=int(np.argmax(scores)); box=boxes.pop(pos)
        if len(box)<2: boxes.append(box);break
        axis=int(np.argmax(np.ptp(colors[box],axis=0)))
        ordered=box[np.argsort(colors[box,axis])]
        cut=int(np.searchsorted(np.cumsum(weights[ordered]),weights[ordered].sum()/2))+1
        cut=max(1,min(cut,len(ordered)-1));boxes.extend([ordered[:cut],ordered[cut:]])
    pal=np.array([np.average(colors[b],axis=0,weights=weights[b]) for b in boxes]).round().astype(np.uint8)
    pal=np.vstack([np.zeros((1,3),dtype=np.uint8),pal])
    while len(pal)<256:pal=np.vstack([pal,pal[-1:]])
    pal.tofile(WORK/'palette.bin')
    keys=np.arange(262144)
    quant=np.column_stack(((keys>>12)*4+2,((keys>>6)&63)*4+2,(keys&63)*4+2)).astype(np.int32)
    lut=np.empty(262144,dtype=np.uint8)
    for start in range(0,len(keys),2048):
        distances=((quant[start:start+2048,None,:]-pal[None,1:,:].astype(np.int32))**2).sum(axis=2)
        lut[start:start+2048]=distances.argmin(axis=1)+1
    lut.tofile(WORK/'lut.bin')
    print('Built 255-color adaptive palette plus transparency.',flush=True)

def read_frame(path):
    data=path.read_bytes();packed=data[10];pos=13
    table=b''
    if packed&128:
        n=3*(2**((packed&7)+1));table=data[pos:pos+n];pos+=n
    while True:
        marker=data[pos];pos+=1
        if marker==0x21:
            pos+=1
            while data[pos]:pos+=data[pos]+1
            pos+=1
        elif marker==0x2c:
            descriptor=data[pos:pos+9];pos+=9;flags=descriptor[8]
            if flags&128:
                n=3*(2**((flags&7)+1));table=data[pos:pos+n];pos+=n
            start=pos;pos+=1
            while data[pos]:pos+=data[pos]+1
            pos+=1
            return table,flags&64,data[start:pos]
        else:raise ValueError('Missing image descriptor')

def assemble():
    frames=[list(map(int,row.split(','))) for row in (WORK/'frames.csv').read_text().splitlines()]
    result=bytearray(b'GIF89a'+struct.pack('<HHBBB',1800,1200,0x70,0,0))
    result.extend(b'\x21\xff\x0bNETSCAPE2.0\x03\x01\x00\x00\x00')
    for i,x,y,w,h in frames:
        table,interlace,lzw=read_frame(WORK/f'encoded-{i:03}.gif')
        size=(len(table)//3).bit_length()-2
        result.extend(b'\x21\xf9\x04'+struct.pack('<BHB',5,8,0)+b'\x00')
        result.extend(b'\x2c'+struct.pack('<HHHHB',x,y,w,h,128|interlace|size)+table+lzw)
    result.append(0x3b);OUT.write_bytes(result)
    print(f'Created {OUT.name}: {len(frames)} frames, 8-second loop, {len(result)/1024/1024:.2f} MB.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['palette','assemble']);a=p.parse_args()
    palette() if a.action=='palette' else assemble()
