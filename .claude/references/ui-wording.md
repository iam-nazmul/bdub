# UI wording (Simple mode)

Approved wording for everyday users (SPEC §1.3, §7.0). Use these strings exactly through `tr()`. Bangla is plain, colloquial Bangladeshi, addressing the user as আপনি. New strings: add them here first, then have the `bangla-linguist` agent review. Entries marked **(verify)** are drafts.

## Main actions

| Key | English | বাংলা |
|---|---|---|
| `action.open` | Open video | ভিডিও খুলুন |
| `action.dub` | Dub to Bangla | বাংলায় ডাব করুন |
| `action.audio.original` | Original | মূল ভাষা |
| `action.audio.bangla` | Bangla | বাংলা |
| `action.subs.on` | Subtitles on | সাবটাইটেল চালু |
| `action.subs.off` | Subtitles off | সাবটাইটেল বন্ধ |
| `action.save` | Save dubbed video | ডাব করা ভিডিও সেভ করুন |
| `action.cancel` | Cancel | বাতিল |
| `action.pause_dub` | Pause dubbing | ডাবিং থামান |
| `action.resume_dub` | Continue dubbing | ডাবিং চালিয়ে যান |
| `action.advanced` | Advanced mode | উন্নত মোড |
| `action.simple` | Simple mode | সহজ মোড |

## Dub options (Simple)

| Key | English | বাংলা |
|---|---|---|
| `opt.voice` | Voice | কণ্ঠ |
| `opt.voice.female` | Female | নারী |
| `opt.voice.male` | Male | পুরুষ |
| `opt.quality` | Quality | মান |
| `opt.quality.fast` | Faster | দ্রুত |
| `opt.quality.better` | Better | উন্নত |
| `opt.start` | Start | শুরু করুন |

## Progress steps

| Stage(s) | English | বাংলা |
|---|---|---|
| decode | Getting the video ready | ভিডিও প্রস্তুত করা হচ্ছে |
| separate | Separating voices from music | কণ্ঠ ও সংগীত আলাদা করা হচ্ছে |
| asr, diarize, segment | Listening to the video | ভিডিও শোনা হচ্ছে |
| mt | Translating to Bangla | বাংলায় অনুবাদ করা হচ্ছে |
| normalize, tts | Creating Bangla voice | বাংলা কণ্ঠ তৈরি হচ্ছে |
| fit, mix | Matching the voice to the video | ভিডিওর সাথে মেলানো হচ্ছে |
| subs | Making subtitles | সাবটাইটেল তৈরি হচ্ছে |
| — | About %n minutes left | আর প্রায় %n মিনিট বাকি |
| — | Less than a minute left | আর এক মিনিটেরও কম বাকি |

## Notices

| Key | English | বাংলা |
|---|---|---|
| `note.ready` | Bangla dub ready | বাংলা ডাব প্রস্তুত |
| `note.slow_pc` | Your dub will be ready in about %n minutes. You can keep watching in the original language. | আপনার ডাব প্রায় %n মিনিটের মধ্যে প্রস্তুত হবে। ততক্ষণ মূল ভাষায় দেখতে পারেন। |
| `note.catching_up` | Dubbing is catching up… | ডাবিং এগিয়ে আসছে… **(verify)** |
| `note.continue` | Continue dubbing this video? | এই ভিডিওর ডাবিং কি চালিয়ে যাবেন? |
| `note.ai_dub` | AI dub | এআই ডাব |
| `note.machine_translated` | Machine translated | যন্ত্রে অনুবাদ করা |

## Errors (one sentence + one action)

| Key | English | বাংলা | Action button |
|---|---|---|---|
| `err.video_missing` | We can't find this video anymore. | ভিডিওটি আর খুঁজে পাওয়া যাচ্ছে না। | Find video… / ভিডিও খুঁজুন… |
| `err.cant_play` | This video can't be played. The file may be damaged. | এই ভিডিওটি চালানো যাচ্ছে না। ফাইলটি হয়তো নষ্ট। | Open another video / অন্য ভিডিও খুলুন |
| `err.protected` | This video is protected and can't be dubbed. | এই ভিডিওটি সুরক্ষিত, তাই ডাব করা যাবে না। | OK / ঠিক আছে |
| `err.no_space` | There isn't enough free space to dub this video. | এই ভিডিও ডাব করার মতো যথেষ্ট জায়গা নেই। | Free up space / জায়গা খালি করুন |
| `err.drive_removed` | The drive was removed. Plug it back in to continue. | ড্রাইভটি খুলে ফেলা হয়েছে। চালিয়ে যেতে আবার লাগান। | Try again / আবার চেষ্টা করুন |
| `err.read_only` | Running in a read-only place. Your dubs will be saved on this computer instead. | অ্যাপটি এমন জায়গায় চলছে যেখানে কিছু সেভ করা যায় না। আপনার ডাব এই কম্পিউটারে সেভ হবে। | OK / ঠিক আছে |
| `err.mac_translocated` | Please move the BanglaDub folder out of Downloads, then open it again. | BanglaDub ফোল্ডারটি Downloads থেকে সরিয়ে আবার খুলুন। | Show folder / ফোল্ডার দেখান |
| `err.linux_noexec` | This drive doesn't allow running apps. Copy the BanglaDub folder to your Home folder and open it from there. | এই ড্রাইভ থেকে অ্যাপ চালানো যায় না। BanglaDub ফোল্ডারটি Home ফোল্ডারে কপি করে সেখান থেকে খুলুন। | OK / ঠিক আছে |
| `err.no_voice_pack` | Bangla voices are missing. Add the voice file to continue. | বাংলা কণ্ঠ পাওয়া যাচ্ছে না। চালিয়ে যেতে কণ্ঠের ফাইল যোগ করুন। | Add file… / ফাইল যোগ করুন… |
| `err.generic` | Something went wrong. Your work is saved. | কিছু একটা সমস্যা হয়েছে। আপনার কাজ সেভ করা আছে। | Try again / আবার চেষ্টা করুন |
| `err.details` | Details | বিস্তারিত | — |

## Settings (Simple)

| Key | English | বাংলা |
|---|---|---|
| `set.language` | Language | ভাষা |
| `set.text_size` | Text size | লেখার আকার |
| `set.sub_size` | Subtitle size | সাবটাইটেলের আকার |
| `set.clear_space` | Clear space used by dubs | ডাবের জন্য ব্যবহৃত জায়গা খালি করুন |
| `set.auto_switch` | Switch to Bangla when the dub is ready | ডাব প্রস্তুত হলে বাংলায় চালু করুন |

## Never show in Simple mode

ASR, MT, TTS, VAD, diarization, model, tier, T1/T2/T3, LUFS, dB, RTF, cache, codec, bitrate, sample rate, file paths, error codes, exception text, "worker", "process", "pipeline".
