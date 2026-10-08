# Rebuild animation/curtain.png from the raw generated sheet animation/curtainclose.png.
# Needs Pillow + numpy. Run from the repo root: python animation/build_curtain_sheet.py
# Every frame is cropped to its curtain rod and stretched to one cell width, so the rod
# ends and the hem land in the same place in every cell. Near-invisible red keying
# specks (alpha 1-4) are dropped. Colours are kept: the fabric already matches the
# curtains painted in the scene.
from PIL import Image; import numpy as np
src=Image.open('animation/curtainclose.png').convert('RGBA')
rods=[(28,414),(477,842),(906,1265),(1333,1694),(1761,2136)]  # rod x-span per frame
TOP,BOT=165,561   # rod top is row 171, hem bottom row 557
CW,CH=360,BOT-TOP
out=Image.new('RGBA',(CW*len(rods),CH),(0,0,0,0))
for i,(x0,x1) in enumerate(rods):
    out.paste(src.crop((x0,TOP,x1+1,BOT)).resize((CW,CH),Image.LANCZOS),(i*CW,0))
a=np.asarray(out).copy()
al=a[...,3]
a[al<16]=0
a[...,3]=np.where(al>200,255,a[...,3])
Image.fromarray(a,'RGBA').save('animation/curtain.png')
print('sheet',CW*len(rods),CH,'cell',CW,'rod top y',171-TOP,'hem y',557-TOP)
