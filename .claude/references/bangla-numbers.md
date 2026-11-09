# Spoken Bangla numbers and forms

Reference for `bdub.text.bn` (SPEC §10.1). Colloquial standard Bangladeshi forms. Bangla numbers 1–99 are irregular, so they must come from a lookup table, not composed from parts.

**Status:** best-effort list. Have the Bangla linguist confirm the whole table (spelling variants exist, e.g. ঊন/উন, ছয়/ছয়, দুইশো/দুশো) before it becomes the test oracle. Mark disputed entries in tests with `# TODO(linguist)`.

## 0–100

| n | spoken | n | spoken | n | spoken | n | spoken |
|---|---|---|---|---|---|---|---|
| 0 | শূন্য | 26 | ছাব্বিশ | 51 | একান্ন | 76 | ছিয়াত্তর |
| 1 | এক | 27 | সাতাশ | 52 | বাহান্ন | 77 | সাতাত্তর |
| 2 | দুই | 28 | আটাশ | 53 | তিপ্পান্ন | 78 | আটাত্তর |
| 3 | তিন | 29 | ঊনত্রিশ | 54 | চুয়ান্ন | 79 | ঊনআশি |
| 4 | চার | 30 | ত্রিশ | 55 | পঞ্চান্ন | 80 | আশি |
| 5 | পাঁচ | 31 | একত্রিশ | 56 | ছাপ্পান্ন | 81 | একাশি |
| 6 | ছয় | 32 | বত্রিশ | 57 | সাতান্ন | 82 | বিরাশি |
| 7 | সাত | 33 | তেত্রিশ | 58 | আটান্ন | 83 | তিরাশি |
| 8 | আট | 34 | চৌত্রিশ | 59 | ঊনষাট | 84 | চুরাশি |
| 9 | নয় | 35 | পঁয়ত্রিশ | 60 | ষাট | 85 | পঁচাশি |
| 10 | দশ | 36 | ছত্রিশ | 61 | একষট্টি | 86 | ছিয়াশি |
| 11 | এগারো | 37 | সাঁইত্রিশ | 62 | বাষট্টি | 87 | সাতাশি |
| 12 | বারো | 38 | আটত্রিশ | 63 | তেষট্টি | 88 | আটাশি |
| 13 | তেরো | 39 | ঊনচল্লিশ | 64 | চৌষট্টি | 89 | ঊননব্বই |
| 14 | চৌদ্দ | 40 | চল্লিশ | 65 | পঁয়ষট্টি | 90 | নব্বই |
| 15 | পনেরো | 41 | একচল্লিশ | 66 | ছেষট্টি | 91 | একানব্বই |
| 16 | ষোলো | 42 | বিয়াল্লিশ | 67 | সাতষট্টি | 92 | বিরানব্বই |
| 17 | সতেরো | 43 | তেতাল্লিশ | 68 | আটষট্টি | 93 | তিরানব্বই |
| 18 | আঠারো | 44 | চুয়াল্লিশ | 69 | ঊনসত্তর | 94 | চুরানব্বই |
| 19 | উনিশ | 45 | পঁয়তাল্লিশ | 70 | সত্তর | 95 | পঁচানব্বই |
| 20 | বিশ | 46 | ছেচল্লিশ | 71 | একাত্তর | 96 | ছিয়ানব্বই |
| 21 | একুশ | 47 | সাতচল্লিশ | 72 | বাহাত্তর | 97 | সাতানব্বই |
| 22 | বাইশ | 48 | আটচল্লিশ | 73 | তিয়াত্তর | 98 | আটানব্বই |
| 23 | তেইশ | 49 | ঊনপঞ্চাশ | 74 | চুয়াত্তর | 99 | নিরানব্বই |
| 24 | চব্বিশ | 50 | পঞ্চাশ | 75 | পঁচাত্তর | 100 | একশো |
| 25 | পঁচিশ | | | | | | |

## Scales (South Asian grouping)

| Value | Word | Example |
|---|---|---|
| 100 | শো (after a number: একশো, দুইশো, তিনশো …) | 250 → দুইশো পঞ্চাশ |
| 1,000 | হাজার | 1,250 → এক হাজার দুইশো পঞ্চাশ |
| 1,00,000 (100 thousand) | লাখ | 2,50,000 → আড়াই লাখ *or* দুই লাখ পঞ্চাশ হাজার |
| 1,00,00,000 (10 million) | কোটি | 1,20,00,000 → এক কোটি বিশ লাখ |

- Western-grouped input (`1,000,000`) is read by value: দশ লাখ.
- Above 99 কোটি, continue with কোটি as a unit: `100 crore` → একশো কোটি.
- Special colloquial forms: 1.5 → দেড়, 2.5 → আড়াই (use for quantities and time; plain decimal reading for measurements is also acceptable; setting).
- Decimal point: দশমিক, digits read one by one: 3.14 → তিন দশমিক এক চার.
- Negative: ঋণাত্মক (formal) / মাইনাস (colloquial) **(linguist to choose default)**.
- Percent: শতাংশ (25% → পঁচিশ শতাংশ).
- Fractions: ১/২ → অর্ধেক, ১/৪ → এক চতুর্থাংশ, ৩/৪ → তিন চতুর্থাংশ; others: "<num> ভাগের <den>"? **(verify)**.
- Ranges: 10–20 → দশ থেকে বিশ.

## Ordinals

| n | form | n | form |
|---|---|---|---|
| 1st | প্রথম | 6th | ষষ্ঠ |
| 2nd | দ্বিতীয় | 7th | সপ্তম |
| 3rd | তৃতীয় | 8th | অষ্টম |
| 4th | চতুর্থ | 9th | নবম |
| 5th | পঞ্চম | 10th | দশম |

11th and above: cardinal + তম (এগারোতম, একুশতম) in colloquial use **(verify)**. Dates use ordinal-like forms for day numbers in formal speech (পহেলা for the 1st of a month), plain cardinal otherwise.

## Digits

| System | Characters |
|---|---|
| Bengali | ০ ১ ২ ৩ ৪ ৫ ৬ ৭ ৮ ৯ |
| Latin | 0 1 2 3 4 5 6 7 8 9 |
| Eastern Arabic | ٠ ١ ٢ ٣ ٤ ٥ ٦ ٧ ٨ ٩ |
| Persian/Urdu (also accept) | ۰ ۱ ۲ ۳ ۴ ۵ ۶ ۷ ۸ ۹ |

Map all to int before reading. Phone numbers, years, and IDs are read digit by digit or in pairs (see below).

## Years, phone numbers

- Years: 1971 → উনিশশো একাত্তর; 2024 → দুই হাজার চব্বিশ.
- Phone numbers: digit by digit (০১৭১২… → শূন্য এক সাত এক দুই …).

## Time of day

| Range (approx.) | Word |
|---|---|
| 04:00–06:00 | ভোর |
| 06:00–12:00 | সকাল |
| 12:00–15:00 | দুপুর |
| 15:00–17:30 | বিকেল |
| 17:30–19:00 | সন্ধ্যা |
| 19:00–04:00 | রাত |

- `:00` → <hour>টা (সকাল দশটা). Hours 1–4 use special forms: একটা, দুইটা/দুটো, তিনটা, চারটা **(linguist to choose)**.
- `:15` → সোয়া <hour>টা; `:30` → সাড়ে <hour>টা (1:30 → দেড়টা, 2:30 → আড়াইটা); `:45` → পৌনে <hour+1>টা.
- Other minutes: <hour>টা <minutes> মিনিট.
- `12:30 PM` → দুপুর সাড়ে বারোটা.
- Digital style (setting): বারোটা ত্রিশ.

## Dates and months

Gregorian months: জানুয়ারি, ফেব্রুয়ারি, মার্চ, এপ্রিল, মে, জুন, জুলাই, আগস্ট, সেপ্টেম্বর, অক্টোবর, নভেম্বর, ডিসেম্বর.

Bangla calendar months (for Bangla-calendar contexts): বৈশাখ, জ্যৈষ্ঠ, আষাঢ়, শ্রাবণ, ভাদ্র, আশ্বিন, কার্তিক, অগ্রহায়ণ, পৌষ, মাঘ, ফাল্গুন, চৈত্র.

Days: শনিবার, রবিবার, সোমবার, মঙ্গলবার, বুধবার, বৃহস্পতিবার, শুক্রবার.

`16 December 1971` → ষোলোই ডিসেম্বর উনিশশো একাত্তর (day suffixes: পহেলা/১লা, দোসরা/২রা, তেসরা/৩রা, চৌঠা/৪ঠা, then -ই: পাঁচই, ষোলোই, একুশে for 21 **(verify full list)**).

## Currency and units

| Input | Spoken |
|---|---|
| ৳, Tk, BDT | টাকা (৳50.25 → পঞ্চাশ টাকা পঁচিশ পয়সা) |
| $ | ডলার (and সেন্ট) |
| ₹ | রুপি |
| € | ইউরো |
| £ | পাউন্ড |
| km, m, cm, mm | কিলোমিটার, মিটার, সেন্টিমিটার, মিলিমিটার |
| kg, g | কিলোগ্রাম (colloquial: কেজি), গ্রাম |
| L, ml | লিটার, মিলিলিটার |
| °C, °F | ডিগ্রি সেলসিয়াস, ডিগ্রি ফারেনহাইট |
| KB, MB, GB, TB | কিলোবাইট, মেগাবাইট, গিগাবাইট, টেরাবাইট |
| km/h | কিলোমিটার প্রতি ঘণ্টা |
| % | শতাংশ |

Currency symbol position doesn't change the reading order: number first, then unit.
