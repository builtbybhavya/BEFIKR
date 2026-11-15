const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'..','app.js'),'utf8');
const catalog=JSON.parse(fs.readFileSync(path.join(__dirname,'..','assets','baat-banao','recordings.json'),'utf8'));
function harness(){
  const players=[],messages=[];
  class Audio {
    constructor(url){this.src=url;this.paused=true;this.currentTime=0;players.push(this);}
    play(){this.paused=false;return Promise.resolve();}
    pause(){this.paused=true;}
  }
  const context={Audio,BEFIKR_RECORDINGS:catalog,state:{scripts:[],callState:'active',nextLineAvailable:false},render:()=>{},toast:x=>messages.push(x)};
  vm.createContext(context);
  vm.runInContext(source.slice(source.indexOf('function prepareBaatScriptAudio('),source.indexOf('FALLBACK_SCRIPTS.forEach(')),context);
  vm.runInContext(source.slice(source.indexOf('function baatCallTurns('),source.indexOf('function stopGeolocation(')),context);
  return {c:context,players,messages};
}
test('All caller scripts play their own local recordings in numeric order',()=>{
  const {c,players}=harness();
  for(const id of Object.keys(catalog.scripts)){
    const script=c.prepareBaatScriptAudio({id,lines:['Old invented text']});
    c.state.scripts=[script];c.state.selectedScript=id;c.state.callState='active';
    assert.ok(script.lines.length>0);
    assert.notEqual(script.lines[0],'Old invented text');
    let count=0;
    for(let i=0;i<script.dialogue.length;i++){
      const before=players.length;c.speakLine(i);
      if(script.dialogue[i].speaker==='user'){
        assert.equal(players.length,before);assert.equal(c.state.nextLineAvailable,true);
        assert.equal(c.baatTurnDisplayText(script,i),script.dialogue[i].text);
      }else{
        const player=players.at(-1);assert.equal(player.src,script.audio_clips[count++]);
        assert.equal(c.state.nextLineAvailable,false);player.onended();assert.equal(c.state.nextLineAvailable,true);
      }
    }
    assert.equal(count,catalog.scripts[id].audio_clips.length);
    c.speakLine(script.dialogue.length);assert.equal(c.state.callState,'ended');
  }
});
test('Verified mother Hindi keeps her transcript and never plays the user line',()=>{
  const {c,players}=harness();
  const script=c.prepareBaatScriptAudio({id:'mother-checking-in-hindi',transcript_pending:false,dialogue:[{speaker:'mother',text:'Hello'},{speaker:'daughter',text:'My reply',audio:'must-not-play'}]});
  c.state.scripts=[script];c.state.selectedScript=script.id;
  c.speakLine(0);assert.equal(players.length,1);c.speakLine(1);assert.equal(players.length,1);
  assert.equal(script.dialogue[1].audio,undefined);assert.equal(c.baatTurnDisplayText(script,1),'My reply');
});
test('Replay stops the previous recording and ignores its late callbacks',()=>{
  const {c,players}=harness();const id='father-checking-in-english';
  c.state.scripts=[c.prepareBaatScriptAudio({id})];c.state.selectedScript=id;
  c.speakLine(0);const first=players[0],lateEnd=first.onended;c.speakLine(0);
  assert.equal(first.paused,true);assert.equal(first.onended,null);lateEnd();
  assert.equal(c.state.audioPlayer,players[1]);assert.equal(c.state.nextLineAvailable,false);
  players[1].onerror();assert.equal(c.state.nextLineAvailable,true);
});
test('The supplied ringtone loops until it is stopped',()=>{
  const {c,players}=harness();c.startIncomingRingtone();
  assert.equal(players[0].src,'/assets/baat-banao/incoming-ringtone.mp3');assert.equal(players[0].loop,true);
  c.stopIncomingRingtone();assert.equal(players[0].paused,true);assert.equal(c.state.ringtonePlayer,null);
});
test('A missing manifest cannot expose previous canned dialogue',()=>{
  const {c}=harness();delete c.BEFIKR_RECORDINGS;
  const script=c.prepareBaatScriptAudio({id:'brother-worried-hindi',lines:['Old text']});
  assert.equal(script.lines.length,0);assert.equal(script.dialogue.length,0);
});

test('Hindi and Hinglish switches show the supplied caller and user text without changing audio',()=>{
  const {c}=harness();
  for(const id of Object.keys(catalog.scripts).filter(id=>id.endsWith('-hindi'))){
    const script=c.prepareBaatScriptAudio({id,language:'Hindi'});
    for(let i=0;i<script.dialogue.length;i++){
      const turn=script.dialogue[i],audio=turn.audio;
      c.state.hindiTranscriptStyle='devanagari';assert.equal(c.baatTurnDisplayText(script,i),turn.text);
      c.state.hindiTranscriptStyle='hinglish';assert.equal(c.baatTurnDisplayText(script,i),turn.hinglish);
      assert.equal(turn.audio,audio);
      if(turn.speaker==='user')assert.equal(turn.audio,undefined);
    }
  }
});
