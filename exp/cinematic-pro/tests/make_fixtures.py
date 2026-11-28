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
# --- 映像分析（段階A）用の合成素材: vafx/（縦540x960・30fps・8秒）---
os.makedirs(FIX+'/vafx',exist_ok=True)
def ff(out,args,fc=None):
    cmd=['ffmpeg','-v','error','-y']+args
    cmd+=['-pix_fmt','yuv420p','-c:v','libx264','-r','30','-g','30','-b:v','2M','-t','8',out]
    if subprocess.run(cmd).returncode:sys.exit('ffmpeg failed: '+out)
SZ='540x960'
src_a=['-f','lavfi','-i','testsrc2=size=%s:rate=30:duration=8'%SZ]
ff(FIX+'/vafx/ok_a.mp4',src_a)
ff(FIX+'/vafx/ok_b.mp4',['-f','lavfi','-i','mandelbrot=size=%s:rate=30'%SZ])
ff(FIX+'/vafx/ok_c.mp4',['-f','lavfi','-i','sierpinski=size=%s:rate=30'%SZ])
ff(FIX+'/vafx/black_mid.mp4',src_a+['-vf',"drawbox=x=0:y=0:w=iw:h=ih:color=black:t=fill:enable='between(t,3,6)'"])
ff(FIX+'/vafx/black_head.mp4',src_a+['-vf',"drawbox=x=0:y=0:w=iw:h=ih:color=black:t=fill:enable='between(t,0,6)'"])
ff(FIX+'/vafx/black_short.mp4',src_a+['-vf',"drawbox=x=0:y=0:w=iw:h=ih:color=black:t=fill:enable='between(t,3.5,4)'"])
ff(FIX+'/vafx/dark.mp4',src_a+['-vf','eq=brightness=-0.45'])
ff(FIX+'/vafx/static.mp4',['-f','lavfi','-i','smptebars=size=%s:rate=30'%SZ])
ff(FIX+'/vafx/flat.mp4',['-f','lavfi','-i','color=c=0x808080:size=%s:rate=30'%SZ])
p=subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','testsrc2=size=%s:rate=30:duration=4'%SZ,'-f','lavfi','-i','mandelbrot=size=%s:rate=30'%SZ,'-filter_complex','[1:v]trim=0:4,setpts=PTS-STARTPTS[b];[0:v][b]concat=n=2:v=1[v]','-map','[v]','-pix_fmt','yuv420p','-c:v','libx264','-r','30','-g','30','-b:v','2M','-t','8',FIX+'/vafx/cut_mid.mp4'])
if p.returncode:sys.exit('ffmpeg failed: cut_mid')
ff(FIX+'/vafx/dup_a.mp4',src_a+['-vf','scale=360:640','-b:v','300k'])
for a,d in ((0,2),(5,7.5),(1,1.6),(6.5,8),(2,5),(3,3.9)):
    ff(FIX+'/vafx/bk_%s_%s.mp4'%(a,d),src_a+['-vf',"drawbox=x=0:y=0:w=iw:h=ih:color=black:t=fill:enable='between(t,%s,%s)'"%(a,d)])
for c in (2,6):
    p=subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','testsrc2=size=%s:rate=30:duration=%d'%(SZ,c),'-f','lavfi','-i','mandelbrot=size=%s:rate=30'%SZ,'-filter_complex','[1:v]trim=0:%d,setpts=PTS-STARTPTS[b];[0:v][b]concat=n=2:v=1[v]'%(8-c),'-map','[v]','-pix_fmt','yuv420p','-c:v','libx264','-r','30','-g','30','-b:v','2M','-t','8',FIX+'/vafx/cut_%d.mp4'%c])
    if p.returncode:sys.exit('ffmpeg failed: cut_%d'%c)
print('vafx ok')
print('fixtures ok:',FIX)
