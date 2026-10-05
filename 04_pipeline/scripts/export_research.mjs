import fs from 'node:fs/promises';
import {Workbook} from '@oai/artifact-tool';
const data=JSON.parse(await fs.readFile(new URL('../work/research_rows.json',import.meta.url),'utf8'));
const wb=Workbook.create();
const out=new URL('../../02_outputs/negotiation_concession/',import.meta.url);
await fs.mkdir(out,{recursive:true});
for(const [name,headers,rows,file] of [
 ['研究记录',data.headers,data.rows,'negotiation_concession_分析.csv'],
 ['材料筛选',data.coverageHeaders,data.coverage,'材料阅读与筛选清单.csv']
]){
 const sheet=wb.worksheets.add(name);
 const matrix=[headers,...rows];
 if(matrix.some(r=>r.length!==headers.length))throw new Error('字段数不一致');
 const range=sheet.getRangeByIndexes(0,0,matrix.length,headers.length);
 range.values=matrix;
 const saved=range.values;
 if(JSON.stringify(saved)!==JSON.stringify(matrix))throw new Error('写入内容发生变化');
 console.log((await wb.inspect({kind:'table',range:`'${name}'!A1:D4`,include:'values',tableMaxRows:4,tableMaxCols:4,maxChars:1800})).ndjson);
 // CSV has no visual styles. Serialize the verified grid with RFC 4180 quoting and a UTF-8 BOM for Excel.
 const csv='\uFEFF'+saved.map(r=>r.map(v=>'"'+String(v??'').replaceAll('"','""')+'"').join(',')).join('\r\n')+'\r\n';
 await fs.writeFile(new URL(file,out),csv,'utf8');
 console.log(file,rows.length,'条记录',headers.length,'列');
}
