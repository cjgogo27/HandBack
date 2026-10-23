// DOM-fixture behavioral checks, not a claim of real-browser visual inspection.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const html=fs.readFileSync(path.join(root,'docs/index.html'),'utf8');
const payload=html.match(/<script id="study-data" type="application\/json">([\s\S]*?)<\/script>/)[1];
const scripts=[...html.matchAll(/<script(?: [^>]*)?>([\s\S]*?)<\/script>/g)];
const elements={};
for(const id of ['study-data','scene','scene-note','cards','clips','peak-images','method','outcome','records','row-count']){
  elements[id]={value:['method','outcome'].includes(id)?'all':'',innerHTML:'',textContent:id==='study-data'?payload:'',
    listeners:{},children:[],append(x){this.children.push(x)},addEventListener(k,f){this.listeners[k]=f}};
}
const document={getElementById(id){assert.ok(elements[id],`Unknown DOM target ${id}`);return elements[id]},createElement(tag){assert.equal(tag,'option');return {}}};
vm.runInNewContext(scripts.at(-1)[1],{document,console}, {timeout:3000});
const count=(text,pattern)=>(text.match(pattern)||[]).length;
assert.equal(elements.scene.children.length,12);
assert.equal(count(elements.cards.innerHTML,/<article /g),7);
assert.equal(count(elements.clips.innerHTML,/<video /g),3);
assert.equal(count(elements.records.innerHTML,/<tr>/g),84);
elements.scene.value='4062104012';elements.scene.listeners.change();
assert.ok(elements.cards.innerHTML.includes('V_4062104012_final.webp'));
assert.ok(!elements.cards.innerHTML.includes('V_4062104002_final.webp'));
elements.method.value='V';elements.outcome.value='joint';elements.method.listeners.change();
assert.equal(count(elements.records.innerHTML,/<tr>/g),6);
elements.outcome.value='retry';elements.outcome.listeners.change();
assert.equal(count(elements.records.innerHTML,/<tr>/g),1);
elements.method.value='all';elements.method.listeners.change();
assert.equal(count(elements.records.innerHTML,/<tr>/g),3);
elements.outcome.value='all';elements.outcome.listeners.change();
assert.equal(count(elements.records.innerHTML,/<tr>/g),84);
assert.ok(html.includes('not continuous motion video'));
console.log(JSON.stringify({state:'passed',checks:10,scope:'DOM-fixture execution; not a real-browser layout or playback test'}));
