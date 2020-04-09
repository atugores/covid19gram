#!/bin/env python
# -*- coding: utf-8 -*-
countries = {
  "Andorra": {
    "flag": "🇦🇩",
    "code": "AD"
  },
  "United Arab Emirates": {
    "flag": "🇦🇪",
    "code": "AE"
  },
  "Afghanistan": {
    "flag": "🇦🇫",
    "code": "AF"
  },
  "Antigua and Barbuda": {
    "flag": "🇦🇬",
    "code": "AG"
  },
  "Anguilla": {
    "flag": "🇦🇮",
    "code": "AI"
  },
  "Albania": {
    "flag": "🇦🇱",
    "code": "AL"
  },
  "Armenia": {
    "flag": "🇦🇲",
    "code": "AM"
  },
  "Angola": {
    "flag": "🇦🇴",
    "code": "AO"
  },
  "Antarctica": {
    "flag": "🇦🇶",
    "code": "AQ"
  },
  "Argentina": {
    "flag": "🇦🇷",
    "code": "AR"
  },
  "American Samoa": {
    "flag": "🇦🇸",
    "code": "AS"
  },
  "Austria": {
    "flag": "🇦🇹",
    "code": "AT"
  },
  "Australia": {
    "flag": "🇦🇺",
    "code": "AU"
  },
  "Aruba": {
    "flag": "🇦🇼",
    "code": "AW"
  },
  "Åland Islands": {
    "flag": "🇦🇽",
    "code": "AX"
  },
  "Azerbaijan": {
    "flag": "🇦🇿",
    "code": "AZ"
  },
  "Bosnia and Herzegovina": {
    "flag": "🇧🇦",
    "code": "BA"
  },
  "Barbados": {
    "flag": "🇧🇧",
    "code": "BB"
  },
  "Bangladesh": {
    "flag": "🇧🇩",
    "code": "BD"
  },
  "Belgium": {
    "flag": "🇧🇪",
    "code": "BE"
  },
  "Burkina Faso": {
    "flag": "🇧🇫",
    "code": "BF"
  },
  "Bulgaria": {
    "flag": "🇧🇬",
    "code": "BG"
  },
  "Bahrain": {
    "flag": "🇧🇭",
    "code": "BH"
  },
  "Burundi": {
    "flag": "🇧🇮",
    "code": "BI"
  },
  "Benin": {
    "flag": "🇧🇯",
    "code": "BJ"
  },
  "Saint Barthélemy": {
    "flag": "🇧🇱",
    "code": "BL"
  },
  "Bermuda": {
    "flag": "🇧🇲",
    "code": "BM"
  },
  "Brunei": {
    "flag": "🇧🇳",
    "code": "BN"
  },
  "Bolivia": {
    "flag": "🇧🇴",
    "code": "BO"
  },
  "Bonaire, Sint Eustatius and Saba": {
    "flag": "🇧🇶",
    "code": "BQ"
  },
  "Brazil": {
    "flag": "🇧🇷",
    "code": "BR"
  },
  "Bahamas": {
    "flag": "🇧🇸",
    "code": "BS"
  },
  "Bhutan": {
    "flag": "🇧🇹",
    "code": "BT"
  },
  "Bouvet Island": {
    "flag": "🇧🇻",
    "code": "BV"
  },
  "Botswana": {
    "flag": "🇧🇼",
    "code": "BW"
  },
  "Belarus": {
    "flag": "🇧🇾",
    "code": "BY"
  },
  "Belize": {
    "flag": "🇧🇿",
    "code": "BZ"
  },
  "Canada": {
    "flag": "🇨🇦",
    "code": "CA"
  },
  "Cocos (Keeling) Islands": {
    "flag": "🇨🇨",
    "code": "CC"
  },
  "Congo (Kinshasa)": {
    "flag": "🇨🇩",
    "code": "CD"
  },
  "Central African Republic": {
    "flag": "🇨🇫",
    "code": "CF"
  },
  "Congo (Brazzaville)": {
    "flag": "🇨🇬",
    "code": "CG"
  },
  "Switzerland": {
    "flag": "🇨🇭",
    "code": "CH"
  },
  "Cote d'Ivoire": {
    "flag": "🇨🇮",
    "code": "CI"
  },
  "Cook Islands": {
    "flag": "🇨🇰",
    "code": "CK"
  },
  "Chile": {
    "flag": "🇨🇱",
    "code": "CL"
  },
  "Cameroon": {
    "flag": "🇨🇲",
    "code": "CM"
  },
  "China": {
    "flag": "🇨🇳",
    "code": "CN"
  },
  "Colombia": {
    "flag": "🇨🇴",
    "code": "CO"
  },
  "Costa Rica": {
    "flag": "🇨🇷",
    "code": "CR"
  },
  "Cuba": {
    "flag": "🇨🇺",
    "code": "CU"
  },
  "Cabo Verde": {
    "flag": "🇨🇻",
    "code": "CV"
  },
  "Curaçao": {
    "flag": "🇨🇼",
    "code": "CW"
  },
  "Christmas Island": {
    "flag": "🇨🇽",
    "code": "CX"
  },
  "Cyprus": {
    "flag": "🇨🇾",
    "code": "CY"
  },
  "Czechia": {
    "flag": "🇨🇿",
    "code": "CZ"
  },
  "Germany": {
    "flag": "🇩🇪",
    "code": "DE"
  },
  "Djibouti": {
    "flag": "🇩🇯",
    "code": "DJ"
  },
  "Denmark": {
    "flag": "🇩🇰",
    "code": "DK"
  },
  "Dominica": {
    "flag": "🇩🇲",
    "code": "DM"
  },
  "Dominican Republic": {
    "flag": "🇩🇴",
    "code": "DO"
  },
  "Cruise Ship": {
    "flag": "🚢"
  },
  "Algeria": {
    "flag": "🇩🇿",
    "code": "DZ"
  },
  "Ecuador": {
    "flag": "🇪🇨",
    "code": "EC"
  },
  "Estonia": {
    "flag": "🇪🇪",
    "code": "EE"
  },
  "Egypt": {
    "flag": "🇪🇬",
    "code": "EG"
  },
  "Western Sahara": {
    "flag": "🇪🇭",
    "code": "EH"
  },
  "Eritrea": {
    "flag": "🇪🇷",
    "code": "ER"
  },
  "Spain": {
    "flag": "🇪🇸",
    "code": "ES"
  },
  "Ethiopia": {
    "flag": "🇪🇹",
    "code": "ET"
  },
  "European Union": {
    "flag": "🇪🇺",
    "code": "EU"
  },
  "Finland": {
    "flag": "🇫🇮",
    "code": "FI"
  },
  "Fiji": {
    "flag": "🇫🇯",
    "code": "FJ"
  },
  "Falkland Islands (Malvinas)": {
    "flag": "🇫🇰",
    "code": "FK"
  },
  "Micronesia": {
    "flag": "🇫🇲",
    "code": "FM"
  },
  "Faroe Islands": {
    "flag": "🇫🇴",
    "code": "FO"
  },
  "France": {
    "flag": "🇫🇷",
    "code": "FR"
  },
  "Gabon": {
    "flag": "🇬🇦",
    "code": "GA"
  },
  "United Kingdom": {
    "flag": "🇬🇧",
    "code": "GB"
  },
  "Grenada": {
    "flag": "🇬🇩",
    "code": "GD"
  },
  "Georgia": {
    "flag": "🇬🇪",
    "code": "GE"
  },
  "French Guiana": {
    "flag": "🇬🇫",
    "code": "GF"
  },
  "Guernsey": {
    "flag": "🇬🇬",
    "code": "GG"
  },
  "Ghana": {
    "flag": "🇬🇭",
    "code": "GH"
  },
  "Gibraltar": {
    "flag": "🇬🇮",
    "code": "GI"
  },
  "Greenland": {
    "flag": "🇬🇱",
    "code": "GL"
  },
  "Gambia": {
    "flag": "🇬🇲",
    "code": "GM"
  },
  "Guinea": {
    "flag": "🇬🇳",
    "code": "GN"
  },
  "Guadeloupe": {
    "flag": "🇬🇵",
    "code": "GP"
  },
  "Equatorial Guinea": {
    "flag": "🇬🇶",
    "code": "GQ"
  },
  "Greece": {
    "flag": "🇬🇷",
    "code": "GR"
  },
  "South Georgia": {
    "flag": "🇬🇸",
    "code": "GS"
  },
  "Guatemala": {
    "flag": "🇬🇹",
    "code": "GT"
  },
  "Guam": {
    "flag": "🇬🇺",
    "code": "GU"
  },
  "Guinea-Bissau": {
    "flag": "🇬🇼",
    "code": "GW"
  },
  "Guyana": {
    "flag": "🇬🇾",
    "code": "GY"
  },
  "Hong Kong": {
    "flag": "🇭🇰",
    "code": "HK"
  },
  "Heard Island and Mcdonald Islands": {
    "flag": "🇭🇲",
    "code": "HM"
  },
  "Honduras": {
    "flag": "🇭🇳",
    "code": "HN"
  },
  "Croatia": {
    "flag": "🇭🇷",
    "code": "HR"
  },
  "Haiti": {
    "flag": "🇭🇹",
    "code": "HT"
  },
  "Hungary": {
    "flag": "🇭🇺",
    "code": "HU"
  },
  "Indonesia": {
    "flag": "🇮🇩",
    "code": "ID"
  },
  "Ireland": {
    "flag": "🇮🇪",
    "code": "IE"
  },
  "Israel": {
    "flag": "🇮🇱",
    "code": "IL"
  },
  "Isle of Man": {
    "flag": "🇮🇲",
    "code": "IM"
  },
  "India": {
    "flag": "🇮🇳",
    "code": "IN"
  },
  "British Indian Ocean Territory": {
    "flag": "🇮🇴",
    "code": "IO"
  },
  "Iraq": {
    "flag": "🇮🇶",
    "code": "IQ"
  },
  "Iran": {
    "flag": "🇮🇷",
    "code": "IR"
  },
  "Iceland": {
    "flag": "🇮🇸",
    "code": "IS"
  },
  "Italy": {
    "flag": "🇮🇹",
    "code": "IT"
  },
  "Jersey": {
    "flag": "🇯🇪",
    "code": "JE"
  },
  "Jamaica": {
    "flag": "🇯🇲",
    "code": "JM"
  },
  "Jordan": {
    "flag": "🇯🇴",
    "code": "JO"
  },
  "Japan": {
    "flag": "🇯🇵",
    "code": "JP"
  },
  "Kenya": {
    "flag": "🇰🇪",
    "code": "KE"
  },
  "Kyrgyzstan": {
    "flag": "🇰🇬",
    "code": "KG"
  },
  "Cambodia": {
    "flag": "🇰🇭",
    "code": "KH"
  },
  "Kiribati": {
    "flag": "🇰🇮",
    "code": "KI"
  },
  "Comoros": {
    "flag": "🇰🇲",
    "code": "KM"
  },
  "Saint Kitts and Nevis": {
    "flag": "🇰🇳",
    "code": "KN"
  },
  "North Korea": {
    "flag": "🇰🇵",
    "code": "KP"
  },
  "South Korea": {
    "flag": "🇰🇷",
    "code": "KR"
  },
  "Kuwait": {
    "flag": "🇰🇼",
    "code": "KW"
  },
  "Cayman Islands": {
    "flag": "🇰🇾",
    "code": "KY"
  },
  "Kazakhstan": {
    "flag": "🇰🇿",
    "code": "KZ"
  },
  "Laos": {
    "flag": "🇱🇦",
    "code": "LA"
  },
  "Lebanon": {
    "flag": "🇱🇧",
    "code": "LB"
  },
  "Saint Lucia": {
    "flag": "🇱🇨",
    "code": "LC"
  },
  "Liechtenstein": {
    "flag": "🇱🇮",
    "code": "LI"
  },
  "Sri Lanka": {
    "flag": "🇱🇰",
    "code": "LK"
  },
  "Liberia": {
    "flag": "🇱🇷",
    "code": "LR"
  },
  "Lesotho": {
    "flag": "🇱🇸",
    "code": "LS"
  },
  "Lithuania": {
    "flag": "🇱🇹",
    "code": "LT"
  },
  "Luxembourg": {
    "flag": "🇱🇺",
    "code": "LU"
  },
  "Latvia": {
    "flag": "🇱🇻",
    "code": "LV"
  },
  "Libya": {
    "flag": "🇱🇾",
    "code": "LY"
  },
  "Morocco": {
    "flag": "🇲🇦",
    "code": "MA"
  },
  "Monaco": {
    "flag": "🇲🇨",
    "code": "MC"
  },
  "Moldova": {
    "flag": "🇲🇩",
    "code": "MD"
  },
  "Montenegro": {
    "flag": "🇲🇪",
    "code": "ME"
  },
  "Saint Martin (French Part)": {
    "flag": "🇲🇫",
    "code": "MF"
  },
  "Madagascar": {
    "flag": "🇲🇬",
    "code": "MG"
  },
  "Marshall Islands": {
    "flag": "🇲🇭",
    "code": "MH"
  },
  "North Macedonia": {
    "flag": "🇲🇰",
    "code": "MK"
  },
  "Mali": {
    "flag": "🇲🇱",
    "code": "ML"
  },
  "Myanmar": {
    "flag": "🇲🇲",
    "code": "MM"
  },
  "Mongolia": {
    "flag": "🇲🇳",
    "code": "MN"
  },
  "Macao": {
    "flag": "🇲🇴",
    "code": "MO"
  },
  "Northern Mariana Islands": {
    "flag": "🇲🇵",
    "code": "MP"
  },
  "Martinique": {
    "flag": "🇲🇶",
    "code": "MQ"
  },
  "Mauritania": {
    "flag": "🇲🇷",
    "code": "MR"
  },
  "Montserrat": {
    "flag": "🇲🇸",
    "code": "MS"
  },
  "Malta": {
    "flag": "🇲🇹",
    "code": "MT"
  },
  "Mauritius": {
    "flag": "🇲🇺",
    "code": "MU"
  },
  "Maldives": {
    "flag": "🇲🇻",
    "code": "MV"
  },
  "Malawi": {
    "flag": "🇲🇼",
    "code": "MW"
  },
  "Mexico": {
    "flag": "🇲🇽",
    "code": "MX"
  },
  "Malaysia": {
    "flag": "🇲🇾",
    "code": "MY"
  },
  "Mozambique": {
    "flag": "🇲🇿",
    "code": "MZ"
  },
  "Namibia": {
    "flag": "🇳🇦",
    "code": "NA"
  },
  "New Caledonia": {
    "flag": "🇳🇨",
    "code": "NC"
  },
  "Niger": {
    "flag": "🇳🇪",
    "code": "NE"
  },
  "Norfolk Island": {
    "flag": "🇳🇫",
    "code": "NF"
  },
  "Nigeria": {
    "flag": "🇳🇬",
    "code": "NG"
  },
  "Nicaragua": {
    "flag": "🇳🇮",
    "code": "NI"
  },
  "Netherlands": {
    "flag": "🇳🇱",
    "code": "NL"
  },
  "Norway": {
    "flag": "🇳🇴",
    "code": "NO"
  },
  "Nepal": {
    "flag": "🇳🇵",
    "code": "NP"
  },
  "Nauru": {
    "flag": "🇳🇷",
    "code": "NR"
  },
  "Niue": {
    "flag": "🇳🇺",
    "code": "NU"
  },
  "New Zealand": {
    "flag": "🇳🇿",
    "code": "NZ"
  },
  "Oman": {
    "flag": "🇴🇲",
    "code": "OM"
  },
  "Panama": {
    "flag": "🇵🇦",
    "code": "PA"
  },
  "Peru": {
    "flag": "🇵🇪",
    "code": "PE"
  },
  "French Polynesia": {
    "flag": "🇵🇫",
    "code": "PF"
  },
  "Papua New Guinea": {
    "flag": "🇵🇬",
    "code": "PG"
  },
  "Philippines": {
    "flag": "🇵🇭",
    "code": "PH"
  },
  "Pakistan": {
    "flag": "🇵🇰",
    "code": "PK"
  },
  "Poland": {
    "flag": "🇵🇱",
    "code": "PL"
  },
  "Saint Pierre and Miquelon": {
    "flag": "🇵🇲",
    "code": "PM"
  },
  "Pitcairn": {
    "flag": "🇵🇳",
    "code": "PN"
  },
  "Puerto Rico": {
    "flag": "🇵🇷",
    "code": "PR"
  },
  "Palestine": {
    "flag": "🇵🇸",
    "code": "PS"
  },
  "Portugal": {
    "flag": "🇵🇹",
    "code": "PT"
  },
  "Palau": {
    "flag": "🇵🇼",
    "code": "PW"
  },
  "Paraguay": {
    "flag": "🇵🇾",
    "code": "PY"
  },
  "Qatar": {
    "flag": "🇶🇦",
    "code": "QA"
  },
  "Réunion": {
    "flag": "🇷🇪",
    "code": "RE"
  },
  "Romania": {
    "flag": "🇷🇴",
    "code": "RO"
  },
  "Serbia": {
    "flag": "🇷🇸",
    "code": "RS"
  },
  "Russia": {
    "flag": "🇷🇺",
    "code": "RU"
  },
  "Rwanda": {
    "flag": "🇷🇼",
    "code": "RW"
  },
  "Saudi Arabia": {
    "flag": "🇸🇦",
    "code": "SA"
  },
  "Solomon Islands": {
    "flag": "🇸🇧",
    "code": "SB"
  },
  "Seychelles": {
    "flag": "🇸🇨",
    "code": "SC"
  },
  "Sudan": {
    "flag": "🇸🇩",
    "code": "SD"
  },
  "Sweden": {
    "flag": "🇸🇪",
    "code": "SE"
  },
  "Singapore": {
    "flag": "🇸🇬",
    "code": "SG"
  },
  "Saint Helena, Ascension and Tristan Da Cunha": {
    "flag": "🇸🇭",
    "code": "SH"
  },
  "Slovenia": {
    "flag": "🇸🇮",
    "code": "SI"
  },
  "Svalbard and Jan Mayen": {
    "flag": "🇸🇯",
    "code": "SJ"
  },
  "Slovakia": {
    "flag": "🇸🇰",
    "code": "SK"
  },
  "Sierra Leone": {
    "flag": "🇸🇱",
    "code": "SL"
  },
  "San Marino": {
    "flag": "🇸🇲",
    "code": "SM"
  },
  "Senegal": {
    "flag": "🇸🇳",
    "code": "SN"
  },
  "Somalia": {
    "flag": "🇸🇴",
    "code": "SO"
  },
  "Suriname": {
    "flag": "🇸🇷",
    "code": "SR"
  },
  "South Sudan": {
    "flag": "🇸🇸",
    "code": "SS"
  },
  "Sao Tome and Principe": {
    "flag": "🇸🇹",
    "code": "ST"
  },
  "El Salvador": {
    "flag": "🇸🇻",
    "code": "SV"
  },
  "Sint Maarten (Dutch Part)": {
    "flag": "🇸🇽",
    "code": "SX"
  },
  "Syria": {
    "flag": "🇸🇾",
    "code": "SY"
  },
  "Eswatini": {
    "flag": "🇸🇿",
    "code": "SZ"
  },
  "Turks and Caicos Islands": {
    "flag": "🇹🇨",
    "code": "TC"
  },
  "Chad": {
    "flag": "🇹🇩",
    "code": "TD"
  },
  "French Southern Territories": {
    "flag": "🇹🇫",
    "code": "TF"
  },
  "Togo": {
    "flag": "🇹🇬",
    "code": "TG"
  },
  "Thailand": {
    "flag": "🇹🇭",
    "code": "TH"
  },
  "Tajikistan": {
    "flag": "🇹🇯",
    "code": "TJ"
  },
  "Tokelau": {
    "flag": "🇹🇰",
    "code": "TK"
  },
  "Timor-Leste": {
    "flag": "🇹🇱",
    "code": "TL"
  },
  "Turkmenistan": {
    "flag": "🇹🇲",
    "code": "TM"
  },
  "Tunisia": {
    "flag": "🇹🇳",
    "code": "TN"
  },
  "Tonga": {
    "flag": "🇹🇴",
    "code": "TO"
  },
  "Turkey": {
    "flag": "🇹🇷",
    "code": "TR"
  },
  "Trinidad and Tobago": {
    "flag": "🇹🇹",
    "code": "TT"
  },
  "Tuvalu": {
    "flag": "🇹🇻",
    "code": "TV"
  },
  "Taiwan*": {
    "flag": "🇹🇼",
    "code": "TW"
  },
  "Tanzania": {
    "flag": "🇹🇿",
    "code": "TZ"
  },
  "Ukraine": {
    "flag": "🇺🇦",
    "code": "UA"
  },
  "Uganda": {
    "flag": "🇺🇬",
    "code": "UG"
  },
  "United States Minor Outlying Islands": {
    "flag": "🇺🇲",
    "code": "UM"
  },
  "United States of America": {
    "flag": "🇺🇸",
    "code": "US"
  },
  "Uruguay": {
    "flag": "🇺🇾",
    "code": "UY"
  },
  "Uzbekistan": {
    "flag": "🇺🇿",
    "code": "UZ"
  },
  "Holy See": {
    "flag": "🇻🇦",
    "code": "VA"
  },
  "Saint Vincent and the Grenadines": {
    "flag": "🇻🇨",
    "code": "VC"
  },
  "Venezuela": {
    "flag": "🇻🇪",
    "code": "VE"
  },
  "Virgin Islands, British": {
    "flag": "🇻🇬",
    "code": "VG"
  },
  "Virgin Islands, U.S.": {
    "flag": "🇻🇮",
    "code": "VI"
  },
  "Vietnam": {
    "flag": "🇻🇳",
    "code": "VN"
  },
  "Vanuatu": {
    "flag": "🇻🇺",
    "code": "VU"
  },
  "Wallis and Futuna": {
    "flag": "🇼🇫",
    "code": "WF"
  },
  "Samoa": {
    "flag": "🇼🇸",
    "code": "WS"
  },
  "Kosovo": {
    "flag": "🇽🇰",
    "code": "XK"
  },
  "Yemen": {
    "flag": "🇾🇪",
    "code": "YE"
  },
  "Mayotte": {
    "flag": "🇾🇹",
    "code": "YT"
  },
  "South Africa": {
    "flag": "🇿🇦",
    "code": "ZA"
  },
  "Zambia": {
    "flag": "🇿🇲",
    "code": "ZM"
  },
  "Zimbabwe": {
    "flag": "🇿🇼",
    "code": "ZW"
  },
  "Global": {
    "flag": "🌐",
    "code": "GBL"
  },
  "MS Zaandam": {
    "flag": "🛳",
    "code": "MSZ"
  }
}