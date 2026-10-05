import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';

const root=fileURLToPath(new URL('../..', import.meta.url));
const out=path.join(root,'02_outputs/qgis_wgs84_package');
const data=JSON.parse(await fs.readFile(path.join(root,'04_pipeline/work/qgis_workbook_data.json'),'utf8'));
const wb=Workbook.create();
const previews=path.join(root,'04_pipeline/work/qgis_previews');
await fs.mkdir(previews,{recursive:true});
const intFields=new Set(['Value','Z','Year_Min','Year_Max','Source_Year']);
const realFields=new Set(['X','Y']);
const numericFields=new Set([...intFields,...realFields]);
const csvEscape=v=>'"'+String(v??'').replaceAll('"','""')+'"';

for (const [i,s] of data.specs.entries()){
  const sheet=wb.worksheets.add(s.sheet);
  const matrix=[s.headers,...s.rows];
  const range=sheet.getRangeByIndexes(0,0,matrix.length,s.headers.length);
  range.values=matrix;
  if(JSON.stringify(range.values)!==JSON.stringify(matrix))throw Error('Workbook values changed '+s.sheet);
  sheet.showGridLines=false;
  range.format.font={name:'Helvetica Neue',size:11,color:'#202B38'};
  range.format.verticalAlignment='top';
  range.format.wrapText=true;
  range.format.rowHeight=90;
  for(let c=0;c<s.headers.length;c++){
    const h=s.headers[c];const col=sheet.getRangeByIndexes(0,c,matrix.length,1);
    let width=20;
    if(['Row_ID','Object_ID','Value','Year_Min','Year_Max','Source_Year','Z','CRS'].includes(h))width=13;
    if(['X','Y'].includes(h))width=14;
    if(h==='Name')width=34;
    if(['Event','Note','Right_Source','Geo_Source','Geometry_Scope','Right_Scope'].includes(h))width=46;
    if(['Geometry_Status','Official_Name','Geo_ID'].includes(h))width=37;
    if(h==='Geometry_File')width=25;
    col.format.columnWidth=width;
    if(numericFields.has(h)){
      const vals=sheet.getRangeByIndexes(1,c,s.rows.length,1);
      vals.setNumberFormat(realFields.has(h)?'0.0000000':'0');
    }
    if(h==='Review')sheet.getRangeByIndexes(1,c,s.rows.length,1).dataValidation={rule:{type:'list',values:['待审理','确认','修改','排除','补证']}};
  }
  const headers=sheet.getRangeByIndexes(0,0,1,s.headers.length);
  headers.format.fill='#25394A';headers.format.font={bold:true,color:'#FFFFFF'};
  headers.format.rowHeight=38;
  headers.format.verticalAlignment='center';
  const table=sheet.tables.add(range,true,'Concession'+i);
  table.showFilterButton=true;
  sheet.freezePanes.freezeRows(1);
  sheet.freezePanes.freezeColumns(2);
  // Value is numeric or null, including when CSV is reopened by QGIS.
  const actual=range.values;
  const csv='\uFEFF'+actual.map(r=>r.map(csvEscape).join(',')).join('\r\n')+'\r\n';
  await fs.writeFile(path.join(out,s.file),csv,'utf8');
  const types=s.headers.map(h=>intFields.has(h)?'Integer':realFields.has(h)?'Real':'String');
  await fs.writeFile(path.join(out,s.file.replace('.csv','.csvt')),types.map(csvEscape).join(',')+'\n');
  console.log((await wb.inspect({kind:'table',range:`'${s.sheet}'!A1:I4`,include:'values',tableMaxRows:4,tableMaxCols:9,maxChars:2000})).ndjson);
  const preview=await wb.render({sheetName:s.sheet,range:s.key==='points'?'A1:J7':'A1:I7',scale:1,format:'png'});
  await fs.writeFile(path.join(previews,s.key+'.png'),new Uint8Array(await preview.arrayBuffer()));
}

const guide=wb.worksheets.add('字段与导入说明');
const guideRows=[
 ['字段或主题','含义／处理方式'],
 ['坐标系','所有交付的空间坐标采用WGS84（EPSG:4326）。GeoJSON使用经度、纬度顺序。'],
 ['X / Y / Z','点表X＝经度，Y＝纬度，Z恒为0；Z是按要求设定，非实测海拔。'],
 ['Value','主要权利／安排变更的单个整数年份。多个年份拆成多行；同年多个事件也分别保留。'],
 ['Value空白','没有可确认的个案变更年、只有时间区间，或仅是观测／模板／理论年份。空白不等于0。'],
 ['Year_Min / Year_Max','只用于已知时间区间。两个端点分列，不表示区间内每年发生了一次变化。'],
 ['Source_Year','来源发表／观测年份，与权利变更年份严格区分。'],
 ['Event_Date','保留原始精度：年、年月或完整日期。不把仅有年份的数据补成一月一日。'],
 ['Object_ID / Row_ID','Object_ID连接同一对象的多条事件；Row_ID唯一标识一条对象—事件记录。'],
 ['Event_Status','documented＝材料记载；future＝未来；proposal＝提议；undetermined＝尚未确定。'],
 ['其他事件状态','future_obligation＝约定未来义务；scheduled_performance＝约定履行，未核实已完成；source_conflict＝来源差异。'],
 ['终止／条件状态','conditional＝附生效条件；renounced＝放弃授权；abandoned＝放弃项目；withdrawn＝撤回；cancelled＝取消；ceased＝活动停止。'],
 ['线形','线形来自官方现状具名对象，含全部选定名称对应线段。不是某个历史时期的完整网络，也不是concession法定边界。'],
 ['候选线形','Barneusaz／Barneuza和Äbibärgeri／Äbibergeri名称对应仍待审理，Geometry_Status明确标示。'],
 ['无唯一坐标表','分开标示面域／集合、非地物客体、无个案实例，以及实物坐标尚未核定。没有用公司地址或村庄点补空。'],
 ['点CSV导入','QGIS：添加分隔文本图层，选01_points_wgs84.csv；UTF-8、逗号、X字段X、Y字段Y、Z字段Z，CRS选EPSG:4326。'],
 ['CSV字段类型','每个CSV随附同名CSVT。Value、Year_Min、Year_Max、Source_Year为整数；XY为实数。'],
 ['线表导入','02_linear_objects.csv是无几何说明表。地图线形直接加载lines_wgs84.geojson，其中也保留逐事件Value。'],
 ['无唯一坐标表导入','03_no_unique_coordinate.csv按无几何表加载，供筛选与审理。'],
 ['点图层便捷导入','也可直接加载points_wgs84.geojson，已包含三维点（Z＝0）与Value。'],
 ['无坐标／无年份','没有制造(0,0)坐标，也没有把未知年填成0；线形未核定的对象保留在说明表。'],
 ['数据规模',`${data.summary.object_count}个对象，点表${data.summary.row_counts.points}行、线表${data.summary.row_counts.lines}行、无唯一坐标表${data.summary.row_counts.nonunique}行。`],
 ['已有记录覆盖','52条时间线与50条关系ID全部有对应；拆分后的对象数不等于独立concession文书数。'],
 ['点坐标来源','瑞士能源局水电站／蓄水设施图层；Moiry餐厅为swisstopo建筑点。'],
 ['坐标转换','swissNAMES3D从LV95转换到WGS84，所用转换标称精度约1米；显示小数位不代表测量精度。'],
 ['审核','所有Review初值为待审理。可选择确认、修改、排除或补证。'],
 ['本轮保留范围','原有时间线和关系数据库未改写；本工作簿与导入文件为新增派生数据。'],
 ['地物线形来源','https://www.swisstopo.admin.ch/fr/modele-du-territoire-swissnames3d'],
 ['点图层来源','https://api3.geo.admin.ch/rest/services/ech/MapServer/ch.bfe.statistik-wasserkraftanlagen'],
 ['坝体点图层','https://api3.geo.admin.ch/rest/services/ech/MapServer/ch.bfe.stauanlagen-bundesaufsicht'],
];
guide.getRangeByIndexes(0,0,guideRows.length,2).values=guideRows;
const gr=guide.getRangeByIndexes(0,0,guideRows.length,2);
gr.format.font={name:'Helvetica Neue',size:11,color:'#202B38'};gr.format.wrapText=true;gr.format.verticalAlignment='top';gr.format.rowHeight=48;
guide.getRange(`A1:A${guideRows.length}`).format.columnWidth=26;
guide.getRange(`B1:B${guideRows.length}`).format.columnWidth=108;
guide.getRange('A1:B1').format.fill='#25394A';guide.getRange('A1:B1').format.font={bold:true,color:'#FFFFFF'};
guide.showGridLines=false;guide.freezePanes.freezeRows(1);
const gp=await wb.render({sheetName:guide.name,range:'A1:B11',scale:1,format:'png'});
await fs.writeFile(path.join(previews,'guide.png'),new Uint8Array(await gp.arrayBuffer()));
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:50},summary:'final error scan',maxChars:1800})).ndjson);
const xlsx=await SpreadsheetFile.exportXlsx(wb);
await xlsx.save(path.join(out,'concession_WGS84_QGIS.xlsx'));
console.log('Saved workbook and 3 typed CSV tables.');
