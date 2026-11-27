"""試験素材の生成（合成。外部の素材や権利のあるデータを使わない）。
使い方: python3 make_fixtures.py [出力先。既定は環境変数 BECOME_FIX または /tmp/become-fixtures]
生成するもの: wavfx/n48m.wav（モノラル48kHz）, wavfx/n441s.wav（ステレオ44.1kHz）, cropfx/right.mp4, cropfx/center.mp4, clip_p.mp4（縦1080x1920・6秒・30fps）, clip_l.mp4（横640x360・2秒。tc.py用）
これらは、元の試験素材と同じ構造（4文・各0.5秒・間0.6秒・計4.4秒／640x360の2秒）の合成物で、元のファイルとは同一ではない。
生成していない素材（vid、ns、dr、riko、am の素材）は、試験の一部が必要とする。手順が未整備のため、該当の試験は「環境不足」と報告される。"""
import os,sys,wave,subprocess
import numpy as np
FIX=sys.argv[1] if len(sys.argv)>1 else os.environ.get('BECOME_FIX','/tmp/become-fixtures')
os.makedirs(FIX+'/wavfx',exist_ok=True);os.makedirs(FIX+'/cropfx',exist_ok=True)
def speech(sr,ch):
    rng=np.random.default_rng(7);t=np.arange(int(4.4*sr))/sr;x=np.zeros_like(t)
    for a in (0.0,1.1,2.2,3.3):
        m=(t>=a)&(t<a+0.5);env=np.sin(np.pi*(t[m]-a)/0.5)**0.5
        x[m]=env*(0.35*np.sin(2*np.pi*180*t[m])+0.12*np.sin(2*np.pi*420*t[m])+0.04*rng.standard_normal(m.sum()))
    x=np.clip(x*1.0,-0.5,0.5);y=(x*32767).astype('<i2')
    return y if ch==1 else np.stack([y,y],1).reshape(-1)
for name,sr,ch in (('n48m',48000,1),('n441s',44100,2)):
    with wave.open(f'{FIX}/wavfx/{name}.wav','wb') as w:
        w.setnchannels(ch);w.setsampwidth(2);w.setframerate(sr);w.writeframes(speech(sr,ch).tobytes())
def video(path,cx):
    W,H,N=640,360,60;rng=np.random.default_rng(3);tex=(rng.random((H,W))*255).astype('u1');fr=[]
    for k in range(N):
        im=np.full((H,W,3),40,'u1');x0=int(cx*W-60);x0=max(0,min(W-120,x0));im[100:260,x0:x0+120]=np.stack([tex[100:260,x0:x0+120]]*3,2);fr.append(im.tobytes())
    p=subprocess.run(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','-','-c:v','libx264','-pix_fmt','yuv420p','-t','2',path],input=b''.join(fr))
    if p.returncode:sys.exit('ffmpeg failed')
video(FIX+'/cropfx/right.mp4',0.82);video(FIX+'/cropfx/center.mp4',0.5)
p=subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','testsrc2=size=1080x1920:rate=30:duration=6','-c:v','libx264','-pix_fmt','yuv420p','-b:v','3M','-g','30',FIX+'/clip_p.mp4'])
if p.returncode:sys.exit('ffmpeg failed (clip_p)')
p=subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','testsrc2=size=640x360:rate=30:duration=2','-c:v','libx264','-pix_fmt','yuv420p','-b:v','600k','-g','30',FIX+'/clip_l.mp4'])
if p.returncode:sys.exit('ffmpeg failed (clip_l)')
print('fixtures ok:',FIX)
