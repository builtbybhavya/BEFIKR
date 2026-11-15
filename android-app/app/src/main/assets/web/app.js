if(typeof window!=="undefined"&&window.L&&window.L.Icon&&window.L.Icon.Default){
  const defaultSvgPin='data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="25" height="41" viewBox="0 0 25 41"><path fill="%231a73e8" stroke="%23ffffff" stroke-width="1.5" d="M12.5 0C5.6 0 0 5.6 0 12.5 0 21.9 12.5 41 12.5 41S25 21.9 25 12.5C25 5.6 19.4 0 12.5 0z"/><circle fill="%23ffffff" cx="12.5" cy="12.5" r="5"/></svg>';
  delete window.L.Icon.Default.prototype._getIconUrl;
  window.L.Icon.Default.mergeOptions({iconUrl:defaultSvgPin,iconRetinaUrl:defaultSvgPin,shadowUrl:""});
}
/* BEFIKR mobile-first PWA client. Demo and unavailable integrations are labelled in the UI. */
const API = "/api";
const BAAT_CATALOG = [
  {caller:"Mother",voice:"female",scenarios:[
    {id:"checking-in",title:"Checking in",english:["Beta, just checking in. Are you okay?","Call me when you get a moment.","I’m right here. Take your time."],hindi:["हेलो बेटा! हाँ, कहाँ पहुँच गई तू? कब से तेरा इंतज़ार कर रही हूँ मैं।","अच्छा, और कितनी देर लगेगी? खाना भी लगा दिया है मैंने। तुझे पता है न, मैं तेरे बिना खाना नहीं खाती।","अच्छा सुन, आज तेरे पापा भी जल्दी घर आ गए हैं। तेरे बारे में ही पूछ रहे थे। कह रहे थे कि बेटी को फ़ोन लगाओ, कहाँ रह गई है।","और सुन, कल तूने मुझे उस कपड़े के बारे में बताया था न, मैंने वह देख लिया है। बहुत सुंदर है! घर आकर मुझे दोबारा दिखाना।","अच्छा, एक काम करना। जब तू घर के पास पहुँच जाए न, तो मुझे बता देना। मैं दरवाज़ा खोल दूँगी। और अपना फ़ोन पास ही रखना, समझी?","चल, ठीक है बेटा। आराम से आना। मैं यहीं हूँ, तेरा इंतज़ार कर रही हूँ."],hinglish:["Hello beta! Haan, kahaan pahunch gayi tu? Kab se tera intezaar kar rahi hoon main.","Achha, aur kitni der lagegi? Khana bhi laga diya hai maine. Tujhe pata hai na, main tere bina khana nahi khaati.","Achha sun, aaj tere papa bhi jaldi ghar aa gaye hain. Tere baare mein hi pooch rahe the. Keh rahe the ki beti ko phone lagao, kahaan reh gayi hai.","Aur sun, kal tune mujhe us kapde ke baare mein bataya tha na, maine woh dekh liya hai. Bahut sundar hai! Ghar aakar mujhe dobara dikhana.","Achha, ek kaam karna. Jab tu ghar ke paas pahunch jaaye na, toh mujhe bata dena. Main darwaaza khol doongi. Aur apna phone paas hi rakhna, samjhi?","Chal, theek hai beta. Aaram se aana. Main yahin hoon, tera intezaar kar rahi hoon."]},
    {id:"worried",title:"Worried",english:["Beta, I haven’t heard from you in a while. Is everything okay?","Please call me when you can. I’m getting worried.","I can come get you. Just let me know what you need."],hindi:["बेटा, काफ़ी देर से तुम्हारा जवाब नहीं आया। सब ठीक है?","जब हो सके मुझे कॉल करना, मुझे चिंता हो रही है।","अगर चाहो तो मैं तुम्हें लेने आ जाऊँ। बस बता देना."],hinglish:["Beta, kaafi der se tumhara jawab nahi aaya. Sab theek hai?","Jab ho sake mujhe call karna, mujhe chinta ho rahi hai.","Agar chaho toh main tumhe lene aa jaaun. Bas bata dena."]}
  ]},
  {caller:"Father",voice:"male",scenarios:[
    {id:"checking-in",title:"Checking in",english:["Hey, just checking—are things going okay?","I wanted to see how your evening is going.","Call me when you’re free, no rush."],hindi:["बेटा, बस पूछ रहा हूँ—सब ठीक चल रहा है?","तुम्हारी शाम कैसी जा रही है, यही जानना था।","फुर्सत मिले तो कॉल करना, कोई जल्दी नहीं."],hinglish:["Beta, bas pooch raha hoon—sab theek chal raha hai?","Tumhari shaam kaisi ja rahi hai, yahi jaan-na tha.","Fursat mile toh call karna, koi jaldi nahi."]},
    {id:"worried",title:"Worried",english:["I haven’t been able to reach you. Is everything all right?","Call me as soon as you can; I’m concerned.","Would you like me to come pick you up?"],hindi:["तुमसे बात नहीं हो पा रही है। सब ठीक तो है?","जब हो सके मुझे कॉल करना, मुझे फ़िक्र हो रही है।","क्या मैं तुम्हें लेने आ जाऊँ?"],hinglish:["Tumse baat nahi ho paa rahi hai. Sab theek toh hai?","Jab ho sake mujhe call karna, mujhe fikr ho rahi hai.","Kya main tumhe lene aa jaaun?"]}
  ]},
  {caller:"Sister",voice:"female",scenarios:[
    {id:"checking-in",title:"Checking in",english:["Hey, just checking in. Did you get there okay?","Call me when you get a chance.","I’m here if you need anything."],hindi:["सुन, बस पूछ रही हूँ—तुम ठीक से पहुँच गई?","मौका मिले तो मुझे कॉल करना।","कुछ चाहिए तो मैं यहीं हूँ."],hinglish:["Sun, bas pooch rahi hoon—tum theek se pahunch gayi?","Mauka mile toh mujhe call karna.","Kuch chahiye toh main yahin hoon."]},
    {id:"worried",title:"Worried",english:["I haven’t heard from you in a while. Is everything okay?","I’m getting worried—please call me when you can.","Want me to come meet you?"],hindi:["काफ़ी देर से तुम्हारा मैसेज नहीं आया। सब ठीक है?","मुझे चिंता हो रही है—हो सके तो कॉल करना।","क्या मैं तुमसे मिलने आ जाऊँ?"],hinglish:["Kaafi der se tumhara message nahi aaya. Sab theek hai?","Mujhe chinta ho rahi hai—ho sake toh call karna.","Kya main tumse milne aa jaaun?"]}
  ]},
  {caller:"Brother",voice:"male",scenarios:[
    {id:"checking-in",title:"Checking in",english:["Hey, just checking—are you doing okay?","Let me know when you get a minute.","I’m around if you need me."],hindi:["सुन, बस पूछ रहा हूँ—सब ठीक है?","फुर्सत मिले तो मुझे बता देना।","ज़रूरत हो तो मैं यहीं हूँ."],hinglish:["Sun, bas pooch raha hoon—sab theek hai?","Fursat mile toh mujhe bata dena.","Zaroorat ho toh main yahin hoon."]},
    {id:"worried",title:"Worried",english:["You haven’t replied for a while. Is everything all right?","I’m a bit worried—call me when you can.","Should I come pick you up?"],hindi:["काफ़ी देर से तुम्हारा जवाब नहीं आया। सब ठीक तो है?","थोड़ी चिंता हो रही है—हो सके तो कॉल करना।","क्या मैं तुम्हें लेने आ जाऊँ?"],hinglish:["Kaafi der se tumhara jawab nahi aaya. Sab theek toh hai?","Thodi chinta ho rahi hai—ho sake toh call karna.","Kya main tumhe lene aa jaaun?"]}
  ]},
  {caller:"Boyfriend",voice:"male",scenarios:[
    {id:"checking-in",title:"Checking in",english:["Hey, just checking in. Are you doing okay?","Call me when you get a chance.","I’m here if you need me."],hindi:["अरे, बस पूछ रहा था—तुम ठीक हो?","मौका मिले तो मुझे कॉल कर लेना।","मैं यहीं हूँ, अगर तुम्हें मेरी ज़रूरत हो."],hinglish:["Arey, bas pooch raha tha—tum theek ho?","Mauka mile toh mujhe call kar lena.","Main yahin hoon, agar tumhe meri zaroorat ho."]},
    {id:"worried",title:"Worried",english:["I haven’t heard from you for a bit. Is everything okay?","I’m getting a little worried—please call when you can.","If you want, I can come meet you."],hindi:["काफ़ी देर से तुम्हारी ख़बर नहीं मिली। सब ठीक है?","थोड़ी चिंता हो रही है—हो सके तो मुझे कॉल करना।","अगर चाहो तो मैं तुमसे मिलने आ जाऊँ."],hinglish:["Kaafi der se tumhari khabar nahi mili. Sab theek hai?","Thodi chinta ho rahi hai—ho sake toh mujhe call karna.","Agar chaho toh main tumse milne aa jaaun."]}
  ]}
];
const FALLBACK_SCRIPTS = BAAT_CATALOG.flatMap(person=>person.scenarios.flatMap(scenario=>["English","Hindi"].map(language=>({
  id:`${person.caller.toLowerCase()}-${scenario.id}-${language.toLowerCase()}`,title:scenario.title,situation:scenario.id,scenario:scenario.id,scenario_label:scenario.title,caller:person.caller,voice:person.voice,language,
  lines:language==="Hindi"?scenario.hindi:scenario.english,hinglish_lines:language==="Hindi"?scenario.hinglish:undefined
}))));
const MOM_CHECKING_HINDI_DIALOGUE = [
  {speaker:"mother",text:"हेलो बेटा! हाँ, कहाँ पहुँच गई तू? कब से तेरा इंतज़ार कर रही हूँ मैं।",hinglish:"Hello beta! Haan, kahaan pahunch gayi tu? Kab se tera intezaar kar rahi hoon main.",audio:"/assets/baat-banao/mom-checking-in-hi/01.mp3"},
  {speaker:"daughter",text:"बस माँ, आ रही हूँ।",hinglish:"Bas Maa, aa rahi hoon."},
  {speaker:"mother",text:"अच्छा, और कितनी देर लगेगी? खाना भी लगा दिया है मैंने। तुझे पता है न, मैं तेरे बिना खाना नहीं खाती।",hinglish:"Achha, aur kitni der lagegi? Khana bhi laga diya hai maine. Tujhe pata hai na, main tere bina khana nahi khaati.",audio:"/assets/baat-banao/mom-checking-in-hi/02.mp3"},
  {speaker:"daughter",text:"हाँ माँ, बस थोड़ी देर में पहुँच जाऊँगी।",hinglish:"Haan Maa, bas thodi der mein pahunch jaaungi."},
  {speaker:"mother",text:"अच्छा सुन, आज तेरे पापा भी जल्दी घर आ गए हैं। तेरे बारे में ही पूछ रहे थे। कह रहे थे कि बेटी को फ़ोन लगाओ, कहाँ रह गई है।",hinglish:"Achha sun, aaj tere papa bhi jaldi ghar aa gaye hain. Tere baare mein hi pooch rahe the. Keh rahe the ki beti ko phone lagao, kahaan reh gayi hai.",audio:"/assets/baat-banao/mom-checking-in-hi/03.mp3"},
  {speaker:"daughter",text:"अच्छा, ठीक है माँ।",hinglish:"Achha, theek hai Maa."},
  {speaker:"mother",text:"और सुन, कल तूने मुझे उस कपड़े के बारे में बताया था न, मैंने वह देख लिया है। बहुत सुंदर है! घर आकर मुझे दोबारा दिखाना।",hinglish:"Aur sun, kal tune mujhe us kapde ke baare mein bataya tha na, maine woh dekh liya hai. Bahut sundar hai! Ghar aakar mujhe dobara dikhana.",audio:"/assets/baat-banao/mom-checking-in-hi/04.mp3"},
  {speaker:"daughter",text:"हाँ माँ, दिखा दूँगी।",hinglish:"Haan Maa, dikha doongi."},
  {speaker:"mother",text:"अच्छा, एक काम करना। जब तू घर के पास पहुँच जाए न, तो मुझे बता देना। मैं दरवाज़ा खोल दूँगी। और अपना फ़ोन पास ही रखना, समझी?",hinglish:"Achha, ek kaam karna. Jab tu ghar ke paas pahunch jaaye na, toh mujhe bata dena. Main darwaaza khol doongi. Aur apna phone paas hi rakhna, samjhi?",audio:"/assets/baat-banao/mom-checking-in-hi/05.mp3"},
  {speaker:"daughter",text:"हाँ माँ।",hinglish:"Haan Maa."},
  {speaker:"mother",text:"चल, ठीक है बेटा। आराम से आना। मैं यहीं हूँ, तेरा इंतज़ार कर रही हूँ।",hinglish:"Chal, theek hai beta. Aaram se aana. Main yahin hoon, tera intezaar kar rahi hoon.",audio:"/assets/baat-banao/mom-checking-in-hi/06.mp3"}
];
const MOM_CHECKING_ENGLISH_DIALOGUE = [
  {speaker:"mother",text:"Hello, sweetheart! Hey, where have you reached? I've been waiting for you for so long."},
  {speaker:"daughter",text:"I'm coming, Mom. I'll be there soon."},
  {speaker:"mother",text:"Alright, how much longer will you take? I've already served dinner. You know I never eat without you."},
  {speaker:"daughter",text:"Yes, Mom. Just a little while longer."},
  {speaker:"mother",text:"Listen, your father came home early today as well. He was asking about you. He said, \"Call our daughter and ask where she has been.\""},
  {speaker:"daughter",text:"Oh, okay, Mom."},
  {speaker:"mother",text:"And listen, remember that dress you told me about yesterday? I found it! It's really beautiful. Show it to me again when you get home."},
  {speaker:"daughter",text:"Yes, Mom. I'll show you."},
  {speaker:"mother",text:"Alright, do one thing. Let me know when you're close to home. I'll open the gate for you. And keep your phone with you, understood?"},
  {speaker:"daughter",text:"Yes, Mom."},
  {speaker:"mother",text:"Alright, sweetheart. Come home safely and take your time. I'll be right here waiting for you."}
];
const momEnglishCheckinFallback=FALLBACK_SCRIPTS.find(script=>script.id==="mother-checking-in-english");
if(momEnglishCheckinFallback){momEnglishCheckinFallback.dialogue=MOM_CHECKING_ENGLISH_DIALOGUE;momEnglishCheckinFallback.lines=MOM_CHECKING_ENGLISH_DIALOGUE.filter(turn=>turn.speaker==="mother").map(turn=>turn.text);}
const momHindiCheckinFallback=FALLBACK_SCRIPTS.find(script=>script.id==="mother-checking-in-hindi");
if(momHindiCheckinFallback){momHindiCheckinFallback.dialogue=MOM_CHECKING_HINDI_DIALOGUE;momHindiCheckinFallback.lines=MOM_CHECKING_HINDI_DIALOGUE.filter(turn=>turn.speaker==="mother").map(turn=>turn.text);momHindiCheckinFallback.hinglish_lines=MOM_CHECKING_HINDI_DIALOGUE.filter(turn=>turn.speaker==="mother").map(turn=>turn.hinglish);}
const MOM_WORRIED_HINDI_DIALOGUE = [
  {speaker:"mother",text:"नमस्ते! बेटा, मेरी आवाज़ सुनाई दे रही है? हाँ, अब बता, सब ठीक है न?",hinglish:"Namaste! Beta, meri awaaz sunai de rahi hai? Haan, ab bata, sab theek hai na?"},
  {speaker:"daughter",text:"हाँ माँ, सब ठीक है।",hinglish:"Haan Maa, sab theek hai."},
  {speaker:"mother",text:"अच्छा। आज तेरा दिन कैसा रहा? सुबह तो बड़ी जल्दी में निकली थी तू।",hinglish:"Achha. Aaj tera din kaisa raha? Subah toh badi jaldi mein nikli thi tu."},
  {speaker:"daughter",text:"हाँ माँ, थोड़ा काम था।",hinglish:"Haan Maa, thoda kaam tha."},
  {speaker:"mother",text:"अच्छा, वह जो तूने बताया था न कि आज तेरा कोई ज़रूरी काम है, वह हो गया?",hinglish:"Achha, woh jo tune bataya tha na ki aaj tera koi zaroori kaam hai, woh ho gaya?"},
  {speaker:"daughter",text:"हाँ, हो गया।",hinglish:"Haan, ho gaya."},
  {speaker:"mother",text:"चलो, अच्छी बात है। देख बेटा, घर आकर आराम करना। मैं तेरे लिए चाय बना दूँगी। और हाँ, तेरे पसंदीदा पकौड़े भी बना रखे हैं।",hinglish:"Chalo, achhi baat hai. Dekh beta, ghar aakar aaram karna. Main tere liye chai bana doongi. Aur haan, tere pasandeeda pakode bhi bana rakhe hain."},
  {speaker:"daughter",text:"अच्छा माँ!",hinglish:"Achha Maa!"},
  {speaker:"mother",text:"हाँ, हाँ! और सुन, पापा भी बस थोड़ी देर में आ जाएँगे। वे कह रहे थे कि आज सब साथ बैठकर खाना खाएँगे।",hinglish:"Haan, haan! Aur sun, papa bhi bas thodi der mein aa jaayenge. Woh keh rahe the ki aaj sab saath baithkar khana khaayenge."},
  {speaker:"daughter",text:"ठीक है माँ।",hinglish:"Theek hai Maa."},
  {speaker:"mother",text:"अच्छा, तू मुझसे बात करती रह। मुझे भी तेरे साथ थोड़ी देर बातें करनी हैं। बहुत दिन हो गए, हमने ढंग से बात ही नहीं की।",hinglish:"Achha, tu mujhse baat karti reh. Mujhe bhi tere saath thodi der baatein karni hain. Bahut din ho gaye, humne dhang se baat hi nahi ki."}
];
const MOM_WORRIED_HINDI_LOOP = [{speaker:"mother",text:"हम्म, अच्छा।",hinglish:"Hmm, achha.",loop:true}];
const momHindiWorriedFallback=FALLBACK_SCRIPTS.find(script=>script.id==="mother-worried-hindi");
if(momHindiWorriedFallback){momHindiWorriedFallback.title="Worried Mom";momHindiWorriedFallback.scenario_label="Worried Mom";momHindiWorriedFallback.dialogue=MOM_WORRIED_HINDI_DIALOGUE;momHindiWorriedFallback.lines=MOM_WORRIED_HINDI_DIALOGUE.filter(turn=>turn.speaker==="mother").map(turn=>turn.text);momHindiWorriedFallback.hinglish_lines=MOM_WORRIED_HINDI_DIALOGUE.filter(turn=>turn.speaker==="mother").map(turn=>turn.hinglish);momHindiWorriedFallback.loop_turns=MOM_WORRIED_HINDI_LOOP;}
const MOM_WORRIED_ENGLISH_DIALOGUE = [
  {speaker:"mother",text:"Hello! Sweetheart, can you hear me? Yes, now tell me, everything is alright, isn't it?"},
  {speaker:"daughter",text:"Yes, Mom. Everything is fine."},
  {speaker:"mother",text:"Alright. How was your day today? You left in such a hurry this morning."},
  {speaker:"daughter",text:"Yes, Mom. I had some work to take care of."},
  {speaker:"mother",text:"Oh, right! You told me you had something important to do today. Did everything go well?"},
  {speaker:"daughter",text:"Yes, it did."},
  {speaker:"mother",text:"That's good to hear. Listen, sweetheart, make sure you get some rest when you come home. I'll make some tea for you. And yes, I've also made your favourite pakoras."},
  {speaker:"daughter",text:"Oh, lovely, Mom!"},
  {speaker:"mother",text:"Of course! And listen, your father will be home in a little while too. He said we should all sit together and have dinner today."},
  {speaker:"daughter",text:"Alright, Mom."},
  {speaker:"mother",text:"Now, keep talking to me. I want to chat with you for a little while too. It's been so long since we've had a proper conversation."}
];
const MOM_WORRIED_ENGLISH_LOOP = [{speaker:"mother",text:"Hmm, okay.",loop:true}];
const momEnglishWorriedFallback=FALLBACK_SCRIPTS.find(script=>script.id==="mother-worried-english");
if(momEnglishWorriedFallback){momEnglishWorriedFallback.title="Worried Mom";momEnglishWorriedFallback.scenario_label="Worried Mom";momEnglishWorriedFallback.dialogue=MOM_WORRIED_ENGLISH_DIALOGUE;momEnglishWorriedFallback.lines=MOM_WORRIED_ENGLISH_DIALOGUE.filter(turn=>turn.speaker==="mother").map(turn=>turn.text);momEnglishWorriedFallback.loop_turns=MOM_WORRIED_ENGLISH_LOOP;}
function prepareBaatScriptAudio(script){
  const entry=globalThis.BEFIKR_RECORDINGS?.scripts?.[script.id];
  const clips=script.audio_clips||entry?.audio_clips||[];
  const pending=script.transcript_pending??entry?.transcript_pending??(script.id!=="mother-checking-in-hindi");
  const result={...script,audio_clips:clips,audio_count:clips.length,transcript_pending:pending};
  if(pending){
    result.lines=[];result.hinglish_lines=[];result.dialogue=[];result.loop_turns=[];
    clips.forEach((audio,index)=>{
      result.dialogue.push({speaker:"caller",text:"",audio,transcript_pending:true});
      if(index<clips.length-1)result.dialogue.push({speaker:"user",text:"",transcript_pending:true});
    });
  }else{
    let index=0;
    const dialogue=script.transcript_pending===false?(script.dialogue||[]):(entry?.dialogue||script.dialogue||[]);
    result.dialogue=dialogue.map(turn=>{
      const copy={...turn};delete copy.audio;
      if(!["daughter","user"].includes(turn.speaker)){
        if(clips[index])copy.audio=clips[index];
        index++;
      }
      return copy;
    });
    result.lines=result.dialogue.filter(turn=>!["daughter","user"].includes(turn.speaker)).map(turn=>turn.text);
    result.hinglish_lines=result.dialogue.filter(turn=>!["daughter","user"].includes(turn.speaker)).map(turn=>turn.hinglish||"");
    result.loop_turns=[];
  }
  if(entry?.loop_audio)result.loop_turns=[{speaker:"caller",text:"",audio:entry.loop_audio,loop:true,transcript_pending:pending}];
  return result;
}
FALLBACK_SCRIPTS.forEach((script,index)=>{FALLBACK_SCRIPTS[index]=prepareBaatScriptAudio(script);});
const state = { token: localStorage.getItem("befikr-token"), user: null, page: "home", authMode: "login", guestDemo: false,
  contacts: (() => { try { return JSON.parse(localStorage.getItem("befikr-contacts") || "[]"); } catch { return []; } })(), reports: [], scripts: FALLBACK_SCRIPTS, selectedScript: FALLBACK_SCRIPTS[0]?.id || "mother-checking-in-english", caller: "Mother", alternatives: null,
  spotRoute: null, spotRouteController: null,
  raahiDemoCatalog: null, raahiDemoPairId: "", raahiDemoTimeBand: "current", raahiDemoResult: null, raahiDemoError: "", raahiDemoLoading: false, raahiDemoRequestId: 0,
  raahiView: "home", routeInput: {origin:"",destination:"",origin_latitude:null,origin_longitude:null,destination_latitude:null,destination_longitude:null}, selectedRouteId: null, routeSort: "shortest", recentTrips: [], routeLoading: false, routeError: "", raahiJourney: null, raahiFeedback: "", raahiPlaceSearch: null,
  sos: null, sosEvents: [], sosLocation: null, sosLocationPending: false, sosLocationError: "", sosAttemptId: 0, nativeSosDispatchedAttempt: 0, tracking: null, watchId: null, deviceLocation: null, mapVisible: false, homeLocationKnown: false, sosHoldTimer: null, sosHoldTriggered: false,
  journey: null, journeyTimer: null, journeyGraceTimer: null, adminTab: "reports", adminReports: [], placeCandidates: [],
  places: [], placesMeta: null, placeSearch: null, placeSearchController: null, safeSpotView: "home", safeSpotCategory: "", placeQuery: "", selectedPlaceId: null, placesLoading: false, toastTimer: null, speechLine: 0,
  mapPicker: null, tapmeRoute: readStoredJson("befikr-tapme-route",null), googleMapsPromise: null, googleMapsReady: false,
  selectedLanguage: "English", hindiTranscriptStyle: "devanagari", callState: "idle", speechPaused: false, nextLineAvailable: false, audioPlayer: null, ringtonePlayer: null,
  raazEvidence: [], raazSubmitting: false, raazLocationQuery: "", raazPreviewUrl: null,
  raazStep: 1, raazScreen: "wizard", raazDraft: {category:"",description:"",occurred_at:"",latitude:"",longitude:"",location_label:"",location_place_id:""}, raazSubmittedReport: null, raazFilter: "all", raazSelectedReportId: null };
const appRoot = document.getElementById("app");
window.onBefikrAndroidPermissions=result=>{if(result?.sms&&result?.location)toast("Android SOS SMS and location permissions are ready.");else if(!result?.sms)toast("SMS permission is required for automatic SOS texts.");};

function esc(value=""){return String(value).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
function readStoredJson(key,fallback){try{return JSON.parse(localStorage.getItem(key)||"null")??fallback;}catch{return fallback;}}
let googleMapsConfigPromise;
function googleMapsConfig(){
  if(!googleMapsConfigPromise){
    googleMapsConfigPromise=api("/maps/config").catch(error=>{
      googleMapsConfigPromise=null;
      throw error;
    });
  }
  return googleMapsConfigPromise;
}

async function renderGoogleMapEmbed(container,mode,parameters,title){
  if(!container?.isConnected)return false;
  let config;
  try{config=await googleMapsConfig();}catch{return false;}
  if(!container.isConnected||!config.google_maps_embed_enabled||!config.google_maps_embed_key)return false;
  const url=new URL(`https://www.google.com/maps/embed/v1/${mode}`);
  url.search=new URLSearchParams({...parameters,region:"in",key:config.google_maps_embed_key});
  const frame=document.createElement("iframe");
  frame.src=url.href;
  frame.title=title;
  frame.referrerPolicy="strict-origin-when-cross-origin";
  frame.allowFullscreen=true;
  frame.loading="lazy";
  container.classList.add("google-map-embed");
  container.removeAttribute("role");
  container.replaceChildren(frame);
  return true;
}

async function ensureGoogleMaps(){
  if(window.google?.maps){state.googleMapsReady=true;return true;}
  if(state.googleMapsPromise)return state.googleMapsPromise;
  state.googleMapsPromise=(async()=>{
    try{
      const config=await googleMapsConfig();
      if(!config.google_maps_enabled||!config.google_maps_browser_key)return false;
      return await new Promise(resolve=>{
        const callback="__befikrGoogleMapsReady";
        window[callback]=()=>{state.googleMapsReady=Boolean(window.google?.maps);resolve(state.googleMapsReady);};
        const script=document.createElement("script");
        script.src=`https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(config.google_maps_browser_key)}&callback=${callback}&loading=async&v=weekly`;
        script.async=true;script.onerror=()=>resolve(false);document.head.appendChild(script);
        setTimeout(()=>resolve(Boolean(window.google?.maps)),12000);
      });
    }catch{return false;}
  })();
  state.googleMapsReady=await state.googleMapsPromise;
  return state.googleMapsReady;
}
function tapMePlan(route){
  const duration=Math.max(1,Math.ceil(Number(route?.minutes)||1));
  const R=Number.isFinite(Number(route?.risk_score))?Number(route.risk_score):50,P=50,T=50,I=50,V=0,E=50,M=50;
  const risk=Math.round((.25*R+.15*P+.10*T+.15*I+.10*V+.10*E+.15*M)*10)/10;
  const base=Math.ceil(duration/120),count=Math.min(12,Math.max(1,Math.ceil(base*(1+risk/100))));
  return {duration,risk,base,count,components:{risk_route:R,risk_population:P,risk_time:T,risk_isolation:I,risk_deviation:V,risk_eta:E,risk_mode:M}};
}
function saveTapMeRoute(route){state.tapmeRoute=route;localStorage.setItem("befikr-tapme-route",JSON.stringify(route));}
function toast(message){const el=document.getElementById("toast");el.textContent=message;el.className="toast show";clearTimeout(state.toastTimer);state.toastTimer=setTimeout(()=>el.className="toast",3400);}
function nativeAndroidAvailable(){try{return Boolean(window.BefikrAndroid?.isAvailable?.());}catch{return false;}}
function offline(){return !navigator.onLine;}
async function api(path,options={}){
  const basePath = path.split("?")[0];
  const urlParams = new URLSearchParams(path.includes("?") ? path.slice(path.indexOf("?")) : "");

  // Offline Voice scripts catalog - instant response
  if(basePath === "/voice/scripts" || basePath === "/scripts"){
    return { scripts: FALLBACK_SCRIPTS };
  }

  // Trusted Contacts - robust offline persistence
  if(basePath === "/contacts" || basePath.startsWith("/contacts/")){
    let saved = [];
    try { saved = JSON.parse(localStorage.getItem("befikr-contacts") || "[]"); } catch(e) { saved = []; }
    if (!Array.isArray(saved)) saved = [];

    if(options.method === "POST"){
      let body = options.body;
      if(typeof body === "string"){ try { body = JSON.parse(body); } catch(e){} }
      body = body || {};
      const newContact = {
        id: "c_" + Date.now() + "_" + Math.random().toString(36).slice(2, 6),
        name: (body.name || "Trusted Contact").trim(),
        phone: (body.phone || "").trim(),
        relationship: (body.relationship || "").trim(),
        created_at: new Date().toISOString()
      };
      saved.push(newContact);
      localStorage.setItem("befikr-contacts", JSON.stringify(saved));
      state.contacts = saved;
      return newContact;
    }
    if(options.method === "DELETE"){
      const idToDelete = basePath.split("/")[2] || "";
      saved = saved.filter(c => c.id !== idToDelete);
      localStorage.setItem("befikr-contacts", JSON.stringify(saved));
      state.contacts = saved;
      return { status: "deleted", id: idToDelete };
    }
    state.contacts = saved;
    return saved;
  }

  // Profile - offline user session
  if(basePath === "/profile"){
    try {
      const stored = JSON.parse(localStorage.getItem("befikr-user") || "null");
      if(stored) return stored;
    } catch(e){}
    return { id: "local_user", name: "Befikr User", email: "user@befikr.app", role: "user" };
  }

  // SOS
  if(basePath === "/sos" || basePath.startsWith("/sos")){
    return { status: "created", delivery_state: "local_only", message: "SOS signal dispatched." };
  }

  const headers={"Content-Type":"application/json",...(state.token?{Authorization:`Bearer ${state.token}`}:{ }),...(options.headers||{})};
  let response;
  try{
    response=await fetch(API+path,{...options,headers,body:options.body&&typeof options.body!=="string"?JSON.stringify(options.body):options.body});
  }catch(e){
    // Zero-network offline fallback for standalone Android / desktop execution
    if(basePath==="/maps/config") return {provider:"offline_ai_decider",offline:true};
    if(basePath==="/routes/data-status") return {state:"operational",mapping_provider:"offline_ai_decider",message:"Offline dataset active on device."};
    if(basePath==="/places/autocomplete"){
      try{
        const q = (urlParams.get("input") || urlParams.get("q") || (options.body && options.body.input) || "").toString().toLowerCase().trim();
        if(!q) return {suggestions:[], places:[], source:"offline_data"};
        const matched = filterOfflinePlaces(q, 10);
        const suggestions = matched.map(p=>({
          place_id: p.id || p.place_id,
          id: p.id || p.place_id,
          name: p.name || p.label,
          label: p.name || p.label,
          address: p.address || "",
          latitude: p.latitude,
          longitude: p.longitude
        }));
        return {suggestions, places:suggestions, source:"offline_data"};
      }catch(err){return {suggestions:[], places:[], source:"offline_fallback"};}
    }
    if(basePath==="/places/resolve"){
      try{
        const pid = urlParams.get("place_id") || options.body?.place_id;
        const p = (state.offlinePlaces||[]).find(item=>item.id===pid) || (state.offlinePlaces||[])[0];
        if(p){
          return {
            place_id: p.id,
            latitude: p.latitude,
            longitude: p.longitude,
            address: p.address,
            attributions: []
          };
        }
      }catch(err){}
      return {place_id:"off_1", latitude:28.6328, longitude:77.2197, address:"Delhi", attributions:[]};
    }
    if(basePath==="/places/nearby"){
      try{
        return {places:state.offlinePlaces||[],source:"offline_data"};
      }catch(err){return {places:[],source:"offline_fallback"};}
    }
    if(basePath.startsWith("/routes")){
      try{
        const orig = (urlParams.get("origin") || (options.body&&options.body.origin) || "").toLowerCase().trim();
        const dest = (urlParams.get("destination") || (options.body&&options.body.destination) || "").toLowerCase().trim();
        const corridors = state.offlineCorridors || [];
        const match = corridors.find(c=>
          (c.origin.includes(orig)||orig.includes(c.origin)) &&
          (c.destination.includes(dest)||dest.includes(c.destination))
        );
        if(match && match.result && match.result.routes && match.result.routes.length){
          return match.result;
        }
        if(corridors.length && corridors[0].result){
          return corridors[0].result;
        }
        return {routes:[],state:"offline_ready"};
      }catch(err){return {routes:[],state:"offline_fallback"};}
    }
    return {status:"ok"};
  }
  if(response.status===204)return null;
  const body=await response.json().catch(()=>({}));
  if(!response.ok)throw new Error(body.detail||body.message||`Request failed (${response.status}).`);
  return body;
}
function shell(content){
  const showNav=state.page!=="auth";
  const adminTools=state.page==="settings"&&["admin","moderator"].includes(state.user?.role)?`<section class="card profile-admin-link"><h3>Admin console</h3><p class="sub">Open the staff tools for authorised report and directory management.</p><button class="btn secondary" data-action="admin">Open admin console</button></section>`:"";
  const navItems=[
    {action:"raahi",label:"Raahi",theme:"raahi",icon:homeIcon("raahi")},
    {action:"raaz",label:"Raaz",theme:"raaz",icon:homeIcon("raaz")},
    {action:"baat-banao",label:"Baat Banao",theme:"baat",icon:homeIcon("baat")},
    {action:"backup",label:"Backup",theme:"backup",icon:homeIcon("backup")},
    {action:"safe-spot",label:"Safe Spot",theme:"spot",icon:homeIcon("spot")}
  ];
  const appNav=`<nav class="bottom-nav" aria-label="Main navigation">${navItems.map(item=>{const active=state.page===item.action;return `<button type="button" data-action="${item.action}" class="nav-item nav-${item.theme}${active?" active":""}" ${active?'aria-current="page"':""} aria-label="${item.label}"><span class="nav-icon" aria-hidden="true">${item.icon}</span><span class="nav-label">${item.label}</span></button>`;}).join("")}</nav>`;
  appRoot.innerHTML=`<div class="shell ${state.page==="home"?"home-shell":""} ${state.page==="settings"?"profile-shell":""} ${state.page==="backup"?"backup-shell":""} ${state.page==="raaz"?"raaz-shell":""}"><header class="topbar"><a class="header-app-icon" href="#" data-action="home" aria-label="BEFIKR home"><img src="/assets/befikr-icon-192.png" alt=""></a><a class="brand header-brand" href="#" data-action="home"><span class="brand-copy"><span class="brand-name">BEFIKR</span><span class="brand-sub">Bhool Ja Saare Dar - Ban BEFIKR!</span></span></a><div class="top-actions"><button class="map-shortcut header-icon-button" data-action="map" aria-label="Location" title="Location">${homeIcon("spot")}</button><button class="user-chip header-icon-button" data-action="profile" aria-label="Profile" title="Profile">${homeIcon("profile")}</button></div></header><main class="layout">${content}${adminTools}</main>${showNav?appNav:""}</div>`;
}
function brandBlock(){return `<a class="brand brand-large" href="#" data-action="home"><span class="brand-mark"><img src="/assets/befikr-icon-192.png" alt=""></span><span class="brand-copy"><span class="brand-name">BEFIKR</span><span class="brand-sub">Bhool Ja Saare Dar - Ban BEFIKR!</span></span></a>`;}
function renderAuth(){
  const login=state.authMode==="login";
  appRoot.innerHTML=`<main class="auth-wrap"><section class="auth-card">${brandBlock()}<h1 class="auth-title">${login?"Welcome back.":"Make space for confidence."}</h1><p class="sub">${login?"Sign in to your private safety workspace.":"Create an account to save contacts, journeys and reports."}</p><form id="auth-form" class="form-grid"><div class="field ${login?"full":""}"><label for="email">Email</label><input id="email" name="email" type="email" autocomplete="email" required maxlength="254"></div>${!login?`<div class="field full"><label for="name">Your name</label><input id="name" name="name" autocomplete="name" required maxlength="80"></div>`:""}<div class="field full"><label for="password">Password</label><input id="password" name="password" type="password" autocomplete="${login?"current-password":"new-password"}" required minlength="${login?"1":"10"}" maxlength="128"><small>${login?"":"Use at least 10 characters."}</small></div><div class="field full actions"><button class="btn" type="submit">${login?"Sign in":"Create account"}</button></div></form><p class="auth-switch">${login?"New to BEFIKR?":"Already have an account?"} <button class="link-button" data-action="auth-switch">${login?"Create an account":"Sign in"}</button></p><p class="tiny-legal">This development version stores account and safety data in the configured local database. Anonymous to other users does not mean technically unidentifiable to the service. Emergency and location features do not contact anyone unless an operational integration is configured.</p></section></main>`;
}
function homeIcon(name){
  const paths={
    home:`<path d="m3 10 9-7 9 7"/><path d="M5 9v12h5v-7h4v7h5V9"/>`,
    raahi:`<path d="M11 4 4.5 7v13l6.5-3 6 3 6.5-3V4l-6.5 3-6-3Z"/><path d="M11 4v13m6-10v13"/><path d="M17 9c0 2-3 5-3 5s-3-3-3-5a3 3 0 1 1 6 0Z"/><circle cx="14" cy="9" r=".8"/>`,
    raaz:`<path d="m4 11 12-5v12L4 13v-2Z"/><path d="M8 14v4a2 2 0 0 0 3 1.7L13 15M18 10l3-2m-2 6 3 1"/>`,
    baat:`<path d="M7 4 4.8 5.2a2 2 0 0 0-.9 2.5c2.5 6.3 6.1 9.9 12.4 12.4a2 2 0 0 0 2.5-.9L20 17l-4-3-2 2a14 14 0 0 1-5-5l2-2-4-5Z"/><path d="M16 5a5 5 0 0 1 4 4m-4-8a9 9 0 0 1 7 7"/>`,
    backup:`<path d="M12 3 21 7v5c0 5-3.7 8.3-9 10-5.3-1.7-9-5-9-10V7l9-4Z"/><circle cx="9" cy="11" r="2"/><circle cx="16" cy="11" r="2"/><path d="M5.5 17a4 4 0 0 1 7 0m0 0a4 4 0 0 1 7 0"/>`,
    spot:`<path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/>`,
    crest:`<path d="M12 3 19 6v5c0 4-2.8 7.2-7 9-4.2-1.8-7-5-7-9V6l7-3Z"/><path d="m9.2 11.8 1.8 1.8 4-4.2"/><path d="M4 7 1.7 5.5v4L4 11m16-4 2.3-1.5v4L20 11"/>`,
    map:`<path d="m3 6 6-3 6 3 6-3v15l-6 3-6-3-6 3V6Z"/><path d="M9 3v15m6-12v15"/><path d="M16 8a2.2 2.2 0 1 1 4.4 0c0 1.8-2.2 4-2.2 4S16 9.8 16 8Z"/>`,
    profile:`<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>`
  };
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths[name]||paths.crest}</svg>`;
}
function homeTile(id,title,tagline,theme){return `<button class="home-tile tile-${theme}" data-action="${id}"><span class="tile-art">${homeIcon(theme)}</span><span class="tile-copy"><strong>${title}</strong><span>${tagline}</span></span><span class="tile-arrow" aria-hidden="true">›</span></button>`;}
function renderHome(){
  const firstName=state.user?.name?.trim().split(/\s+/)[0]||"there";
  shell(`<section class="home-dashboard"><header class="home-brand"><img class="home-app-icon" src="/assets/befikr-icon-192.png" alt="BEFIKR app icon"><span class="home-brand-copy"><strong class="home-brand-name">BEFIKR</strong><span class="home-brand-tagline">Bhool Ja Saare Dar - Ban BEFIKR!</span></span><button class="home-sos" data-action="home-sos" aria-label="Hold to create an SOS event and open help options">SOS</button></header><button class="home-profile-header" data-action="profile" aria-label="${state.user?"Open your profile":"Sign in or create an account"}"><span class="home-profile-greeting"><small>${state.user?"YOUR BEFIKR PROFILE":"WELCOME TO BEFIKR"}</small><strong>Hello, ${esc(firstName)}!</strong><span>${state.user?"View your profile & settings":"Sign in or create an account"}</span></span><span class="home-profile-portrait" aria-hidden="true">${profileAvatar()}</span></button><div class="home-tiles" aria-label="BEFIKR safety modules">${homeTile("raahi","Raahi","Route Smart,<br>Reach Safe.","raahi")}${homeTile("raaz","Raaz","Naam Rahe Raaz,<br>Safety Ki Awaaz.","raaz")}${homeTile("baat-banao","Baat Banao","Ring Ring,<br>Awkwardness Gone!","baat")}${homeTile("backup","Backup","One Tap, Your Gang's<br>Got Your Back!","backup")}${homeTile("safe-spot","Safe Spot","Need a Breather? Find Your Safe Corner!","spot")}</div></section>`);
}
function renderMap(){
  const location=state.deviceLocation;
  const lat=location?.latitude,lon=location?.longitude;
  const latText=Number.isFinite(lat)?Number(lat).toFixed(5):"",lonText=Number.isFinite(lon)?Number(lon).toFixed(5):"";
  const name=state.user?.name?.split(" ")[0]||"there";
  const initial=(state.user?.name||"B").slice(0,1).toUpperCase();
  const mapHtml=location&&state.mapVisible
    ?`<div id="general-location-map" class="map-frame map-interactive spot-map location-map-preview" role="application" aria-label="Map centered on your current location">Loading map…</div><div id="general-map-attribution" class="map-attribution"></div>`
    :`<div class="location-map-empty"><span class="location-map-art" aria-hidden="true">${homeIcon("map")}</span><h3>${location?"Ready to explore?":"Your map starts here"}</h3><p>${location?"Load the map to see your current location.":"Choose your current location to get started."}</p></div>`;
  shell(`<div class="spot-page location-page"><header class="spot-welcome"><div><span class="spot-eyebrow">BEFIKR · MAP &amp; LOCATION</span><h1>Hello, ${esc(name)}!</h1><p>Find your location. Explore nearby.</p></div><span class="spot-avatar" aria-hidden="true">${esc(initial)}</span></header>
    <section class="location-control-card" aria-labelledby="location-control-title"><div class="location-card-heading"><span class="location-page-icon" aria-hidden="true">${homeIcon("spot")}</span><div><h2 id="location-control-title">Your current location</h2><p>${location?"Location found · ready to view on the map":"Find where you are with your device location."}</p></div></div>
      <div class="spot-search-actions"><button class="spot-search-button" data-action="map-locate">${location?"Refresh location":"Use my location"}</button><button class="spot-search-button secondary" data-action="map-load" ${location?"":"disabled"}>${state.mapVisible&&location?"Refresh map":"View on map"}</button></div>
      <p class="spot-data-note" data-location-feedback role="status" aria-live="polite"></p>
      ${location?`<details class="location-coordinates"><summary>Location details</summary><p>Latitude: ${latText}<br>Longitude: ${lonText}</p></details>`:""}
      <p class="spot-data-note location-consent-note">${location?"Loading the map shares this location with the map provider.":"Location permission is requested only when you tap Use my location."}</p>
    </section>
    <section class="location-preview-section" aria-labelledby="location-preview-title"><div class="spot-quick-heading"><h2 id="location-preview-title">Map Preview</h2><span>${location&&state.mapVisible?"Your current location":"Explore your surroundings"}</span></div>${mapHtml}</section>
    <div class="spot-quick-heading"><h2>Quick Access</h2><span>Keep exploring</span></div><div class="spot-home-categories location-shortcuts"><button data-action="raahi"><span class="spot-category-icon location-route-icon" aria-hidden="true">${homeIcon("raahi")}</span><strong>Raahi</strong><small>Plan your route</small></button><button data-action="safe-spot"><span class="spot-category-icon" aria-hidden="true">${homeIcon("spot")}</span><strong>Safe Spots</strong><small>Find nearby help</small></button></div>
    <p class="spot-data-note">The map shows your location. Find routes in Raahi and nearby public places in Safe Spots.</p></div>`);
  if(location&&state.mapVisible)requestAnimationFrame(()=>drawGeneralMap(Number(lat),Number(lon)));
}
async function drawGeneralMap(latitude,longitude){
  const element=document.getElementById("general-location-map");if(!element)return;
  const attribution=document.getElementById("general-map-attribution");
  if(await ensureGoogleMaps()){
    const point={lat:latitude,lng:longitude};
    const map=new google.maps.Map(element,{center:point,zoom:15,mapTypeControl:false,streetViewControl:false,fullscreenControl:true});
    new google.maps.Marker({position:point,map,title:"Your chosen location"});
    state.generalMap={type:"google",map};
    if(attribution)attribution.textContent="Google Maps";
    return;
  }
  const padLat=0.008,padLon=Math.min(0.03,0.008/Math.max(0.15,Math.cos(latitude*Math.PI/180)));
  const bbox=[longitude-padLon,latitude-padLat,longitude+padLon,latitude+padLat].map(value=>value.toFixed(5)).join(",");
  const embed=new URLSearchParams({bbox,layer:"mapnik",marker:`${latitude},${longitude}`});
  const openUrl=`https://www.openstreetmap.org/?mlat=${encodeURIComponent(latitude)}&mlon=${encodeURIComponent(longitude)}#map=17/${encodeURIComponent(latitude)}/${encodeURIComponent(longitude)}`;
  element.innerHTML=`<iframe title="OpenStreetMap map centered on your chosen location" loading="lazy" referrerpolicy="strict-origin-when-cross-origin" src="https://www.openstreetmap.org/export/embed.html?${embed}"></iframe>`;
  if(attribution)attribution.innerHTML=`Map data © <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap contributors</a> · <a href="${openUrl}" target="_blank" rel="noopener noreferrer">Open larger map</a>`;
}
function openMapPicker(target,preferredPoint,place){
  const routeField=target==="raahi-origin"?"origin":target==="raahi-destination"?"destination":null;
  const input=state.routeInput;
  const selected=preferredPoint||(routeField
    ?[input[`${routeField}_latitude`],input[`${routeField}_longitude`]]
    :target==="raaz"?[state.raazDraft.latitude||null,state.raazDraft.longitude||null]:[state.placeSearch?.latitude,state.placeSearch?.longitude]);
  const lat=selected[0]!=null&&Number.isFinite(Number(selected[0]))?Number(selected[0]):Number(state.deviceLocation?.latitude??28.6139);
  const lng=selected[1]!=null&&Number.isFinite(Number(selected[1]))?Number(selected[1]):Number(state.deviceLocation?.longitude??77.209);
  const savedPlaceId=routeField&&input[`${routeField}_place_id`];
  const chosenPlace=place||(!preferredPoint&&savedPlaceId
    ?{label:input[routeField],address:input[`${routeField}_address`],placeId:savedPlaceId}:null);
  state.mapPicker={target,returnPage:state.page,latitude:lat,longitude:lng,place:chosenPlace};
  state.page="map-picker";renderMapPicker();
}
function renderMapPicker(){
  const picker=state.mapPicker;
  if(!picker)return;
  const {target,latitude,longitude,place}=picker;
  const isPlaces=target==="places";
  const stop=target==="raaz"?"Incident location":target==="raahi-origin"?"Pickup":"Drop-off";
  const title=isPlaces?"Choose nearby search location":`${place?"Confirm":"Choose"} ${stop.toLowerCase()}`;
  const confirmLabel=isPlaces?"Find nearby places":`Confirm ${stop.toLowerCase()}`;
  const instruction=isPlaces?"Adjust the pin if needed, then confirm to find nearby places.":place?"Confirm this place or move the pin on the map.":"Tap the map or drag the pin to choose the exact point.";
  const selectedLabel=isPlaces?`${latitude.toFixed(6)}, ${longitude.toFixed(6)}`:place?.label||`Selected ${stop.toLowerCase()} pin`;
  const externalUrl=place?googlePlaceUrl({name:place.label,address:place.address,latitude,longitude,google_place_id:place.placeId||place.place_id}):"";
  const placeInfo=place?`<div id="map-pin-place-info">${place.address?`<p class="map-picker-instructions">${esc(place.address)}</p>`:""}<a class="spot-map-link" href="${esc(externalUrl)}" target="_blank" rel="noopener noreferrer">View this place in Google Maps</a>${googlePlacesAttribution()}${placeProviderAttribution([place])}</div>`:"";
  if(state.pinMap?.type==="leaflet")state.pinMap.map.remove();
  state.pinMap=null;
  shell(`<div class="map-picker-page">
    <header class="spot-subhead"><button class="spot-back" data-action="map-picker-back" aria-label="Back">←</button><h1>${title}</h1></header>
    <p id="map-picker-instruction" class="map-picker-instructions">${instruction}</p>
    <div id="map-pin-picker" class="map-pin-picker" role="application" aria-label="Interactive map location picker"></div>
    <div class="map-pin-summary"><span>${isPlaces?"Selected coordinates":stop}</span><strong id="map-pin-coordinates" aria-live="polite">${esc(selectedLabel)}</strong></div>
    ${placeInfo}
    <div class="map-picker-actions">
      <button class="spot-secondary" data-action="map-picker-current">Use my location</button>
      <button class="spot-directions" data-action="map-picker-confirm">${confirmLabel}</button>
    </div>
    <p class="map-picker-instructions" data-location-feedback role="status"></p>${isPlaces?`<p class="spot-data-note">The chosen location is shared with BEFIKR and Google Places when you search.</p>`:""}
  </div>`);
  requestAnimationFrame(drawMapPicker);
}
async function drawMapPicker(){
  const element=document.getElementById("map-pin-picker"),picker=state.mapPicker;
  if(!element||!picker)return;
  const center={lat:picker.latitude,lng:picker.longitude};
  if(state.pinMap?.type==="leaflet"){
    try{state.pinMap.map.remove();}catch(e){}
  }
  state.pinMap=null;
  element.hidden=false;

  const googleMapReady=await ensureGoogleMaps();
  if(!element.isConnected||state.mapPicker!==picker)return;
  if(googleMapReady){
    const map=new google.maps.Map(element,{center,zoom:16,mapTypeControl:false,streetViewControl:false,fullscreenControl:true,clickableIcons:false});
    const marker=new google.maps.Marker({position:center,map,draggable:true,title:picker.place?.label||"Move pin to choose a point"});
    const info=new google.maps.InfoWindow();
    marker.addListener("click",()=>{
      const title=document.createElement("strong");
      title.textContent=picker.place?.label||"Selected pin";
      info.setContent(title);
      info.open({map,anchor:marker});
    });
    map.addListener("click",event=>{info.close();marker.setPosition(event.latLng);setMapPickerCoordinates(event.latLng.lat(),event.latLng.lng());});
    marker.addListener("dragend",event=>{info.close();setMapPickerCoordinates(event.latLng.lat(),event.latLng.lng());});
    state.pinMap={type:"google",map,marker};
    return;
  }

  // Guaranteed Leaflet rendering without removing element
  if(!window.L){element.textContent="The map is currently unavailable.";return;}
  const map=L.map(element,{scrollWheelZoom:true}).setView([center.lat,center.lng],15);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{maxZoom:19,attribution:"© OpenStreetMap contributors"}).addTo(map);
  const pinIcon=L.divIcon({
    className:"spot-marker-shell",
    html:"<span class='spot-marker' style='background:#1a73e8'>⌖</span>",
    iconSize:[34,40],
    iconAnchor:[17,38]
  });
  const marker=L.marker([center.lat,center.lng],{draggable:true,icon:pinIcon}).addTo(map).bindTooltip("Drag or tap map to set location");
  map.on("click",event=>{
    marker.setLatLng(event.latlng);
    setMapPickerCoordinates(event.latlng.lat,event.latlng.lng);
  });
  marker.on("dragend",event=>{
    const pos=event.target.getLatLng();
    setMapPickerCoordinates(pos.lat,pos.lng);
  });
  state.pinMap={type:"leaflet",map,marker};
  requestAnimationFrame(()=>{if(element.isConnected)map.invalidateSize();});
}
function setMapPickerCoordinates(latitude,longitude){
  const picker=state.mapPicker;
  if(!picker)return;
  const hadPlace=Boolean(picker.place);
  picker.latitude=Number(latitude);
  picker.longitude=Number(longitude);
  picker.place=null;
  if(hadPlace&&!state.pinMap){
    renderMapPicker();
    return;
  }
  document.getElementById("map-pin-place-info")?.remove();
  const output=document.getElementById("map-pin-coordinates");
  if(output)output.textContent=picker.target==="places"
    ?`${picker.latitude.toFixed(6)}, ${picker.longitude.toFixed(6)}`
    :picker.target==="raaz"?"Selected incident location":picker.target==="raahi-origin"?"Selected pickup pin":"Selected drop-off pin";
  if(hadPlace){
    state.pinMap?.marker.setTitle("Move pin to choose a point");
    const instruction=document.getElementById("map-picker-instruction");
    if(instruction)instruction.textContent="Tap the map or drag the pin to adjust the selected point.";
  }
}
function confirmMapPin(){
  if(!state.mapPicker)return;
  const {target,latitude,longitude,place}=state.mapPicker,lat=Number(latitude),lng=Number(longitude);
  if(state.pinMap?.type==="leaflet")state.pinMap.map.remove();
  state.pinMap=null;state.mapPicker=null;
  if(target==="raaz"){
    state.raazDraft.latitude=String(lat);state.raazDraft.longitude=String(lng);
    state.raazDraft.location_label=String(place?.address||place?.label||"Pinned incident location").slice(0,300);
    state.raazDraft.location_place_id=place?.placeId||place?.place_id||"";
    state.page="raaz";state.raazStep=3;renderRaaz();return;
  }
  if(target==="places"){
    state.placeSearch={latitude:lat,longitude:lng,radius_km:5};
    state.page="safe-spot";
    searchNearbyPlaces();
    return;
  }
  const start=target==="raahi-origin",prefix=start?"origin":"destination",label=start?"Pickup":"Drop-off";
  state.routeInput[prefix]=place?.label||`${label} pin`;
  state.routeInput[`${prefix}_latitude`]=lat;
  state.routeInput[`${prefix}_longitude`]=lng;
  state.routeInput[`${prefix}_place_id`]=place?.placeId||place?.place_id||null;
  state.routeInput[`${prefix}_address`]=place?.address||null;
  state.page="raahi";state.raahiView="home";renderRaahi();toast(`${label} confirmed.`);
}
function pageHead(title,tagline,description){return `<div class="page-head"><div><span class="eyebrow">${tagline}</span><h1 class="page-title">${title}</h1><p>${description}</p></div><button class="back-btn" data-action="home">← Home</button></div>`;}
function moduleGreeting(module,tagline,theme){const name=state.user?.name?.split(" ")[0]||"there";const initial=(state.user?.name||"B").slice(0,1).toUpperCase();return `<header class="module-greeting ${theme}-welcome"><div><span class="module-greeting-eyebrow">BEFIKR · ${module}</span><h1>Hello, ${esc(name)}!</h1><p>${esc(tagline)}</p></div><span class="module-greeting-avatar" aria-hidden="true">${esc(initial)}</span></header>`;}
function riskLabel(key){return ({incident:"Report severity / frequency",freshness:"Fresh reported concern",population:"Population risk context",lighting:"Poor lighting risk",time_of_day:"Time-of-day risk",historical:"Historical risk",isolation:"Route isolation risk"})[key]||key;}
function riskPrototypeHtml(){return `<details class="raahi-risk-prototype"><summary>Experimental risk calculator</summary><p>Manual exploratory inputs only. No Safetipin, Nirakshak or Delhi government feed is connected. This score is not validated.</p><form id="risk-form" class="form-grid">${["incident","freshness","population","lighting","time_of_day","historical","isolation"].map(key=>`<div class="field"><label for="risk-${key}">${riskLabel(key)} · 0–100</label><input id="risk-${key}" name="${key}" type="number" min="0" max="100" placeholder="Unknown"></div>`).join("")}<div class="field"><label for="risk-length">Segment length (km)</label><input id="risk-length" name="length_km" type="number" min="0.1" max="500" step="0.1" value="1" required></div><div class="field"><label for="risk-latitude">Approximate segment latitude · optional</label><input id="risk-latitude" name="latitude" type="number" min="-90" max="90" step="any" placeholder="Not added"></div><div class="field"><label for="risk-longitude">Approximate segment longitude · optional</label><input id="risk-longitude" name="longitude" type="number" min="-180" max="180" step="any" placeholder="Not added"></div><div class="field full actions"><button class="btn" type="submit">Calculate prototype estimate</button></div></form><div id="risk-result"></div></details>`;}
function recentTripMarkup(){return state.recentTrips.length?`<div class="raahi-recent-list">${state.recentTrips.slice(0,3).map((trip,index)=>`<button class="raahi-recent-item" data-action="raahi-recent" data-index="${index}"><span class="raahi-recent-icon">◷</span><span><strong>${esc(trip.destination)}</strong><small>From ${esc(trip.origin)} · this session</small></span><span class="raahi-chevron">›</span></button>`).join("")}</div>`:`<p class="raahi-muted">Destinations you search this session will appear here.</p>`;}
function raahiDemoRatingHtml(assessment){
  if(!assessment)return "";
  if(!assessment.matched||!assessment.record){
    return `<div class="raahi-demo-rating unknown"><strong>No demo rating for this journey</strong><p>${esc(assessment.available===false?assessment.notice:"This directed area pair is not in the uploaded dataset. No colour has been assigned.")}</p></div>`;
  }
  const row=assessment.record;
  const tone=({GREEN:"green",YELLOW:"yellow",RED:"red"})[row.safety_label];
  if(!tone)return "";
  return `<div class="raahi-demo-rating ${tone}">
    <div class="raahi-demo-rating-head"><span class="raahi-demo-badge ${tone}">${esc(row.safety_label)} · DEMO</span><strong>${esc(row.safety_score_synthetic_0_100)}<small> / 100</small></strong></div>
    <h3>${esc(row.from_area)} → ${esc(row.to_area)}</h3>
    <p>${esc(assessment.time_band)} · ${esc(assessment.time_window)} IST</p>
    <p>Synthetic safety score; higher means safer in this demo.</p>
    <dl class="raahi-demo-factors"><div><dt>Lighting</dt><dd>${esc(row.lighting_index_synthetic_0_100)}/100</dd></div><div><dt>Pedestrian activity</dt><dd>${esc(row.pedestrian_activity_index_synthetic_0_100)}/100</dd></div><div><dt>CCTV coverage</dt><dd>${esc(row.cctv_coverage_index_synthetic_0_100)}/100</dd></div></dl>
    <p class="raahi-demo-disclosure">Synthetic demo data, not real incident or police data. This area-pair rating does not identify safer streets or rank map alternatives.</p>
  </div>`;
}
function raahiDemoPanelHtml(){
  const catalog=state.raahiDemoCatalog;
  if(!catalog)return `<section class="raahi-card raahi-demo-panel"><span class="raahi-eyebrow">SYNTHETIC DATA</span><h2>Route safety demo</h2><p>${esc(state.raahiDemoError||"Loading your Delhi route dataset…")}</p>${state.raahiDemoError?'<button class="raahi-secondary" type="button" data-action="raahi-demo-load">Retry dataset</button>':""}</section>`;
  if(!catalog.available)return `<section class="raahi-card raahi-demo-panel"><h2>Route safety demo unavailable</h2><p>${esc(catalog.notice)}</p><button class="raahi-secondary" type="button" data-action="raahi-demo-load">Retry dataset</button></section>`;
  const pairs=catalog.route_pairs||[];
  const pair=pairs.find(item=>item.route_segment_id===state.raahiDemoPairId)||pairs[0];
  const band=state.raahiDemoTimeBand||"current";
  return `<section class="raahi-card raahi-demo-panel"><span class="raahi-eyebrow">YOUR DELHI DATASET · SYNTHETIC DEMO</span><h2>Preview route safety colours</h2>
    <p>Choose one of the ${esc(catalog.counts.route_pairs)} area pairs and a time of day. This preview works without a Google Maps key.</p>
    <form id="raahi-demo-form"><label for="raahi-demo-pair">Route pair<select id="raahi-demo-pair" name="pair" required>${pairs.map(item=>`<option value="${esc(item.route_segment_id)}" ${item.route_segment_id===pair?.route_segment_id?"selected":""}>${esc(item.from_area)} → ${esc(item.to_area)}</option>`).join("")}</select></label>
    <label for="raahi-demo-time">Time of journey<select id="raahi-demo-time" name="time_band"><option value="current" ${band==="current"?"selected":""}>Current Delhi time</option>${(catalog.time_bands||[]).map(item=>`<option value="${esc(item.name)}" ${band===item.name?"selected":""}>${esc(item.name)} · ${esc(item.time_window)} IST</option>`).join("")}</select></label>
    <button class="raahi-primary" type="submit" ${state.raahiDemoLoading?"disabled":""}>${state.raahiDemoLoading?"Loading colour…":"Show demo colour"}</button></form>
    <div class="raahi-demo-legend" aria-label="Dataset colour counts">${["GREEN","YELLOW","RED"].map(label=>`<span class="raahi-demo-badge ${label.toLowerCase()}">${label} · ${Number(catalog.counts.labels[label]||0)}</span>`).join("")}</div>
    ${!catalog.counts.labels.RED?'<p>No red entries are present in this dataset.</p>':""}
    <div id="raahi-demo-result" aria-live="polite">${state.raahiDemoResult?raahiDemoRatingHtml(state.raahiDemoResult):state.raahiDemoError?`<p>${esc(state.raahiDemoError)}</p>`:""}</div>
    <p class="raahi-demo-disclosure">For demonstration only. Real-world safety is not assessed by this dataset.</p></section>`;
}
async function loadRaahiDemoCatalog(){
  try{state.raahiDemoCatalog=await api("/routes/safety-demo");state.raahiDemoError="";}
  catch(error){state.raahiDemoError=error.message||"The dataset could not be loaded.";}
}
async function previewRaahiDemo(form){
  const input=formData(form);
  const pair=state.raahiDemoCatalog?.route_pairs?.find(item=>item.route_segment_id===input.pair);
  if(!pair)return;
  state.raahiDemoPairId=pair.route_segment_id;state.raahiDemoTimeBand=input.time_band;
  state.raahiDemoResult=null;state.raahiDemoError="";state.raahiDemoLoading=true;
  const requestId=(state.raahiDemoRequestId||0)+1;state.raahiDemoRequestId=requestId;
  const button=form.querySelector('button[type="submit"]');button.disabled=true;button.textContent="Loading colour…";
  const output=document.getElementById("raahi-demo-result");output.textContent="Loading the selected demo rating…";
  try{
    const result=await api("/routes/safety-demo",{method:"POST",body:{origin:pair.from_area,destination:pair.to_area,time_band:input.time_band}});
    if(state.raahiDemoRequestId!==requestId)return;
    state.raahiDemoResult=result;
    if(output.isConnected)output.innerHTML=raahiDemoRatingHtml(result);
  }catch(error){
    if(state.raahiDemoRequestId!==requestId)return;
    state.raahiDemoError=error.message||"Could not load the demo rating.";
    if(output.isConnected)output.textContent=state.raahiDemoError;
  }finally{
    if(state.raahiDemoRequestId===requestId)state.raahiDemoLoading=false;
    if(button.isConnected){button.disabled=false;button.textContent="Show demo colour";}
  }
}
function renderRaahi(){
  const recentHtml=recentTripMarkup();
  if(state.raahiView==="journey"||state.raahiView==="arrived"){
    const route=(state.alternatives?.routes||[]).find(item=>item.id===state.raahiJourney?.routeId);
    if(!route){state.raahiView="home";state.raahiJourney=null;return renderRaahi();}
    if(state.raahiView==="journey"){
      shell(`<div class="raahi-page"><header class="raahi-subhead"><button class="raahi-back" data-action="raahi-results" aria-label="Back to routes">←</button><div><span class="raahi-eyebrow">RAAHI · YOUR JOURNEY</span><h1>Your Journey</h1><p>Directions are handled by your maps app.</p></div><span class="raahi-sharing-off">BEFIKR sharing off</span></header><div class="raahi-detail-risk"><span class="raahi-risk-symbol">ⓘ</span><div><strong>BEFIKR is not tracking this journey</strong><p>BEFIKR isn't collecting or sharing your live location with contacts. Google Maps has its own location settings and may use a different route.</p></div></div><div id="route-journey-map" class="route-map raahi-map" role="img" aria-label="Planned walking route map"></div>${mapAttribution()}<section class="raahi-card"><h2>Trip overview</h2><div class="raahi-journey-points"><div><span class="start-dot"></span><span><small>Starting point</small><strong>${esc(state.routeInput.origin)}</strong></span></div><div><span class="end-pin">●</span><span><small>Destination</small><strong>${esc(state.routeInput.destination)}</strong></span></div></div><div class="raahi-metrics"><div><small>Estimated time</small><strong>${Number.isFinite(Number(route.minutes))?`${esc(route.minutes)} min`:"Unavailable"}</strong></div><div><small>Distance</small><strong>${Number.isFinite(Number(route.distance_km))?`${Number(route.distance_km).toFixed(2)} km`:"Unavailable"}</strong></div></div></section><button class="raahi-primary" data-action="raahi-reopen-directions">Open walking directions in Google Maps</button><p class="raahi-muted raahi-center">This opens an external maps service. No in-app turn-by-turn guidance or BEFIKR live location sharing is active.</p><div class="raahi-journey-actions"><button data-action="safe-spot"><span>⌖</span>Safe Spot</button><button data-action="raaz"><span>◉</span>Report a concern</button><button data-action="backup"><span>☎</span>Backup</button></div><button class="raahi-end-trip" data-action="raahi-arrived">I've arrived</button><p class="raahi-muted raahi-center">Marking arrival is manual; BEFIKR does not verify your location.</p></div>`);
      requestAnimationFrame(()=>drawRouteMap({...state.alternatives,routes:[route]},"route-journey-map"));
      return;
    }
    const feedbackOptions=[["comfortable","☺","Comfortable"],["concerns","😐","Some concerns"],["unsafe","☹","Felt unsafe"]];
    shell(`<div class="raahi-page raahi-arrival-page"><div class="raahi-arrival-check" aria-hidden="true">✓</div><span class="raahi-eyebrow">JOURNEY COMPLETE · MANUAL CHECK-IN</span><h1>You've marked your arrival</h1><p class="raahi-arrival-sub">Hope you had a comfortable journey.</p><section class="raahi-card"><div class="raahi-metrics"><div><small>Distance</small><strong>${Number.isFinite(Number(route.distance_km))?`${Number(route.distance_km).toFixed(2)} km`:"Unavailable"}</strong></div><div><small>Estimated time</small><strong>${Number.isFinite(Number(route.minutes))?`${esc(route.minutes)} min`:"Unavailable"}</strong></div></div><div class="raahi-arrival-route"><strong>${esc(route.label||"Walking route")}</strong><small>${esc(state.routeInput.origin)} → ${esc(state.routeInput.destination)}</small><span>BEFIKR location sharing was off</span></div></section><h2>How was your journey?</h2><div class="raahi-feedback-grid">${feedbackOptions.map(([value,icon,label])=>`<button class="${state.raahiFeedback===value?"selected":""}" data-action="raahi-feedback" data-feedback="${value}" aria-pressed="${state.raahiFeedback===value}"><span>${icon}</span><small>${label}</small></button>`).join("")}</div><p class="raahi-muted raahi-center">Your selection stays in this page and is not sent as a safety report.</p><button class="raahi-primary" data-action="raahi-journey-home">Back to Raahi</button></div>`);
      return;
    }
  if(state.raahiView==="details"){
    const route=(state.alternatives?.routes||[]).find(item=>item.id===state.selectedRouteId);
    if(!route){state.raahiView=state.alternatives?"results":"home";return renderRaahi();}
    shell(`<div class="raahi-page"><header class="raahi-subhead"><button class="raahi-back" data-action="raahi-results" aria-label="Back to routes">←</button><div><span class="raahi-eyebrow">ROUTE DETAILS</span><h1>${esc(route.label)}</h1></div></header><div class="raahi-detail-risk"><span class="raahi-risk-symbol">ⓘ</span><div><strong>Safety rating unavailable</strong><p>Based on walking-network data only. This route is not certified safe.</p></div></div><div id="route-detail-map" class="route-map raahi-map" role="img" aria-label="Selected pedestrian route map"></div>${mapAttribution()}${state.alternatives?.safety_demo?.matched?raahiDemoRatingHtml(state.alternatives.safety_demo):""}<section class="raahi-card"><h2>Why this route?</h2><ul class="raahi-reasons"><li>Follows pedestrian route geometry from ${esc(route.provider||"the map provider")}.</li><li>Travel time is an estimate, not live navigation.</li><li>No route-matched Safetipin or Nirakshak audit is connected.</li></ul></section><section class="raahi-card"><h2>Route information</h2><div class="raahi-metrics"><div><small>Estimated time</small><strong>${Number.isFinite(Number(route.minutes))?`${esc(route.minutes)} min`:"Unavailable"}</strong></div><div><small>Distance</small><strong>${Number.isFinite(Number(route.distance_km))?`${Number(route.distance_km).toFixed(2)} km`:"Unavailable"}</strong></div></div></section><button class="raahi-primary" data-action="raahi-start-journey">Open route in Google Maps</button><button class="raahi-secondary" data-action="route-to-tapme">Use this route for Tap Me</button><p class="raahi-muted raahi-center">Google Maps may choose a different route for navigation. BEFIKR does not provide live tracking or verified safety ratings.</p><button class="raahi-secondary" data-action="route-status">Check safety data status</button><div id="route-status-result"></div></div>`);
    requestAnimationFrame(()=>drawRouteMap({...state.alternatives,routes:[route]},"route-detail-map"));
    return;
  }
  if(state.raahiView==="results"){
    shell(`<div class="raahi-page"><header class="raahi-subhead"><button class="raahi-back" data-action="raahi-home" aria-label="Back to route planner">←</button><div><span class="raahi-eyebrow">RAAHI · WALKING ROUTES</span><h1>Choose a route</h1><p>${esc(state.routeInput.origin)} <span aria-hidden="true">→</span> ${esc(state.routeInput.destination)}</p></div></header><div class="raahi-detail-risk compact"><span class="raahi-risk-symbol">ⓘ</span><div><strong>Safety ratings unavailable</strong><p>Compare walking time and distance; no route safety ranking is connected.</p></div></div>${raahiDemoRatingHtml(state.alternatives?.safety_demo)}<section id="raahi-directions-preview" class="raahi-card raahi-embed-preview" hidden><h2>Google Maps walking preview</h2><div class="raahi-embed-map"></div><p class="raahi-muted">This preview may show a different route from the options below.</p><button class="spot-map-link" type="button" data-action="raahi-open-directions">Open directions in Google Maps</button></section><div id="route-result">${state.routeLoading?`<div class="raahi-loading" role="status"><span class="raahi-spinner" aria-hidden="true"></span><strong>Finding walking routes…</strong><small>This can take a little while while the map provider looks up both places.</small></div>`:state.routeError?`<div class="raahi-empty-route"><strong>Could not load walking routes</strong><p>${esc(state.routeError)}</p><button class="raahi-secondary" data-action="raahi-home">Edit places</button></div>`:state.alternatives?routeResultHtml(state.alternatives):""}</div><button class="raahi-secondary" data-action="route-status">View data source status</button><div id="route-status-result"></div></div>`);
    void showRaahiDirectionsPreview();
    if(state.alternatives)requestAnimationFrame(()=>drawRouteMap(state.alternatives));
    return;
  }
  shell(`<div class="raahi-page"><header class="raahi-welcome"><div><span class="raahi-eyebrow">BEFIKR · RAAHI</span><h1>Hello, ${esc(state.user?.name?.split(" ")[0]||"there")}!</h1><p>Route Smart Reach Safe.</p></div><span class="raahi-welcome-avatar" aria-hidden="true">${esc((state.user?.name||"B").slice(0,1).toUpperCase())}</span></header><form id="route-form" class="raahi-plan-card">${raahiStopField("origin")}<div class="raahi-route-connector" aria-hidden="true"></div>${raahiStopField("destination")}<button class="raahi-primary" type="submit">Find walking routes</button><button class="raahi-secondary" type="button" data-action="external-route">Open walking directions in Google Maps</button><p class="raahi-safe-note">Walking routes depend on the configured map provider. Verified personal-safety ratings are not connected.</p></form><section id="raahi-place-preview" class="raahi-card raahi-embed-preview" hidden></section><section class="raahi-quick-section"><h2>Quick access</h2><div class="raahi-quick-grid"><button class="raahi-quick-card" data-action="raahi-scroll-recent"><span class="raahi-quick-icon">◷</span><strong>Recent trips</strong><small>Your recent destinations</small></button><button class="raahi-quick-card" data-action="safe-spot"><span class="raahi-quick-icon safe">✓</span><strong>Safe Spots</strong><small>Find nearby places</small></button></div></section><section class="raahi-recent-section" id="raahi-recent"><div class="raahi-section-heading"><h2>Recent destinations</h2><span>This session</span></div>${recentHtml}</section><div class="raahi-notice"><strong>Your safety matters</strong><p>Raahi shows available walking routes and their estimated distance and time. It cannot label a route safe without verified audit data.</p></div>${raahiDemoPanelHtml()}${riskPrototypeHtml()}</div>`);
}
function raahiStopField(field){
  const pickup=field==="origin";
  const label=pickup?"Pickup":"Drop-off";
  const address=state.routeInput[`${field}_address`];
  return `<div class="raahi-stop-field">
    <div class="raahi-stop-row">
      <span class="raahi-stop-icon ${pickup?"start-dot":"end-pin"}" aria-hidden="true"></span>
      <label class="raahi-stop-copy" for="${field}">
        <small>${label}</small>
        <input name="${field}" id="${field}" required maxlength="160" value="${esc(state.routeInput[field])}"
          placeholder="Search for a place or address" autocomplete="off" role="combobox" aria-autocomplete="list"
          aria-expanded="false" aria-controls="raahi-${field}-options">
      </label>
      <button class="raahi-pin-button" type="button" data-action="map-pick" data-target="raahi-${field}">Pick on map</button>
    </div>
    <small class="raahi-confirmed-address" ${address?"":"hidden"}>${esc(address||"")}</small>
    <div class="raahi-place-panel" id="raahi-${field}-suggestions" hidden>
      <div id="raahi-${field}-options" role="listbox" aria-label="${label} suggestions"></div>
      <p class="raahi-place-message" role="status"></p>
      <p class="spot-google-attribution raahi-place-attribution" translate="no" hidden>Google Maps</p>
    </div>
    <button class="spot-map-link raahi-place-preview-button" type="button" data-action="raahi-place-preview" data-field="${field}" ${state.routeInput[field]?.trim()?"":"hidden"}>Show ${label.toLowerCase()} on Google Maps</button>
  </div>`;
}

function updateRaahiPlacePanel(search,message=""){
  const {input,items,active}=search;
  if(!input.isConnected)return;
  const panel=document.getElementById(`raahi-${input.name}-suggestions`);
  if(!panel)return;
  const options=panel.querySelector('[role="listbox"]');
  options.innerHTML=items.map((place,index)=>`<div role="option" id="raahi-${input.name}-option-${index}" aria-selected="${index===active}"
    class="raahi-place-option" data-action="raahi-select-place" data-index="${index}">
    <span aria-hidden="true">⌖</span><div><strong>${esc(place.label)}</strong>${place.address?`<small>${esc(place.address)}</small>`:""}</div>
  </div>`).join("");
  panel.querySelector("[role=status]").textContent=message;
  panel.querySelector(".raahi-place-attribution").hidden=!items.length;
  panel.hidden=!items.length&&!message;
  input.setAttribute("aria-expanded",String(Boolean(items.length)));
  if(active>=0){
    const option=options.children[active];
    input.setAttribute("aria-activedescendant",option.id);
    option.scrollIntoView({block:"nearest"});
  }else input.removeAttribute("aria-activedescendant");
}

function cancelRaahiPlaceSearch(){
  const search=state.raahiPlaceSearch;
  if(!search)return;
  clearTimeout(search.timer);
  search.controller?.abort();
  search.items=[];
  search.active=-1;
  updateRaahiPlacePanel(search);
  state.raahiPlaceSearch=null;
}

function onRaahiPlaceInput(input){
  const field=input.name;
  const fieldElement=input.closest(".raahi-stop-field");
  fieldElement.querySelector(".raahi-confirmed-address").hidden=true;
  fieldElement.querySelector(".raahi-place-preview-button").hidden=!input.value.trim();
  const preview=document.getElementById("raahi-place-preview");
  if(preview?.dataset.field===field){preview.hidden=true;preview.replaceChildren();}
  state.routeInput[field]=input.value;
  state.routeInput[`${field}_latitude`]=null;
  state.routeInput[`${field}_longitude`]=null;
  state.routeInput[`${field}_place_id`]=null;
  state.routeInput[`${field}_address`]=null;
  startNamedPlaceSearch(input);
}
function startNamedPlaceSearch(input){
  const existing=state.raahiPlaceSearch;
  const sessionToken=existing?.input===input&&!existing.resolving?existing.sessionToken:null;
  cancelRaahiPlaceSearch();
  const query=input.value.trim();
  if(query.length<2)return;
  const search={input,items:[],active:-1,controller:new AbortController(),sessionToken:sessionToken||crypto.randomUUID(),context:input.id==="raaz-location-search"?"raaz":"raahi"};
  state.raahiPlaceSearch=search;
  search.timer=setTimeout(async()=>{
    if(state.raahiPlaceSearch!==search||!input.isConnected)return;
    updateRaahiPlacePanel(search,"Searching places…");
    try{
      const result=await api("/places/autocomplete",{method:"POST",body:{input:query,session_token:search.sessionToken},signal:search.controller.signal});
      if(state.raahiPlaceSearch!==search||!input.isConnected)return;
      search.items=result.suggestions.map(place=>({id:place.place_id,label:place.name||place.label,address:place.address}));
      updateRaahiPlacePanel(search,search.items.length?"":"No matching places. Try an area, landmark or postcode.");
    }catch(error){
      if(state.raahiPlaceSearch===search)updateRaahiPlacePanel(search,error.message);
    }
  },350);
}

function raahiEmbedPoint(points,field){
  const id=points[`${field}_place_id`];
  if(id)return `place_id:${id}`;
  const latitude=points[`${field}_latitude`],longitude=points[`${field}_longitude`];
  if(Number.isFinite(latitude)&&Number.isFinite(longitude))return `${latitude},${longitude}`;
  return points[`${field}_address`]||points[field]||"";
}

async function showRaahiPlacePreview(field){
  const form=document.getElementById("route-form");
  const preview=document.getElementById("raahi-place-preview");
  if(!form||!preview||!["origin","destination"].includes(field))return;
  const points=readRaahiRouteForm(form);
  const query=raahiEmbedPoint(points,field);
  if(!query)return;
  cancelRaahiPlaceSearch();
  const previewName=field==="origin"?"Pickup":"Drop-off";
  const placeId=points[`${field}_place_id`];
  const latitude=points[`${field}_latitude`],longitude=points[`${field}_longitude`];
  const pinned=Number.isFinite(latitude)&&Number.isFinite(longitude);
  const externalQuery=placeId?[points[field],points[`${field}_address`]].filter(Boolean).join(", "):query;
  const externalParams=new URLSearchParams({api:"1",query:externalQuery});
  if(placeId)externalParams.set("query_place_id",placeId);
  const link=`https://www.google.com/maps/search/?${externalParams}`;
  preview.hidden=false;
  preview.dataset.field=field;
  preview.innerHTML=`<h2>${previewName} on Google Maps</h2><div class="raahi-embed-map" role="status">Loading map…</div><a class="spot-map-link" href="${esc(link)}" target="_blank" rel="noopener noreferrer">Open in Google Maps</a>`;
  const map=preview.querySelector(".raahi-embed-map");
  const mode=placeId?"place":pinned?"view":"search";
  const parameters=placeId?{q:query}:pinned?{center:query,zoom:"16"}:{q:query,center:"28.6139,77.2090",zoom:"10"};
  if(!await renderGoogleMapEmbed(map,mode,parameters,`${previewName} location in Google Maps`)&&map.isConnected){
    map.remove();
  }
}

async function showRaahiDirectionsPreview(){
  const preview=document.getElementById("raahi-directions-preview");
  if(!preview)return;
  const points=state.routeInput;
  const origin=raahiEmbedPoint(points,"origin"),destination=raahiEmbedPoint(points,"destination");
  if(!origin||!destination)return;
  const map=preview.querySelector(".raahi-embed-map");
  const embedded=await renderGoogleMapEmbed(map,"directions",{origin,destination,mode:"walking",units:"metric"},"Google Maps walking directions");
  if(!preview.isConnected)return;
  if(!embedded){map.remove();preview.querySelector("h2").remove();}
  if(!embedded||!state.alternatives?.routes?.some(route=>route.geometry?.coordinates?.length>1))preview.querySelector("p").remove();
  preview.hidden=false;
}

async function selectRaahiPlace(index){
  const search=state.raahiPlaceSearch;
  const place=search?.items[index];
  if(!place||search.resolving)return;
  search.resolving=true;
  search.items=[];
  search.active=-1;
  updateRaahiPlacePanel(search,"Opening this place…");
  try{
    const result=await api("/places/resolve",{method:"POST",body:{place_id:place.id,session_token:search.sessionToken},signal:search.controller.signal});
    if(state.raahiPlaceSearch!==search||!search.input.isConnected)return;
    cancelRaahiPlaceSearch();
    openMapPicker(search.context==="raaz"?"raaz":`raahi-${search.input.name}`,[result.latitude,result.longitude],{
      label:place.label.slice(0,160),address:result.address||place.address,placeId:result.place_id||place.id,attributions:result.attributions,
    });
  }catch(error){
    if(state.raahiPlaceSearch===search)updateRaahiPlacePanel(search,`${error.message} Edit the search to try again.`);
  }
}

function routeResultHtml(result){
  const all=(result.routes||[]).filter(route=>route.geometry?.coordinates?.length>1);
  const routes=[...all].sort((a,b)=>state.routeSort==="fastest"?Number(a.minutes)-Number(b.minutes):Number(a.distance_km)-Number(b.distance_km));
  if(!routes.length)return `<div class="raahi-empty-route"><strong>${esc(result.provider_state==="demo_only"?"Walking routes are not configured yet":"Walking routes unavailable")}</strong><p>${esc(result.warning)}</p>${(result.routes||[]).length?`<div class="raahi-placeholder-routes">${result.routes.map(route=>`<div class="raahi-route-card disabled"><strong>${esc(route.label)}</strong><span>Route geometry unavailable</span></div>`).join("")}</div>`:""}</div>`;
  return `<div class="raahi-sort-tabs"><button class="${state.routeSort==="fastest"?"selected":""}" data-action="raahi-sort" data-sort="fastest">Fastest</button><button class="${state.routeSort==="shortest"?"selected":""}" data-action="raahi-sort" data-sort="shortest">Shortest</button><button class="unavailable" disabled title="Requires verified safety audit data">Safest · unavailable</button></div><div id="route-map" class="route-map raahi-map" role="img" aria-label="Pedestrian route options drawn on an OpenStreetMap map"></div>${mapAttribution()}<div class="raahi-route-list">${routes.map((route,index)=>`<button class="raahi-route-card ${route.id===state.selectedRouteId?"selected":""}" data-action="route-detail" data-route-id="${esc(route.id)}"><span class="raahi-route-radio" aria-hidden="true">${route.id===state.selectedRouteId?"●":""}</span><span class="raahi-route-copy"><strong>Route ${String.fromCharCode(65+index)}</strong><small>${Number(route.distance_km).toFixed(2)} km · about ${esc(route.minutes)} min</small><span>${esc(route.label)} · ${esc(route.provider||"walking network")}</span></span><span class="raahi-safety-tag">Safety data unavailable</span><span class="raahi-chevron" aria-hidden="true">›</span></button>`).join("")}</div><p class="raahi-muted">Walking time is an estimate. Route geometry is not a safety rating or turn-by-turn navigation.</p>`;
}
async function drawRouteMap(result,elementId="route-map"){
  const element=document.getElementById(elementId);if(!element)return;
  if(state.routeMap?.type==="leaflet")state.routeMap.map.remove();
  state.routeMap=null;
  const routeChoices=[...(result.routes||[])].filter(route=>route.geometry?.coordinates?.length>1).sort((a,b)=>state.routeSort==="fastest"?Number(a.minutes)-Number(b.minutes):Number(a.distance_km)-Number(b.distance_km));
  const googleReady=await ensureGoogleMaps();
  if(!element.isConnected)return;
  if(googleReady){
    const map=new google.maps.Map(element,{center:{lat:28.6139,lng:77.209},zoom:13,mapTypeControl:false,streetViewControl:false,fullscreenControl:true});
    const bounds=new google.maps.LatLngBounds(),overlays=[],colors=["#6986ad","#8c78b5","#a48668"];
    for(const [index,route] of routeChoices.entries()){
      const selected=route.id===state.selectedRouteId;
      const path=route.geometry.coordinates.map(([lng,lat])=>({lat:Number(lat),lng:Number(lng)}));
      const line=new google.maps.Polyline({path,strokeColor:selected?"#6035ad":colors[index%colors.length],strokeOpacity:selected?.95:.72,strokeWeight:selected?6:4,map});
      overlays.push(line);path.forEach(point=>bounds.extend(point));
    }
    const first=routeChoices[0]?.geometry.coordinates;
    if(first?.length){new google.maps.Marker({position:{lat:first[0][1],lng:first[0][0]},map,label:"S",title:"Starting point"});new google.maps.Marker({position:{lat:first.at(-1)[1],lng:first.at(-1)[0]},map,label:"D",title:"Destination"});}
    if(!bounds.isEmpty())map.fitBounds(bounds,36);
    state.routeMap={type:"google",map,overlays};
    return;
  }
  if(state.routeInput.origin_place_id||state.routeInput.destination_place_id){
    const link=document.createElement("a");
    link.className="spot-map-link";
    link.href=googleDirectionsUrl(state.routeInput.origin,state.routeInput.destination,state.routeInput);
    link.target="_blank";
    link.rel="noopener noreferrer";
    link.textContent="View these places and directions in Google Maps";
    element.replaceWith(link);
    if(link.nextElementSibling?.classList.contains("map-attribution"))link.nextElementSibling.remove();
    return;
  }
  if(!window.L){element.textContent="Map library is unavailable. Open the route in Google Maps.";return;}
  const map=L.map(element,{scrollWheelZoom:false});state.routeMap={type:"leaflet",map};
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{maxZoom:19,attribution:"© OpenStreetMap contributors"}).addTo(map);
  const colors=["#6986ad","#8c78b5","#a48668"],layers=[];
  for(const [index,route] of routeChoices.entries()){
    const selected=route.id===state.selectedRouteId;
    const line=L.geoJSON(route.geometry,{style:{color:selected?"#6035ad":colors[index%colors.length],weight:selected?6:4,opacity:selected?.95:.72,dashArray:selected?null:"8 7"}}).addTo(map);
    layers.push(line);
  }
  if(layers.length){const group=L.featureGroup(layers);map.fitBounds(group.getBounds().pad(.12));const first=routeChoices[0]?.geometry.coordinates;if(first?.length){L.circleMarker([first[0][1],first[0][0]],{radius:7,color:"#276b51",fillOpacity:1}).addTo(map).bindTooltip("Start");L.circleMarker([first[first.length-1][1],first[first.length-1][0]],{radius:7,color:"#d84850",fillOpacity:1}).addTo(map).bindTooltip("Destination");}}
  requestAnimationFrame(()=>map.invalidateSize());
}
function raazHasLocation(){return state.raazDraft.latitude!==""&&state.raazDraft.longitude!=="";}
function resetRaazDraft(){
  for(const item of state.raazEvidence){
    URL.revokeObjectURL(item.previewUrl);
    if(item.uploaded&&!item.linked)void api(`/evidence/${item.uploaded.id}`,{method:"DELETE"}).catch(()=>{});
  }
  state.raazEvidence=[];state.raazLocationQuery="";
  state.raazDraft={category:"",description:"",occurred_at:"",latitude:"",longitude:"",location_label:"",location_place_id:""};
}
function addRaazEvidence(files){
  if(state.raazSubmitting)return;
  const allowed=["image/jpeg","image/png","image/webp","video/mp4","video/webm"];
  for(const file of files){
    if(state.raazEvidence.length>=3){toast("You can attach up to 3 photos or videos.");break;}
    if(!allowed.includes(file.type)||!file.size||file.size>10*1024*1024){toast(`${file.name}: choose a supported photo/video up to 10 MB.`);continue;}
    if(state.raazEvidence.some(item=>item.file.name===file.name&&item.file.size===file.size&&item.file.lastModified===file.lastModified))continue;
    state.raazEvidence.push({id:crypto.randomUUID(),file,previewUrl:URL.createObjectURL(file),uploaded:null,linked:false});
  }
  renderRaaz();
}
function raazEvidenceHtml(){
  return `<section class="raaz-evidence"><label class="raaz-evidence-picker"><span class="raaz-evidence-icon" aria-hidden="true">＋</span><span><strong>Add photos or videos</strong><small>Optional · up to 3 files · 10 MB each<br>JPEG, PNG, WebP, MP4 or WebM</small></span><input id="raaz-evidence-files" type="file" accept="image/jpeg,image/png,image/webp,video/mp4,video/webm" multiple ${state.raazSubmitting?"disabled":""}></label><div class="raaz-evidence-list">${state.raazEvidence.map(item=>`<div class="raaz-evidence-item">${item.file.type.startsWith("image/")?`<img src="${esc(item.previewUrl)}" alt="Selected evidence photo">`:'<span class="raaz-video-icon" aria-hidden="true">▶</span>'}<span><strong>${esc(item.file.name)}</strong><small>${(item.file.size/1024/1024).toFixed(2)} MB</small></span><button type="button" data-action="raaz-evidence-preview" data-id="${esc(item.id)}">Preview</button><button type="button" data-action="raaz-evidence-remove" data-id="${esc(item.id)}" aria-label="Remove ${esc(item.file.name)}">Remove</button></div>`).join("")}</div><p class="raaz-form-note">Attachments are sent with your report and are available only to you and authorised reviewers.</p></section>`;
}
function raazSavedEvidenceHtml(items=[]){
  return items.length?`<section class="raaz-saved-evidence"><h3>Evidence</h3>${items.map(item=>`<button class="raaz-secondary" type="button" data-action="raaz-evidence-open" data-id="${esc(item.id)}">${item.mime_type.startsWith("video/")?"Video":"Photo"} · ${esc(item.filename)}</button>`).join("")}</section>`:"";
}
function closeRaazPreview(){
  document.getElementById("raaz-evidence-viewer")?.remove();
  if(state.raazPreviewUrl){URL.revokeObjectURL(state.raazPreviewUrl);state.raazPreviewUrl=null;}
}
function showRaazPreview(url,type,name,owned=false){
  closeRaazPreview();if(owned)state.raazPreviewUrl=url;
  const modal=document.createElement("div");modal.id="raaz-evidence-viewer";modal.className="raaz-evidence-viewer";
  modal.setAttribute("role","dialog");modal.setAttribute("aria-modal","true");modal.setAttribute("aria-label","Evidence preview");
  modal.innerHTML=`<div><button type="button" data-action="raaz-evidence-close" aria-label="Close preview">Close ✕</button><h2>${esc(name)}</h2>${type.startsWith("video/")?`<video src="${esc(url)}" controls playsinline preload="metadata"></video>`:`<img src="${esc(url)}" alt="Evidence photo preview">`}</div>`;
  document.body.append(modal);modal.querySelector("button").focus();
}
async function openSavedRaazEvidence(id){
  const response=await fetch(`/api/evidence/${encodeURIComponent(id)}`,{headers:{Authorization:`Bearer ${state.token}`},cache:"no-store"});
  if(!response.ok)throw new Error("This attachment is unavailable or you do not have access.");
  const blob=await response.blob();
  if(!["image/jpeg","image/png","image/webp","video/mp4","video/webm"].includes(blob.type))throw new Error("This file type cannot be previewed.");
  showRaazPreview(URL.createObjectURL(blob),blob.type,"Report evidence",true);
}
async function submitRaazReport(){
  if(state.raazSubmitting)return;
  const draft=state.raazDraft;
  if(!draft.category||draft.description.trim().length<10)return toast("Complete the category and description before submitting.");
  const body={category:draft.category,description:draft.description.trim(),occurred_at:draft.occurred_at||null,
    latitude:draft.latitude===""?null:Number(draft.latitude),longitude:draft.longitude===""?null:Number(draft.longitude),
    location_label:draft.location_label||null,location_place_id:draft.location_place_id||null,evidence_ids:[]};
  state.raazSubmitting=true;renderRaaz();
  try{
    for(const item of state.raazEvidence){
      if(!item.uploaded){
        const response=await fetch("/api/evidence",{method:"POST",headers:{Authorization:`Bearer ${state.token}`,"Content-Type":item.file.type,"X-Filename":encodeURIComponent(item.file.name)},body:item.file});
        const result=await response.json();if(!response.ok)throw new Error(result.detail||"Attachment upload failed.");
        item.uploaded=result;
      }
      body.evidence_ids.push(item.uploaded.id);
    }
    const result=await api("/reports",{method:"POST",body});
    state.raazEvidence.forEach(item=>item.linked=true);
    state.raazSubmittedReport=result;state.raazScreen="submitted";state.raazStep=5;state.raazSelectedReportId=null;
    toast(result.message);await loadPageData("raaz");
  }catch(error){
    if(!state.raazEvidence.length&&error.message.includes("Could not reach")){
      const queue=getOfflineReports();queue.push({...body,local_id:crypto.randomUUID(),saved_at:new Date().toISOString()});saveOfflineReports(queue);
      toast("Saved on this device only. This report has NOT been submitted.");
    }else toast(`${error.message||"Could not upload your evidence."} Your draft and selected files are still here; retry when connected.`);
  }finally{
    state.raazSubmitting=false;if(state.page==="raaz")renderRaaz();
  }
}
const RAAZ_CATEGORIES=[
  {id:"harassment",label:"Harassment",icon:"!"},
  {id:"suspicious activity",label:"Suspicious activity",icon:"◉"},
  {id:"poor lighting",label:"Poor lighting",icon:"☾"},
  {id:"unsafe public transport",label:"Unsafe transport",icon:"▣"},
  {id:"isolated area",label:"Isolated area",icon:"⌖"},
  {id:"recurring local concern",label:"Recurring concern",icon:"↻"},
  {id:"other",label:"Other",icon:"•••"}
];
function raazProgress(active){
  const labels=["Category","Description","Location & time","Review","Submitted"];
  return `<ol class="raaz-progress" aria-label="Report steps">${labels.map((label,index)=>{const step=index+1;const className=step<active?"complete":step===active?"current":"";return `<li class="${className}" ${step===active?'aria-current="step"':""}><span>${step<active?"✓":step}</span><small>${label}</small></li>`;}).join("")}</ol>`;
}
function raazCategoryLabel(category){return RAAZ_CATEGORIES.find(item=>item.id===category)?.label||category||"Not selected";}
function raazStatusMessage(status){return ({pending_review:"Received by the service and awaiting review. This report is not public.",under_review:"This report is currently under review.",corroborated:"The review record marks this report as corroborated. This is not a guarantee of safety.",validated:"The review record marks this report as validated. This is not a guarantee of safety.",rejected:"This report was not validated in review. You can submit an appeal."})[status]||"The latest review status is shown here.";}
function renderRaaz(){
  const pending=JSON.parse(localStorage.getItem("befikr-report-queue")||"[]");
  const screen=state.raazScreen||"wizard";
  const step=state.raazStep||1;
  const tabs=`<div class="raaz-tabs" role="tablist" aria-label="Raaz sections"><button class="raaz-tab ${screen!=="reports"?"active":""}" type="button" data-action="raaz-tab" data-screen="wizard" aria-selected="${screen!=="reports"}">Report a concern</button><button class="raaz-tab ${screen==="reports"?"active":""}" type="button" data-action="raaz-tab" data-screen="reports" aria-selected="${screen==="reports"}">My reports</button></div>`;
  const queueNotice=pending.length?`<div class="raaz-offline-note"><span aria-hidden="true">!</span><div><strong>${pending.length} saved draft${pending.length===1?"":"s"} not submitted</strong><small>These reports are stored on this device only.</small></div><button type="button" data-action="sync-reports">Retry</button></div>`:"";
  let content="";
  if(screen==="submitted"){
    const report=state.raazSubmittedReport||{};
    content=`${raazProgress(5)}<section class="raaz-receipt"><span class="raaz-receipt-check" aria-hidden="true">✓</span><h2>Report received</h2><p>${esc(report.message||"Your report was received by this development service and is awaiting review. It is not public.")}</p><div class="raaz-receipt-status"><span>Status</span><strong class="raaz-status-pill pending">${esc(statusLabel(report.status||"pending_review"))}</strong></div>${report.id?`<small class="raaz-report-id">Report ID · ${esc(report.id.slice(0,12).toUpperCase())}</small>`:""}<p class="raaz-privacy-note">Your report is linked to your account so you can follow its status. It is not a public post. A submitted report has not been independently verified.</p><div class="raaz-receipt-actions"><button class="raaz-primary" type="button" data-action="raaz-tab" data-screen="reports">View my reports</button><button class="raaz-secondary" type="button" data-action="raaz-new-report">Submit another report</button></div></section>`;
  }else if(screen==="reports"){
    content=`<section class="raaz-reports-card"><header class="raaz-panel-heading"><div><span class="raaz-eyebrow">YOUR ACCOUNT</span><h2>${state.raazSelectedReportId?"Report details":"My reports"}</h2></div>${state.raazSelectedReportId?`<button class="raaz-back-link" type="button" data-action="raaz-report-back">← All reports</button>`:`<button class="raaz-new-report" type="button" data-action="raaz-new-report">＋ New report</button>`}</header><p class="raaz-panel-sub">Status reflects the latest review record. It is not a safety guarantee.</p>${!state.raazSelectedReportId?`<div class="raaz-filters" role="group" aria-label="Filter reports">${[["all","All"],["pending","Pending"],["resolved","Resolved"]].map(([filter,label])=>`<button type="button" class="raaz-filter ${state.raazFilter===filter?"active":""}" data-action="raaz-filter" data-filter="${filter}" aria-pressed="${state.raazFilter===filter}">${label}</button>`).join("")}</div>`:""}${reportListHtml()}</section>`;
  }else{
    const draft=state.raazDraft;
    let formContent="";
    if(step===1){
      formContent=`<div class="raaz-step-heading"><span>STEP 1 OF 4</span><h2>Select a category</h2><p>Choose the concern that best describes what you experienced.</p></div><div class="raaz-category-grid">${RAAZ_CATEGORIES.map(item=>`<button class="raaz-category ${draft.category===item.id?"selected":""}" type="button" data-action="raaz-category" data-category="${esc(item.id)}" aria-pressed="${draft.category===item.id}"><span class="raaz-category-icon">${item.icon}</span><strong>${esc(item.label)}</strong><span class="raaz-category-check" aria-hidden="true">${draft.category===item.id?"✓":""}</span></button>`).join("")}</div><p class="raaz-form-note">Reports are reviewed before any approved information is considered for safety awareness.</p><button class="raaz-primary" type="button" data-action="raaz-next">Next <span aria-hidden="true">→</span></button>`;
    }else if(step===2){
      formContent=`<div class="raaz-step-heading"><span>STEP 2 OF 4</span><h2>Add a description</h2><p>Describe what happened and when. Avoid names and details that identify other people.</p></div><label class="raaz-label" for="raaz-description">What would you like reviewed?</label><textarea class="raaz-description" id="raaz-description" name="description" minlength="10" maxlength="2000" placeholder="Share the relevant details…">${esc(draft.description)}</textarea><div class="raaz-field-caption"><span>Do not include personal contact details.</span><span>${draft.description.length}/2000</span></div>${raazEvidenceHtml()}<div class="raaz-step-actions"><button class="raaz-secondary" type="button" data-action="raaz-back">Back</button><button class="raaz-primary" type="button" data-action="raaz-next">Next <span aria-hidden="true">→</span></button></div>`;
    }else if(step===3){
      const locationText=raazHasLocation()?draft.location_label||`${draft.latitude}, ${draft.longitude}`:"No location added";
      formContent=`<div class="raaz-step-heading"><span>STEP 3 OF 4</span><h2>Location &amp; time</h2><p>Add where the incident happened. Both location and time are optional.</p></div><div class="raaz-location-actions"><button type="button" class="raaz-secondary" data-action="raaz-location">Use my current location</button><button type="button" class="raaz-secondary" data-action="raaz-map-pick">Choose on map</button></div><p class="raaz-form-note" data-location-feedback role="status"></p><div class="raahi-stop-field raaz-place-search"><label class="raaz-label" for="raaz-location-search">Search by place name</label><input id="raaz-location-search" name="incident" type="search" maxlength="160" value="${esc(state.raazLocationQuery)}" placeholder="Search an area, address or landmark" autocomplete="off" role="combobox" aria-autocomplete="list" aria-expanded="false" aria-controls="raahi-incident-options"><div class="raahi-place-panel" id="raahi-incident-suggestions" hidden><div id="raahi-incident-options" role="listbox" aria-label="Incident location suggestions"></div><p class="raahi-place-message" role="status"></p><p class="spot-google-attribution raahi-place-attribution" translate="no" hidden>Google Maps</p></div></div><div class="raaz-location-card"><span class="raaz-detail-icon" aria-hidden="true">⌖</span><span><strong>${raazHasLocation()?"Selected incident location":"Incident location"}</strong><small>${esc(locationText)}</small></span>${raazHasLocation()?`<button type="button" data-action="raaz-clear-location">Remove</button>`:""}</div><details class="raaz-manual-location"><summary>Enter coordinates manually</summary><div class="raaz-coordinate-grid"><label class="raaz-label" for="raaz-latitude">Latitude<input id="raaz-latitude" name="latitude" type="number" min="-90" max="90" step="any" value="${esc(draft.latitude)}"></label><label class="raaz-label" for="raaz-longitude">Longitude<input id="raaz-longitude" name="longitude" type="number" min="-180" max="180" step="any" value="${esc(draft.longitude)}"></label></div></details><label class="raaz-label" for="raaz-occurred">Approximate date and time · optional<input id="raaz-occurred" name="occurred_at" type="datetime-local" value="${esc(draft.occurred_at)}"></label><p class="raaz-form-note">Place-name searches use Google Places. Only the location you confirm is attached to your report.</p><div class="raaz-step-actions"><button class="raaz-secondary" type="button" data-action="raaz-back">Back</button><button class="raaz-primary" type="button" data-action="raaz-next">Review <span aria-hidden="true">→</span></button></div>`;
    }else{
      const occurred=draft.occurred_at?new Date(draft.occurred_at).toLocaleString():"Not added";
      const location=raazHasLocation()?(draft.location_label||`${draft.latitude}, ${draft.longitude}`):"Not added";
      formContent=`<div class="raaz-step-heading"><span>STEP 4 OF 4</span><h2>Review your report</h2><p>Check the details before sending this report for review.</p></div><div class="raaz-review-list"><div class="raaz-review-row"><span class="raaz-detail-icon">▣</span><span><small>Category</small><strong>${esc(raazCategoryLabel(draft.category))}</strong></span><button type="button" data-action="raaz-edit-step" data-step="1">Edit</button></div><div class="raaz-review-row"><span class="raaz-detail-icon">▤</span><span><small>Description</small><strong>${esc(draft.description)}</strong></span><button type="button" data-action="raaz-edit-step" data-step="2">Edit</button></div><div class="raaz-review-row"><span class="raaz-detail-icon">⌖</span><span><small>Approximate location</small><strong>${esc(location)}</strong></span><button type="button" data-action="raaz-edit-step" data-step="3">Edit</button></div><div class="raaz-review-row"><span class="raaz-detail-icon">▦</span><span><small>Date &amp; time</small><strong>${esc(occurred)}</strong></span></div><div class="raaz-review-row"><span class="raaz-detail-icon">＋</span><span><small>Evidence</small><strong>${state.raazEvidence.length?state.raazEvidence.map(item=>esc(item.file.name)).join(" · "):"No attachments"}</strong></span></div></div><div class="raaz-privacy-note"><strong>Account-linked report</strong><br>Your identity is hidden from other users, but the report is linked to your account for review and status updates. It is not a public post.</div><div class="raaz-step-actions"><button class="raaz-secondary" type="button" data-action="raaz-back">Back</button><button class="raaz-primary" type="submit" ${state.raazSubmitting?"disabled":""}>${state.raazSubmitting?"Uploading and submitting…":"Submit report"} <span aria-hidden="true">→</span></button></div>`;
    }
    content=`${raazProgress(step)}<form id="report-form" class="raaz-wizard-card" novalidate>${formContent}</form>`;
  }
  shell(`<div class="raaz-page">${moduleGreeting("RAAZ","Naam Rahe Raaz, Safety Ki Awaaz.","raaz")}${tabs}${queueNotice}${content}</div>`);
}
function reportListHtml(){
  const rows=state.reports||[];
  const selected=state.raazSelectedReportId?rows.find(item=>item.id===state.raazSelectedReportId):null;
  if(state.raazSelectedReportId){
    if(!selected)return `<button class="raaz-back-link" type="button" data-action="raaz-report-back">← All reports</button><div class="raaz-empty"><strong>Report not found in this account.</strong>Refresh your reports to check again.</div>`;
    const statusClass=["validated","corroborated"].includes(selected.status)?"resolved":selected.status==="rejected"?"rejected":"pending";
    return `<article class="raaz-report-detail"><div class="raaz-report-detail-top"><span class="raaz-report-id">REPORT · ${esc(selected.id.slice(0,12).toUpperCase())}</span><span class="raaz-status-pill ${statusClass}">${esc(statusLabel(selected.status))}</span></div><h3>${esc(raazCategoryLabel(selected.category))}</h3><p class="raaz-report-description">${esc(selected.description)}</p><div class="raaz-report-meta"><span>Submitted</span><strong>${new Date(selected.created_at).toLocaleString()}</strong></div>${selected.occurred_at?`<div class="raaz-report-meta"><span>Approximate incident time</span><strong>${new Date(selected.occurred_at).toLocaleString()}</strong></div>`:""}${selected.location_label?`<div class="raaz-report-meta"><span>Incident location</span><strong>${esc(selected.location_label)}</strong></div>`:""}${raazSavedEvidenceHtml(selected.evidence)}<div class="raaz-status-explanation"><strong>Current status</strong><p>${esc(raazStatusMessage(selected.status))}</p><small>Last updated ${new Date(selected.updated_at||selected.created_at).toLocaleString()}</small></div><button class="raaz-secondary raaz-refresh-status" type="button" data-action="raaz-refresh-status" data-id="${esc(selected.id)}">Refresh status</button>${selected.status==="rejected"?`<form class="appeal-form raaz-appeal-form" data-report-id="${esc(selected.id)}"><label class="raaz-label">Appeal this decision<input name="message" minlength="10" maxlength="1000" placeholder="Tell the review team what should be reconsidered." required></label><button class="raaz-primary" type="submit">Submit appeal</button></form>`:""}</article>`;
  }
  const filter=state.raazFilter||"all";
  const filtered=rows.filter(item=>filter==="pending"?["submitted","pending_review","under_review"].includes(item.status):filter==="resolved"?["corroborated","validated","rejected"].includes(item.status):true);
  if(!rows.length)return `<div class="raaz-empty"><span aria-hidden="true">▤</span><strong>No reports yet</strong><p>Reports you submit from this account will appear here.</p><button class="raaz-primary" type="button" data-action="raaz-new-report">Report a concern</button></div>`;
  if(!filtered.length)return `<div class="raaz-empty"><strong>No ${filter} reports</strong><p>Try another status filter.</p></div>`;
  return `<div class="raaz-report-list">${filtered.map(item=>{const statusClass=["validated","corroborated"].includes(item.status)?"resolved":item.status==="rejected"?"rejected":"pending";return `<article class="raaz-report-card"><div class="raaz-report-card-top"><span class="raaz-report-id">REPORT · ${esc(item.id.slice(0,12).toUpperCase())}</span><span class="raaz-status-pill ${statusClass}">${esc(statusLabel(item.status))}</span></div><strong>${esc(raazCategoryLabel(item.category))}</strong><p>${esc(item.description.slice(0,150))}${item.description.length>150?"…":""}</p><small>${new Date(item.created_at).toLocaleString()}</small><button class="raaz-report-open" type="button" data-action="raaz-report-detail" data-id="${esc(item.id)}">View details <span aria-hidden="true">→</span></button></article>`;}).join("")}</div>`;
}
function statusLabel(value){return ({pending_review:"Pending review",under_review:"Under review",corroborated:"Corroborated",validated:"Validated",rejected:"Rejected",submitted:"Submitted",needs_attention:"Needs your attention",lower_reported_risk:"Lower reported risk",elevated_reported_risk:"Elevated reported risk",caution:"Caution",insufficient:"Insufficient information"})[value]||value;}
function renderBaat(){
  const people=["Mother","Father","Sister","Brother","Boyfriend"];
  if(!people.includes(state.caller))state.caller="Mother";
  const callerScripts=state.scripts.filter(item=>item.caller===state.caller);
  const languages=["English","Hindi"];
  const selectedLanguage=languages.includes(state.selectedLanguage)?state.selectedLanguage:"English";
  const languageScripts=callerScripts.filter(item=>item.language===selectedLanguage);
  const currentScript=callerScripts.find(item=>item.id===state.selectedScript);
  const activeScript=languageScripts.find(item=>item.scenario===(currentScript?.scenario||"checking-in"))||languageScripts[0]||callerScripts[0];
  if(activeScript&&state.selectedScript!==activeScript.id)state.selectedScript=activeScript.id;
  if(state.selectedLanguage!==selectedLanguage)state.selectedLanguage=selectedLanguage;
  const selectedCaller=state.caller==="Mother"?"Mom":state.caller;
  const activeTurn=baatCallTurns(activeScript)[state.speechLine];
  const callerTiles=people.map((name,index)=>`<button class="baat-persona ${state.caller===name?"selected":""}" data-action="caller" data-caller="${esc(name)}" aria-pressed="${state.caller===name}"><span class="baat-persona-avatar persona-${index}">${esc(name.slice(0,1))}</span><strong>${name==="Mother"?"Mom":esc(name)}</strong></button>`).join("");
  const hindiTranscriptControl=selectedLanguage==="Hindi"?`<div class="baat-hindi-display"><span>Hindi transcript</span><div class="baat-transcript-switch" role="group" aria-label="Hindi transcript format"><button type="button" data-action="hindi-transcript-style" data-style="devanagari" class="${state.hindiTranscriptStyle==="devanagari"?"selected":""}" aria-pressed="${state.hindiTranscriptStyle==="devanagari"}">हिन्दी</button><button type="button" data-action="hindi-transcript-style" data-style="hinglish" class="${state.hindiTranscriptStyle==="hinglish"?"selected":""}" aria-pressed="${state.hindiTranscriptStyle==="hinglish"}">Hinglish</button></div></div>`:"";
  let callStage="";
  if(state.callState==="ringing")callStage=`<section class="baat-stage baat-ringing"><span class="baat-eyebrow">INCOMING CALL · RINGING</span><div class="baat-stage-avatar ringing-avatar">${esc(selectedCaller.slice(0,1))}</div><h2>${esc(selectedCaller)}</h2><p>${esc(activeScript?.title||"Calling you")}</p><div class="baat-call-actions"><button class="baat-round-action decline" data-action="call-decline"><span aria-hidden="true">☎</span><small>Decline</small></button><button class="baat-round-action answer" data-action="call-answer"><span aria-hidden="true">☎</span><small>Answer</small></button></div><p class="baat-simulated-note">This simulated call keeps ringing until you answer or decline. It does not use your phone network.</p></section>`;
  else if(state.callState==="active")callStage=`<section class="baat-stage baat-active"><span class="baat-eyebrow">SIMULATED CALL · ${state.speechPaused?"PAUSED":"IN PROGRESS"}</span><div class="baat-stage-avatar">${esc(selectedCaller.slice(0,1))}</div><h2>${esc(selectedCaller)}</h2><p>${esc(activeScript?.title||"Conversation")}</p><div class="baat-live-line"><span class="baat-wave" aria-hidden="true">♫</span><div><small>${esc(baatTurnSpeaker(activeScript,state.speechLine,selectedCaller))}</small><p>${esc(baatTurnDisplayText(activeScript,state.speechLine)||"Your simulated call is ready.")}</p></div></div><div class="baat-controls"><button data-action="call-pause" class="baat-control" ${!activeTurn?.audio?"disabled":""}><span aria-hidden="true">${state.speechPaused?"▶":"Ⅱ"}</span><small>${state.speechPaused?"Resume":"Pause"}</small></button><button data-action="call-replay" class="baat-control"><span aria-hidden="true">↻</span><small>Replay</small></button><button data-action="call-end" class="baat-control baat-end"><span aria-hidden="true">☎</span><small>End Call</small></button></div><button class="baat-continue" data-action="call-answer" ${state.nextLineAvailable?"":"disabled"}>Continue call</button><p class="baat-simulated-note">${activeTurn?.speaker==="user"?"Reply in your own voice, then continue when ready. Your voice is not recorded.":activeTurn?.loop?"Continue when ready to hear the supplied acknowledgment again.":activeTurn?.speaker==="daughter"?"Your reply is shown as transcript only. No voice is played.":activeTurn?.audio?"Only the supplied MP3 recording plays; no other voice is used.":"No MP3 is attached to this line yet. It stays transcript-only."}</p></section>`;
  else if(state.callState==="ended")callStage=`<section class="baat-stage baat-ended"><div class="baat-check" aria-hidden="true">✓</div><h2>Call Ended</h2><p>You’re safe. Take a deep breath.</p><button class="baat-home-button" data-action="call-reset"><span aria-hidden="true">⌂</span>Back to Baat Banao</button><p class="baat-simulated-note">This was a simulated call. No real call was placed.</p></section>`;
  shell(`<div class="baat-page"><header class="baat-welcome"><div><span class="baat-eyebrow">BEFIKR · BAAT BANAO</span><h1>Hello, ${esc(state.user?.name?.split(" ")[0]||"there")}!</h1><p>Ring Ring, Awkwardness Gone!</p></div><span class="baat-avatar" aria-hidden="true">${esc((state.user?.name||"B").slice(0,1).toUpperCase())}</span></header>${state.callState==="idle"?`<div class="baat-prompt"><span class="baat-prompt-icon">${homeIcon("raaz")}</span><div><strong>Set up your call</strong><p>Choose who calls and what they say. Then start a simulated call.</p></div><span class="baat-chevron" aria-hidden="true">›</span></div><section class="baat-start-card"><button class="baat-call-button" data-action="call-start" aria-label="Start a simulated call">${homeIcon("baat")}</button><h2>Call Me</h2><p>Tap to start a fake incoming call</p><span class="baat-call-badge">SIMULATED · NO REAL CALL</span></section><section class="baat-panel"><div class="baat-section-title"><div><span class="baat-eyebrow">WHO’S CALLING?</span><h2>Choose your caller</h2></div><span class="baat-section-icon">♙</span></div><div class="baat-persona-grid">${callerTiles}</div></section><section class="baat-panel"><div class="baat-section-title"><div><span class="baat-eyebrow">CHOOSE SCRIPT</span><h2>Language & script</h2></div><span class="baat-section-icon">♫</span></div><div class="baat-language-list">${languages.map(language=>`<button class="baat-language ${selectedLanguage===language?"selected":""}" data-action="script-language" data-language="${esc(language)}" aria-pressed="${selectedLanguage===language}"><span>${language==="Hindi"?"हिन्दी":"English"}</span><span class="baat-language-check" aria-hidden="true">${selectedLanguage===language?"✓":""}</span></button>`).join("")}</div><label class="baat-field baat-script-select" for="script-select"><span>Choose a script</span><select id="script-select">${languageScripts.map(item=>`<option value="${esc(item.id)}" ${activeScript?.id===item.id?"selected":""}>${item.id.startsWith("mother-worried-")?"Worried Mom":item.scenario==="worried"?`Worried ${selectedCaller}`:`${selectedCaller} checking in`}</option>`).join("")}</select></label>${hindiTranscriptControl}<p class="baat-device-note">Only supplied MP3 recordings play. Lines without MP3 files and daughter replies stay transcript-only. No synthesized or device voice is used. This feature does not place a real call.</p></section>`:callStage}</div>`);
}
function renderBackup(){
  if(!state.user){
    const emergencyContent=state.sos?`<header class="backup-section-heading"><span class="backup-section-icon event-icon">!</span><span><h2>SOS actions</h2><small>Available on this device</small></span></header><p class="backup-event-message">Sign in to manage saved trusted contacts. You can still call emergency services or choose a recipient in your messaging app.</p>${sosActionsHtml()}`:`<header class="backup-section-heading"><span class="backup-section-icon event-icon">!</span><span><h2>Emergency help</h2><small>Sign in to manage trusted contacts</small></span></header><a class="btn danger" href="tel:112">Call emergency services · 112</a>`;
    shell(`<div class="backup-page">${moduleGreeting("BACKUP","One Tap, Your Gang's Got Your Back!","backup")}<section class="backup-panel backup-event-panel">${emergencyContent}</section></div>`);
    return;
  }
  const running=state.tracking;
  const journey=state.journey;
  const locationTime=running?.location_at?new Date(running.location_at).toLocaleTimeString([],{hour:"numeric",minute:"2-digit"}):"";
  const expiry=running?.expires_at?new Date(running.expires_at).toLocaleTimeString([],{hour:"numeric",minute:"2-digit"}):"";
  const nextCheckin=journey?.next_due_at?new Date(journey.next_due_at).toLocaleTimeString([],{hour:"numeric",minute:"2-digit"}):"";
  const checkinCount=Number(journey?.checkins_completed??(journey?.events||[]).length);
  const tapmePlanPreview=state.tapmeRoute?tapMePlan(state.tapmeRoute):null;
  const tapmeTotal=Number(journey?.total_checkins)||tapmePlanPreview?.count||1;
  const checkinDots=Array.from({length:tapmeTotal},(_,index)=>`<span class="backup-progress-dot ${index<checkinCount?"complete":index===checkinCount?"next":""}" aria-hidden="true"></span>`).join("");
  const trackingContacts=state.contacts.length?state.contacts.map(contact=>`<label class="backup-contact-choice"><input type="checkbox" name="recipient_ids" value="${esc(contact.id)}"><span><strong>${esc(contact.name)}</strong><small>${esc(contact.relationship||"Trusted contact")}</small></span></label>`).join(""):`<p class="backup-empty-contacts">Add trusted contacts below. You can start a private journey record without selecting any.</p>`;
  const trackingContent=running?`<div class="backup-session-state"><span class="backup-status-pill active"><i></i> Journey active</span><strong>${esc(running.destination||"Journey in progress")}</strong><p>${expiry?`Session ends at ${expiry}. `:""}${locationTime?`Last location saved at ${locationTime}.`:"No location saved yet."}</p></div><div class="backup-location-note"><span class="backup-location-icon">${homeIcon("map")}</span><span><strong>${locationTime?"Location saved to your account":"Location stays private"}</strong><small>Update it only when you choose. BEFIKR does not share live location with contacts.</small></span></div><div class="backup-actions"><button class="backup-primary" type="button" data-action="track-location">Update location now</button><button class="backup-secondary" type="button" data-action="track-stop">Stop journey</button></div>`:`<form id="tracking-form" class="backup-form"><label class="backup-field" for="track-destination"><span>Destination or journey note <small>Optional</small></span><input id="track-destination" name="destination" maxlength="160" placeholder="Where are you heading?"></label><label class="backup-field" for="track-duration"><span>Journey session</span><select id="track-duration" name="duration_minutes"><option value="30">30 minutes</option><option value="60">1 hour</option><option value="120" selected>2 hours</option><option value="480">8 hours</option></select></label><fieldset class="backup-contact-picker"><legend>Choose contacts for your record <small>Location is not sent to them</small></legend>${trackingContacts}</fieldset><p class="backup-privacy-note">This creates a private journey record in your account. It does not enable live sharing or contact alerts.</p><button class="backup-primary" type="submit">Start journey</button></form>`;
  const tapContent=journey?journey.status==="completed"?`<div class="backup-session-state"><span class="backup-status-pill active"><i></i>Journey complete</span><strong>${esc(journey.destination||"Your journey")}</strong><p>All ${tapmeTotal} route-based check-ins are recorded.</p></div><button class="backup-primary" data-action="checkin-dismiss">Done</button>`:`<div class="backup-session-state"><span class="backup-status-pill ${journey.status==="needs_attention"?"attention":"active"}"><i></i>${journey.status==="needs_attention"?"Check-in due":"Monitoring"}</span><strong>${esc(journey.destination||"Your journey")}</strong><p>${nextCheckin?`Next check-in at ${nextCheckin}.`:"Your next check-in is scheduled."} ${checkinCount} of ${tapmeTotal} planned check-ins recorded · ${esc(journey.duration_minutes||tapmeRoute?.minutes||"")} min route.</p></div><div class="backup-checkin-progress"><div class="backup-progress-track">${checkinDots}</div><div class="backup-progress-caption"><span>Route check-ins</span><span>${checkinCount} / ${tapmeTotal}</span></div></div><div class="backup-tap-actions"><button class="backup-tap-button" type="button" data-action="checkin-safe"><span aria-hidden="true">☝</span><strong>I’M OKAY</strong></button><button class="backup-secondary" type="button" data-action="checkin-cancel">End Tap Me</button></div><p class="backup-privacy-note">Reminders run while this app stays open. Missing a check-in only changes the local status; no contacts are notified.</p>`:tapmePlanPreview?`<div class="backup-tap-route"><small>RAAHI ROUTE</small><strong>${esc(state.tapmeRoute.origin)} → ${esc(state.tapmeRoute.destination)}</strong><span>${Number(state.tapmeRoute.distance_km||0).toFixed(2)} km · about ${tapmePlanPreview.duration} min</span><div class="tapme-equation"><strong>${tapmePlanPreview.count} check-ins suggested</strong><small>Rₜ = 0.25R + 0.15P + 0.10T + 0.15I + 0.10V + 0.10E + 0.15M = ${tapmePlanPreview.risk}/100</small><small>N = ceil(ceil(D ÷ 120) × (1 + Rₜ ÷ 100)), limited to 1–12.</small></div><p>Risk inputs without verified route data use neutral placeholders; route deviation is set to 0 because live tracking is off. This is a prototype schedule, not a safety score.</p><button class="backup-primary" type="button" data-action="checkin-start">Start Tap Me · ${tapmePlanPreview.count} check-ins</button><button class="backup-secondary" type="button" data-action="tapme-edit-route">Change pickup or destination on map</button></div>`:`<div class="backup-tap-route"><strong>Choose a Raahi route first</strong><p>Tap Me uses the route duration and both pinned endpoints to calculate the number of check-ins.</p><button class="backup-primary" type="button" data-action="tapme-open-raahi">Choose pickup and destination in Raahi</button></div>`;
  const eventHistory=state.sosEvents.length?`<details class="backup-history"><summary>Recent SOS records <span>${state.sosEvents.length}</span></summary><div class="backup-history-list">${state.sosEvents.slice(0,5).map(item=>`<div><span><strong>${esc(statusLabel(item.status))}</strong><small>${new Date(item.created_at).toLocaleString()}</small></span><small>Delivery ${esc(item.delivery_state)}</small></div>`).join("")}</div></details>`:"";
  shell(`<div class="backup-page">${moduleGreeting("BACKUP","One Tap, Your Gang's Got Your Back!","backup")}<section class="backup-sos-hero" aria-label="Emergency support"><span class="backup-kicker">YOUR SAFETY TOOLKIT</span><button class="backup-sos-trigger" type="button" data-action="sos" aria-label="Create an SOS event and open help options"><span class="backup-sos-halo" aria-hidden="true"></span><span class="backup-sos-shield" aria-hidden="true">${homeIcon("backup")}</span><strong>SOS</strong><small>TAP TO ACTIVATE</small></button><p class="backup-sos-tagline">One Tap, Your Gang's Got Your Back!</p><p class="backup-sos-disclosure">${nativeAndroidAvailable()?"On Android, SOS sends SMS to saved contacts and opens the 112 dialer after permissions are granted.":"Creates an SOS event, then shows call and text options for you to confirm."}</p>${nativeAndroidAvailable()?`<button class="backup-secondary android-sos-permission-setup" type="button" data-action="android-sos-permissions">Set up Android SOS permissions</button>`:""}</section><section class="backup-panel backup-track-panel"><header class="backup-section-heading"><span class="backup-section-icon">${homeIcon("map")}</span><span><h2>Track Me</h2><small>Private journey session</small></span><span class="backup-status-pill ${running?"active":"idle"}"><i></i>${running?"Active":"Not started"}</span></header>${trackingContent}<div class="backup-map-access"><p>Open the map to choose your location and preview streets after you consent.</p><button class="backup-map-link" type="button" data-action="map">${homeIcon("map")} Open map & location</button></div></section><section class="backup-panel backup-tap-panel"><header class="backup-section-heading"><span class="backup-section-icon tap-icon">☝</span><span><h2>Tap Me</h2><small>Check in with yourself</small></span><span class="backup-status-pill ${journey?journey.status==="needs_attention"?"attention":"active":"idle"}"><i></i>${journey?journey.status==="needs_attention"?"Check-in due":"Monitoring":"Not started"}</span></header>${tapContent}</section><section class="backup-panel backup-contacts-panel"><header class="backup-section-heading"><span class="backup-section-icon contacts-icon">${homeIcon("backup")}</span><span><h2>Trusted Contacts</h2><small>${state.contacts.length} saved · manage your chosen contacts</small></span></header><form id="contact-form" class="backup-contact-form"><label class="backup-field" for="contact-name"><span>Name</span><input id="contact-name" name="name" required maxlength="80" placeholder="Contact name"></label><div class="backup-form-grid"><label class="backup-field" for="contact-relation"><span>Relationship</span><input id="contact-relation" name="relationship" maxlength="40" placeholder="Friend, sibling…"></label><label class="backup-field" for="contact-phone"><span>Phone number</span><input id="contact-phone" name="phone" required maxlength="32" type="tel" placeholder="+91"></label></div><button class="backup-secondary" type="submit">Add trusted contact</button></form><div class="backup-contact-list">${contactListHtml()}</div></section>${state.sos?`<section class="backup-panel backup-event-panel"><header class="backup-section-heading"><span class="backup-section-icon event-icon">!</span><span><h2>SOS event</h2><small>Event ${esc(statusLabel(state.sos.status))} · delivery ${esc(state.sos.delivery_state)}</small></span></header><p class="backup-event-message">${esc(state.sos.message||"No external alert was sent.")}</p>${state.sos.status==="created"&&state.sos.id?`<button class="backup-secondary" data-action="cancel-sos">Cancel event</button>`:""}${sosActionsHtml()}</section>`:""}${eventHistory}<p class="backup-safety-note"><strong>${nativeAndroidAvailable()?"SOS delivery":"Keep control of every action."}</strong> ${nativeAndroidAvailable()?"SMS is sent after Android permission is granted. The 112 dialer opens, and the phone owner taps Call. WhatsApp opens its recipient picker when chosen.":"Calls and messages open on your device for your review. This development version does not dispatch emergency services or notify contacts automatically."}</p></div>`);
}
function contactListHtml(){if(!state.contacts.length)return `<div class="empty"><strong>No trusted contacts yet.</strong>Add someone you choose above.</div>`;return `<div class="list">${state.contacts.map(c=>`<div class="list-row"><div><strong>${esc(c.name)}</strong><p>${esc(c.relationship||"Trusted contact")} · ${esc(c.phone)}</p></div><button class="btn small ghost" data-action="contact-remove" data-id="${esc(c.id)}">Remove</button></div>`).join("")}</div>`;}
function sosActionsHtml(){
  if(!state.sos||state.sos.status!=="created")return "";
  const loc=state.sosLocation;
  const mapsUrl=loc?`https://maps.google.com/?q=${Number(loc.latitude).toFixed(6)},${Number(loc.longitude).toFixed(6)}`:"";
  const message=`SOS!!- ${mapsUrl||"Current location unavailable"}`;
  const contactActions=state.contacts.map(contact=>{
    const enteredPhone=String(contact.phone||"").trim();
    let digits=enteredPhone.replace(/\D/g,"");
    if(!digits)return "";
    if(digits.startsWith("00"))digits=digits.slice(2);
    if(digits.length===11&&digits.startsWith("0"))digits=digits.slice(1);
    if(digits.length===13&&digits.startsWith("910"))digits=`91${digits.slice(3)}`;
    if(digits.length===10)digits=`91${digits}`;
    const phone=`+${digits}`;
    const messageActions=state.sosLocationPending?`<small>Finding your location before preparing the message…</small>`:nativeAndroidAvailable()?`<small>SMS handled automatically by Android</small><button class="btn secondary" type="button" data-action="sos-whatsapp">WhatsApp</button>`:`<a class="btn secondary" href="${esc(`sms:${phone}?body=${encodeURIComponent(message)}`)}">SMS</a><a class="btn secondary" href="${esc(`https://wa.me/${digits}?text=${encodeURIComponent(message)}`)}" target="_blank" rel="noopener noreferrer">WhatsApp</a>`;
    return `<div class="sos-contact-actions"><strong>${esc(contact.name)}</strong><a class="btn secondary" href="tel:${esc(phone)}">Call</a>${messageActions}</div>`;
  }).join("");
  const unlistedRecipientActions=state.sosLocationPending?`<p class="helper">Finding your location; message options will appear shortly.</p>`:`<div class="sos-contact-actions"><strong>Choose a recipient</strong>${nativeAndroidAvailable()?`<button class="btn secondary" type="button" data-action="sos-whatsapp">Open WhatsApp recipient picker</button>`:`<a class="btn secondary" href="sms:?body=${encodeURIComponent(message)}">SMS</a><a class="btn secondary" href="https://wa.me/?text=${encodeURIComponent(message)}" target="_blank" rel="noopener noreferrer">WhatsApp</a><button class="btn secondary" type="button" data-action="sos-copy">Copy message</button>`}</div>`;
  const locationStatus=mapsUrl
    ?`<p><a href="${esc(mapsUrl)}" target="_blank" rel="noopener noreferrer">Open your current location in Google Maps</a></p>`
    :state.sosLocationPending
      ?`<p class="helper" role="status">Finding your current location. Call options are ready now.</p>`
      :`<p class="helper" role="status">${esc(state.sosLocationError||"Current location unavailable.")}</p><button type="button" class="btn small secondary" data-action="sos-retry-location">Retry location</button>`;
  return `<div class="result-box error sos-next-steps"><div class="result-title">Emergency actions</div><p>Call for help now. In India, use 112 for emergency services, or call one of your trusted contacts.</p>${locationStatus}<div class="actions"><a class="btn danger" href="tel:112">Call emergency services · 112</a></div>${contactActions||unlistedRecipientActions}<p class="helper">${nativeAndroidAvailable()?"Android submits the SMS after permission is granted. The 112 dialer still requires you to tap Call. WhatsApp opens a recipient picker; you choose and send there.":`Message draft: “${esc(message)}”. SMS opens your messaging app; WhatsApp opens a recipient chooser or that contact’s chat. Review and tap Send in the chosen app. Calls open your phone app and need your confirmation.`}</p></div>`;
}
function filteredSafePlaces(){
  const query=state.placeQuery.trim().toLowerCase();
  const cat=state.safeSpotCategory;
  const pool=(state.places&&state.places.length)?state.places:(state.offlinePlaces||[]);
  return pool.filter(place=>{
    if(cat&&place.category!==cat)return false;
    const text=[place.name,place.address,place.category_label,place.category].join(" ").toLowerCase();
    return !query||text.includes(query);
  });
}
function mapAttribution(){return state.googleMapsReady?`<div class="map-attribution">Google Maps</div>`:`<div class="map-attribution">© OpenStreetMap contributors</div>`;}
function safeSpotIcon(category){const icon={hospital:"✚",support:"●",public_space:"⌂",public_place:"⌂",park:"♧",restaurant:"◉",cafe:"☕",police:"⬟"}[category]||"⌖";return `<span class="spot-category-icon ${esc(category||"all")}" aria-hidden="true">${icon}</span>`;}
const SAFE_SPOT_CATEGORIES=[["","All"],["police","Police"],["hospital","Hospitals"],["park","Parks"],["public_space","Public spaces"],["restaurant","Restaurants"],["cafe","Cafes"],["directory","Directory"],["support","Support"]];
function safeSpotCategoryTabs(){return `<div class="spot-filter-row" role="group" aria-label="Filter nearby places">${SAFE_SPOT_CATEGORIES.map(([value,label])=>`<button class="spot-filter ${state.safeSpotCategory===value?"active":""}" type="button" data-action="places-category" data-category="${value}" aria-pressed="${state.safeSpotCategory===value}">${label}</button>`).join("")}</div>`;}
function placesUseDirectory(){return ["directory","support"].includes(state.safeSpotCategory);}

function safeSpotSourceLabel(place){return ({user_csv:"Nearby place",managed_directory:"Directory",google_places:"Google Maps"})[place.source_kind]||"Community map";}
function googlePlacesAttribution(){return `<p class="spot-google-attribution" translate="no">Google Maps</p>`;}
function placeProviderAttribution(places){
  const attributions=new Map();
  for(const place of places){
    for(const attribution of place.attributions||[]){
      if(attribution.provider)attributions.set(attribution.providerUri||attribution.provider_uri||attribution.provider,attribution);
    }
  }
  if(!attributions.size)return "";
  const providers=[...attributions.values()].map(attribution=>{
    const name=esc(attribution.provider);
    const url=attribution.providerUri||attribution.provider_uri||"";
    return /^https?:\/\//i.test(url)?`<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${name}</a>`:name;
  });
  return `<p class="spot-provider-attribution">${providers.join(" · ")}</p>`;
}
function googleNearbySearchTerm(){
  const category=state.safeSpotCategory==="police"?"Police stations":SAFE_SPOT_CATEGORIES.find(([value])=>value===state.safeSpotCategory)?.[1];
  return state.placeQuery||category||"public places";
}
function googleNearbyPlacesLink(label,className,searchTerm){
  if(!state.placeSearch)return "";
  const {latitude,longitude}=state.placeSearch;
  const params=new URLSearchParams({api:"1",query:`${searchTerm||googleNearbySearchTerm()} near ${latitude},${longitude}`});
  return `<a class="${className}" href="https://www.google.com/maps/search/?${esc(params.toString())}" target="_blank" rel="noopener noreferrer">${label}</a>`;
}
function safeSpotGoogleLinksHtml(){
  if(!state.placeSearch||state.placesLoading)return "";
  const categories={police:"police stations",hospital:"hospitals",restaurant:"restaurants",cafe:"cafes",park:"parks",public_space:"public spaces",directory:"public places",support:"women support centres"};
  const terms=state.safeSpotCategory?[categories[state.safeSpotCategory]||"public places"]:["police stations","hospitals","restaurants","cafes","parks"];
  return `<section class="spot-google-search-links" aria-label="More nearby places in Google Maps"><h2>Search nearby in Google Maps</h2><div>${terms.map(term=>googleNearbyPlacesLink(`Search nearby ${esc(term)} in Google Maps ↗`,"spot-google-search-link",term)).join("")}</div></section>`;
}
async function embedNearbyGoogleSearch(container){
  if(!container||!state.placeSearch||placesUseDirectory())return false;
  const {latitude,longitude}=state.placeSearch;
  return renderGoogleMapEmbed(container,"search",{q:googleNearbySearchTerm(),center:`${latitude},${longitude}`,zoom:13},"Search Google Maps near your chosen location");
}
function placesSearchUnavailable(){
  return ["csv_dataset_unavailable","google_places_not_configured","google_places_unavailable","places_unavailable"].includes(state.placesMeta?.source_state);
}
function spotRouteKey(place){
  return JSON.stringify([state.placeSearch?.latitude,state.placeSearch?.longitude,place.id,place.latitude,place.longitude]);
}
function spotRouteSummaryHtml(place){
  const journey=state.spotRoute?.key===spotRouteKey(place)?state.spotRoute:null;
  if(!journey||journey.loading)return `<div class="spot-route-summary" role="status"><span class="raahi-spinner" aria-hidden="true"></span><p>Finding your walking route…</p></div>`;
  if(!journey.route)return `<div class="spot-route-summary"><strong>Walking route unavailable</strong><p>${esc(journey.error||"A walking route could not be found. Try again.")}</p><button type="button" class="spot-directions" data-action="place-directions" data-id="${esc(place.id)}">Retry route</button></div>`;
  const route=journey.route;
  return `<section class="spot-route-summary"><div class="spot-route-metrics"><span><small>Walking distance</small><strong>${Number(route.distance_km).toFixed(2)} km</strong></span><span><small>Estimated time</small><strong>${esc(route.minutes)} min</strong></span></div><p>From your chosen location to ${esc(place.name)}.</p><p class="spot-data-note">Walking route estimate. Check signs and access along the way.</p>${route.steps?.length?`<details class="spot-route-steps"><summary>Walking directions</summary><ol>${route.steps.map(step=>`<li><span>${esc(step.instruction)}</span><small>${Number(step.distance_m)>=1000?`${(Number(step.distance_m)/1000).toFixed(1)} km`:`${Number(step.distance_m)} m`}</small></li>`).join("")}</ol></details>`:""}</section>`;
}
async function loadSpotRoute(place,force=false){
  const key=spotRouteKey(place);
  if(!force&&state.spotRoute?.key===key)return;
  state.spotRouteController?.abort();
  const controller=new AbortController();state.spotRouteController=controller;
  const origin=state.placeSearch;
  state.spotRoute={key,loading:true,route:null,error:""};
  const update=()=>{if(!controller.signal.aborted&&state.page==="safe-spot"&&state.safeSpotView==="detail"&&state.selectedPlaceId===place.id)renderSafeSpot();};
  update();
  const timer=setTimeout(()=>controller.abort(),65000);
  try{
    if(!origin)throw new Error("Choose your starting location first.");
    const googleReady=await ensureGoogleMaps();
    if(controller.signal.aborted)throw new Error("Route request cancelled.");
    const result=await api("/routes/alternatives",{method:"POST",signal:controller.signal,body:{context:"safe_spot",origin:"Your chosen location",destination:place.name.slice(0,160),origin_latitude:origin.latitude,origin_longitude:origin.longitude,destination_latitude:Number(place.latitude),destination_longitude:Number(place.longitude),use_google_maps:googleReady}});
    if(controller.signal.aborted)throw new Error("Route request cancelled.");
    const routes=(result.routes||[]).filter(route=>route.geometry?.type==="LineString"&&route.geometry.coordinates?.length>1&&Number.isFinite(Number(route.distance_km))&&Number.isFinite(Number(route.minutes)));
    const route=routes.sort((a,b)=>Number(a.distance_km)-Number(b.distance_km))[0];
    state.spotRoute={key,loading:false,route:route||null,origin:{...origin},error:route?"":"The walking route service is unavailable for these points. Please retry shortly."};
  }catch(error){
    if(state.spotRouteController!==controller)return;
    state.spotRoute={key,loading:false,route:null,error:controller.signal.aborted?"The route request timed out. Please retry.":error.message};
  }finally{
    clearTimeout(timer);
    if(state.spotRouteController===controller){
      state.spotRouteController=null;
      // A timeout should replace the loading state; a cancelled older request must not.
      if(state.page==="safe-spot"&&state.safeSpotView==="detail"&&state.selectedPlaceId===place.id)renderSafeSpot();
    }
  }
}
async function drawSpotRouteMap(place){
  const element=document.getElementById("place-detail-map");if(!element)return;
  const journey=state.spotRoute?.key===spotRouteKey(place)?state.spotRoute:null;
  const route=journey?.route;
  if(state.placeMap?.type==="leaflet"){
    try{state.placeMap.map.remove();}catch(e){}
  }
  state.placeMap=null;
  element.hidden=false;

  const googleReady=await ensureGoogleMaps();
  if(!element.isConnected)return;
  const origin=state.placeSearch?[Number(state.placeSearch.latitude),Number(state.placeSearch.longitude)]:[28.6328,77.2197];
  const dest=[Number(place.latitude),Number(place.longitude)];

  if(googleReady&&route?.geometry?.coordinates){
    const coordinates=route.geometry.coordinates;
    const map=new google.maps.Map(element,{center:{lat:coordinates[0][1],lng:coordinates[0][0]},zoom:14,mapTypeControl:false,streetViewControl:false,fullscreenControl:true});
    const path=coordinates.map(([lng,lat])=>({lat,lng})),bounds=new google.maps.LatLngBounds();
    new google.maps.Polyline({map,path,strokeColor:"#1a73e8",strokeWeight:6,strokeOpacity:.95});
    path.forEach(point=>bounds.extend(point));
    new google.maps.Marker({map,position:path[0],label:"S",title:"Starting point"});
    new google.maps.Marker({map,position:path.at(-1),label:"D",title:place.name});
    map.fitBounds(bounds,32);state.placeMap={type:"google",map};return;
  }

  // Guaranteed Leaflet rendering
  if(!window.L){element.textContent="The map could not load. Check your connection and retry.";return;}
  const map=L.map(element,{scrollWheelZoom:false}).setView(dest,14);
  state.placeMap={type:"leaflet",map};
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{maxZoom:19,attribution:"© OpenStreetMap contributors"}).addTo(map);

  // Origin marker
  L.circleMarker(origin,{radius:8,color:"#fff",weight:3,fillColor:"#1a73e8",fillOpacity:1}).addTo(map).bindTooltip("Your chosen location");

  // Destination safe spot pin
  const cat=place.category||"spot";
  const catIcon={hospital:"✚",police:"⬟",park:"♧",public_space:"⌂",restaurant:"◉",cafe:"☕"}[cat]||"⬟";
  const destPin=L.divIcon({className:"spot-marker-shell",html:`<span class='spot-marker'>${catIcon}</span>`,iconSize:[34,40],iconAnchor:[17,38]});
  L.marker(dest,{icon:destPin}).addTo(map).bindTooltip(esc(place.name));

  if(route?.geometry?.coordinates){
    const line=L.geoJSON(route.geometry,{style:{color:"#1a73e8",weight:6,opacity:.95}}).addTo(map);
    map.fitBounds(line.getBounds().pad(.15));
  } else {
    const directLine=L.polyline([origin,dest],{color:"#1a73e8",weight:5,dashArray:"6, 8",opacity:0.85}).addTo(map);
    map.fitBounds(directLine.getBounds().pad(.2));
  }
  const attribution=document.getElementById("place-detail-map-attribution");
  if(attribution)attribution.innerHTML='<span>© OpenStreetMap contributors</span>';
  requestAnimationFrame(()=>{if(element.isConnected)map.invalidateSize();});
}
function renderSafeSpot(){
  const queryValue=esc(state.placeQuery);
  if(state.safeSpotView==="detail"){
    const place=(state.places||[]).find(item=>item.id===state.selectedPlaceId);
    if(!place){state.safeSpotView="results";return renderSafeSpot();}
    const distance=Number.isFinite(Number(place.distance_km))?`${esc(place.distance_km)} km straight-line distance`:"Distance unavailable";
    shell(`<div class="spot-page"><header class="spot-subhead"><button class="spot-back" data-action="places-results" aria-label="Back to nearby places">←</button><h1>Route to Safe Spot</h1></header><div id="place-detail-map" class="spot-map spot-detail-map" role="img" aria-label="Walking route to ${esc(place.name)}"></div><div id="place-detail-map-attribution" class="map-attribution"></div>${spotRouteSummaryHtml(place)}<section class="spot-detail-title">${safeSpotIcon(place.category)}<div><div class="spot-title-line"><h2>${esc(place.name)}</h2><span class="spot-source-tag community">${esc(safeSpotSourceLabel(place))}</span></div><p>${distance}</p>${place.source_kind==="google_places"?googlePlacesAttribution():""}${placeProviderAttribution([place])}</div></section><section class="spot-info-section"><h3>About</h3><p>${esc(place.category_label||place.category)} near your chosen location. Check current hours and service availability.</p></section><section class="spot-info-section"><h3>Address</h3><p>${esc(place.address||"Address not listed")}</p></section><section class="spot-contact-card"><div><h3>Contact</h3>${place.phone?`<a href="tel:${esc(String(place.phone).replace(/[^\d+]/g,""))}">${esc(place.phone)}</a>`:`<p>Phone number not listed</p>`}</div>${place.phone?`<a class="spot-call-button" href="tel:${esc(String(place.phone).replace(/[^\d+]/g,""))}" aria-label="Call ${esc(place.name)}">☎</a>`:""}</section><p class="spot-data-note">Opening hours and current availability have not been confirmed.</p><button class="spot-directions" data-action="place-directions" data-id="${esc(place.id)}">Refresh walking route</button><button class="spot-search-button secondary" data-action="places-map-pick">Change starting point</button></div>`);
    requestAnimationFrame(()=>drawSpotRouteMap(place));
    return;
  }
  if(state.safeSpotView==="results"){
    const places=filteredSafePlaces();
    shell(`<div class="spot-page"><header class="spot-subhead"><button class="spot-back" data-action="places-home" aria-label="Back to Safe Spots home">←</button><button class="spot-location-pill" data-action="places-map-pick">⌖ Chosen location <span>Update ›</span></button></header><h1 class="spot-results-title">Nearby Safe Spots</h1><form id="places-form" class="spot-search-inline"><input name="query" type="search" maxlength="100" value="${queryValue}" placeholder="Search this list"><input type="hidden" name="latitude" value="${esc(state.placeSearch?.latitude??"")}"><input type="hidden" name="longitude" value="${esc(state.placeSearch?.longitude??"")}"><input type="hidden" name="radius_km" value="5"><button type="submit" aria-label="Search nearby places">⌕</button></form>${safeSpotCategoryTabs()}<div class="spot-results-heading"><strong>${state.placesLoading?"Searching nearby…":placesSearchUnavailable()?"Search unavailable":`${places.length} place${places.length===1?"":"s"}`}</strong>${!state.placesLoading&&places.length?`<button class="spot-map-link" data-action="places-map">View map</button>`:""}</div><div id="places-results">${placeResultsHtml()}</div>${safeSpotGoogleLinksHtml()}<div class="spot-data-note">Showing places within 5 km by straight-line distance from your chosen point, nearest first. Check current hours and availability.</div></div>`);

    return;
  }
  if(state.safeSpotView==="map"){
    const places=filteredSafePlaces();
    const selected=places.find(item=>item.id===state.selectedPlaceId)||places[0];
    shell(`<div class="spot-page"><header class="spot-subhead"><button class="spot-back" data-action="places-results" aria-label="Back to nearby places">←</button><h1>Safe Spot</h1></header><div id="places-map" class="spot-map" role="img" aria-label="Map of nearby places"></div><div id="places-map-attribution" class="map-attribution"></div>${selected?`<section class="spot-map-place-card">${safeSpotIcon(selected.category)}<div><strong>${esc(selected.name)}</strong><p>${esc(selected.distance_km)} km · ${esc(safeSpotSourceLabel(selected))}</p></div><button data-action="place-open" data-id="${esc(selected.id)}" aria-label="Open ${esc(selected.name)} details">›</button></section>`:`<div class="spot-map-place-card empty">${esc(state.placesMeta?.empty_message||"No places to display.")}</div>`}${selected?.source_kind==="google_places"?googlePlacesAttribution():""}${placeProviderAttribution(places)}<button class="spot-directions" data-action="places-results">View nearby places</button></div>`);
    requestAnimationFrame(()=>drawPlacesMap("places-map",places));
    return;
  }
  shell(`<div class="spot-page"><header class="spot-welcome"><div><span class="spot-eyebrow">BEFIKR · SAFE SPOTS</span><h1>Hello, ${esc(state.user?.name?.split(" ")[0]||"there")}!</h1><p>Need a Breather? Find Your Safe Corner!</p></div><span class="spot-avatar" aria-hidden="true">${esc((state.user?.name||"B").slice(0,1).toUpperCase())}</span></header><form id="places-form" class="spot-search-form"><label class="spot-search-box"><span aria-hidden="true">⌕</span><input name="query" type="search" maxlength="100" value="${queryValue}" placeholder="Search for help…" aria-label="Search nearby place names"></label><input name="latitude" type="hidden" value="${esc(state.placeSearch?.latitude??"")}"><input name="longitude" type="hidden" value="${esc(state.placeSearch?.longitude??"")}"><input name="radius_km" type="hidden" value="5"><div class="spot-search-actions"><button type="button" class="spot-search-button" data-action="places-location">Use my location</button><button type="button" class="spot-search-button secondary" data-action="places-map-pick">Pick on map</button></div><p class="spot-data-note" data-location-feedback role="status"></p><details class="spot-manual-location"><summary>Enter coordinates manually</summary><div><label for="spot-lat">Latitude</label><input id="spot-lat" name="latitude-manual" type="number" min="-90" max="90" step="any" placeholder="28.6139"><label for="spot-lon">Longitude</label><input id="spot-lon" name="longitude-manual" type="number" min="-180" max="180" step="any" placeholder="77.2090"><button type="button" data-action="places-manual-search">Search these coordinates</button></div></details></form><section class="spot-home-categories"><button data-action="places-category" data-category="hospital">${safeSpotIcon("hospital")}<strong>Hospitals</strong></button><button data-action="places-category" data-category="police">${safeSpotIcon("police")}<strong>Police stations</strong></button><button data-action="places-category" data-category="park">${safeSpotIcon("park")}<strong>Nearby parks</strong></button><button data-action="places-category" data-category="public_space">${safeSpotIcon("public_space")}<strong>Public spaces</strong></button><button data-action="places-category" data-category="restaurant">${safeSpotIcon("restaurant")}<strong>Restaurants</strong></button><button data-action="places-category" data-category="cafe">${safeSpotIcon("cafe")}<strong>Cafes</strong></button></section><button class="spot-safety-promo" data-action="places-location">${safeSpotIcon("police")}<span><strong>Your Safety First</strong><small>Find nearby public and support places using your chosen location.</small></span><b aria-hidden="true">›</b></button><div class="spot-quick-heading"><h2>Quick Access</h2><span>Emergency help</span></div><a class="spot-emergency-card" href="tel:112"><span class="spot-emergency-icon">☎</span><span><strong>Emergency Helpline 112</strong><small>India’s national emergency number · opens your phone</small></span><b aria-hidden="true">›</b></a><div class="spot-data-note">Confirm a map pin to find places within 5 km, nearest first.</div></div>`);
}
function placeResultsHtml(){
  if(state.placesLoading){
    const label=placesUseDirectory()?"Checking the directory…":"Finding places within 5 km…";
    return `<div class="spot-loading"><span class="raahi-spinner" aria-hidden="true"></span><strong>${label}</strong></div>`;
  }
  const places=filteredSafePlaces();
  const meta=state.placesMeta||{};
  if(!places.length){
    const unavailable=placesSearchUnavailable();
    const heading=unavailable?"Nearby search is unavailable":state.places.length?"No places match your search":"No nearby places found";
    const message=unavailable?meta.message:state.places.length?"Try a shorter search.":meta.empty_message;

    return `<div class="spot-empty"><strong>${heading}</strong><p>${esc(message||"Choose another location or category.")}</p>${unavailable?`<button type="button" class="spot-map-link" data-action="places-retry">Try again</button>`:""}</div>`;
  }
  const attribution=places.some(place=>place.source_kind==="google_places")?googlePlacesAttribution():"";
  return `<div class="spot-place-list">${places.map(place=>{const managed=place.source_kind==="managed_directory";return `<button class="spot-place-card" data-action="place-open" data-id="${esc(place.id)}">${safeSpotIcon(place.category)}<span class="spot-place-copy"><strong>${esc(place.name)}</strong><small>${esc(place.distance_km)} km · ${esc(place.category_label||place.category)}</small><span>${esc(place.address||"Address not listed")}</span></span><span class="spot-source-tag ${managed?"managed":"community"}">${esc(safeSpotSourceLabel(place))}</span><span class="spot-chevron" aria-hidden="true">›</span></button>`;}).join("")}</div>${attribution}${placeProviderAttribution(places)}${meta.source_state==="google_places_partial"&&meta.message?`<p class="spot-source-note">${esc(meta.message)}</p>`:""}`;
}
async function drawPlacesMap(elementId,places=filteredSafePlaces()){
  const element=document.getElementById(elementId);if(!element)return;
  const attribution=document.getElementById(`${elementId}-attribution`);
  if(state.placeMap?.type==="leaflet"){
    try{state.placeMap.map.remove();}catch(e){}
  }
  state.placeMap=null;
  element.hidden=false;

  const center=state.placeSearch?{lat:Number(state.placeSearch.latitude),lng:Number(state.placeSearch.longitude)}:{lat:28.6328,lng:77.2197};
  const googleMapReady=await ensureGoogleMaps();
  if(!element.isConnected)return;
  if(googleMapReady){
    const map=new google.maps.Map(element,{center,zoom:14,mapTypeControl:false,streetViewControl:false,fullscreenControl:true});
    const bounds=new google.maps.LatLngBounds();
    if(state.placeSearch){new google.maps.Marker({position:center,map,label:"Y",title:"Your chosen location"});bounds.extend(center);}
    for(const place of places){const point={lat:Number(place.latitude),lng:Number(place.longitude)};if(!Number.isFinite(point.lat)||!Number.isFinite(point.lng))continue;const marker=new google.maps.Marker({position:point,map,title:place.name});marker.addListener("click",()=>{state.selectedPlaceId=place.id;state.safeSpotView="detail";renderSafeSpot();void loadSpotRoute(place);});bounds.extend(point);}
    if(!bounds.isEmpty())map.fitBounds(bounds,36);
    state.placeMap={type:"google",map};
    return;
  }

  // Guaranteed Leaflet rendering without hiding element
  if(!window.L){element.textContent="Map library is currently unavailable.";return;}
  if(attribution)attribution.textContent="© OpenStreetMap contributors";
  const map=L.map(element,{scrollWheelZoom:true});state.placeMap={type:"leaflet",map};
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{maxZoom:19,attribution:"© OpenStreetMap contributors"}).addTo(map);
  const osmCenter=[center.lat,center.lng],bounds=[];
  if(state.placeSearch&&Number.isFinite(center.lat)&&Number.isFinite(center.lng)){
    L.circleMarker(osmCenter,{radius:8,color:"#fff",weight:3,fillColor:"#1a73e8",fillOpacity:1}).addTo(map).bindTooltip("Your chosen location");
    bounds.push(osmCenter);
  }
  const displayPlaces=(places&&places.length)?places:(state.offlinePlaces||[]);
  for(const place of displayPlaces){
    const point=[Number(place.latitude),Number(place.longitude)];
    if(!Number.isFinite(point[0])||!Number.isFinite(point[1]))continue;
    const cat=place.category||"spot";
    const catIcon={hospital:"✚",police:"⬟",park:"♧",public_space:"⌂",restaurant:"◉",cafe:"☕"}[cat]||"⬟";
    const pin=L.divIcon({className:"spot-marker-shell",html:`<span class='spot-marker'>${catIcon}</span>`,iconSize:[34,40],iconAnchor:[17,38]});
    const marker=L.marker(point,{icon:pin}).addTo(map).bindTooltip(esc(place.name));
    marker.on("click",()=>{
      state.selectedPlaceId=place.id;state.safeSpotView="detail";renderSafeSpot();void loadSpotRoute(place);
    });
    bounds.push(point);
  }
  if(bounds.length>1)map.fitBounds(L.latLngBounds(bounds).pad(.16));else map.setView(osmCenter,14);
  requestAnimationFrame(()=>{if(element.isConnected)map.invalidateSize();});
}
function profileIcon(name){
  const paths={
    contacts:`<circle cx="9" cy="8" r="3"/><path d="M3.5 20a5.5 5.5 0 0 1 11 0"/><path d="M16 5.5a3 3 0 0 1 0 5.8M17 14a5 5 0 0 1 3.5 4.8"/>`,
    settings:`<circle cx="12" cy="12" r="3.5"/><path d="M21.42 10.76 L21.42 13.24 L19.24 13.94 L18.50 15.75 L19.54 17.78 L17.78 19.54 L15.75 18.50 L13.94 19.24 L13.24 21.42 L10.76 21.42 L10.06 19.24 L8.25 18.50 L6.22 19.54 L4.46 17.78 L5.50 15.75 L4.76 13.94 L2.58 13.24 L2.58 10.76 L4.76 10.06 L5.50 8.25 L4.46 6.22 L6.22 4.46 L8.25 5.50 L10.06 4.76 L10.76 2.58 L13.24 2.58 L13.94 4.76 L15.75 5.50 L17.78 4.46 L19.54 6.22 L18.50 8.25 L19.24 10.06 Z"/>`,
    shield:`<path d="M12 3 20 6v5c0 5-3.2 8.3-8 10-4.8-1.7-8-5-8-10V6l8-3Z"/><path d="m9 12 2 2 4-4"/>`,
    help:`<circle cx="12" cy="12" r="9"/><path d="M9.7 9a2.4 2.4 0 1 1 4.1 1.7c-1.1 1.1-1.8 1.3-1.8 3"/><path d="M12 17.5h.01"/>`,
    info:`<circle cx="12" cy="12" r="9"/><path d="M12 11v5m0-8h.01"/>`,
    logout:`<path d="M10 17l5-5-5-5m5 5H3"/><path d="M12 3h6a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-6"/>`
  };
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths[name]||paths.info}</svg>`;
}
function profileAvatar(){return `<svg viewBox="0 0 100 100" role="img" aria-label="Profile portrait illustration"><circle cx="50" cy="50" r="49" fill="#f1def8"/><path d="M17 95V54c0-23 13-39 33-39s34 16 34 39v41H17Z" fill="#30131f"/><path d="M22 100c2-19 13-29 28-29s27 10 29 29H22Z" fill="#ead5c6"/><path d="M42 65h16v16H42z" fill="#d99372"/><ellipse cx="50" cy="47" rx="22" ry="27" fill="#f5b78e"/><path d="M28 45c0-21 10-33 24-33 17 0 25 14 22 33-4-8-9-12-16-15-6 6-17 10-30 10v5Z" fill="#291722"/><path d="M30 45c-4 9-3 24 1 31l-9 12V49c0-20 10-35 28-38-14 7-20 18-20 34Zm40-3c6 8 5 24 1 33l8 12V48c0-20-10-33-27-37 13 7 18 18 18 31Z" fill="#291722"/><circle cx="42" cy="48" r="1.7" fill="#3a2020"/><circle cx="59" cy="48" r="1.7" fill="#3a2020"/><path d="M45 59c3 2 7 2 10 0" fill="none" stroke="#a95054" stroke-width="1.7" stroke-linecap="round"/><path d="M38 76c7 6 17 6 24 0" fill="none" stroke="#bd9c56" stroke-width="2"/></svg>`;}
function renderSettings(){
  const name=esc(state.user?.name||"BEFIKR member"),email=esc(state.user?.email||"");
  const privacyRows=`<div class="profile-status-row"><span><strong>Maps & routing</strong><small>Map previews and public-place search; no live route safety rating.</small></span><b>Partial</b></div><div class="profile-status-row"><span><strong>SOS & notifications</strong><small>Call and text handoff needs your confirmation; nothing sends automatically.</small></span><b>Partial</b></div><div class="profile-status-row"><span><strong>Track Me & Tap Me</strong><small>Sessions run in the app; background alerts and escalation are not configured.</small></span><b>Partial</b></div><div class="profile-status-row"><span><strong>Baat Banao</strong><small>Simulated calls play your supplied voice recordings.</small></span><b>Demo</b></div><div class="profile-status-row"><span><strong>Reports & attachments</strong><small>Private photo and video evidence for your Raaz reports.</small></span><b>Available</b></div>`;
  shell(`<section class="profile-page"><header class="profile-header"><button class="profile-back" data-action="home"><span aria-hidden="true">‹</span> Back</button><h1>Profile</h1><button class="profile-gear" data-action="profile-settings" aria-label="Open app settings">${profileIcon("settings")}</button></header>
    <section class="profile-hero"><div class="profile-avatar">${profileAvatar()}</div><h2>${name}</h2><p>${email}</p><details class="profile-edit"><summary>Edit Profile</summary><form id="profile-form" class="profile-edit-form"><label for="profile-name">Display name</label><input id="profile-name" name="name" required maxlength="80" value="${name}"><button type="submit">Save changes</button></form></details></section>
    <section class="profile-menu" aria-label="Profile options"><button class="profile-row" data-action="backup"><span class="profile-row-icon icon-contacts">${profileIcon("contacts")}</span><span class="profile-row-label">My Trusted Contacts</span><span class="profile-chevron" aria-hidden="true">›</span></button>
      <details class="profile-menu-item" id="profile-app-settings"><summary class="profile-row"><span class="profile-row-icon icon-settings">${profileIcon("settings")}</span><span class="profile-row-label">App Settings</span><span class="profile-chevron" aria-hidden="true">›</span></summary><div class="profile-detail-panel"><p>BEFIKR asks for location only when you choose a feature that needs it. Notifications and background monitoring are not configured in this build.</p><div class="profile-setting-row"><span>Interface</span><strong>BEFIKR · warm theme</strong></div></div></details>
      <details class="profile-menu-item"><summary class="profile-row"><span class="profile-row-icon icon-shield">${profileIcon("shield")}</span><span class="profile-row-label">Privacy &amp; Security</span><span class="profile-chevron" aria-hidden="true">›</span></summary><div class="profile-detail-panel"><p>Your account is private to your session. Location is requested only after you choose a location feature.</p><div class="profile-status-list">${privacyRows}</div><div class="profile-detail-actions"><button data-action="export-data">Export my data</button><button class="profile-delete" data-action="delete-account">Delete account and data</button></div></div></details>
      <details class="profile-menu-item"><summary class="profile-row"><span class="profile-row-icon icon-help">${profileIcon("help")}</span><span class="profile-row-label">Help &amp; Support</span><span class="profile-chevron" aria-hidden="true">›</span></summary><div class="profile-detail-panel"><p>This development build is not monitored as an emergency service. If you need immediate help, contact your local emergency service directly.</p><p class="profile-small-note">Manage trusted contacts in Backup, or find nearby help in Safe Spots.</p></div></details>
      <details class="profile-menu-item"><summary class="profile-row"><span class="profile-row-icon icon-info">${profileIcon("info")}</span><span class="profile-row-label">About BEFIKR</span><span class="profile-chevron" aria-hidden="true">›</span></summary><div class="profile-detail-panel"><strong>BEFIKR</strong><p>Everyday safety support, designed around your choices.</p><p class="profile-small-note">A development preview. SOS does not dispatch emergency services, and route safety ratings are not connected.</p></div></details>
    </section><button class="profile-logout" data-action="logout">${profileIcon("logout")}<span>Log Out</span></button></section>`);
}
function renderAdmin(){
  const tabs=["reports","appeals","places","audit"];
  let body="";
  if(state.adminTab==="reports")body=adminReportsHtml();
  if(state.adminTab==="appeals")body=state.appeals?.length?state.appeals.map(a=>`<article class="admin-report"><strong>Appeal ${esc(a.id.slice(0,8))}</strong><p>${esc(a.message)}</p><div class="actions"><button class="btn small" data-action="appeal-review" data-id="${esc(a.id)}" data-decision="reopen">Reopen for review</button><button class="btn small secondary" data-action="appeal-review" data-id="${esc(a.id)}" data-decision="upheld">Uphold rejection</button></div></article>`).join(""):`<div class="empty"><strong>No pending appeals.</strong></div>`;
  if(state.adminTab==="places")body=adminPlacesHtml();
  if(state.adminTab==="audit")body=state.audit?.length?state.audit.map(a=>`<div class="list-row"><div><strong>${esc(a.action)}</strong><p>${esc(a.target_type)} · ${esc(a.target_id)} · ${esc(a.detail)} · ${new Date(a.created_at).toLocaleString()}</p></div></div>`).join(""):`<div class="empty"><strong>No audit events yet.</strong></div>`;
  shell(`${pageHead("Operations console","Authorised staff","Review sensitive reports only when needed. Access is role-gated; actions are written to an audit log.")}<section class="card"><div class="metrics"><div class="metric"><strong>${state.dashboard?.total_users??"—"}</strong><span>Accounts</span></div><div class="metric"><strong>${state.dashboard?.pending_review??"—"}</strong><span>Reports to review</span></div><div class="metric"><strong>${state.dashboard?.pending_appeals??"—"}</strong><span>Pending appeals</span></div></div><p class="inline-note">${esc(state.dashboard?.note||"SOS figures count saved events; they do not represent dispatched alerts.")}</p></section><section class="card"><nav class="admin-tabs" aria-label="Admin tools">${tabs.map(t=>`<button class="tab-btn ${t===state.adminTab?"active":""}" data-action="admin-tab" data-tab="${t}">${t[0].toUpperCase()+t.slice(1)}</button>`).join("")}</nav><div>${body||`<div class="empty">Loading administrative information…</div>`}</div></section>`);
}
function adminReportsHtml(){if(!state.adminReports?.length)return `<div class="empty"><strong>No reports in this queue.</strong>Pending reports will appear here for authorised review.</div>`;return state.adminReports.map(r=>`<article class="admin-report"><div class="admin-report-meta">${esc(r.category)} · ${esc(statusLabel(r.status))} · ${new Date(r.created_at).toLocaleString()}</div>${r.nearby_similar_reporters?`<span class="tag amber">${r.nearby_similar_reporters} other reporter${r.nearby_similar_reporters===1?"":"s"} in a similar place/time — review independently</span>`:""}<p>${esc(r.description)}</p><div class="admin-report-meta">Account: ${esc(r.reporter_email)} · approximate location: ${r.latitude==null?"not provided":`${esc(r.latitude)}, ${esc(r.longitude)}`}</div>${r.history?.length?`<p class="admin-report-meta">History: ${r.history.map(h=>`${esc(h.old_status||"new")} → ${esc(h.new_status)}${h.reason?` (${esc(h.reason)})`:""}`).join(" · ")}</p>`:""}${raazSavedEvidenceHtml(r.evidence)}<form class="moderation-form" data-id="${esc(r.id)}"><div class="form-grid"><div class="field"><label>Status</label><select name="status">${["under_review","corroborated","validated","rejected"].map(s=>`<option value="${s}" ${s===r.status?"selected":""}>${statusLabel(s)}</option>`).join("")}</select></div><div class="field"><label>Internal reason</label><input name="reason" maxlength="1000" placeholder="Required when changing a validated report"></div><div class="field full"><button class="btn small" type="submit">Save review decision</button></div></div></form></article>`).join("");}
const TINYFISH_RAAHI_PLACES_PROMPT="Build a source-backed candidate dataset of public places within Delhi NCT for BEFIKR Safe Spots. Find police stations, hospitals or clinics, parks, public spaces/community centres/libraries, restaurants, and cafes. Include only real, currently identifiable places with a public source page and a precise street address and latitude/longitude supported by that source. Do not infer coordinates, operating hours, or safety ratings. Return columns exactly: name, category (police, hospital, park, public_space, restaurant, cafe), address, latitude, longitude, phone, source_url, source_date, dataset_id. Prefer official Delhi government, municipal, police, and hospital sources; otherwise use an identifiable public listing. Keep a direct source_url for every row. A human will review each source and coordinate before publication. This dataset is for place discovery only and must not label a location or route safe.";
const TINYFISH_RAAHI_RESEARCH_PROMPT="Research primary, public sources for pedestrian route-safety context datasets covering Delhi NCT that BEFIKR Raahi could lawfully reference. Look for street lighting, footpaths, crossings, pedestrian infrastructure, public transit access, road works, and aggregate/de-identified incident or safety-audit data. Do not collect personal data, infer safety from place popularity, or create a safety score. Return one row per dataset/source with columns exactly: dataset_name, indicator, publisher, source_url, geographic_coverage, spatial_precision, coverage_period, published_at, update_cadence, license_or_terms, access_method, limitations, usable_for_route_context (yes/no). Prefer official Delhi Government, Delhi Police, transport/municipal agencies, data.gov.in, and documented audit programs. Mark unavailable or unclear fields as unknown; cite the page that supports each row.";
function adminPlacesHtml(){
  const categories=[["police","Police station"],["hospital","Hospital"],["park","Park"],["public_space","Public space"],["restaurant","Restaurant"],["cafe","Cafe"],["support","Support organisation"]];
  const prompt=`<section class="admin-report tinyfish-source-card"><h3>TinyFish · Delhi place candidates</h3><p>Copy this prompt into TinyFish Datasets, build and export the CSV, then upload it below. Imported rows stay private until reviewed.</p><textarea id="tinyfish-raahi-prompt" rows="7" readonly aria-label="TinyFish dataset prompt">${esc(TINYFISH_RAAHI_PLACES_PROMPT)}</textarea><div class="actions"><button class="btn small secondary" type="button" data-action="tinyfish-copy-prompt">Copy TinyFish prompt</button><a class="btn small ghost" href="https://agent.tinyfish.chat/playground/datasets" target="_blank" rel="noopener noreferrer">Open TinyFish Datasets</a></div></section>`;
  const research=`<section class="admin-report tinyfish-source-card"><h3>TinyFish · Raahi source research</h3><p>Use this prompt in TinyResearch to identify official route-context datasets and their limits. It does not generate a safety score or feed route decisions automatically.</p><textarea id="tinyfish-raahi-research-prompt" rows="7" readonly aria-label="TinyFish Raahi research prompt">${esc(TINYFISH_RAAHI_RESEARCH_PROMPT)}</textarea><div class="actions"><button class="btn small secondary" type="button" data-action="tinyfish-copy-research-prompt">Copy research prompt</button><a class="btn small ghost" href="https://agent.tinyfish.chat/playground/research" target="_blank" rel="noopener noreferrer">Open TinyResearch</a></div></section>`;
  const importForm=`<form id="tinyfish-import-form" class="admin-report tinyfish-import-form"><strong>Import TinyFish CSV for review</strong><p>Required headers: name, category, address, latitude, longitude, source_url. Optional: phone, source_date, dataset_id.</p><label class="field">CSV file<input name="file" type="file" accept=".csv,text/csv" required></label><button class="btn small" type="submit">Import candidates</button><small>Up to 250 rows. They do not appear in Safe Spots until individually reviewed and approved.</small></form>`;
  const pending=state.placeCandidates||[];
  const candidates=pending.length?`<section class="admin-candidate-list"><h3>Pending TinyFish candidates <span class="tag amber">${pending.length}</span></h3>${pending.map(item=>`<article class="admin-report tinyfish-candidate"><div class="admin-report-meta">${esc(item.category.replaceAll("_"," "))} · imported ${new Date(item.created_at).toLocaleDateString()}</div><strong>${esc(item.name)}</strong><p>${esc(item.address)} · ${Number(item.latitude).toFixed(5)}, ${Number(item.longitude).toFixed(5)}</p>${item.phone?`<p>${esc(item.phone)}</p>`:""}<p>Source: <a href="${esc(item.source_url)}" target="_blank" rel="noopener noreferrer">${esc(item.source_url)}</a>${item.source_date?` · source date ${esc(item.source_date)}`:""}${item.dataset_id?` · dataset ${esc(item.dataset_id)}`:""}</p><div class="actions"><button class="btn small" type="button" data-action="tinyfish-candidate-review" data-id="${esc(item.id)}" data-decision="approve">Review and approve</button><button class="btn small secondary" type="button" data-action="tinyfish-candidate-review" data-id="${esc(item.id)}" data-decision="reject">Reject</button></div></article>`).join("")}</section>`:`<div class="empty"><strong>No pending TinyFish candidates.</strong>Imported rows will appear here for review before they can show in Safe Spots.</div>`;
  const form=`<form id="place-admin-form" class="form-grid"><div class="field"><label>Name</label><input name="name" required maxlength="120"></div><div class="field"><label>Category</label><select name="category">${categories.map(([id,label])=>`<option value="${id}">${label}</option>`).join("")}</select></div><div class="field"><label>Address</label><input name="address" required maxlength="240"></div><div class="field"><label>Phone · optional</label><input name="phone" maxlength="32"></div><div class="field"><label>Latitude</label><input name="latitude" type="number" step="any" required></div><div class="field"><label>Longitude</label><input name="longitude" type="number" step="any" required></div><div class="field"><label>Source / verification reference</label><input name="source" required maxlength="200"></div><div class="field"><label>Source page · optional</label><input name="source_url" type="url" maxlength="1000"></div><div class="field"><label>Verification date</label><input name="verified_at" type="date" required></div><div class="field full actions"><button class="btn" type="submit">Add verified listing</button></div></form>`;
  const places=state.places?.length?state.places.map(place=>`<details class="admin-report"><summary><strong>${esc(place.name)}</strong> · ${place.active?"Active":"Inactive"}</summary><form class="place-edit-form" data-id="${esc(place.id)}" style="margin-top:14px"><div class="form-grid"><div class="field"><label>Name</label><input name="name" value="${esc(place.name)}" required maxlength="120"></div><div class="field"><label>Category</label><select name="category">${categories.map(([id,label])=>`<option value="${id}" ${place.category===id?"selected":""}>${label}</option>`).join("")}</select></div><div class="field"><label>Address</label><input name="address" value="${esc(place.address)}" required maxlength="240"></div><div class="field"><label>Phone</label><input name="phone" value="${esc(place.phone||"")}" maxlength="32"></div><div class="field"><label>Latitude</label><input name="latitude" type="number" step="any" value="${esc(place.latitude)}" required></div><div class="field"><label>Longitude</label><input name="longitude" type="number" step="any" value="${esc(place.longitude)}" required></div><div class="field"><label>Source</label><input name="source" value="${esc(place.source)}" required maxlength="200"></div><div class="field"><label>Source page · optional</label><input name="source_url" type="url" value="${esc(place.source_url||"")}" maxlength="1000"></div><div class="field"><label>Verification date</label><input name="verified_at" type="date" value="${esc(String(place.verified_at).slice(0,10))}" required></div><input type="hidden" name="active" value="${Boolean(place.active)}"><div class="field full actions"><button class="btn small" type="submit">Save listing</button><button class="btn small secondary" type="button" data-action="place-toggle" data-id="${esc(place.id)}">${place.active?"Deactivate listing":"Reactivate listing"}</button></div></div></form><p class="admin-report-meta">Verified ${esc(place.verified_at)} · source ${esc(place.source)}${place.source_url?` · <a href="${esc(place.source_url)}" target="_blank" rel="noopener noreferrer">Source page</a>`:""}</p></details>`).join(""):`<div class="empty"><strong>No Safe Spot listings.</strong>Add a listing only after checking its source and details.</div>`;
  return `${prompt}${research}${importForm}<section class="tinyfish-review-note"><strong>Review each candidate before approval.</strong> Check that the source supports the place name, category, and coordinates. Approval adds a place listing; it does not certify that the place or its surrounding route is safe.</section>${candidates}<div class="divider"></div>${form}<div class="divider"></div>${places}`;
}
function parseCsv(text){
  const rows=[];let row=[],cell="",quoted=false;
  for(let index=0;index<text.length;index++){
    const character=text[index];
    if(quoted){if(character==='"'&&text[index+1]==='"'){cell+='"';index++;}else if(character==='"')quoted=false;else cell+=character;continue;}
    if(character==='"'){quoted=true;continue;}
    if(character===","){row.push(cell);cell="";continue;}
    if(character==="\n"){row.push(cell);rows.push(row);row=[];cell="";continue;}
    if(character!=="\r")cell+=character;
  }
  if(quoted)throw new Error("The CSV contains an unclosed quoted field.");
  if(cell.length||row.length){row.push(cell);rows.push(row);}
  const populatedRows=rows.filter(values=>values.some(value=>value.trim()));
  if(populatedRows.length<2)throw new Error("The CSV needs a header row and at least one data row.");
  const headers=populatedRows.shift().map(value=>value.trim().toLowerCase().replace(/[\s-]+/g,"_").replace(/[^a-z0-9_]/g,""));
  return populatedRows.map(values=>Object.fromEntries(headers.map((header,index)=>[header,(values[index]||"").trim()])));
}

function render(){
  if(state.page==="auth"||(!state.user&&!state.guestDemo))return renderAuth();
  switch(state.page){
    case "map": return renderMap();
    case "map-picker": return renderMapPicker();
    case "raahi": return renderRaahi();
    case "raaz": return renderRaaz();
    case "baat-banao": return renderBaat();
    case "backup": return renderBackup();
    case "safe-spot": return renderSafeSpot();
    case "settings": return renderSettings();
    case "admin": return renderAdmin();
    default: return renderHome();
  }
}

async function loadPageData(page){
  try{
    if(page==="raahi"&&!state.raahiDemoCatalog)await loadRaahiDemoCatalog();
    if(page==="raaz"){state.reports=await api("/reports");}
    if(page==="backup"){
      const [contacts,sosEvents]=await Promise.all([api("/contacts"),api("/sos")]);state.contacts=contacts;state.sosEvents=sosEvents;
      const trackingId=localStorage.getItem("befikr-tracking-id");
      if(trackingId){try{state.tracking=await api(`/tracking/${trackingId}`);if(state.tracking.status!=="active"){state.tracking=null;localStorage.removeItem("befikr-tracking-id");}}catch{state.tracking=null;localStorage.removeItem("befikr-tracking-id");}}
      const journeyId=localStorage.getItem("befikr-journey-id");
      if(journeyId){try{state.journey=await api(`/checkins/${journeyId}`);if(!["active","needs_attention"].includes(state.journey.status)){state.journey=null;localStorage.removeItem("befikr-journey-id");}else scheduleJourneyTimers();}catch{state.journey=null;localStorage.removeItem("befikr-journey-id");}}
    }
    if(page==="baat-banao"){
      try{
        const response=await api("/voice/scripts");
        state.scripts=(response?.scripts&&response.scripts.length?response.scripts:FALLBACK_SCRIPTS).map(prepareBaatScriptAudio);
      }catch{
        state.scripts=FALLBACK_SCRIPTS.map(prepareBaatScriptAudio);
      }
      if(!state.selectedScript||!state.scripts.some(s=>s.id===state.selectedScript))state.selectedScript=state.scripts[0]?.id;
    }
    if(page==="admin"){const [dashboard,reports]=await Promise.all([api("/admin/dashboard"),api("/admin/reports")]);state.dashboard=dashboard;state.adminReports=reports;if(state.adminTab==="places"){[state.places,state.placeCandidates]=await Promise.all([api("/admin/places"),api("/admin/place-candidates")]);}}
  }catch(e){toast(e.message);if(page==="admin"&&e.message.includes("Administrator")){state.page="home";}}
  render();
}
function go(page){
  cancelRaahiPlaceSearch();
  closeRaazPreview();
  if(state.page==="baat-banao"&&page!=="baat-banao"){stopIncomingRingtone();stopBaatAudio();}
  if(page==="profile")page=state.user?"settings":"auth";
  if(page==="auth")state.guestDemo=false;
  if(page==="home"&&!state.user)state.guestDemo=true;
  if(state.guestDemo&&!state.user&&!(["home","map","baat-banao","auth"].includes(page))){state.guestDemo=false;state.page="auth";renderAuth();toast("Sign in or create an account to use this module.");return;}
  if(page==="admin"&&!(["admin","moderator"].includes(state.user?.role)))return toast("Administrator access is restricted.");
  state.page=page;render();loadPageData(page);
}
function getOfflineReports(){
  const reports=readStoredJson("befikr-report-queue",[]);
  return Array.isArray(reports)?reports:[];
}
function saveOfflineReports(items){localStorage.setItem("befikr-report-queue",JSON.stringify(items));}
async function syncOfflineReports(){const queue=getOfflineReports();if(!queue.length)return toast("There are no locally saved reports.");let sent=0;const remaining=[];for(const item of queue){try{await api("/reports",{method:"POST",body:item});sent++;}catch(e){remaining.push(item);}}saveOfflineReports(remaining);await loadPageData("raaz");toast(sent?`${sent} report${sent===1?"":"s"} submitted; ${remaining.length} remain on this device.`:"Reports are still not submitted. Check your connection and retry.");}
function formData(form){const data=new FormData(form);const object={};for(const [key,value] of data.entries()){if(key==="recipient_ids"){object.recipient_ids=object.recipient_ids||[];object.recipient_ids.push(value);}else object[key]=value;}return object;}
function locationErrorMessage(code){
  switch(code){
    case "insecure": return "Open BEFIKR on HTTPS or localhost to use device location.";
    case "unsupported": return "Location is unavailable in this browser. Try opening BEFIKR in Chrome or Edge.";
    case 1: return "Location access is blocked. Allow Location for BEFIKR in your browser and check your device’s location settings.";
    case 3: return "The location request timed out. If you’re using the built-in browser, try opening BEFIKR in Chrome or Edge.";
    default: return "Your device couldn’t determine its location. Check your location settings or try Chrome or Edge.";
  }
}

function locationRequestError(code){
  const error=new Error(locationErrorMessage(code));
  error.locationCode=code;
  return error;
}

function requestDeviceLocation({timeout=15000,maximumAge=30000,deadline,enableHighAccuracy=false}={}){
  if(window.isSecureContext===false)return Promise.reject(locationRequestError("insecure"));
  if(!navigator.geolocation)return Promise.reject(locationRequestError("unsupported"));

  return new Promise((resolve,reject)=>{
    const fail=code=>{
      clearTimeout(timer);
      reject(locationRequestError(code));
    };
    const timer=deadline?setTimeout(()=>fail(3),deadline):null;
    try{
      navigator.geolocation.getCurrentPosition(({coords})=>{
        clearTimeout(timer);
        const {latitude,longitude}=coords;
        if(!Number.isFinite(latitude)||!Number.isFinite(longitude))return fail(2);
        resolve({latitude,longitude});
      },error=>fail(error.code),{enableHighAccuracy,timeout,maximumAge});
    }catch(error){
      fail(error.name==="SecurityError"?1:2);
    }
  });
}

async function geolocate(success,button){
  if(button?.disabled)return;
  const status=button?.closest(".actions, .map-picker-actions, .spot-search-actions, .raaz-location-actions")?.nextElementSibling;
  const feedback=status?.matches("[data-location-feedback]")?status:null;
  const show=message=>{
    if(feedback)feedback.textContent=message;
    else toast(message);
  };
  if(button)button.disabled=true;
  show("Finding your location…");
  try{
    let position;
    try{
      position=await requestDeviceLocation({timeout:8000,deadline:12000});
    }catch(error){
      if(![2,3].includes(error.locationCode)||(button&&!button.isConnected))throw error;
      show("Trying again with precise location…");
      position=await requestDeviceLocation({timeout:18000,deadline:22000,maximumAge:0,enableHighAccuracy:true});
    }
    if(button&&!button.isConnected)return;
    if(feedback)show("Location found.");
    const {latitude,longitude}=position;
    await success(latitude,longitude);
  }catch(error){
    if(!button||button.isConnected)show(error.message);
  }finally{
    if(button)button.disabled=false;
  }
}
function requestPlacesLocation(button){
  const form=document.getElementById("places-form");
  if(!form)return toast("Open Safe Spots to choose a location.");
  geolocate((latitude,longitude)=>{
    if(state.page!=="safe-spot"||!form.isConnected)return;
    state.placeQuery=form.elements.query.value.trim();
    openMapPicker("places",[latitude,longitude]);
  },button);
}
async function searchNearbyPlaces(){
  if(!state.placeSearch)return toast("Choose a point or use your current location first.");
  state.placeSearchController?.abort();
  const controller=new AbortController();
  state.placeSearchController=controller;
  const body={...state.placeSearch,radius_km:5,source:"csv"};
  if(state.safeSpotCategory)body.category=state.safeSpotCategory;
  state.places=[];
  state.placesMeta=null;
  state.placesLoading=true;
  state.selectedPlaceId=null;
  state.safeSpotView="results";
  renderSafeSpot();
  try{
    const result=await api("/places/nearby",{method:"POST",body,signal:controller.signal});
    if(controller.signal.aborted)return;
    if(!Array.isArray(result?.places))throw new Error("Nearby search returned an invalid response.");
    state.places=result.places;
    state.placesMeta=result;
  }catch(error){
    if(controller.signal.aborted)return;
    state.placesMeta={source_state:"places_unavailable",message:error.message||"Nearby search could not be completed."};
  }finally{
    if(state.placeSearchController===controller){
      state.placeSearchController=null;
      state.placesLoading=false;
      if(state.page==="safe-spot"&&state.safeSpotView==="results")renderSafeSpot();
    }
  }
}
function googleDirectionsUrl(origin,destination,points={}){
  const start=points.origin_latitude!=null&&points.origin_longitude!=null?`${points.origin_latitude},${points.origin_longitude}`:origin;
  const end=points.destination_latitude!=null&&points.destination_longitude!=null?`${points.destination_latitude},${points.destination_longitude}`:destination;
  const params=new URLSearchParams({api:"1",origin:start,destination:end,travelmode:"walking"});
  if(points.origin_place_id)params.set("origin_place_id",points.origin_place_id);
  if(points.destination_place_id)params.set("destination_place_id",points.destination_place_id);
  return `https://www.google.com/maps/dir/?${params}`;
}
function googlePlaceUrl(place){
  const params=new URLSearchParams({api:"1",query:`${place.name||"Place"} ${place.address||`${place.latitude},${place.longitude}`}`});
  if(place.google_place_id)params.set("query_place_id",place.google_place_id);
  return `https://www.google.com/maps/search/?${params}`;
}
async function createSosEvent(){
  if(state.sosLocationPending)return;
  const attemptId=++state.sosAttemptId;
  const initialEvent={status:"created",delivery_state:state.user?"saving":"local_only",message:state.user?"Saving this SOS event. Calls and message options are available now.":"SOS actions are available on this device. No account event was saved."};
  state.sos=initialEvent;
  if(!state.user)state.guestDemo=true;
  state.page="backup";
  void refreshSosLocation(attemptId,{dispatch:true});
  toast("SOS actions are ready. Call 112 or a contact now; location and message options are preparing.");
  if(!state.user)return;
  try{
    const savedEvent=await api("/sos",{method:"POST",body:{}});
    if(state.sosAttemptId!==attemptId)return;
    state.sos=savedEvent;
    if(state.sosLocation)void saveSosLocation(attemptId,savedEvent.id,state.sosLocation);
    await loadPageData("backup");
  }catch{
    if(state.sosAttemptId!==attemptId)return;
    state.sos={...initialEvent,delivery_state:"local_only",message:"SOS event could not be saved to the BEFIKR server. Call and message options remain available on this device."};
    try{state.contacts=await api("/contacts");}catch{}
    if(state.page==="backup")renderBackup();
  }
}
async function refreshSosLocation(attemptId,{dispatch=false}={}){
  if(state.sosLocationPending||state.sos?.status!=="created")return;
  state.sosLocation=null;
  state.sosLocationError="";
  state.sosLocationPending=true;
  const options=dispatch&&nativeAndroidAvailable()
    ?{timeout:8500,deadline:9000}
    :{timeout:15000,deadline:20000,maximumAge:dispatch?30000:0};
  const request=requestDeviceLocation(options);
  if(state.page==="backup")renderBackup();

  let location=null;
  let errorMessage="";
  try{location=await request;}catch(error){errorMessage=error.message;}
  if(state.sosAttemptId!==attemptId)return;
  state.sosLocation=location;
  state.sosLocationError=errorMessage;
  state.sosLocationPending=false;
  if(state.page==="backup")renderBackup();
  if(dispatch&&nativeAndroidAvailable())void dispatchNativeSos(attemptId,location);
  if(location&&state.user&&state.sos?.id)void saveSosLocation(attemptId,state.sos.id,location);
}

async function saveSosLocation(attemptId,eventId,location){
  try{
    const updated=await api(`/sos/${eventId}/location`,{method:"PATCH",body:location});
    if(state.sosAttemptId===attemptId&&state.sos?.id===eventId)state.sos={...state.sos,...updated};
  }catch{}
}

async function dispatchNativeSos(attemptId,location){
  if(!nativeAndroidAvailable()||attemptId!==state.sosAttemptId||state.nativeSosDispatchedAttempt===attemptId)return;
  state.nativeSosDispatchedAttempt=attemptId;
  let contacts=state.user?[...state.contacts]:[];
  if(state.user){try{contacts=await api("/contacts");state.contacts=contacts;}catch{}}
  if(attemptId!==state.sosAttemptId)return;
  const mapsUrl=location?`https://maps.google.com/?q=${Number(location.latitude).toFixed(6)},${Number(location.longitude).toFixed(6)}`:"";
  const message=`SOS!!- ${mapsUrl||"Current location unavailable"}`;
  try{window.BefikrAndroid.dispatchSos(JSON.stringify(contacts),message,mapsUrl);}
  catch{toast("Android could not start SOS actions. Open the 112 dialer and use the message options.");}
}
function scheduleJourneyTimers(){
  clearTimeout(state.journeyTimer);clearTimeout(state.journeyGraceTimer);
  if(!state.journey||state.journey.status!=="active")return;
  const due=new Date(state.journey.next_due_at).getTime();
  const graceMs=(Number(state.journey.grace_minutes)||10)*60000;
  state.journeyTimer=setTimeout(()=>{
    toast("Tap Me check-in is due. Open Backup and choose ‘I’m safe’ or end the journey.");
    state.journeyGraceTimer=setTimeout(async()=>{
      try{state.journey=await api(`/checkins/${state.journey.id}`);if(state.journey.status==="needs_attention")toast("Tap Me is marked ‘needs attention’. No contacts were notified.");if(state.page==="backup")render();}
      catch(error){toast(error.message);}
    },Math.max(0,due+graceMs-Date.now()));
  },Math.max(0,due-Date.now()));
}
function baatCallTurns(script){
  if(Array.isArray(script?.dialogue)&&script.dialogue.length)return [...script.dialogue,...(script.loop_turns||[])];
  return (script?.lines||[]).map(text=>({speaker:"caller",text}));
}
function baatTurnDisplayText(script,index){
  const turn=baatCallTurns(script)[index];
  if(turn?.transcript_pending)return turn.speaker==="user"?"Your turn. Reply when you're ready.":"Transcript will be added soon.";
  if(turn)return script?.language==="Hindi"&&state.hindiTranscriptStyle==="hinglish"?(turn.hinglish||turn.text||""):(turn.text||"");
  if(script?.language==="Hindi"&&state.hindiTranscriptStyle==="hinglish")return script.hinglish_lines?.[index]||script.lines?.[index]||"";
  return script?.lines?.[index]||"";
}
function baatTurnSpeaker(script,index,callerLabel){
  const turn=baatCallTurns(script)[index],speaker=turn?.speaker;
  if(speaker==="user")return script?.language==="Hindi"?(state.hindiTranscriptStyle==="hinglish"?"Aap":"आप"):"You";
  if(turn?.source_label)return script?.language==="Hindi"&&state.hindiTranscriptStyle==="hinglish"?(turn.speaker_label_hinglish||callerLabel):turn.source_label;
  if(speaker==="mother")return script?.language==="English"?"Mom":state.hindiTranscriptStyle==="hinglish"?"Maa":"माँ";
  if(speaker==="daughter")return script?.language==="English"?"You":state.hindiTranscriptStyle==="hinglish"?"Beti":"बेटी";
  return callerLabel;
}
function stopBaatAudio(){
  const audio=state.audioPlayer;
  if(audio){audio.onended=null;audio.onerror=null;audio.pause();try{audio.currentTime=0;}catch{}}
  state.audioPlayer=null;
}
function stopIncomingRingtone(){
  const player=state.ringtonePlayer;state.ringtonePlayer=null;
  if(player){player.pause();try{player.currentTime=0;}catch{}}
}
function startIncomingRingtone(){
  stopIncomingRingtone();
  const player=new Audio("/assets/baat-banao/incoming-ringtone.mp3");
  player.loop=true;player.preload="auto";player.volume=0.8;state.ringtonePlayer=player;
  player.play().catch(()=>{if(state.ringtonePlayer===player){state.ringtonePlayer=null;toast("Could not play the incoming ringtone. You can still answer the call.");}});
}
function speakLine(index){
  const script=state.scripts.find(item=>item.id===state.selectedScript)||state.scripts.find(item=>item.language===state.selectedLanguage)||state.scripts[0];
  if(!script)return toast("Choose a call script first.");
  const turns=baatCallTurns(script);
  if(index>=turns.length){if(script.loop_turns?.length)index=script.dialogue.length;else{state.callState="ended";state.nextLineAvailable=false;state.speechPaused=false;stopBaatAudio();render();return toast("Simulated call ended.");}}
  state.speechLine=index;state.speechPaused=false;state.nextLineAvailable=false;stopBaatAudio();
  const turn=turns[index];
  if(["daughter","user"].includes(turn.speaker)){state.nextLineAvailable=true;render();return;}
  render();
  if(turn.audio){
    const player=new Audio(turn.audio);state.audioPlayer=player;let fallbackStarted=false;
    const finishTurn=()=>{if(state.callState==="active"&&state.audioPlayer===player){state.audioPlayer=null;state.nextLineAvailable=true;state.speechPaused=false;render();}};
    const useFallback=()=>{if(fallbackStarted||state.audioPlayer!==player||state.callState!=="active")return;fallbackStarted=true;state.audioPlayer=null;state.nextLineAvailable=true;state.speechPaused=false;render();toast("This recording could not be played. Replay it or continue when ready.");};
    player.onended=finishTurn;player.onerror=useFallback;
    player.play().catch(useFallback);return;
  }
  state.nextLineAvailable=true;render();toast("No MP3 is attached to this line yet. It stays transcript-only; no other voice will play.");
}
function stopGeolocation(){if(state.watchId!=null){navigator.geolocation.clearWatch(state.watchId);state.watchId=null;}}

document.addEventListener("click",async event=>{
  const button=event.target.closest("[data-action]");if(!button)return;
  const action=button.dataset.action;
  try{
    if(state.raazSubmitting&&action.startsWith("raaz-"))return toast("Your report is being submitted. Please wait.");
    if(action==="raaz-map-pick"){cancelRaahiPlaceSearch();openMapPicker("raaz");return;}
    if(action==="raaz-evidence-preview"){const item=state.raazEvidence.find(item=>item.id===button.dataset.id);if(item)showRaazPreview(item.previewUrl,item.file.type,item.file.name);return;}
    if(action==="raaz-evidence-open"){await openSavedRaazEvidence(button.dataset.id);return;}
    if(action==="raaz-evidence-close"){closeRaazPreview();return;}
    if(action==="raaz-evidence-remove"){
      const item=state.raazEvidence.find(item=>item.id===button.dataset.id);if(!item)return;
      if(item.uploaded)await api(`/evidence/${item.uploaded.id}`,{method:"DELETE"});
      URL.revokeObjectURL(item.previewUrl);state.raazEvidence=state.raazEvidence.filter(other=>other!==item);renderRaaz();return;
    }
    if(action==="raahi-demo-load"){await loadRaahiDemoCatalog();if(state.page==="raahi")renderRaahi();return;}
    if(action==="raahi-select-place"){await selectRaahiPlace(Number(button.dataset.index));return;}
    if(action==="raahi-place-preview"){await showRaahiPlacePreview(button.dataset.field);return;}
    if(action==="raaz-tab"){const screen=button.dataset.screen==="reports"?"reports":"wizard";state.raazScreen=screen;state.raazSelectedReportId=null;if(screen==="wizard"&&state.raazStep===5){state.raazStep=1;resetRaazDraft();state.raazSubmittedReport=null;}renderRaaz();return;}
    if(action==="raaz-category"){state.raazDraft.category=button.dataset.category||"";renderRaaz();return;}
    if(action==="raaz-next"){if(state.raazStep===1&&!state.raazDraft.category)return toast("Choose a category to continue.");if(state.raazStep===2&&state.raazDraft.description.trim().length<10)return toast("Add at least 10 characters so the report can be reviewed.");if(state.raazStep===3&&(state.raazDraft.latitude==="")!==(state.raazDraft.longitude===""))return toast("Add both coordinates, or leave both empty.");state.raazStep=Math.min(4,state.raazStep+1);renderRaaz();return;}
    if(action==="raaz-back"){state.raazStep=Math.max(1,state.raazStep-1);renderRaaz();return;}
    if(action==="raaz-edit-step"){state.raazStep=Math.max(1,Math.min(4,Number(button.dataset.step)||1));renderRaaz();return;}
    if(action==="raaz-location"){geolocate((lat,lon)=>{if(state.page!=="raaz"||state.raazStep!==3)return;state.raazDraft.latitude=lat.toFixed(5);state.raazDraft.longitude=lon.toFixed(5);state.raazDraft.location_label="Current location";state.raazDraft.location_place_id="";renderRaaz();toast("Current location added.");},button);return;}
    if(action==="raaz-clear-location"){state.raazDraft.latitude="";state.raazDraft.longitude="";state.raazDraft.location_label="";state.raazDraft.location_place_id="";state.raazLocationQuery="";renderRaaz();return;}
    if(action==="raaz-new-report"){state.raazScreen="wizard";state.raazStep=1;resetRaazDraft();state.raazSubmittedReport=null;state.raazSelectedReportId=null;renderRaaz();return;}
    if(action==="raaz-filter"){state.raazFilter=button.dataset.filter||"all";state.raazSelectedReportId=null;renderRaaz();return;}
    if(action==="raaz-report-detail"){state.raazSelectedReportId=button.dataset.id;renderRaaz();return;}
    if(action==="raaz-report-back"){state.raazSelectedReportId=null;renderRaaz();return;}
    if(action==="raaz-refresh-status"){const update=await api(`/reports/status/${button.dataset.id}`);state.reports=state.reports.map(item=>item.id===update.id?{...item,...update}:item);renderRaaz();toast("Report status refreshed from the review record.");return;}
    if(action==="home-sos"){
      if(state.sosPointerSeen){state.sosPointerSeen=false;if(state.sosHoldTriggered)state.sosHoldTriggered=false;return;}
      await createSosEvent();return;
    }
    if(action==="home-location"||action==="map"){go("map");return;}
    if(action==="map-locate"){geolocate((lat,lon)=>{state.deviceLocation={latitude:lat,longitude:lon};state.mapVisible=false;state.homeLocationKnown=true;renderMap();},button);return;}
    if(action==="map-load"){if(!state.deviceLocation)return toast("Choose your current location first.");state.mapVisible=true;renderMap();return;}
     if(action==="places-location"){requestPlacesLocation(button);return;}
     if(action==="places-map-pick"){
       const query=document.getElementById("places-form")?.elements.query;
       if(query)state.placeQuery=query.value.trim();
       openMapPicker("places");
       return;
     }
     if(action==="map-pick"){cancelRaahiPlaceSearch();openMapPicker(button.dataset.target||"raahi-origin");return;}
     if(action==="map-picker-back"){const page=state.mapPicker?.returnPage||"home";state.mapPicker=null;state.pinMap=null;state.page=page;render();return;}
     if(action==="map-picker-current"){geolocate((lat,lng)=>{setMapPickerCoordinates(lat,lng);if(state.pinMap?.type==="google"){const point={lat,lng};state.pinMap.map.setCenter(point);state.pinMap.marker.setPosition(point);}else if(state.pinMap?.type==="leaflet"){const point=[lat,lng];state.pinMap.map.setView(point,16);state.pinMap.marker.setLatLng(point);}},button);return;}
     if(action==="map-picker-confirm"){confirmMapPin();return;}
    if(action==="places-manual-search"){const form=document.getElementById("places-form");if(!form)return;const latitude=form.elements["latitude-manual"].value.trim(),longitude=form.elements["longitude-manual"].value.trim();if(!latitude||!longitude)return toast("Enter both latitude and longitude first.");form.elements.latitude.value=latitude;form.elements.longitude.value=longitude;form.requestSubmit();return;}
     if(action==="places-category"){
       state.safeSpotCategory=button.dataset.category||"";
       if(!state.placeSearch){
         state.placeSearch={latitude:28.6328,longitude:77.2197,radius_km:5};
       }
       state.safeSpotView="results";
       searchNearbyPlaces();
       return;
     }

    if(action==="places-retry"){searchNearbyPlaces();return;}
    if(action==="places-home"){state.safeSpotView="home";renderSafeSpot();return;}
    if(action==="places-results"){state.safeSpotView="results";renderSafeSpot();return;}
    if(action==="places-map"){state.safeSpotView="map";renderSafeSpot();return;}
    if(action==="place-open"){const place=state.places.find(item=>item.id===button.dataset.id);if(!place)return;state.selectedPlaceId=place.id;state.safeSpotView="detail";renderSafeSpot();await loadSpotRoute(place);return;}
     if(action==="place-directions"){
       const place=state.places.find(item=>item.id===button.dataset.id);
       if(!place)return toast("This listing is no longer available.");
       state.selectedPlaceId=place.id;state.safeSpotView="detail";
       await loadSpotRoute(place,true);return;
     }
     if(action==="place-save-google"){const place=state.places.find(item=>item.id===button.dataset.id);if(!place)return toast("This listing is no longer available.");window.open(googlePlaceUrl(place),"_blank","noopener,noreferrer");return;}
    if(action==="raahi-home"){state.raahiView="home";state.routeLoading=false;renderRaahi();return;}
    if(action==="raahi-results"){state.raahiView="results";renderRaahi();return;}
    if(action==="route-detail"){state.selectedRouteId=button.dataset.routeId;state.raahiView="details";renderRaahi();return;}
    if(action==="raahi-sort"){state.routeSort=button.dataset.sort==="fastest"?"fastest":"shortest";renderRaahi();return;}
    if(action==="raahi-scroll-recent"){document.getElementById("raahi-recent")?.scrollIntoView({behavior:"smooth",block:"start"});return;}
     if(action==="raahi-recent"){const trip=state.recentTrips[Number(button.dataset.index)];if(!trip)return;state.routeInput={...trip};state.raahiView="home";renderRaahi();requestAnimationFrame(()=>document.getElementById("route-form")?.requestSubmit());return;}
     if(action==="raahi-open-directions"){window.open(googleDirectionsUrl(state.routeInput.origin,state.routeInput.destination,state.routeInput),"_blank","noopener,noreferrer");return;}
     if(action==="raahi-start-journey"){const route=(state.alternatives?.routes||[]).find(item=>item.id===state.selectedRouteId);if(!route)return toast("Choose a route first.");state.raahiJourney={routeId:route.id,startedAt:new Date().toISOString()};state.raahiView="journey";window.open(googleDirectionsUrl(state.routeInput.origin,state.routeInput.destination,state.routeInput),"_blank","noopener,noreferrer");renderRaahi();return;}
     if(action==="raahi-reopen-directions"){window.open(googleDirectionsUrl(state.routeInput.origin,state.routeInput.destination,state.routeInput),"_blank","noopener,noreferrer");return;}
     if(action==="route-to-tapme"){const route=(state.alternatives?.routes||[]).find(item=>item.id===state.selectedRouteId);if(!route)return toast("Choose a route first.");saveTapMeRoute({...state.routeInput,route_id:route.id,route_label:route.label,distance_km:route.distance_km,minutes:route.minutes,risk_score:route.risk_score,provider:route.provider});state.page="backup";renderBackup();loadPageData("backup");return;}
    if(action==="raahi-arrived"){state.raahiView="arrived";state.raahiFeedback="";renderRaahi();return;}
    if(action==="raahi-feedback"){state.raahiFeedback=button.dataset.feedback;renderRaahi();return;}
    if(action==="raahi-journey-home"){state.raahiJourney=null;state.raahiFeedback="";state.raahiView="home";renderRaahi();return;}
     if(action==="external-route"){
       const form=document.getElementById("route-form");
       if(!form?.reportValidity())return;
       const {origin,destination}=readRaahiRouteForm(form);
       window.open(googleDirectionsUrl(origin,destination,state.routeInput),"_blank","noopener,noreferrer");
       return;
     }
     if(action==="tapme-open-raahi"||action==="tapme-edit-route"){if(state.tapmeRoute)state.routeInput={...state.tapmeRoute};state.page="raahi";state.raahiView="home";renderRaahi();loadPageData("raahi");return;}
     if(action==="checkin-start"){const route=state.tapmeRoute;if(!route)return toast("Choose a Raahi route first.");const plan=tapMePlan(route);const body={duration_minutes:plan.duration,destination:route.destination,grace_minutes:10,...plan.components};state.journey=await api("/checkins/start",{method:"POST",body});localStorage.setItem("befikr-journey-id",state.journey.id);scheduleJourneyTimers();renderBackup();toast(`Tap Me started with ${state.journey.total_checkins} route-based check-ins.`);return;}
     if(action==="checkin-dismiss"){state.journey=null;localStorage.removeItem("befikr-journey-id");renderBackup();return;}
    if(action==="tapme"){go("backup");setTimeout(()=>{const card=[...document.querySelectorAll(".card")].find(item=>item.querySelector("h3")?.textContent.includes("Tap Me"));card?.scrollIntoView({behavior:"smooth",block:"start"});},350);return;}
    if(action==="profile-settings"){const panel=document.getElementById("profile-app-settings");if(panel){panel.open=true;panel.scrollIntoView({behavior:"smooth",block:"center"});}return;}
    if(action==="home"||action==="raahi"||action==="raaz"||action==="backup"||action==="safe-spot"||action==="baat-banao"||action==="settings"||action==="admin"||action==="profile"){event.preventDefault();go(action);return;}
    if(action==="auth-switch"){state.authMode=state.authMode==="login"?"register":"login";render();return;}
    if(action==="login"){state.guestDemo=false;state.page="auth";renderAuth();return;}
    if(action==="guest-call"){state.guestDemo=true;state.page="baat-banao";state.callState="idle";render();return;}
    if(action==="route-status"){const result=await api("/routes/data-status");const target=document.getElementById("route-status-result");if(!target){toast(result.message);return;}target.innerHTML=`<div class="result-box warning"><div class="result-title">${esc(result.state)} safety data</div>${esc(result.message)}<p>Route geometry provider: ${esc(result.mapping_provider)}. Safety sources — Nirakshak: ${esc(result.nirakshak_state)}; Safetipin: ${esc(result.safetipin_state)}; data.gov.in: ${esc(result.data_gov_state)}; DDA GIS: ${esc(result.dda_state)}; Google Places: ${esc(result.google_places_state)}.</p><p><a href="https://data.gov.in" target="_blank" rel="noopener noreferrer">data.gov.in</a> · <a href="https://dda.gov.in/gis" target="_blank" rel="noopener noreferrer">DDA GIS</a> · <a href="https://developers.google.com/maps/documentation/places/web-service" target="_blank" rel="noopener noreferrer">Google Places</a> · <a href="https://osmnx.readthedocs.io/" target="_blank" rel="noopener noreferrer">OSMnx</a> · <a href="https://docs.mapbox.com/api/navigation/directions/" target="_blank" rel="noopener noreferrer">Mapbox Directions</a> · <a href="https://safetyscore.safetipin.com/projects" target="_blank" rel="noopener noreferrer">Safetipin projects</a></p>${result.source_url?`<p><a href="${esc(result.source_url)}" target="_blank" rel="noopener noreferrer">Delhi Transport Department report</a></p>`:""}</div>`;return;}
    if(action==="report-location"){geolocate((lat,lon)=>{document.getElementById("report-lat").value=lat.toFixed(4);document.getElementById("report-lon").value=lon.toFixed(4);toast("Approximate coordinates added. Review them before submitting.");});return;}
    if(action==="sync-reports"){await syncOfflineReports();return;}
    if(action==="caller"){stopIncomingRingtone();stopBaatAudio();state.callState="idle";state.nextLineAvailable=false;state.speechPaused=false;const scenario=state.scripts.find(item=>item.id===state.selectedScript)?.scenario||"checking-in";state.caller=button.dataset.caller;const matchingScript=state.scripts.find(item=>item.caller===state.caller&&item.language===state.selectedLanguage&&item.scenario===scenario)||state.scripts.find(item=>item.caller===state.caller&&item.language===state.selectedLanguage);if(matchingScript)state.selectedScript=matchingScript.id;render();return;}
    if(action==="script-language"){stopIncomingRingtone();stopBaatAudio();state.callState="idle";state.nextLineAvailable=false;state.speechPaused=false;const scenario=state.scripts.find(item=>item.id===state.selectedScript)?.scenario||"checking-in";state.selectedLanguage=button.dataset.language;const next=state.scripts.find(item=>item.caller===state.caller&&item.language===state.selectedLanguage&&item.scenario===scenario);if(next)state.selectedScript=next.id;render();return;}
    if(action==="hindi-transcript-style"){state.hindiTranscriptStyle=button.dataset.style==="hinglish"?"hinglish":"devanagari";render();return;}
    if(action==="call-start"){state.callState="ringing";state.speechLine=0;state.nextLineAvailable=false;state.speechPaused=false;render();startIncomingRingtone();return;}
    if(action==="call-answer"){if(state.callState==="ringing"){stopIncomingRingtone();state.callState="active";speakLine(0);}else if(state.callState==="active"&&state.nextLineAvailable){speakLine(state.speechLine+1);}return;}
    if(action==="call-decline"||action==="call-end"){stopIncomingRingtone();stopBaatAudio();state.callState="ended";state.nextLineAvailable=false;state.speechPaused=false;render();return;}
    if(action==="call-reset"){stopIncomingRingtone();stopBaatAudio();state.callState="idle";state.speechLine=0;state.nextLineAvailable=false;state.speechPaused=false;render();return;}
    if(action==="call-pause"){if(!state.audioPlayer)return toast("Pause is available only for a supplied MP3 recording.");if(state.audioPlayer.paused){state.audioPlayer.play().catch(()=>toast("Could not resume the recorded voice."));state.speechPaused=false;}else{state.audioPlayer.pause();state.speechPaused=true;}render();return;}
    if(action==="call-replay"){state.nextLineAvailable=false;speakLine(state.speechLine);return;}
    if(action==="contact-remove"){await api(`/contacts/${button.dataset.id}`,{method:"DELETE"});state.contacts=await api("/contacts");render();toast("Contact removed.");return;}
    if(action==="sos"){await createSosEvent();return;}
    if(action==="sos-retry-location"){await refreshSosLocation(state.sosAttemptId);return;}
    if(action==="android-sos-permissions"){if(!nativeAndroidAvailable())return toast("Android permissions are available in the installed BEFIKR app.");window.BefikrAndroid.requestSosPermissions();return;}
    if(action==="sos-whatsapp"){const location=state.sosLocation;const mapsUrl=location?`https://maps.google.com/?q=${Number(location.latitude).toFixed(6)},${Number(location.longitude).toFixed(6)}`:"";const message=`SOS!!- ${mapsUrl||"Current location unavailable"}`;if(nativeAndroidAvailable())window.BefikrAndroid.openWhatsApp(message);else window.open(`https://wa.me/?text=${encodeURIComponent(message)}`,"_blank","noopener,noreferrer");return;}
    if(action==="sos-copy"){const url=state.sosLocation?`https://maps.google.com/?q=${Number(state.sosLocation.latitude).toFixed(6)},${Number(state.sosLocation.longitude).toFixed(6)}`:"Current location unavailable";const message=`SOS!!- ${url}`;if(!navigator.clipboard?.writeText)return toast("Copy is unavailable here; use the SMS or WhatsApp draft.");await navigator.clipboard.writeText(message);toast("SOS message copied.");return;}
    if(action==="cancel-sos"&&!state.sos?.id){state.sosAttemptId++;state.sosLocationPending=false;state.sos=null;render();toast("Local SOS screen closed.");return;}
    if(action==="cancel-sos"){state.sosAttemptId++;state.sosLocationPending=false;state.sos=await api(`/sos/${state.sos.id}/cancel`,{method:"POST"});state.sosEvents=await api("/sos");render();toast("Emergency event cancelled in the development service.");return;}
    if(action==="track-stop"){await api(`/tracking/${state.tracking.id}/stop`,{method:"POST"});stopGeolocation();state.tracking=null;localStorage.removeItem("befikr-tracking-id");render();toast("Journey stopped; last stored location was deleted.");return;}
    if(action==="track-location"){geolocate(async(lat,lon)=>{try{await api(`/tracking/${state.tracking.id}/location`,{method:"POST",body:{latitude:lat,longitude:lon}});state.tracking.location_at=new Date().toISOString();render();toast("Last location saved to this account. It was not shared with contacts.");}catch(e){toast(e.message);}});return;}
    if(action==="checkin-safe"){state.journey=await api(`/checkins/${state.journey.id}/respond`,{method:"POST"});if(state.journey.status==="completed"){clearTimeout(state.journeyTimer);clearTimeout(state.journeyGraceTimer);localStorage.removeItem("befikr-journey-id");}else{state.journey=await api(`/checkins/${state.journey.id}`);scheduleJourneyTimers();}renderBackup();toast(state.journey.status==="completed"?"All planned Tap Me check-ins are complete.":"Check-in recorded. No one else was notified.");return;}
    if(action==="checkin-cancel"){await api(`/checkins/${state.journey.id}/cancel`,{method:"POST"});clearTimeout(state.journeyTimer);clearTimeout(state.journeyGraceTimer);state.journey=null;localStorage.removeItem("befikr-journey-id");render();toast("Tap Me journey ended.");return;}
    if(action==="admin-tab"){state.adminTab=button.dataset.tab;if(state.adminTab==="appeals")state.appeals=await api("/admin/appeals");if(state.adminTab==="places"){[state.places,state.placeCandidates]=await Promise.all([api("/admin/places"),api("/admin/place-candidates")]);}if(state.adminTab==="audit")state.audit=await api("/admin/audit-logs");if(state.adminTab==="reports")state.adminReports=await api("/admin/reports");render();return;}
    if(action==="tinyfish-copy-prompt"||action==="tinyfish-copy-research-prompt"){const prompt=document.getElementById(action==="tinyfish-copy-prompt"?"tinyfish-raahi-prompt":"tinyfish-raahi-research-prompt")?.value||"";try{await navigator.clipboard.writeText(prompt);toast("TinyFish prompt copied.");}catch{toast("Select and copy the TinyFish prompt from the text box.");}return;}
    if(action==="tinyfish-candidate-review"){const decision=button.dataset.decision;if(decision==="approve"&&!confirm("Review the linked source and coordinates before approval. This will add the listing to Safe Spots; it does not certify the place as safe. Approve this candidate?"))return;const result=await api(`/admin/place-candidates/${button.dataset.id}`,{method:"PATCH",body:{decision,notes:""}});[state.places,state.placeCandidates]=await Promise.all([api("/admin/places"),api("/admin/place-candidates")]);render();toast(result.message);return;}
    if(action==="appeal-review"){await api(`/admin/appeals/${button.dataset.id}?decision=${button.dataset.decision}`,{method:"PATCH"});state.appeals=await api("/admin/appeals");render();toast("Appeal status updated.");return;}
    if(action==="place-toggle"){const place=state.places.find(item=>item.id===button.dataset.id);if(!place)return;await api(`/admin/places/${place.id}`,{method:"PATCH",body:{name:place.name,category:place.category,address:place.address,latitude:place.latitude,longitude:place.longitude,phone:place.phone||"",source:place.source,source_url:place.source_url||"",verified_at:place.verified_at,active:!Boolean(place.active)}});state.places=await api("/admin/places");render();toast("Safe Spot listing status updated.");return;}
    if(action==="export-data"){const data=await api("/profile/export");data.unsent_local_report_drafts=getOfflineReports();const blob=new Blob([JSON.stringify(data,null,2)],{type:"application/json"});const link=document.createElement("a");link.href=URL.createObjectURL(blob);link.download="befikr-my-data.json";link.click();URL.revokeObjectURL(link.href);return;}
    if(action==="logout"){if(state.raazSubmitting)return toast("Please wait for your report to finish submitting.");resetRaazDraft();closeRaazPreview();state.reports=[];state.raazSubmittedReport=null;state.raazScreen="wizard";state.raazStep=1;try{await api("/auth/logout",{method:"POST"});}catch{}localStorage.removeItem("befikr-token");localStorage.removeItem("befikr-user");state.token=null;state.user=null;state.guestDemo=true;state.page="home";render();return;}
    if(action==="delete-account"){if(!confirm("Delete your BEFIKR account and all associated data from this development database? This cannot be undone."))return;await api("/profile",{method:"DELETE"});localStorage.removeItem("befikr-token");localStorage.removeItem("befikr-user");saveOfflineReports([]);state.token=null;state.user=null;state.guestDemo=true;state.page="home";render();toast("Account and associated data deleted.");return;}
  }catch(error){toast(error.message||"Something went wrong. Please try again.");}
});

document.addEventListener("pointerdown",event=>{
  const button=event.target.closest('[data-action="home-sos"]');if(!button)return;
  state.sosPointerSeen=true;state.sosHoldTriggered=false;button.classList.add("is-holding");
  try{button.setPointerCapture(event.pointerId);}catch{}
  clearTimeout(state.sosHoldTimer);
  state.sosHoldTimer=setTimeout(()=>{state.sosHoldTriggered=true;button.classList.remove("is-holding");createSosEvent();},900);
});
document.addEventListener("mousedown",event=>{
  if(event.target.closest(".raahi-place-option"))event.preventDefault();
});
document.addEventListener("pointerup",event=>{
  const button=event.target.closest('[data-action="home-sos"]');if(!button)return;
  clearTimeout(state.sosHoldTimer);button.classList.remove("is-holding");
  if(!state.sosHoldTriggered)toast("Hold SOS briefly to save the event and open call/text options. Nothing is sent automatically.");
});
document.addEventListener("pointercancel",event=>{
  if(!event.target.closest('[data-action="home-sos"]'))return;
  clearTimeout(state.sosHoldTimer);state.sosPointerSeen=false;state.sosHoldTriggered=false;
  document.querySelector('[data-action="home-sos"]')?.classList.remove("is-holding");
});

function readRaahiRouteForm(form){
  for(const field of ["origin","destination"]){
    const value=form.elements[field].value.trim();
    if(value!==String(state.routeInput[field]||"").trim()){
      state.routeInput[`${field}_latitude`]=null;
      state.routeInput[`${field}_longitude`]=null;
      state.routeInput[`${field}_place_id`]=null;
      state.routeInput[`${field}_address`]=null;
    }
    state.routeInput[field]=value;
  }
  return state.routeInput;
}

document.addEventListener("input",event=>{
  const field=event.target;
  if(field.id==="raaz-location-search"){state.raazLocationQuery=field.value;startNamedPlaceSearch(field);return;}
  if(field.form?.id==="route-form"&&["origin","destination"].includes(field.name)){
    onRaahiPlaceInput(field);
    return;
  }
  if(field.form?.id!=="report-form"||!field.name)return;
  if(Object.prototype.hasOwnProperty.call(state.raazDraft,field.name))state.raazDraft[field.name]=field.value;
  if(["raaz-latitude","raaz-longitude"].includes(field.id)){state.raazDraft.location_label="Selected coordinates";state.raazDraft.location_place_id="";}
  if(field.id==="raaz-description"){
    const counter=document.querySelector(".raaz-field-caption span:last-child");
    if(counter)counter.textContent=`${field.value.length}/2000`;
  }
});
document.addEventListener("pointerdown",event=>{
  const search=state.raahiPlaceSearch;
  if(search&&!event.target.closest(".raahi-stop-field"))cancelRaahiPlaceSearch();
});
document.addEventListener("focusin",event=>{
  const search=state.raahiPlaceSearch;
  if(search&&event.target!==search.input)cancelRaahiPlaceSearch();
});
document.addEventListener("keydown",event=>{
  const search=state.raahiPlaceSearch;
  if(!search||event.target!==search.input)return;
  if(event.key==="Escape"){
    cancelRaahiPlaceSearch();
    return;
  }
  if(!search.items.length)return;
  if(event.key==="ArrowDown"||event.key==="ArrowUp"){
    event.preventDefault();
    const step=event.key==="ArrowDown"?1:-1;
    search.active=search.active<0&&step<0?search.items.length-1:(search.active+step+search.items.length)%search.items.length;
    updateRaahiPlacePanel(search);
  }else if(event.key==="Enter"&&search.active>=0){
    event.preventDefault();
    selectRaahiPlace(search.active);
  }
});
document.addEventListener("change",event=>{
  if(event.target.id==="raaz-evidence-files"){addRaazEvidence([...event.target.files]);return;}
  if(event.target.closest("#raahi-demo-form")){
    const form=event.target.closest("form"),values=formData(form);
    state.raahiDemoPairId=values.pair;state.raahiDemoTimeBand=values.time_band;
    state.raahiDemoRequestId++;state.raahiDemoLoading=false;state.raahiDemoResult=null;state.raahiDemoError="";
    document.getElementById("raahi-demo-result").textContent="Select Show demo colour to preview this journey.";
    const button=form.querySelector('button[type="submit"]');button.disabled=false;button.textContent="Show demo colour";
    return;
  }
  if(event.target.id!=="script-select")return;
  const next=state.scripts.find(item=>item.id===event.target.value&&item.caller===state.caller&&item.language===state.selectedLanguage);
  if(!next)return;
  stopIncomingRingtone();stopBaatAudio();state.selectedScript=next.id;state.callState="idle";state.speechLine=0;state.nextLineAvailable=false;state.speechPaused=false;

  render();
});

document.addEventListener("keydown",event=>{if(event.key==="Escape")closeRaazPreview();});

document.addEventListener("submit",async event=>{
  const form=event.target;const id=form.id;
  try{
    if(id==="raahi-demo-form"){event.preventDefault();await previewRaahiDemo(form);return;}
    if(id==="auth-form"){
      event.preventDefault();const data=formData(form);const route=state.authMode==="login"?"/auth/login":"/auth/register";if(state.authMode==="register")data.name=data.name.trim();data.email=data.email.trim().toLowerCase();const result=await api(route,{method:"POST",body:data});state.token=result.access_token;state.user=result.user;state.guestDemo=false;localStorage.setItem("befikr-token",state.token);localStorage.setItem("befikr-user",JSON.stringify(state.user));state.page="home";render();toast("Signed in. You are in the BEFIKR development service.");return;
    }
    if(id==="route-form"){
      event.preventDefault();
      cancelRaahiPlaceSearch();
      readRaahiRouteForm(form);
      state.alternatives=null;state.selectedRouteId=null;state.routeError="";state.routeLoading=true;state.raahiView="results";renderRaahi();
      try{const useGoogle=await ensureGoogleMaps();const result=await api("/routes/alternatives",{method:"POST",body:{...state.routeInput,use_google_maps:useGoogle}});state.alternatives=result;state.routeLoading=false;const ordered=[...(result.routes||[])].filter(route=>route.geometry?.coordinates?.length>1).sort((a,b)=>state.routeSort==="fastest"?Number(a.minutes)-Number(b.minutes):Number(a.distance_km)-Number(b.distance_km));state.selectedRouteId=ordered[0]?.id||null;state.recentTrips=[{...state.routeInput},...state.recentTrips.filter(item=>item.origin!==state.routeInput.origin||item.destination!==state.routeInput.destination)].slice(0,8);renderRaahi();}
      catch(error){state.routeLoading=false;state.routeError=error.message||"The route request could not be completed.";renderRaahi();}
      return;
    }
    if(id==="risk-form"){
      event.preventDefault();const raw=formData(form),inputs={};for(const key of ["incident","freshness","population","lighting","time_of_day","historical","isolation"])inputs[key]=raw[key]===""?null:Number(raw[key]);const result=await api("/routes/risk",{method:"POST",body:{segments:[{...inputs,length_km:Number(raw.length_km),latitude:raw.latitude===""?null:Number(raw.latitude),longitude:raw.longitude===""?null:Number(raw.longitude)}]}});const r=result.route;const cls=r.classification==="lower_reported_risk"?"green":r.classification==="elevated_reported_risk"?"red":"amber";document.getElementById("risk-result").innerHTML=`<div class="result-box ${cls===`amber`?"warning":""}"><div class="result-title">${r.score==null?"Insufficient information":`Prototype score ${r.score} / 100`}</div><span class="tag ${cls}">${esc(statusLabel(r.classification))}</span><p>Confidence ${r.confidence}% · model coverage ${Math.round((result.segments[0].coverage||0)*100)}%${result.segments[0].aggregated_validated_reports?" · includes privacy-filtered validated report signal":""}</p><ul>${r.explanation.map(x=>`<li>${esc(x)}</li>`).join("")}</ul></div>`;return;
    }
    if(id==="report-form"){
      event.preventDefault();
      if(state.raazStep!==4)return;
      await submitRaazReport();return;
    }
    if(form.classList.contains("appeal-form")){event.preventDefault();await api(`/reports/${form.dataset.reportId}/appeal`,{method:"POST",body:formData(form)});toast("Appeal submitted for review.");await loadPageData("raaz");return;}
    if(id==="contact-form"){event.preventDefault();await api("/contacts",{method:"POST",body:formData(form)});state.contacts=await api("/contacts");render();toast("Trusted contact added.");return;}
    if(id==="tracking-form"){
      event.preventDefault();const body=formData(form);body.recipient_ids=body.recipient_ids||[];body.duration_minutes=Number(body.duration_minutes);state.tracking=await api("/tracking/start",{method:"POST",body});localStorage.setItem("befikr-tracking-id",state.tracking.id);render();toast(state.tracking.message);return;
    }
    if(id==="places-form"){
      event.preventDefault();
      const data=formData(form);
      let latitude=Number(data.latitude||NaN),longitude=Number(data.longitude||NaN);
      if(!(Math.abs(latitude)<=90&&Math.abs(longitude)<=180)){
        latitude=state.placeSearch?.latitude||28.6328;
        longitude=state.placeSearch?.longitude||77.2197;
      }
      state.placeQuery=(data.query||"").trim();
      state.placeSearch={latitude,longitude,radius_km:Number(data.radius_km||5)};
      await searchNearbyPlaces();
      return;
    }
    if(id==="tinyfish-import-form"){
      event.preventDefault();
      const file=form.elements.file.files?.[0];
      if(!file)return toast("Choose the TinyFish CSV file first.");
      if(file.size>2_000_000)return toast("Choose a CSV file under 2 MB.");
      const rows=parseCsv(await file.text());
      if(rows.length>250)return toast("Import up to 250 candidates at a time.");
      const candidates=rows.map((row,index)=>{
        const name=row.name||row.place_name;
        const category=row.category||row.place_type;
        const address=row.address||row.full_address;
        const latitude=Number(row.latitude||row.lat||NaN);
        const longitude=Number(row.longitude||row.lng||row.lon||NaN);
        const source_url=row.source_url||row.source_link;
        if(!name||!category||!address||!source_url){
          throw new Error(`Candidate ${index+1} needs name, category, address, and source_url.`);
        }
        if(!(latitude>=28&&latitude<=29.2&&longitude>=76&&longitude<=78)){
          throw new Error(`Candidate ${index+1} needs valid latitude and longitude in the Delhi region.`);
        }
        let source;
        try{source=new URL(source_url);}catch{throw new Error(`Candidate ${index+1} has an invalid source URL.`);}
        if(!["http:","https:"].includes(source.protocol)||source.username||source.password){
          throw new Error(`Candidate ${index+1} needs a source URL with HTTP or HTTPS and no credentials.`);
        }
        return {name,category,address,latitude,longitude,source_url,phone:row.phone||"",source_date:row.source_date||null,dataset_id:row.dataset_id||null};
      });
      const result=await api("/admin/place-candidates/import",{method:"POST",body:{candidates}});
      state.placeCandidates=await api("/admin/place-candidates");
      render();
      toast(`${result.imported} candidates imported. ${result.duplicates} duplicates skipped.`);
      return;
    }
    if(id==="profile-form"){event.preventDefault();state.user=await api("/profile",{method:"PATCH",body:formData(form)});render();toast("Profile updated.");return;}
    if(form.classList.contains("moderation-form")){event.preventDefault();await api(`/admin/reports/${form.dataset.id}/status`,{method:"PATCH",body:formData(form)});state.adminReports=await api("/admin/reports");render();toast("Review decision saved and audited.");return;}
    if(form.classList.contains("place-edit-form")){event.preventDefault();const data=formData(form);data.latitude=Number(data.latitude);data.longitude=Number(data.longitude);data.active=String(data.active)==="true";data.source_url=(data.source_url||"").trim();data.verified_at=new Date(data.verified_at).toISOString();await api(`/admin/places/${form.dataset.id}`,{method:"PATCH",body:data});state.places=await api("/admin/places");render();toast("Safe Spot listing updated.");return;}
    if(id==="place-admin-form"){event.preventDefault();const data=formData(form);data.latitude=Number(data.latitude);data.longitude=Number(data.longitude);data.verified_at=data.verified_at?new Date(data.verified_at).toISOString():new Date().toISOString();data.source=data.source.trim();data.source_url=(data.source_url||"").trim();await api("/admin/places",{method:"POST",body:data});state.places=await api("/admin/places");render();toast("Safe Spot listing added.");return;}
  }catch(error){toast(error.message||"Something went wrong. Please try again.");}
});

async function init(){
  if("serviceWorker" in navigator)navigator.serviceWorker.register("/sw.js").catch(()=>{});
  try{
    const res=await fetch("/data/offline_data.json");
    if(res.ok){
      const data=await res.json();
      state.offlinePlaces=data.places||[];
      state.offlineCorridors=data.corridors||[];
      if(!state.places||!state.places.length) state.places=data.places||[];
    }
  }catch(err){}
  if(!state.scripts||!state.scripts.length){
    state.scripts=FALLBACK_SCRIPTS.map(prepareBaatScriptAudio);
  }
  if(!state.selectedScript)state.selectedScript=state.scripts[0]?.id;
  try{
    const localContacts=JSON.parse(localStorage.getItem("befikr-contacts")||"[]");
    if(Array.isArray(localContacts)&&localContacts.length) state.contacts=localContacts;
  }catch(e){}
  if(state.token){
    try{
      state.user=await api("/profile");
      if(state.user) localStorage.setItem("befikr-user",JSON.stringify(state.user));
    }catch{
      try{state.user=JSON.parse(localStorage.getItem("befikr-user")||"null");}catch{state.user=null;}
    }
  }
  if(!state.user){
    try{state.user=JSON.parse(localStorage.getItem("befikr-user")||"null");}catch{state.user=null;}
  }
  if(!state.user){state.guestDemo=true;state.page="home";}
  render();
}
window.addEventListener("online",()=>{if(state.page==="raaz"&&state.user)toast("You’re online again. Retry saved drafts from RAAZ when ready.");render();});
window.addEventListener("offline",render);
init().catch(error=>{
  console.error("BEFIKR could not start",error);
  const status=document.getElementById("app-loading");
  if(status)status.textContent="BEFIKR couldn’t open. Refresh the page to try again.";
});
