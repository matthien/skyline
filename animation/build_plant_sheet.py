# Rebuild animation/plant.png from the raw generated sheet animation/plantgrowth.png.
# Needs Pillow + numpy. Run from the repo root: python animation/build_plant_sheet.py
from PIL import Image; import numpy as np
src=np.asarray(Image.open('animation/plantgrowth.png').convert('RGBA')).astype(float)
al=src[...,3]
frames=[(86,272),(420,625),(785,986),(1151,1363),(1502,1731),(1889,2125)]
BASE=614; TOP=200  # sheet rows kept: 200..BASE
CW=280; CH=BASE-TOP+1+4
# class colours in the sheet -> painted-plant tones
src_cols=np.array([(35,20,40),(102,61,79),(195,104,93),(120,50,60)],float)
dst_cols=np.array([(120,78,72),(132,81,79),(206,104,92),(140,66,70)],float)
rgb=src[...,:3]
d=((rgb[...,None,:]-src_cols[None,None])**2).sum(-1)
cls=d.argmin(-1)
new=dst_cols[cls]
out=np.zeros((CH,CW*6,4))
for i,(x0,x1) in enumerate(frames):
    band=al[560:600,x0:x1+1]>128
    xs=np.where(band.any(axis=0))[0]+x0
    cx=(xs.min()+xs.max())/2
    ox=int(round(i*CW+CW/2-cx))
    for x in range(x0-5,x1+6):
        tx=x+ox
        out[0:BASE-TOP+1,tx,:3]=new[TOP:BASE+1,x]
        out[0:BASE-TOP+1,tx,3]=al[TOP:BASE+1,x]
out[...,3]=np.where(out[...,3]>200,255,out[...,3])
Image.fromarray(out.astype(np.uint8),'RGBA').save('animation/plant.png')
print('sheet',CW*6,CH,'cell',CW,'pot centre x',CW/2,'pot bottom y',BASE-TOP)

# Background patches: what each window looks like with its painted plant removed.
# Shown under the sprite while the animation plays, so the growing plant doesn't
# sit on top of the painted one. skyline.png itself is never edited.
sky=np.asarray(Image.open('skyline.png').convert('RGB')).astype(float)
def save_patch(name,x0,y0,x1,y1,fill):
    patch=fill(x0,y0,x1,y1)
    Image.fromarray(np.clip(patch,0,255).astype(np.uint8),'RGB').save(f'animation/{name}.png')
    print(name,'at',x0,y0,'size',x1-x0,y1-y0)
def fill_rows(x0,y0,x1,y1):
    # wall and ledge run horizontally: blend each row between its left and right neighbours
    out=np.empty((y1-y0,x1-x0,3))
    for i,y in enumerate(range(y0,y1)):
        l=sky[y,x0-4:x0].mean(0); r=sky[y,x1:x1+4].mean(0)
        t=np.linspace(0,1,x1-x0)[:,None]; out[i]=l*(1-t)+r*t
    return out
def fill_cols(x0,y0,x1,y1):
    # glass and curtain run vertically: extend each column down from above the plant
    col=np.median(sky[y0-12:y0,x0:x1],axis=0)
    return np.repeat(col[None],y1-y0,axis=0)
save_patch('plant-patch-rb',1500,779,1538,820,fill_rows)
save_patch('plant-patch-lt',300,557,325,584,fill_cols)
