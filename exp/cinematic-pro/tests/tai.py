"""段階B-0: 視覚意図カードと複数フレーム判定（モデル不要の純粋関数）の試験"""
import os,subprocess
REPO=os.environ.get('BECOME_REPO','/home/claude/become-studio')
r=subprocess.run(['node','tai.js'],env={**os.environ,'PLAN':REPO+'/exp/design/price-of-staying.design.json'},capture_output=True,text=True,cwd=os.path.dirname(os.path.abspath(__file__)))
print(r.stdout+r.stderr)
