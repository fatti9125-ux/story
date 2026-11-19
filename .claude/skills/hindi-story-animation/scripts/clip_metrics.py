import sys, subprocess, numpy as np, json
W,H=320,180
def frames(path):
    p=subprocess.Popen(['ffmpeg','-v','error','-i',path,'-vf',f'scale={W}:{H}','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
    while True:
        b=p.stdout.read(W*H*3)
        if len(b)<W*H*3: break
        yield np.frombuffer(b,np.uint8).reshape(H,W,3).astype(np.int16)
res={}
for path in sys.argv[1:]:
    prev=None; diffs=[]; lum=[]; changed=[]
    for f in frames(path):
        lum.append(float(f.mean()))
        if prev is not None:
            d=np.abs(f-prev).max(axis=2)
            diffs.append(float(d.mean())); changed.append(float((d>12).mean()))
        prev=f
    diffs=np.array(diffs); changed=np.array(changed)
    # classification
    still = changed<0.0005           # identical frame (hold)
    cut = changed>0.45
    # run lengths of holds between changes -> exposure ("on 1s/2s/3s")
    runs=[]; r=1
    for s in still:
        if s: r+=1
        else: runs.append(r); r=1
    runs.append(r)
    runs=np.array(runs)
    hist={k:int((runs==k).sum()) for k in range(1,7)}; hist['7+']=int((runs>=7).sum())
    res[path.split('/')[-1]]=dict(
        unique_frames=int((~still).sum()+1), held_pct=round(100*still.mean(),1),
        cuts=[round((i+1)/30,2) for i in np.where(cut)[0]],
        exposure_hist=hist, mean_changed_area_pct=round(100*changed[~still&~cut].mean(),2) if (~still&~cut).any() else 0,
        lum_min=round(min(lum),1), lum_max=round(max(lum),1),
        dark_frames=[round(i/30,2) for i,l in enumerate(lum) if l<12][:3]+(['...'] if sum(l<12 for l in lum)>3 else []))
    print(path.split('/')[-1], json.dumps(res[path.split('/')[-1]]), flush=True)
json.dump(res,open('clip_metrics.json','w'),indent=1)
