import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {loadOmowright} from '/home/ubuntuhong/.codex/plugins/cache/sisyphuslabs/omo/5.1.15/skills/browser/scripts/omowright.mjs';
const dir=path.dirname(new URL(import.meta.url).pathname);
const {omowright}=await loadOmowright();
const profile=fs.mkdtempSync(path.join(os.tmpdir(),'cbnx-report-qa-'));
const browser=await omowright.connectPipe({browserPath:'/usr/bin/google-chrome',browserArgs:['--headless','--no-sandbox','--no-first-run',`--user-data-dir=${profile}`],storageRoot:profile});
try{
 const page=await browser.newTab(`file://${dir}/report.html`);
 const probe=JSON.parse(execFileSync('node',['/home/ubuntuhong/.codex/plugins/cache/sisyphuslabs/omo/5.1.15/skills/ulw-research/scripts/report-tools.mjs','layout-probe','--json'],{encoding:'utf8'})).source;
 for(const width of [1280,768,375]){
  await omowright.emulate(page,{width,height:900,deviceScaleFactor:1,mobile:false,hasTouch:false});
  await page.evaluate('document.fonts.ready');
  const boxes=await page.evaluate(probe);
  fs.writeFileSync(path.join(dir,`boxes-${width}.json`),JSON.stringify(boxes,null,2));
  fs.writeFileSync(path.join(dir,`screen-${width}.png`),await page.screenshot({fullPage:true}));
 }
 const assets=await page.evaluate(`Array.from(document.images).map(i=>({src:i.getAttribute('src'),complete:i.complete,w:i.naturalWidth,h:i.naturalHeight}))`);
 fs.writeFileSync(path.join(dir,'asset-manifest.json'),JSON.stringify(assets,null,2));
 console.log(JSON.stringify({profiles:'task-owned',widths:[1280,768,375],assets},null,2));
}finally{await browser.close();fs.rmSync(profile,{recursive:true,force:true});}
