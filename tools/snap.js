// 앱으로 디지몬 상세(#file)를 렌더링해 HTML 스냅샷을 뽑는다
const {chromium}=require('playwright');const fs=require('fs');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:900,height:1200}});
await p.goto('http://localhost:8765/');await p.evaluate(()=>{try{localStorage.setItem('csd-lang','ko')}catch(e){}});
await p.goto('http://localhost:8765/');await p.waitForTimeout(1500);
const list=await p.evaluate(()=>ALL.filter(d=>d.no).map(d=>[d.no,d.name]));
const out={};
for(const [no,name] of list){
  out[no]=await p.evaluate(async n=>{select(n,false);await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));const f=document.querySelector('#file');return {name:n,html:f.innerHTML}},name);
}
fs.writeFileSync('/home/claude/dex/static/snap.json',JSON.stringify(out));console.log(Object.keys(out).length);await b.close()})();
