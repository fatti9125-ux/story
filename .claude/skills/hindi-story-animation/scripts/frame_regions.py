# usage: regions.py clip.mp4 start end  -> per-frame changed bbox (in 640x360 coords) + area%
import sys, subprocess, numpy as np
path, a, b = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
W,H=640,360
p=subprocess.Popen(['ffmpeg','-v','error','-ss',str(a),'-to',str(b),'-i',path,'-f','rawvideo','-pix_fmt','gray','-'],stdout=subprocess.PIPE)
prev=None; i=0
while True:
    buf=p.stdout.read(W*H)
    if len(buf)<W*H: break
    f=np.frombuffer(buf,np.uint8).astype(np.int16)
    f=f.reshape(H,W)
    if prev is not None:
        d=np.abs(f-prev)>18
        area=d.mean()*100
        if area>0.02:
            ys,xs=np.where(d)
            print(f"{a+i/30:6.2f} f{i:3d} area={area:5.2f}% bbox=x{xs.min()}-{xs.max()} y{ys.min()}-{ys.max()}")
        else:
            print(f"{a+i/30:6.2f} f{i:3d} HOLD")
    prev=f; i+=1
