const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '..', 'app.js'), 'utf8');
const functions = source.slice(source.indexOf('function filteredSafePlaces('), source.indexOf('function profileIcon('));
const place = {id:'csv-2', name:'Connaught Place PS', address:'Delhi', category:'police', category_label:'Police Station', source_kind:'user_csv', distance_km:1.2, latitude:28.6329, longitude:77.2197, phone:'', notes:'CSV data', source:'[Prior]'};
function harness(api = async () => ({routes:[]})) {
  let html = '';
  const context = {
    state:{page:'safe-spot', safeSpotView:'detail', selectedPlaceId:place.id, places:[place], placeSearch:{latitude:28.62,longitude:77.21}, placeQuery:'', safeSpotCategory:'', placesMeta:{source_state:'csv_dataset'}, spotRoute:null},
    URLSearchParams, AbortController, setTimeout, clearTimeout,
    api, ensureGoogleMaps:async()=>false, requestAnimationFrame:()=>{},
    document:{getElementById:()=>null}, shell:value=>{html=value;},
    esc:value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])),
    window:{open:()=>{throw Error('Safe Spot route must stay in BEFIKR');}}
  };
  vm.createContext(context); vm.runInContext(functions, context);
  return {context,html:()=>html};
}
const route = (id,km) => ({id,distance_km:km,minutes:12,provider:'osmnx_openstreetmap',geometry:{type:'LineString',coordinates:[[77.21,28.62],[77.2197,28.6329]]}});
test('Safe Spot pages use normal place wording and show an in-app route',()=>{
  const {context:c,html}=harness();
  for (const screen of ['home','results','map','detail']) {
    c.state.safeSpotView=screen;c.renderSafeSpot();
    assert.doesNotMatch(html(),/Uploaded CSV|User-provided CSV|CSV notes|CSV entries/i);
    assert.doesNotMatch(html(),/Get Directions in Google Maps|Open in Google Maps to save/);
    assert.doesNotMatch(html(),/data-action="places-source"/);
  }
  assert.match(html(),/Route to Safe Spot/);
  assert.match(html(),/place-detail-map/);
  c.state.safeSpotView='results';c.renderSafeSpot();
  assert.equal((html().match(/class="spot-google-search-link"/g)||[]).length,5);
  assert.ok(html().indexOf('spot-google-search-links')>html().indexOf('spot-place-card'));
  const links=[...html().matchAll(/class="spot-google-search-link" href="([^"]+)"/g)];
  const categories=['police stations','hospitals','restaurants','cafes','parks'];
  for (let i=0;i<links.length;i++) {
    const url=new URL(links[i][1].replaceAll('&amp;','&'));
    assert.equal(url.searchParams.get('api'),'1');
    assert.equal(url.searchParams.get('query'),`${categories[i]} near 28.62,77.21`);
  }
  c.state.safeSpotCategory='hospital';c.renderSafeSpot();
  assert.equal((html().match(/class="spot-google-search-link"/g)||[]).length,1);
  assert.match(html(),/Search nearby hospitals in Google Maps/);
  c.state.places=[];c.renderSafeSpot();
  assert.match(html(),/Search nearby hospitals in Google Maps/);
  c.state.placesLoading=true;c.renderSafeSpot();
  assert.doesNotMatch(html(),/class="spot-google-search-link"/);

});
test('Selection requests the confirmed endpoints and displays the shortest walking path',async()=>{
  const calls=[];
  const {context:c,html}=harness(async(endpoint,options)=>{calls.push({endpoint,options});return {routes:[route('long',2),route('short',1.5)]};});
  await c.loadSpotRoute(place);
  assert.equal(calls[0].endpoint,'/routes/alternatives');
  assert.equal(calls[0].options.body.origin_latitude,28.62);
  assert.equal(calls[0].options.body.destination_longitude,77.2197);
  assert.equal(c.state.spotRoute.route.id,'short');
  assert.match(html(),/1.50 km/);assert.match(html(),/12 min/);
  await c.loadSpotRoute(place);assert.equal(calls.length,1);
  await c.loadSpotRoute(place,true);assert.equal(calls.length,2);
});
test('Provider failure offers retry without fabricating a straight-line route',async()=>{
  const {context:c,html}=harness(async()=>{throw Error('Network unavailable');});
  await c.loadSpotRoute(place);
  assert.equal(c.state.spotRoute.route,null);assert.equal(c.state.spotRoute.loading,false);
  assert.match(html(),/Walking route unavailable/);assert.match(html(),/Retry route/);
});
test('Missing start point never sends a routing request',async()=>{
  const {context:c,html}=harness(()=>{throw Error('must not call API');});c.state.placeSearch=null;
  await c.loadSpotRoute(place);assert.match(html(),/Choose your starting location first/);
});
test('An older delayed request cannot replace the newly selected destination',async()=>{
  let finish,started;
  const ready=new Promise(resolve=>started=resolve);
  const waiting=new Promise(resolve=>finish=resolve);
  const second={...place,id:'csv-3',name:'Another place',longitude:77.23};
  let count=0;
  const {context:c}=harness(async()=>{if(++count===1){started();return waiting;}return {routes:[route('new',2)]};});
  const first=c.loadSpotRoute(place);await ready;
  c.state.places.push(second);c.state.selectedPlaceId=second.id;
  await c.loadSpotRoute(second);
  finish({routes:[route('old',1)]});await first;
  assert.equal(c.state.spotRoute.route.id,'new');
});
