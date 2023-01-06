import pytz

MAX_FILE_SIZE_MB = 10  # 10 MB limit
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Zero indexed header levels, users will be displayed 1 indexed option names
TABLE_HEADER_LEVELS = [
    {
        "key": "0",
        "label": "One",
    },
    {
        "key": "1",
        "label": "Two",
    },
    {
        "key": "2",
        "label": "Three",
    },
]

LANGUAGES = [
    ("ab", "Abkhaz"),
    ("aa", "Afar"),
    ("af", "Afrikaans"),
    ("ak", "Akan"),
    ("sq", "Albanian"),
    ("am", "Amharic"),
    ("ar", "Arabic"),
    ("an", "Aragonese"),
    ("hy", "Armenian"),
    ("as", "Assamese"),
    ("av", "Avaric"),
    ("ae", "Avestan"),
    ("ay", "Aymara"),
    ("az", "Azerbaijani"),
    ("bm", "Bambara"),
    ("ba", "Bashkir"),
    ("eu", "Basque"),
    ("be", "Belarusian"),
    ("bn", "Bengali"),
    ("bh", "Bihari"),
    ("bi", "Bislama"),
    ("bs", "Bosnian"),
    ("br", "Breton"),
    ("bg", "Bulgarian"),
    ("my", "Burmese"),
    ("ca", "Catalan"),
    ("ch", "Chamorro"),
    ("ce", "Chechen"),
    ("ny", "Chichewa"),
    ("zh", "Chinese"),
    ("cv", "Chuvash"),
    ("kw", "Cornish"),
    ("co", "Corsican"),
    ("cr", "Cree"),
    ("hr", "Croatian"),
    ("cs", "Czech"),
    ("da", "Danish"),
    ("dv", "Divehi"),
    ("nl", "Dutch"),
    ("dz", "Dzongkha"),
    ("en", "English"),
    ("eo", "Esperanto"),
    ("et", "Estonian"),
    ("ee", "Ewe"),
    ("fo", "Faroese"),
    ("fj", "Fijian"),
    ("fi", "Finnish"),
    ("fr", "French"),
    ("ff", "Fula"),
    ("gl", "Galician"),
    ("ka", "Georgian"),
    ("de", "German"),
    ("el", "Greek"),
    ("gn", "Guaraní"),
    ("gu", "Gujarati"),
    ("ht", "Haitian"),
    ("ha", "Hausa"),
    ("he", "Hebrew (modern)"),
    ("hz", "Herero"),
    ("hi", "Hindi"),
    ("ho", "Hiri Motu"),
    ("hu", "Hungarian"),
    ("ia", "Interlingua"),
    ("id", "Indonesian"),
    ("ie", "Interlingue"),
    ("ga", "Irish"),
    ("ig", "Igbo"),
    ("ik", "Inupiaq"),
    ("io", "Ido"),
    ("is", "Icelandic"),
    ("it", "Italian"),
    ("iu", "Inuktitut"),
    ("ja", "Japanese"),
    ("jv", "Javanese"),
    ("kl", "Kalaallisut"),
    ("kn", "Kannada"),
    ("kr", "Kanuri"),
    ("ks", "Kashmiri"),
    ("kk", "Kazakh"),
    ("km", "Khmer"),
    ("ki", "Kikuyu"),
    ("rw", "Kinyarwanda"),
    ("ky", "Kirghiz"),
    ("kv", "Komi"),
    ("kg", "Kongo"),
    ("ko", "Korean"),
    ("ku", "Kurdish"),
    ("kj", "Kwanyama"),
    ("la", "Latin"),
    ("lb", "Luxembourgish"),
    ("lg", "Luganda"),
    ("li", "Limburgish"),
    ("ln", "Lingala"),
    ("lo", "Lao"),
    ("lt", "Lithuanian"),
    ("lu", "Luba-Katanga"),
    ("lv", "Latvian"),
    ("gv", "Manx"),
    ("mk", "Macedonian"),
    ("mg", "Malagasy"),
    ("ms", "Malay"),
    ("ml", "Malayalam"),
    ("mt", "Maltese"),
    ("mi", "Māori"),
    ("mr", "Marathi (Marāṭhī)"),
    ("mh", "Marshallese"),
    ("mn", "Mongolian"),
    ("na", "Nauru"),
    ("nv", "Navajo, Navaho"),
    ("nb", "Norwegian Bokmål"),
    ("nd", "North Ndebele"),
    ("ne", "Nepali"),
    ("ng", "Ndonga"),
    ("nn", "Norwegian Nynorsk"),
    ("no", "Norwegian"),
    ("ii", "Nuosu"),
    ("nr", "South Ndebele"),
    ("oc", "Occitan"),
    ("oj", "Ojibwe"),
    ("cu", "Old Church Slavonic"),
    ("om", "Oromo"),
    ("or", "Oriya"),
    ("os", "Ossetian"),
    ("pa", "Panjabi"),
    ("pi", "Pāli"),
    ("fa", "Persian"),
    ("pl", "Polish"),
    ("ps", "Pashto"),
    ("pt", "Portuguese"),
    ("qu", "Quechua"),
    ("rm", "Romansh"),
    ("rn", "Kirundi"),
    ("ro", "Romanian"),
    ("ru", "Russian"),
    ("sa", "Sanskrit (Saṁskṛta)"),
    ("sc", "Sardinian"),
    ("sd", "Sindhi"),
    ("se", "Northern Sami"),
    ("sm", "Samoan"),
    ("sg", "Sango"),
    ("sr", "Serbian"),
    ("gd", "Scottish Gaelic"),
    ("sn", "Shona"),
    ("si", "Sinhala"),
    ("sk", "Slovak"),
    ("sl", "Slovene"),
    ("so", "Somali"),
    ("st", "Southern Sotho"),
    ("es", "Spanish"),
    ("su", "Sundanese"),
    ("sw", "Swahili"),
    ("ss", "Swati"),
    ("sv", "Swedish"),
    ("ta", "Tamil"),
    ("te", "Telugu"),
    ("tg", "Tajik"),
    ("th", "Thai"),
    ("ti", "Tigrinya"),
    ("bo", "Tibetan"),
    ("tk", "Turkmen"),
    ("tl", "Tagalog"),
    ("tn", "Tswana"),
    ("to", "Tonga"),
    ("tr", "Turkish"),
    ("ts", "Tsonga"),
    ("tt", "Tatar"),
    ("tw", "Twi"),
    ("ty", "Tahitian"),
    ("ug", "Uighur"),
    ("uk", "Ukrainian"),
    ("ur", "Urdu"),
    ("uz", "Uzbek"),
    ("ve", "Venda"),
    ("vi", "Vietnamese"),
    ("vo", "Volapük"),
    ("wa", "Walloon"),
    ("cy", "Welsh"),
    ("wo", "Wolof"),
    ("fy", "Western Frisian"),
    ("xh", "Xhosa"),
    ("yi", "Yiddish"),
    ("yo", "Yoruba"),
    ("za", "Zhuang"),
    ("zu", "Zulu"),
]

TIMEZONES = [
    {
        "key": zone,
        "label": zone,
    }
    for zone in pytz.all_timezones
]


COLUMN_TYPES = [
    {
        "key": "number",
        "label": "Number",
    },
    {
        "key": "string",
        "label": "String",
    },
    {
        "key": "date",
        "label": "Date",
    },
    {
        "key": "gender",
        "label": "Gender",
    },
    {
        "key": "url",
        "label": "Url",
    },
    {
        "key": "geo_area",
        "label": "Geo Area",
    },
    {
        "key": "datetime",
        "label": "Datetime",
    },
]
