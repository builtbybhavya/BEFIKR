const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),crypto=require('node:crypto'),path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'..','app.js'),'utf8');
function setup(){
 let html='',calls=[],urls=[];
 const context={state:{user:{name:'Test'},page:'raaz',raazStep:2,raazScreen:'wizard',raazDraft:{category:'poor lighting',description:'The street lights are broken.',latitude:'',longitude:'',occurred_at:'',location_label:'',location_place_id:''},raazEvidence:[],raazLocationQuery:'',reports:[],routeInput:{origin:'Existing pickup',destination:'Existing drop'},pinMap:null,raazSubmitting:false},crypto,
 URL:{createObjectURL:()=>{const value='blob:test-'+urls.length;urls.push(value);return value;},revokeObjectURL:()=>{}},
 esc:value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])),
 toast:()=>{},shell:value=>html=value,moduleGreeting:()=>'',getOfflineReports:()=>[],saveOfflineReports:()=>{},localStorage:{getItem:()=>null},requestAnimationFrame:()=>{},drawMapPicker:()=>{},statusLabel:value=>value,
 document:{getElementById:()=>null},api:async(endpoint,options)=>{calls.push({endpoint,options});return {id:'report-ok',message:'Received'};},loadPageData:async()=>{},
 fetch:async(endpoint,options)=>{calls.push({endpoint,options});return {ok:true,json:async()=>({id:'file-ok'})};},googlePlaceUrl:()=>'',googlePlacesAttribution:()=>'',placeProviderAttribution:()=>''};
 vm.createContext(context);
 vm.runInContext(source.slice(source.indexOf('function raazHasLocation('),source.indexOf('function statusLabel(')),context);
 vm.runInContext(source.slice(source.indexOf('function openMapPicker('),source.indexOf('async function drawMapPicker(')),context);
 vm.runInContext(source.slice(source.indexOf('function setMapPickerCoordinates('),source.indexOf('function pageHead(')),context);
 return {c:context,html:()=>html,calls};
}
const file=(name='proof.png',type='image/png',size=100)=>({name,type,size,lastModified:1});
test('Evidence selection survives steps, previews files and enforces limits',()=>{
 const {c,html}=setup();c.addRaazEvidence([file()]);assert.equal(c.state.raazEvidence.length,1);assert.match(html(),/proof.png/);assert.match(html(),/Preview/);
 c.state.raazStep=3;c.renderRaaz();assert.match(html(),/Use my current location/);assert.match(html(),/Choose on map/);assert.match(html(),/Search by place name/);
 c.state.raazStep=4;c.renderRaaz();assert.match(html(),/proof.png/);
 c.addRaazEvidence([file('bad.html','text/html'),file('large.mp4','video/mp4',11*1024*1024)]);assert.equal(c.state.raazEvidence.length,1);
 c.addRaazEvidence([file('two.png'),file('three.mp4','video/mp4'),file('four.png')]);assert.equal(c.state.raazEvidence.length,3);
});
test('Map pin confirmation changes the incident point without changing Raahi',()=>{
 const {c}=setup();c.state.raazStep=3;c.openMapPicker('raaz',[28.6,77.2]);
 assert.equal(c.state.page,'map-picker');assert.equal(c.state.raazDraft.latitude,'');
 c.setMapPickerCoordinates(28.7,77.3);assert.equal(c.state.raazDraft.latitude,'');
 c.confirmMapPin();assert.equal(c.state.page,'raaz');assert.equal(c.state.raazDraft.latitude,'28.7');assert.equal(c.state.raazStep,3);
 assert.equal(c.state.routeInput.origin,'Existing pickup');assert.equal(c.state.routeInput.destination,'Existing drop');
});
test('Named location stores the chosen address and place ID after confirmation',()=>{
 const {c}=setup();c.openMapPicker('raaz',[28.6,77.2],{label:'India Gate',address:'India Gate, New Delhi',placeId:'google-id'});c.confirmMapPin();
 assert.equal(c.state.raazDraft.location_label,'India Gate, New Delhi');assert.equal(c.state.raazDraft.location_place_id,'google-id');
 c.state.raazStep=4;c.renderRaaz();
});
test('Submission uploads real files then attaches their IDs with the confirmed location',async()=>{
 const {c,calls}=setup();c.addRaazEvidence([file()]);c.state.raazStep=4;c.state.raazDraft.latitude='0';c.state.raazDraft.longitude='0';c.state.raazDraft.location_label='Pinned point';
 await c.submitRaazReport();assert.equal(calls[0].endpoint,'/api/evidence');assert.equal(calls[0].options.body.name,'proof.png');
 const report=calls.find(call=>call.endpoint==='/reports');assert.equal(report.options.body.evidence_ids[0],'file-ok');assert.equal(report.options.body.latitude,0);assert.equal(report.options.body.location_label,'Pinned point');assert.equal(c.state.raazEvidence[0].linked,true);assert.equal(c.state.raazScreen,'submitted');
});
test('Failed attachment uploads retain the selected file and never submit a report',async()=>{
 const {c,calls}=setup();c.addRaazEvidence([file()]);c.fetch=async()=>({ok:false,json:async()=>({detail:'File rejected'})});await c.submitRaazReport();
 assert.equal(calls.length,0);assert.equal(c.state.raazEvidence.length,1);assert.equal(c.state.raazSubmitting,false);assert.equal(c.state.raazScreen,'wizard');
});
test('Google Places selections open the incident map confirmation, not a Raahi destination',async()=>{
 const {c}=setup();let target;
 vm.runInContext(source.slice(source.indexOf('async function selectRaahiPlace('),source.indexOf('function routeResultHtml(')),c);
 const input={isConnected:true,name:'incident'};
 c.state.raahiPlaceSearch={input,context:'raaz',items:[{id:'google-id',label:'India Gate',address:'Delhi'}],controller:{signal:{}},sessionToken:'session'};
 c.updateRaahiPlacePanel=()=>{};c.cancelRaahiPlaceSearch=()=>{};c.openMapPicker=(...args)=>target=args;
 c.api=async()=>({latitude:28.61,longitude:77.23,address:'India Gate, Delhi',place_id:'google-id'});
 await c.selectRaahiPlace(0);assert.equal(target[0],'raaz');assert.equal(target[1][0],28.61);assert.equal(target[2].placeId,'google-id');
});
