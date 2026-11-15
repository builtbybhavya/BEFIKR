# Supplied Baat Banao transcripts and recordings

All 20 caller/scenario/language combinations use the user-supplied transcripts and
local MP3s. The 19 new transcripts join the original Mom Checking In Hindi script.
All ten Hindi scripts include Hinglish for every caller and user turn. The switch
changes displayed text only; the same Hindi audio plays.

There are 141 caller recordings (about 14.8 MB). No external voice service, speech
synthesis, substitute voice or user-dialogue audio is used. The supplied Samsung
ringtone loops until Answer, Decline or End.

| Script folder | Recordings | Transcript |
|---|---:|---|
| mom-checking-in-hi | 6 | Supplied transcript |
| mom-checking-in-eng | 6 | Supplied transcript |
| worried-mom-hi | 5 | Supplied transcript |
| worried-mom-eng | 5 | Supplied transcript |
| father-checking-in-hi | 7 | Supplied transcript |
| father-checking-in-eng | 7 | Supplied transcript |
| worried-father-hi | 7 | Supplied transcript |
| worried-father-eng | 7 | Supplied transcript |
| sister-checking-in-hi | 7 | Supplied transcript |
| sister-checking-in-eng | 7 | Supplied transcript |
| worried-sister-hi | 9 | Supplied transcript |
| worried-sister-eng | 10 | Supplied transcript |
| brother-checking-in-hi | 7 | Supplied transcript |
| brother-checking-in-eng | 7 | Supplied transcript |
| worried-brother-hi | 7 | Supplied transcript |
| worried-brother-eng | 7 | Supplied transcript |
| boyfriend-checking-in-hi | 7 | Supplied transcript |
| boyfriend-checking-in-eng | 9 | Supplied transcript |
| worried-boyfriend-hi | 7 | Supplied transcript |
| worried-boyfriend-eng | 7 | Supplied transcript |

## Transcript source and roles

The source of truth is `backend/fixtures/baat_transcripts.json`, with the original
19-script submission preserved in `baat_transcripts_supplied.txt`. Original text
is kept, including its English words within Hindi. Hinglish is a readable Roman
transliteration. The original Mom Hindi transcript and Hinglish are retained.

Every turn has an explicit canonical `speaker`: `caller` or `user`, plus its
original source label. Daughter, girlfriend, beti, premika and other user replies
have no audio. The sister-to-sister scripts use the same source label on both
sides; alternate turns were classified as caller/user before applying corrections.
The user side is shown distinctly as You / आप / Aap.

Per the user's correction, this Worried Sister Hindi caller line was removed:

> बहुत अच्छा। और हाँ, घर पहुँचकर मेरे कमरे में आना। मुझे तुझसे एक ज़रूरी बात भी करनी है।

Its Hinglish is also removed. All other reply lines remain, including the two
now-adjacent silent replies. There are nine caller lines and nine recordings in
this script. Across all 20 scripts, every caller line has exactly one recording.
The new five-line Worried Mom transcripts replace the previous six-line versions;
no old placeholder dialogue or acknowledgment loop is appended.

## Playback and offline use

Playback supports Pause/Resume, Replay, Continue and End. Ending, leaving Baat Banao,
changing caller/language/script or replaying stops the current audio. User turns
never construct an audio player, even if an audio field were supplied accidentally.
No final numbered recording is inferred to be a repeated loop. An explicit
`loop.mp3`, if supplied, can serve as a repeated caller acknowledgment.

The filename `worried-boyfriend-hi/1..mp3` was corrected to `1.mp3`; no audio
content was changed. Both `1.mp3` and `01.mp3` naming are supported. Numeric sorting
keeps `10.mp3` after `9.mp3`. Missing/duplicate sequence numbers are rejected.

`backend/app/baat_recordings.py` reads the canonical transcripts and actual folders
for both voice API endpoints. Generated `recordings.json` and `recordings.js`
provide identical audio and transcript metadata for guest/offline calls. Rebuild
these catalogs after editing recordings or transcripts:

```powershell
python backend/build_baat_recordings.py
```

Clip URLs include a content hash. The PWA shell caches all 141 clips, transcripts
and the ringtone after successful online installation. When deploying a rebuilt
catalog, bump the service-worker cache version and catalog script URL.

Tests verify file URLs, numeric order, source-text fidelity, Hinglish coverage,
role separation and playback state. They do not claim manual listening or timing
alignment with the spoken words inside each supplied recording.
