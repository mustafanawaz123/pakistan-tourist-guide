import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'pakistan_tourism.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.executescript('''
        CREATE TABLE IF NOT EXISTS terrain_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            icon TEXT,
            color TEXT,
            gradient_start TEXT,
            gradient_end TEXT
        );
        CREATE TABLE IF NOT EXISTS cities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            terrain_type_id INTEGER,
            name TEXT NOT NULL,
            province TEXT,
            description TEXT,
            image_url TEXT,
            gallery_images TEXT,
            best_season TEXT,
            climate_info TEXT,
            local_food TEXT,
            accommodation_luxury TEXT,
            accommodation_standard TEXT,
            accommodation_budget TEXT,
            accommodation_backpacker TEXT,
            highlights TEXT,
            FOREIGN KEY(terrain_type_id) REFERENCES terrain_types(id)
        );
        CREATE TABLE IF NOT EXISTS attractions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city_id INTEGER,
            name TEXT NOT NULL,
            description TEXT,
            image_url TEXT,
            category TEXT,
            budget_levels TEXT,
            priority INTEGER DEFAULT 3,
            duration_hours REAL DEFAULT 2.0,
            time_of_day TEXT DEFAULT 'any',
            entry_fee_pkr INTEGER DEFAULT 0,
            tip TEXT,
            FOREIGN KEY(city_id) REFERENCES cities(id)
        );
        CREATE TABLE IF NOT EXISTS hotels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city_id INTEGER,
            name TEXT NOT NULL,
            budget_level TEXT DEFAULT 'standard',
            stars INTEGER DEFAULT 3,
            price_per_night_pkr INTEGER DEFAULT 5000,
            address TEXT,
            amenities TEXT,
            description TEXT,
            booking_tip TEXT,
            FOREIGN KEY(city_id) REFERENCES cities(id)
        );
    ''')
    conn.commit()

    # Clear existing data
    c.execute('DELETE FROM hotels')
    c.execute('DELETE FROM attractions')
    c.execute('DELETE FROM cities')
    c.execute('DELETE FROM terrain_types')
    c.execute('DELETE FROM sqlite_sequence WHERE name IN ("hotels","attractions","cities","terrain_types")')
    conn.commit()

    # ── TERRAIN TYPES ─────────────────────────────────────────────
    terrains = [
        (1, 'Mountains',        'Towering peaks, glaciers, and high-altitude passes of the Karakoram, Hindu Kush and Himalayas.', '⛰️', '#2d6a4f', '#1a4a3a', '#2d8a5e'),
        (2, 'Rivers',           'Mighty rivers like the Indus, Jhelum, and Chenab shaping civilization for millennia.',            '🌊', '#1e5f7a', '#1a3a6a', '#2d6ea4'),
        (3, 'Deserts',          'Vast sand dunes, ancient caravan routes, and nomadic culture across Cholistan and Thar.',         '🏜️', '#b5651d', '#6a3a1a', '#c49a38'),
        (4, 'Beaches',          'Pristine coastline along the Arabian Sea with turquoise waters and dramatic sea cliffs.',         '🏖️', '#0077b6', '#1a4a6a', '#00b4d8'),
        (5, 'Historical Sites', 'Millennia of civilization from Indus Valley to Mughal Empire preserved in stone and mortar.',     '🏛️', '#6a0dad', '#4a1a5a', '#8a2da4'),
        (6, 'Lakes',            'Crystal-clear mountain lakes fed by glaciers, ranging from sapphire blue to emerald green.',      '💧', '#0096c7', '#1a3a5a', '#2d7a9a'),
        (7, 'Valleys',          'Lush green valleys carpeted with wildflowers, fruit orchards, and ancient cultures.',             '🌿', '#2d8a5e', '#1a4a2a', '#4a9a3a'),
        (8, 'Wildlife & Forests','Dense juniper forests, snow leopard habitat, and rare biodiversity in protected national parks.','🦁', '#3a5a00', '#2a3a1a', '#4a6a1a'),
    ]
    c.executemany('INSERT INTO terrain_types(id,name,description,icon,color,gradient_start,gradient_end) VALUES(?,?,?,?,?,?,?)', terrains)
    conn.commit()

    # ── CITIES ────────────────────────────────────────────────────
    def city(tid, name, province, desc, img_seed, gallery_seeds, season, climate, food,
             lux, std, bud, bp, highlights):
        return (
            tid, name, province, desc,
            f'https://picsum.photos/seed/{img_seed}/800/500',
            json.dumps([f'https://picsum.photos/seed/{s}/800/500' for s in gallery_seeds]),
            season, climate, food, lux, std, bud, bp,
            json.dumps(highlights)
        )

    cities_data = [
        # Mountains (tid=1)
        city(1,'Skardu','Gilgit-Baltistan',
             'Skardu is the gateway to some of the world\'s highest peaks including K2 and Broad Peak. Nestled at 2,228 m on the Indus River, it blends dramatic desert landscapes with emerald lakes and ancient forts. A paradise for mountaineers, trekkers and photographers alike.',
             'skardu','skardu1 skardu2 skardu3 skardu4'.split(),
             'May–September','Cool summers (10-25°C), harsh winters with snowfall. Best visited May–Sep.','Chapshuro (buckwheat bread with apricot jam)',
             'Serena Skardu (luxury riverside resort)','Shangrila Resort standard rooms','Al-Haj Guest House','Mountain Backpackers Hostel',
             ['Gateway to K2 Base Camp','Satpara Lake turquoise waters','Cold Desert of Sarfaranga','Shigar Fort & Palace']),

        city(1,'Hunza','Gilgit-Baltistan',
             'Hunza Valley is arguably Pakistan\'s most breathtaking destination, flanked by Rakaposhi, Ultar Sar and Bojahagur peaks. Famous for its hospitable Wakhi and Burusho people, centuries-old Baltit and Altit forts, and legendary longevity of its residents. Cherry blossom season in April turns the valley pink and white.',
             'hunza','hunza1 hunza2 hunza3 hunza4'.split(),
             'April–October','Mild summers (15-28°C), cold winters. Famous April blossom season.','Diram (dried apricot soup with walnut)',
             'Serena Hunza (premium heritage hotel)','Eagle\'s Nest Hotel','Old Hunza Inn','Hunza Backpackers',
             ['Baltit Fort UNESCO heritage','Attabad Lake turquoise jewel','Rakaposhi view point','Cherry blossom festival April']),

        city(1,'Gilgit','Gilgit-Baltistan',
             'Gilgit is the capital of Gilgit-Baltistan and the main hub for adventure tourism in northern Pakistan. It sits at the confluence of three mighty mountain ranges: Karakoram, Hindu Kush, and Himalayas. The Karakoram Highway passes through here, connecting China to Pakistan.',
             'gilgit','gilgit1 gilgit2 gilgit3 gilgit4'.split(),
             'April–October','Warm dry summers (20-35°C), cold winters. Monsoon rarely reaches here.','Gilgiti Chappali Kebab with Hunza salty tea',
             'Gilgit Serena Hotel','Madina Hotel Gilgit','New Masherbrum Hotel','City Guest House Gilgit',
             ['Confluence of three mountain ranges','Kargah Buddha rock carving','Gilgit Bazaar local culture','Gateway to Karakoram Highway']),

        city(1,'Chitral','Khyber Pakhtunkhwa',
             'Chitral is a remote district nestled in the Hindu Kush, home to the unique Kalash people who maintain ancient pre-Islamic traditions. Tirich Mir, the world\'s highest Hindu Kush peak at 7,708 m, towers over the town. The Chitral Fort and bazaar reflect a rich blend of Central Asian and South Asian cultures.',
             'chitral','chitral1 chitral2 chitral3 chitral4'.split(),
             'May–September','Short cool summers, very cold winters with heavy snow. Lowari Pass can close.','Shandur Polo Festival food – mutton karahi',
             'Hindukush Heights Hotel','Chitral Inn','Shah Naz Hotel','Riverside Backpackers',
             ['Kalash Valleys and ancient culture','Tirich Mir peak views','Shandur Polo Festival (July)','Chitral Fort and Old Bazaar']),

        city(1,'Murree','Punjab',
             'Murree is Punjab\'s most beloved hill station, perched at 2,300 m in the Pir Panjal range. Its colonial-era Mall Road, pine forests, and panoramic Himalayan views make it ideal for a cool summer escape from the plains. Snow in winter transforms it into a festive family destination.',
             'murree','murree1 murree2 murree3 murree4'.split(),
             'October–March (snow), April–June (spring)','Cool year-round; snow Nov–Feb. Crowded in summer weekends.','Kashmiri Chai with Murree biscuits',
             'Pearl Continental Bhurban','Lockwood Hotel Murree','Sajid Guest House','Murree Youth Hostel',
             ['Mall Road colonial architecture','Pine forest walks','Pindi Point cable car','Snow activities in winter']),

        # Rivers (tid=2)
        city(2,'Attock','Punjab',
             'Attock sits at the confluence of the Indus and Kabul rivers, guarded by the magnificent 16th-century Attock Fort built by Emperor Akbar. The fort overlooks the dramatic meeting of the blue Kabul River and the muddy Indus. It was the historic gateway between the subcontinent and Central Asia.',
             'attock','attock1 attock2 attock3 attock4'.split(),
             'October–March','Hot summers (up to 45°C), mild winters. Best Oct–Mar.','Attock Saag with Makki ki Roti',
             'Margala Hotel Attock','Attock City Hotel','Green Valley Guest House','Backpacker Lodge Attock',
             ['Attock Fort (Akbar era)','Indus-Kabul river confluence','Historic bridge views','Camphor Garden ruins']),

        city(2,'Tarbela','Khyber Pakhtunkhwa',
             'Tarbela Dam is the world\'s largest earth-filled dam, impounding the mighty Indus River to create a vast reservoir. Built in 1976, it generates massive hydroelectric power for Pakistan. The reservoir and surrounding wetlands attract migratory birds and offer boating and fishing.',
             'tarbela','tarbela1 tarbela2 tarbela3 tarbela4'.split(),
             'October–April','Hot summers, pleasant winters. Avoid July–August monsoon flooding.','Tarbela Dam trout fish fry',
             'Tarbela Lake Resort','WAPDA Guest House Tarbela','Haripur City Hotel','Tarbela Camping Ground',
             ['World\'s largest earth dam','Tarbela Lake boating','Migratory bird watching','Power generation tunnels view']),

        city(2,'Sukkur','Sindh',
             'Sukkur is one of the oldest cities in Sindh, sitting on the right bank of the Indus River. The Lloyd Barrage (Sukkur Barrage) is an engineering marvel that transformed the Sindh desert into fertile farmland. The Sukkur island of Bukkur contains ancient ruins, and the city\'s busy bazaars are famous for sindhi embroidery.',
             'sukkur','sukkur1 sukkur2 sukkur3 sukkur4'.split(),
             'November–February','Extremely hot summers (up to 50°C). Only visit Oct–Mar.','Sindhi Biryani and Sai Bhaji',
             'Indus Hotel Sukkur','Hotel One Sukkur','Mehran Hotel Sukkur','Sukkur Budget Inn',
             ['Sukkur Barrage engineering marvel','Sadhu Belo Hindu temple island','Sat Manzil historical tower','Indus River boat rides']),

        city(2,'Kalabagh','Punjab',
             'Kalabagh is a historic town on the west bank of the Indus in the Mianwali district, surrounded by the Salt Range hills. The town has ancient salt mines nearby and a picturesque setting where the Indus cuts through rocky gorges. Its old bazaar preserves traditional crafts.',
             'kalabagh','kalabagh1 kalabagh2 kalabagh3 kalabagh4'.split(),
             'October–March','Hot summers, mild winters. Salt Range area best in spring.','Mianwali Dumba Karahi (ram meat)',
             'Indus View Hotel Mianwali','Kalabagh Guest House','Salt Range Rest House','Riverside Camping Kalabagh',
             ['Indus gorge rock formations','Kalabagh Salt Range mines','Ancient Indus riverboat culture','Nili Bar wetland birds']),

        city(2,'Rohri','Sindh',
             'Rohri is the twin city of Sukkur across the Indus, connected by the Lansdowne Bridge. The city hosts the famous Shrine of Khwaja Khizr on Bukkar Island, a unique mosque on a rocky Indus island venerated for centuries. Fossil hunting in the nearby limestone hills is popular.',
             'rohri','rohri1 rohri2 rohri3 rohri4'.split(),
             'November–February','Extreme heat in summer. Best November–February.','Rohri Fish Tikka (Indus catfish)',
             'Sukkur Serena (nearby)','Hotel Mehran Rohri','Rohri City Lodge','River View Backpackers',
             ['Khwaja Khizr shrine on river island','Lansdowne Bridge historic span','Fossil limestone hills','Indus delta wetlands']),

        # Deserts (tid=3)
        city(3,'Bahawalpur','Punjab',
             'Bahawalpur is the gateway to the Cholistan Desert, one of Pakistan\'s richest cultural cities with stunning Noor Mahal palace. The former princely state boasts magnificent Nawab-era palaces, the Derawar Fort rising from the desert sands, and the Cholistan Jeep Rally — one of Asia\'s biggest off-road events.',
             'bahawalpur','bahawalpur1 bahawalpur2 bahawalpur3 bahawalpur4'.split(),
             'November–February','Extremely hot summers (50°C+). Only visit Nov–Feb for comfortable weather.','Siri Paye (goat trotters) and Bahawalpur Sajji',
             'Noor Mahal Heritage Hotel','Hotel One Bahawalpur','Al-Farooq Hotel','Desert Youth Hostel',
             ['Derawar Fort in Cholistan Desert','Noor Mahal palace','Cholistan Jeep Rally (Feb)','Lal Suhanra National Park']),

        city(3,'Umarkot','Sindh',
             'Umarkot (Amarkot) is a historic desert town in Tharparkar, famous as the birthplace of Emperor Akbar. Its ancient fort once protected the Thar Desert trade routes. The surrounding Thar Desert is dotted with Hindu temples, colourful villages, and the unique culture of the Thari people.',
             'umarkot','umarkot1 umarkot2 umarkot3 umarkot4'.split(),
             'November–February','Very hot summers. The Thar becomes colourful post-monsoon (Sept–Oct) too.','Thari Laddoo (millet sweet) and Kerhi (buttermilk curry)',
             'Thar Desert Resort Umarkot','Hotel Rajput Umarkot','Umarkot Rest House','Desert Camping Thar',
             ['Umarkot Fort (Akbar\'s birthplace)','Thar Desert camel safari','Hindu temples of Tharparkar','Thari folk music and embroidery']),

        city(3,'Mithi','Sindh',
             'Mithi is the capital of Tharparkar district, the only district in Pakistan with a Hindu majority, creating a unique Hindu-Muslim cultural fusion in the Thar Desert. The town is known for colourful handicrafts, intricate mirror embroidery, and a community where both Eid and Diwali are celebrated together.',
             'mithi','mithi1 mithi2 mithi3 mithi4'.split(),
             'November–January','Desert heat is extreme April–September. Visit only in winter.','Mithi Seero (wheat sweet) and Ghee Rotla',
             'Desert Pearl Hotel Mithi','Mithi Guest House','PWD Rest House Mithi','Desert Tent Camping',
             ['Hindu-Muslim harmony culture','Mirror embroidery handicrafts','Thar Desert sand dunes','Ancient stepwells (vav)']),

        city(3,'Rahim Yar Khan','Punjab',
             'Rahim Yar Khan district borders the Cholistan Desert and Rajasthan, containing rich archaeological sites and the Lal Suhanra National Park. The city is a commercial hub with connections to the Cholistan jeep tracks. The Pir Saddar Din shrine and old fort ruins attract heritage visitors.',
             'rahimyarkhan','rahimyarkhan1 rahimyarkhan2 rahimyarkhan3 rahimyarkhan4'.split(),
             'November–February','Very hot summers. Winter is mild and pleasant for desert exploration.','Seraiki Saji (whole roasted chicken/lamb)',
             'Margalla Hotel RYK','Hotel One Rahim Yar Khan','Gulshan Hotel RYK','Budget Inn RYK',
             ['Lal Suhanra National Park','Cholistan Desert edge jeep rides','Pir Saddar Din shrine','Bahawal Victoria Hospital heritage building']),

        # Beaches (tid=4)
        city(4,'Karachi','Sindh',
             'Karachi is Pakistan\'s largest city and commercial capital, home to 20 million people on the Arabian Sea coast. Its beaches — Clifton, Seaview, Hawkes Bay, French Beach — stretch for kilometres. The city mixes cosmopolitan energy, Mughal-era mosques, colonial architecture, and one of Asia\'s largest fish harbours.',
             'karachi','karachi1 karachi2 karachi3 karachi4'.split(),
             'November–March','Humid coastal city; winters mild (15-25°C), summers hot and humid (30-38°C).','Karachi Biryani and Bun Kebab',
             'Pearl Continental Karachi','Marriott Karachi','Budget Inn Clifton','Karachi Youth Hostel',
             ['Clifton Beach and Sea View','Empress Market colonial bazaar','Mohatta Palace museum','Karachi Fish Harbour seafood']),

        city(4,'Gwadar','Balochistan',
             'Gwadar is Pakistan\'s strategic deep-sea port city on the Makran Coast, being developed into a major hub under CPEC. Its pristine beaches, Hammerhead cliff, and surrounding lunar-like landscape are stunning. The turquoise waters and golden cliffs create surreal scenery unlike anywhere else in Pakistan.',
             'gwadar','gwadar1 gwadar2 gwadar3 gwadar4'.split(),
             'October–April','Hot and humid summers. Winters mild (20-28°C), ideal for beach visits.','Gwadar Sajji (whole fish) and Crab curry',
             'PC Gwadar (planned luxury)','Beach Luxury Hotel Gwadar','Marina Lodge Gwadar','CPEC Guesthouse Gwadar',
             ['Hammerhead cliff panorama','Gwadar Port CPEC development','Ormara turtle beach nearby','Pishukan mangroves']),

        city(4,'Ormara','Balochistan',
             'Ormara is a quiet fishing town on the Makran Coast with spectacular untouched beaches and the famous turtle nesting sites. The golden sand beaches, dramatic sea stacks, and clear turquoise water make it a hidden gem. Green sea turtles come ashore to nest here from November to January.',
             'ormara','ormara1 ormara2 ormara3 ormara4'.split(),
             'October–March','Mild winters perfect for beach camping. Avoid May–August extreme heat.','Ormara Grilled Fish and Makrani Pulao',
             'Ormara Beach Bungalows','Fisherman\'s Inn Ormara','Coastal Rest House Ormara','Beach Camping Ormara',
             ['Sea turtle nesting (Nov–Jan)','Pristine untouched beaches','Sea stack rock formations','Makran Coastal Highway drive']),

        city(4,'Kund Malir','Balochistan',
             'Kund Malir is the most celebrated beach on the Makran Coast, featuring 25 km of golden sand flanked by ochre and rust-coloured hills plunging into turquoise sea. Considered one of the most beautiful beaches in Asia, it has no permanent settlement, preserving its wild pristine character.',
             'kundmalir','kundmalir1 kundmalir2 kundmalir3 kundmalir4'.split(),
             'November–February','Ideal winter beach weather (20-30°C). Extremely hot May–September.','BBQ fresh catch fish on beach',
             'Beach Camping only (luxury tents available)','Kund Malir Camping','Roadside Dhaba stay','Wild Beach Camping',
             ['25 km pristine golden beach','Rust-coloured cliff backdrop','Crystal turquoise Arabian Sea','Pakistan\'s most photogenic beach']),

        # Historical (tid=5)
        city(5,'Lahore','Punjab',
             'Lahore is Pakistan\'s cultural heart and second-largest city, the seat of Mughal grandeur and Sikh heritage. Walled City of Lahore, Lahore Fort (Shahi Qila), Badshahi Mosque, and Shalimar Gardens are UNESCO World Heritage Sites. Its food street culture, vibrant bazaars, and arts scene make it South Asia\'s most energetic cultural capital.',
             'lahore','lahore1 lahore2 lahore3 lahore4'.split(),
             'October–March','Hot summers (40°C+), foggy winters (5-15°C). Best October–March.','Lahori Chargha, Paya, and Nihari',
             'Pearl Continental Lahore','Avari Hotel Lahore','Regent Plaza Lahore','Lahore Old City Hostel',
             ['Lahore Fort & Sheesh Mahal','Badshahi Mosque (17th century)','Gawalmandi Food Street','Wagah Border Flag ceremony']),

        city(5,'Taxila','Punjab',
             'Taxila is one of the most important archaeological sites in Asia, a UNESCO World Heritage Site that was a major centre of Buddhist civilization from the 5th century BC to the 2nd century AD. The site contains ruins of three cities spanning 1,000 years, with thousands of artifacts displayed in the Taxila Museum.',
             'taxila','taxila1 taxila2 taxila3 taxila4'.split(),
             'October–April','Mild climate. Avoid June–August heat. Spring and autumn ideal.','Taxila Daal Mash and Chapli Kebab',
             'Holiday Inn Express Islamabad (nearby)','Taxila Museum Guest House','Wah Cantt Hotel','Youth Hostel Taxila',
             ['Taxila UNESCO Archaeological Complex','Taxila Museum (Gandhara art)','Jaulian Monastery ruins','Sirkap ancient city ruins']),

        city(5,'Larkana','Sindh',
             'Larkana district contains Mohenjo-daro, one of the world\'s first planned cities built around 2500 BC by the Indus Valley Civilization. The UNESCO World Heritage Site\'s brick-paved streets, drainage systems, and Great Bath reveal an astonishing urban civilization predating Rome by 2,000 years. The site museum houses remarkable bronze-age artifacts.',
             'larkana','larkana1 larkana2 larkana3 larkana4'.split(),
             'November–February','Extreme heat April–September. Only visit in winter.','Larkana Sindhi Curry and Sajji',
             'Indus Hotel Larkana','Hotel Mehran Larkana','Al-Murtaza Hotel Larkana','Traveller Rest House Larkana',
             ['Mohenjo-daro UNESCO World Heritage','Great Bath of Indus civilization','Mohenjo-daro Museum artifacts','Indus Valley brick architecture']),

        city(5,'Peshawar','Khyber Pakhtunkhwa',
             'Peshawar is one of Asia\'s oldest continuously inhabited cities, at the eastern gateway of the Khyber Pass. Its Old City bazaars — Qissa Khwani (Storytellers\' Bazaar), Copper Bazaar, and Cloth Market — have been trading for 2,500 years. The Peshawar Museum houses the world\'s finest Gandhara Buddhist sculpture collection.',
             'peshawar','peshawar1 peshawar2 peshawar3 peshawar4'.split(),
             'October–April','Hot summers (42°C), cool winters. Best October–April.','Peshawar Kabuli Pulao and Chapli Kebab',
             'Pearl Continental Peshawar','Islamabad Hotel Peshawar','Shelton\'s Rezidor Hotel','Old City Guesthouse Peshawar',
             ['Qissa Khwani Bazaar storytellers','Peshawar Museum Gandhara art','Bala Hisar Fort','Khyber Pass visit (permit needed)']),

        city(5,'Multan','Punjab',
             'Multan is called the "City of Saints" for its hundreds of Sufi shrines, most notably the spectacular Shrine of Bahauddin Zakariya and Shah Rukn-e-Alam. One of the subcontinent\'s oldest cities (over 5,000 years), its famous blue glazed pottery, mango orchards, and Sufi qawwali music culture make it unmissable.',
             'multan','multan1 multan2 multan3 multan4'.split(),
             'October–March','Extreme heat (50°C in June); excellent winter weather Oct–Mar.','Multani Sohan Halwa and Multani Karahi',
             'Ramada by Wyndham Multan','Sindbad Hotel Multan','Al-Madina Hotel Multan','Multan Backpackers Inn',
             ['Shah Rukn-e-Alam shrine (14th cent.)','Multan Fort Qila Kohna Qasim Bagh','Blue glazed pottery workshops','Hussain Agahi Bazaar']),

        # Lakes (tid=6)
        city(6,'Naran','Khyber Pakhtunkhwa',
             'Naran is the base camp for Saif-ul-Muluk Lake, the most photographed lake in Pakistan, set against the fairy-tale backdrop of Malika Parbat (5,291 m). The Kaghan Valley town sits at 2,409 m and is surrounded by alpine meadows, glaciers, and dense pine forests. It\'s one of Pakistan\'s most visited mountain resorts.',
             'naran','naran1 naran2 naran3 naran4'.split(),
             'June–September','Very cold winters; road opens May. Summer 10-22°C. Busy July–Aug.','Kaghan Valley trout fish with Naan',
             'Lalazar Hotel Naran','Pine Park Hotel Naran','Naran Guest House','Valley View Backpackers',
             ['Saif-ul-Muluk Lake (fairy-tale setting)','Babusar Pass (4,173 m)','Lulusar Lake alpine meadows','White-water rafting Kunhar River']),

        city(6,'Gojal/Attabad','Gilgit-Baltistan',
             'Attabad Lake was formed in 2010 when a catastrophic landslide blocked the Hunza River, creating a 20 km long turquoise lake of stunning beauty. The lake\'s milky turquoise color from glacial flour is otherworldly. The boat journey through the lake and into PTDC tunnels is one of Pakistan\'s most dramatic travel experiences.',
             'attabad','attabad1 attabad2 attabad3 attabad4'.split(),
             'April–October','Access via boat or KKH tunnels. Cold winters close upper Hunza.','Wakhi Bread (Garmino) with Yak butter tea',
             'Attabad Lake Resort (luxury tents)','Gojal Inn','Upper Hunza Guest House','Lakeside Camping Attabad',
             ['Attabad turquoise lake boat ride','PTDC KKH tunnels through the lake','Borith Lake nearby','Khunjerab Pass (75 km north)']),

        city(6,'Islamabad','Islamabad Capital Territory',
             'Islamabad, Pakistan\'s modern capital, is built at the foot of the Margalla Hills, giving it parks, hiking trails, and man-made Rawal Lake within the city. Designed by architect Constantinos Doxiadis in the 1960s, its grid layout, wide tree-lined boulevards, Faisal Mosque (one of the world\'s largest), and Shakarparian Park make it one of South Asia\'s greenest capitals.',
             'islamabad','islamabad1 islamabad2 islamabad3 islamabad4'.split(),
             'October–April','Mild climate; hot June–August; pleasant spring and autumn. Monsoon July–Aug.','Potohari Siri Paye and Islamabad Dahi Baray',
             'Serena Hotel Islamabad','Marriott Islamabad','Envoy Continental Hotel','Capital Backpackers Islamabad',
             ['Faisal Mosque (world\'s largest)','Margalla Hills hiking trails','Lok Virsa Museum folk heritage','Pakistan Monument panorama']),

        city(6,'Upper Dir','Khyber Pakhtunkhwa',
             'Upper Dir district in KPK contains the stunning Kumrat Valley with pristine lakes like Jahaz Banda and Patigai Lake, surrounded by dense Deodar cedar forests. This relatively undiscovered gem has clear streams, alpine meadows, and traditional Dardic culture. The forests are some of Pakistan\'s finest.',
             'upperdir','upperdir1 upperdir2 upperdir3 upperdir4'.split(),
             'May–September','Road access improves May–October. Alpine climate, cold nights even in summer.','Dir-style thick chapli kebab with green chutney',
             'Kumrat Valley Resort','Jahaz Banda Camp','Dir Rest House','Forest Camping Upper Dir',
             ['Kumrat Valley dense cedar forest','Jahaz Banda alpine plateau','Patigai Lake crystal waters','Traditional Dardic Kohistani villages']),

        # Valleys (tid=7)
        city(7,'Swat','Khyber Pakhtunkhwa',
             'Swat is called the "Switzerland of Pakistan" for its lush green mountains, white-water rivers, skiing in Malam Jabba, and Buddhist ruins at Butkara and Udegram. The Swat River valley is lined with apple orchards, trout streams, and the scenic resort town of Kalam at its head. Its Gandhara Buddhist heritage is extraordinary.',
             'swat','swat1 swat2 swat3 swat4'.split(),
             'April–October','Pleasant summers (15-28°C). Skiing possible Jan–Feb at Malam Jabba.','Swati Trout and Chapli Kebab',
             'Serena Swat Hotel','Miandam Holiday Home','Swat Hotel Mingora','Kalam Backpackers Inn',
             ['Malam Jabba ski resort','Kalam Valley alpine meadows','Butkara Stupa Buddhist ruins','Swat Museum Gandhara treasures']),

        city(7,'Kaghan','Khyber Pakhtunkhwa',
             'Kaghan Valley stretches 155 km from Balakot to Babusar Pass, rising from subtropical forests to arctic alpine tundra. The Kunhar River rushes through, creating spectacular gorges and waterfalls. Shogran plateau offers panoramic Himalayan views, and the valley is famous for trout fishing, jeep safaris, and crisp mountain air.',
             'kaghan','kaghan1 kaghan2 kaghan3 kaghan4'.split(),
             'May–September','Road to Naran opens May–June. Alpine climate. Babusar Pass July–Sept only.','Kaghan Trout fry with Naan and salad',
             'Shogran Cottages (luxury chalets)','Kiwai Hotel Kaghan','Balakot Guest House','Riverside Camping Kaghan',
             ['Shogran plateau panoramic views','Kunhar River white-water rafting','Lulusar Lake emerald waters','Babusar Pass (4,173 m) trekking']),

        city(7,'Neelum Valley','Azad Jammu & Kashmir',
             'Neelum Valley is AJK\'s crown jewel, a 200 km ribbon of emerald green valleys, rivers, and snow-capped peaks along the Line of Control. The Neelum River with its turquoise waters, dense forests, and traditional Kashmiri villages create scenes of extraordinary beauty. Arang Kel, accessible only by cable car, is nicknamed "Heaven on Earth".',
             'neelum','neelum1 neelum2 neelum3 neelum4'.split(),
             'April–October','Lush spring and summer. Road can close in winter. Best July–September.','Kashmiri Kehwa tea with Kashmiri Wazwan',
             'Kera Lake Resort Neelum','Sharda Valley Hotel','Keran Guest House AJK','Arang Kel Camping',
             ['Arang Kel "Heaven on Earth"','Sharda ancient university ruins','Ratti Gali Lake alpine trekking','Neelum River emerald waters']),

        city(7,'Kalash Valleys','Khyber Pakhtunkhwa',
             'The Kalash Valleys (Bumburet, Rumbur, Birir) near Chitral are home to the Kalash people, an indigenous group with ancient polytheistic traditions, colorful dress, and unique festivals. Their festivals of Chilam Joshi (spring) and Uchal (summer) are among Pakistan\'s most vibrant cultural experiences. The lush valleys contrast dramatically with the surrounding Hindu Kush peaks.',
             'kalash','kalash1 kalash2 kalash3 kalash4'.split(),
             'May–October (festivals: May, Aug, Dec)','Remote mountain valleys; mild summers. Best visit during Chilam Joshi (May).','Kalash Walnut bread and Wine (local tradition)',
             'Kalash Cultural Centre Guesthouse','Bumburet Valley Inn','Community Guesthouse Rumbur','Kalash Camping',
             ['Chilam Joshi spring festival','Traditional Kalash dress and dance','Ancient Kalash wooden shrines','Unique pre-Islamic Kalash culture']),

        # Wildlife (tid=8)
        city(8,'Ziarat','Balochistan',
             'Ziarat is Balochistan\'s scenic hill station set in the world\'s second-largest juniper forest, with trees up to 5,000 years old. The cool climate, Afghan-style architecture, and the Residency where Quaid-e-Azam Muhammad Ali Jinnah spent his final days make it historically significant. In spring, the hills burst with wildflowers.',
             'ziarat','ziarat1 ziarat2 ziarat3 ziarat4'.split(),
             'May–September','Cool summers (10-20°C) in contrast to hot Balochistan plains. Snow in winter.','Ziarat Apple and dried fruits; Balochi Sajji',
             'Ziarat Residency Hotel','Forest Rest House Ziarat','PTDC Motel Ziarat','Ziarat Youth Hostel',
             ['Ancient 5,000-year-old juniper forest','Quaid-e-Azam Residency museum','Ziarat valley wildflower meadows','Kach Desert contrast nearby']),

        city(8,'Ayubia','Khyber Pakhtunkhwa',
             'Ayubia National Park near Murree protects dense oak, pine, and rhododendron forests in the Galis hill stations. The park is home to leopards, barking deer, yellow-throated martens, and hundreds of bird species. The famous Ayubia Chair Lift and the Pipeline Track through forest canopy are popular activities.',
             'ayubia','ayubia1 ayubia2 ayubia3 ayubia4'.split(),
             'April–October','Cool and green; beautiful autumn foliage. Snow in winter.','Kaghan trout; Galis-style Handi gosht',
             'Pine Hills Hotel Ayubia','Jungle Inn Ayubia','Forest Rest House Nathiagali','Ayubia Camping Ground',
             ['Ayubia Chair Lift forest ride','Pipeline Track wildlife walk','Leopard habitat jungle trails','Nathiagali hill station views']),

        city(8,'Deosai','Gilgit-Baltistan',
             'Deosai National Park is the world\'s second-highest plateau at 4,114 m, a vast treeless highland of wildflowers, rushing streams, and golden eagles. It is one of the last strongholds of the Himalayan Brown Bear. In July and August the entire plateau carpets with wildflowers in a display of colour seen nowhere else in Pakistan.',
             'deosai','deosai1 deosai2 deosai3 deosai4'.split(),
             'July–September','Plateau only accessible July–September. Extreme cold and snow rest of year.','Camp-cooked Daal Chawal; Skardu provisions',
             'Luxury Camping Deosai (glamping tents)','PTDC Camp Deosai','Basic Camping','Wild Camping Deosai',
             ['July wildflower carpet (world-class)','Himalayan Brown Bear sightings','Sheosar Lake high-altitude','Golden eagle and lammergeier raptors']),

        city(8,'Naltar','Gilgit-Baltistan',
             'Naltar Valley is a hidden gem 40 km from Gilgit with dense pine forests, unique blue, green and emerald coloured lakes, and a ski slope used by the Pakistan Army ski team. The Naltar Lakes at 3,578 m display extraordinary colours from minerals. In winter it transforms into Pakistan\'s best ski destination.',
             'naltar','naltar1 naltar2 naltar3 naltar4'.split(),
             'June–September (summer); January–March (skiing)','High altitude valley; cool summers, heavy snow winters. Jeep required.','Hunza-style Chapshuro with Diram apricot jam',
             'Naltar Cottage Resort','PAF Guest House Naltar','Naltar Village Inn','Forest Camping Naltar',
             ['Naltar tri-coloured lakes (blue/green/emerald)','Naltar Ski Resort (Pakistan\'s best)','Dense pine and fir forest walks','Golden eagle and snow leopard habitat']),
    ]

    cols = ('terrain_type_id','name','province','description','image_url','gallery_images',
            'best_season','climate_info','local_food',
            'accommodation_luxury','accommodation_standard','accommodation_budget','accommodation_backpacker',
            'highlights')
    placeholders = ','.join(['?']*len(cols))
    c.executemany(f'INSERT INTO cities({",".join(cols)}) VALUES({placeholders})', cities_data)
    conn.commit()

    # Build city name→id map
    c.execute('SELECT id, name FROM cities')
    city_map = {row['name']: row['id'] for row in c.fetchall()}

    # ── ATTRACTIONS ───────────────────────────────────────────────
    def att(city_name, name, desc, slug, category, budget_levels, priority, duration, tod, fee, tip):
        return (
            city_map[city_name], name, desc,
            f'https://picsum.photos/seed/{slug}/600/400',
            category,
            json.dumps(budget_levels),
            priority, duration, tod, fee, tip
        )

    attractions_data = [

        # SKARDU
        att('Skardu','Satpara Lake','A stunning turquoise lake at 2,636 m fed by glacial streams, surrounded by barren mountains and rich in rainbow trout. The lake is a key water reservoir for Skardu and a perfect picnic and boating spot.','satparalake','nature',['all'],1,3.0,'morning',200,'Hire a boat for PKR 500 for a lake tour; best light is early morning.'),
        att('Skardu','Shangrila Resort / Lower Kachura Lake','One of Pakistan\'s most photographed spots, Shangrila Resort sits on the shore of emerald Lower Kachura Lake with a plane-shaped restaurant. The lakeside gardens and mountain reflections are magical.','shangrila','nature',['all'],1,3.0,'morning',300,'Arrive before 9am to beat tour groups; the café serves excellent trout breakfast.'),
        att('Skardu','Shigar Fort','A 420-year-old Raja\'s fort converted into a heritage hotel, featuring intricately carved wooden ceilings, apricot orchards, and mountain views. Even non-guests can tour the public areas and gardens.','shigarfort','culture',['all'],2,2.0,'afternoon',500,'Book lunch at the fort restaurant—best local Balti cuisine in the area.'),
        att('Skardu','Sarfaranga Cold Desert','Pakistan\'s only cold desert at 2,226 m, a dramatic landscape of golden sand dunes ringed by snow-capped peaks. Jeep drives, camel rides, and ATV rides are available.','sarfaranga','adventure',['all'],2,3.0,'morning',0,'Visit at sunrise for the best golden hour light on the dunes; temperatures drop sharply after sunset.'),
        att('Skardu','Buddha Rock Carvings','7th-century rock carvings near Satpara depicting the Buddha and inscriptions in Brahmi script, among the oldest Buddhist rock art in Pakistan. A quiet, spiritual historical site.','buddharock','culture',['all'],3,1.5,'morning',0,'A guide from Skardu city can explain the historical context; the site is a 20-min drive from town.'),
        att('Skardu','Deosai National Park','The world\'s second-highest plateau accessible as a day trip from Skardu. July wildflower carpet is world-class; Himalayan Brown Bears are often spotted at Sheosar Lake.','deosaipark','nature',['all'],1,8.0,'morning',300,'Full day jeep trip; depart by 6am to maximize wildlife sightings; bring warm clothing even in July.'),

        # HUNZA
        att('Hunza','Baltit Fort','A 700-year-old fort perched high above Karimabad, the ancestral seat of the Mirs of Hunza. Its Tibetan-influenced architecture, carved wooden galleries, and panoramic views over the Hunza Valley to Rakaposhi are unforgettable.','baltitfort','culture',['all'],1,2.5,'morning',600,'Go early morning when Rakaposhi turns pink in the rising sun; excellent local guide available at the fort.'),
        att('Hunza','Attabad Lake','A 21 km turquoise lake formed by a 2010 landslide. Its vivid turquoise color from glacial minerals makes it one of the most photographed lakes in Pakistan. Boat rides reveal submerged villages.','attabadlake','nature',['all'],1,3.0,'morning',300,'Boat hire PKR 800 per person for a 40-min scenic cruise; paddle boats also available.'),
        att('Hunza','Altit Fort','The older sister of Baltit Fort at 900 years old, recently restored by the Aga Khan Trust. Its wooden architecture and the old village (Altit Village) below with traditional stone houses are fascinating.','altitfort','culture',['all'],2,2.0,'afternoon',400,'The attached café serves excellent Hunzai mulberry tea; visit after Baltit for complementary perspectives.'),
        att('Hunza','Rakaposhi Viewpoint','Diran Base Camp at Minapin village offers one of the world\'s most accessible views of an 8,000 m peak—Rakaposhi (7,788 m) fills the entire sky. A short hike to the moraine gives even closer views.','rakaposhi','nature',['all'],1,2.0,'morning',0,'Best viewed before 10am before clouds form; Diran Base Camp 2-hour hike from Minapin for serious trekkers.'),
        att('Hunza','Ganish Village Heritage Walk','The oldest village in Hunza, with 900-year-old watchtowers, shrines, and a Persian-inscribed mosque. Walking its narrow lanes with a local guide is one of the best cultural experiences in northern Pakistan.','ganishvillage','culture',['all'],2,2.0,'afternoon',200,'Hire a local guide at the village entrance; the teahouse serves excellent Hunzai dry-fruit tea.'),

        # GILGIT
        att('Gilgit','Kargah Buddha','A 7th-century rock carving of a standing Buddha, 10 m tall, carved into a cliff face above the Kargah Nullah gorge. It is the largest and best preserved Buddha carving in the Gilgit-Baltistan region.','kargahbuddha','culture',['all'],1,1.5,'morning',0,'The 1 km walk along the gorge to the carving is itself scenic; best photographic light in morning.'),
        att('Gilgit','Gilgit Bazaar & Local Market','The vibrant main bazaar of Gilgit where traders from Central Asia, China, and the subcontinent have traded for centuries. Fresh apricots, dried fruits, local wool handicrafts, and Chitrali caps are highlights.','gilgitbazaar','shopping',['all'],2,2.0,'afternoon',0,'Bargain hard; best time 3-6pm when all shops are open; try the fresh-pressed pomegranate juice.'),
        att('Gilgit','Gilgit River Suspension Bridge','A historic suspension bridge over the fast-flowing Gilgit River with swaying wooden planks—crossing it is a rite of passage for visitors. Views of the jade-green river gorge are dramatic.','gilgitbridge','adventure',['budget','backpacker','standard'],3,1.0,'any',0,'The bridge leads to a quiet village—explore the apricot orchards on the far bank.'),
        att('Gilgit','Naltar Valley Day Trip','40 km from Gilgit, Naltar Valley has tri-coloured lakes (blue, green, emerald), dense pine forest, and Pakistan\'s top ski slope. An essential day trip from Gilgit.','naltar','nature',['all'],1,8.0,'morning',0,'Hire a 4WD jeep from Gilgit bazaar for about PKR 4,000; bring warm layers as temperature drops significantly.'),

        # CHITRAL
        att('Chitral','Kalash Valleys (Bumburet)','The living cultural heritage of the Kalash people, 40 km from Chitral—colorful wooden houses, ancient stone shrines, and a unique pre-Islamic polytheistic culture survive here. Chilam Joshi festival in May is extraordinary.','kalashvalley','culture',['all'],1,4.0,'morning',500,'Hire a local Kalash guide from the cultural centre; photography requires permission and respect for customs.'),
        att('Chitral','Chitral Fort','The imposing fort of the Mehtars of Chitral, built on a high bluff above the Chitral River. The fort museum houses weapons, royal regalia, and photographs of the historic 1895 Chitral Siege.','chitralfort','culture',['all'],2,2.0,'morning',300,'The view from the fort battlements over the Chitral Valley to Tirich Mir is exceptional on clear days.'),
        att('Chitral','Shandur Pass & Polo Festival','Shandur Pass at 3,700 m is the world\'s highest polo ground, hosting the annual Shandur Polo Festival in July when Chitral and Gilgit teams compete in the shadow of snow peaks.','shandurpass','culture',['all'],1,6.0,'morning',0,'Festival in early July—book accommodation months in advance; the jeep road from Chitral is scenic.'),
        att('Chitral','Shahi Mosque Chitral','A beautiful old Friday mosque in the heart of Chitral bazaar with carved wooden pillars and traditional Chitrali architecture. The surrounding bazaar sells unique Chitrali embroidered caps and woollen products.','shahmosquechitral','spiritual',['all'],3,1.0,'morning',0,'Visit during early morning prayer time for atmospheric experience; non-Muslims welcome outside prayer times.'),

        # MURREE
        att('Murree','Mall Road Murree','Murree\'s colonial-era promenade with Victorian-style shops, food stalls, toy train rides, and panoramic Himalayan views. The 19th-century churches and old British Raj buildings are charming.','murreemall','culture',['all'],1,2.5,'afternoon',0,'Evenings are magical when the bazaar lights up; avoid weekends for smaller crowds.'),
        att('Murree','Pindi Point Cable Car','A 1.5 km cable car ride over dense pine forests from Murree to Pindi Point, with panoramic views over Murree hills. The summit has paragliding in summer and sledding in winter.','pindipoint','adventure',['all'],2,2.0,'morning',600,'Book cable car tickets in advance during summer; less crowded on weekday mornings.'),
        att('Murree','Patriata (New Murree)','3 km from Murree, Patriata has a chair lift and cable car offering views over the Pir Panjal range. In winter it becomes a snow play zone; in summer it has mountain biking trails.','patriata','adventure',['all'],2,2.0,'afternoon',800,'The chair lift up to Patriata summit gives 360-degree Himalayan panoramas; carry a jacket even in summer.'),
        att('Murree','Pine Forest Walks','The dense pine forests around Murree have trails through Ghora Gali, Sunny Bank, and Changla Gali, offering wildlife spotting (monkeys, deer) and cool shade in summer.','mureeforest','nature',['all'],2,2.0,'morning',0,'The trail to Ghora Gali (3 km) is well-marked; hire a guide for the longer trails to Nathiagali.'),

        # ATTOCK
        att('Attock','Attock Fort','A magnificent Mughal fort built by Emperor Akbar in 1581 at the confluence of Indus and Kabul rivers. The fort has 15 m high walls, royal chambers, and commanded the historic crossing point into the subcontinent.','attockfort','culture',['all'],1,2.5,'morning',200,'Entry permit needed from military as it\'s still active; the view of river confluence from ramparts is extraordinary.'),
        att('Attock','Indus-Kabul River Confluence','The point where the blue Kabul River meets the brown Indus—visible from the Attock Bridge. The colour contrast of the two rivers merging is a natural spectacle seen from the old bridge.','indusconfluence','nature',['all'],1,1.5,'morning',0,'Best viewed from the old colonial-era bridge on foot; photography is permitted from the public bridge.'),
        att('Attock','Hasan Abdal (Panja Sahib)','The Sikh holy Gurdwara of Panja Sahib in nearby Hasan Abdal is one of the holiest sites in Sikhism. The handprint of Guru Nanak Dev Ji preserved in stone and the serene tank make it remarkable.','panjasakib','spiritual',['all'],2,2.0,'morning',0,'International Sikh pilgrims visit year-round; the Gurdwara serves free langar (community meal) to all visitors.'),
        att('Attock','Camphor Garden Ruins','The ruins of a Mughal-era garden palace near the Attock Fort, with traces of water channels and pavilion foundations set in a tranquil riverside setting.','camphorgardenattock','culture',['budget','backpacker','standard'],4,1.0,'afternoon',0,'Combine with Attock Fort visit for a half-day Mughal history tour.'),

        # TARBELA
        att('Tarbela','Tarbela Dam Viewpoint','The world\'s largest earth-filled dam—238 m high, 2,743 m long—creates a dramatic industrial landscape. The WAPDA viewing platform offers stunning views over the vast blue reservoir.','tarbeladam','nature',['all'],1,2.0,'morning',0,'Entry requires permission from WAPDA (arrange in advance); the spillway in monsoon is spectacular.'),
        att('Tarbela','Tarbela Lake Boating','The 80 km² Tarbela reservoir is excellent for boating, fishing for mahseer and catfish, and birdwatching. The forested islands within the lake are nesting grounds for migratory birds.','tarbelaking','nature',['all'],2,3.0,'morning',400,'Hire a motorboat from the PTDC jetty; early morning is best for migratory bird sightings.'),
        att('Tarbela','Khanpur Dam & Lake','20 km from Tarbela, Khanpur Dam has a beautiful blue lake popular for jet skiing, wakeboarding, and snorkelling in clear water. Rocky cliffs frame the lake dramatically.','khanpurdam','adventure',['all'],1,3.0,'morning',300,'Weekends are crowded; water sports equipment available for hire; excellent cliff jumping spots for adventurers.'),

        # SUKKUR
        att('Sukkur','Sukkur Barrage','The Lloyd Barrage (1932) spans the mighty Indus for 1.5 km and irrigates 7 million acres of Sindh—one of the greatest irrigation projects of the British era. Walking its observation deck gives views of the vast river.','sukkurbarrage','culture',['all'],1,2.0,'morning',0,'Guided tours available from WAPDA office; the barrage is most impressive during high Indus flow June–September.'),
        att('Sukkur','Sadhu Belo Island Temple','A Hindu island temple complex in the Indus reached by boat, with colourful painted shrines, peacocks, and a resident sadhu community. A unique slice of Sindhi Hindu heritage.','sadhubelo','spiritual',['all'],1,2.0,'morning',100,'Boats depart from the Sukkur riverbank; remove shoes before entering the temple complex.'),
        att('Sukkur','Sat Manzil (Seven-Storey Palace)','A historic seven-storey palace tower in Sukkur city built by a wealthy merchant, now partly ruined but offering sweeping Indus River views from the upper floors.','satmanzil','culture',['all'],2,1.5,'afternoon',100,'Visit with a local guide who can narrate the legends of the building; rooftop views at sunset are excellent.'),
        att('Sukkur','Sukkur Old Bazaar','The labyrinthine old bazaar of Sukkur sells Sindhi ajrak (block-printed fabric), clay pots, and dried fish. The Sindhi craftswomen demonstrating ajrak printing are worth photographing.','sukkurbazaar','shopping',['all'],2,2.0,'afternoon',0,'Best visited 4-7pm; the spice section smells incredible; try fresh sugarcane juice from the street vendors.'),

        # KALABAGH
        att('Kalabagh','Indus River Gorge Walk','At Kalabagh the Indus cuts through spectacular limestone gorges of the Salt Range. Walking the riverbank gorge reveals dramatic rock formations and the old salt-trading town.','kalabaghgorge','nature',['all'],1,2.0,'morning',0,'Best in early morning when river mist fills the gorge; local fishermen offer boat rides on the Indus.'),
        att('Kalabagh','Kalabagh Salt Range Mines','The ancient Salt Range contains rock salt mines with pink, red, and white crystal formations. The nearby Khewra Salt Mine (70 km away) is one of the world\'s largest.','kalabaghsalt','nature',['all'],2,3.0,'morning',200,'Khewra Salt Mine (70 km) is the premier experience; combine with Kalabagh gorge for a full day.'),
        att('Kalabagh','Local Kalabagh Bazaar','The traditional market town of Kalabagh has preserved its riverside market character with wooden-fronted shops and boat builders on the Indus bank—a rare glimpse of old Punjab river culture.','kalabagh','culture',['budget','backpacker','standard'],3,1.5,'afternoon',0,'Try the local chai at the riverside tea stalls while watching boats on the Indus.'),

        # ROHRI
        att('Rohri','Khwaja Khizr Shrine','An ancient white-domed shrine on Bukkar Island in the Indus, reached by a short boat ride. Dedicated to the patron saint of rivers and travellers, it is a place of quiet beauty and faith.','khwajakhizr','spiritual',['all'],1,2.0,'morning',50,'Boats depart from Rohri riverbank; the shrine is especially atmospheric at dawn prayer time.'),
        att('Rohri','Lansdowne Bridge','A historic 1889 railway and road bridge spanning the Indus at Rohri-Sukkur, one of the longest bridges in Asia at its time of construction. Walking across gives dramatic Indus River views.','lansdownebridge','culture',['all'],2,1.0,'afternoon',0,'Walk across at sunset for golden-hour photography of the wide Indus; the old bridge has Victorian ironwork.'),
        att('Rohri','Fossil Hills of Rohri','The limestone hills near Rohri are rich in Eocene marine fossils including shark teeth, sea urchins, and whale bones, remnants of the ancient Tethys Sea that once covered this region.','rohrifossils','nature',['budget','backpacker','standard'],3,2.0,'morning',0,'Hire a local guide from Rohri bazaar for PKR 500 to find the best fossil sites; bring water and sun protection.'),

        # BAHAWALPUR
        att('Bahawalpur','Derawar Fort','A massive 40-tower desert fort rising dramatically from the Cholistan sand dunes, built in the 9th century and rebuilt by the Nawabs of Bahawalpur. Best photographed at sunrise or sunset when the ochre walls glow.','derawarfort','culture',['all'],1,3.0,'morning',500,'Hire a 4WD jeep from Bahawalpur (90 km, 2.5 hrs); the drive through Cholistan dunes is itself spectacular.'),
        att('Bahawalpur','Noor Mahal Palace','A stunning 1872 Nawabi palace in Italian Baroque style with ornate interiors, Belgian chandeliers, and immaculate gardens. Now a heritage hotel, it is one of Pakistan\'s finest examples of Victorian-era princely architecture.','noormahal','culture',['all'],1,2.0,'afternoon',500,'Book the guided heritage tour; the rooftop sunset view over Bahawalpur is excellent; dinner in the palace restaurant is a highlight.'),
        att('Bahawalpur','Lal Suhanra National Park','A wildlife reserve at the edge of the Cholistan Desert with blackbuck antelope, chinkara gazelle, and migratory Houbara Bustards. Safari jeeps explore sand dunes, forest, and wetland zones.','lalsuhanra','nature',['all'],2,4.0,'morning',400,'Safari jeeps depart at 6am and 4pm; the best wildlife sightings are at dusk when animals congregate at water points.'),
        att('Bahawalpur','Bahawalpur Museum','Houses an excellent collection of Nawabi-era artifacts, Cholistan Desert ethnography, and Indus Valley archaeological finds from the region. The old British-era museum building is architecturally attractive.','bahawalpurmuseum','culture',['all'],3,1.5,'afternoon',100,'Closed Mondays; the Nawabi jewelry collection is particularly impressive; photography allowed in some sections.'),

        # UMARKOT
        att('Umarkot','Umarkot Fort','The historic fort where Emperor Akbar was born in 1542, now a well-maintained museum with Rajput-style architecture. The fort museum displays local history and a hall dedicated to Akbar\'s birth.','umarkotfort','culture',['all'],1,2.0,'morning',200,'Excellent English-language displays; the fort caretaker provides free informal tours with fascinating stories.'),
        att('Umarkot','Thar Desert Camel Safari','A guided camel safari from Umarkot into the Thar Desert dunes, visiting nomadic Rajput and Bheel communities in colourful decorated villages. Overnight desert camping under the stars is possible.','tharcamel','adventure',['all'],1,4.0,'morning',1500,'Book through Umarkot guesthouses; overnight safari PKR 4,000 per person includes meals and camel; beautiful stargazing.'),
        att('Umarkot','Hindu Temples of Tharparkar','Dozens of beautifully carved Hindu temples dot the Tharparkar landscape—Parkar Nagar, Nagarparkar, and Jain temples are particularly fine examples of the region\'s 1,000-year Hindu architectural heritage.','thartemples','spiritual',['all'],2,3.0,'morning',0,'Nagarparkar (50 km south) has the finest temples; local Hindu community serves tea to visitors; photography very welcome.'),

        # MITHI
        att('Mithi','Thar Sand Dunes Walk','The golden sand dunes near Mithi are photogenic and peaceful—walking at sunset when the light turns amber creates extraordinary photography opportunities. Local camel herders will pose for photos.','mithidunes','nature',['all'],1,2.0,'afternoon',0,'Sunset walk (5-7pm) is the best experience; bring warm clothes as it cools rapidly after dark.'),
        att('Mithi','Mithi Handicraft Village','Mithi\'s women artisans produce intricate mirror-work embroidery (sheesha work), clay pottery, and woven baskets. Visiting their workshops is a direct way to experience Thari culture and support local crafts.','mithicrafts','culture',['all'],2,2.0,'afternoon',0,'Buy directly from artisans (PKR 200–2,000 for embroidered items); bargaining is acceptable but respectful pricing matters.'),
        att('Mithi','Diwali-Eid Celebration Visit','Mithi is unique in Pakistan where Hindu and Muslim communities celebrate each other\'s festivals side by side. If visiting during a festival, the inter-faith celebrations are a powerful human experience.','mithifestival','culture',['all'],1,3.0,'any',0,'Check festival dates before travel; local hotels will arrange cultural visits to Hindu and Muslim homes.'),

        # RAHIM YAR KHAN
        att('Rahim Yar Khan','Lal Suhanra National Park','The park near RYK has blackbuck herds, chinkara gazelles, and diverse bird life on the edge of Cholistan Desert. It is one of Punjab\'s most important protected areas.','lalsuhanraryk','nature',['all'],1,4.0,'morning',400,'Morning safari (6-9am) is essential; the Indian Wolf has been spotted here—request wolf habitat areas from rangers.'),
        att('Rahim Yar Khan','Cholistan Desert Edge Jeep Drive','From RYK jeeps head into the Cholistan (also called Rohi) Desert, visiting ancient wells (tobas), 16th-century forts, and nomadic communities living in circular huts (khaliyas).','cholistandesert','adventure',['all'],2,5.0,'morning',2000,'Hire a 4WD from RYK transport stand; bring extra water and fuel; GPS recommended for deep desert tracks.'),
        att('Rahim Yar Khan','Pir Saddar Din Shrine','A revered Sufi shrine complex with a beautifully tiled courtyard and ancient trees. The annual Urs festival draws tens of thousands of devotees for qawwali music and communal meals.','pirsaddardin','spiritual',['all'],3,1.5,'afternoon',0,'The qawwali performance on Thursday evenings is open to all; the langar serves free food to everyone.'),

        # KARACHI
        att('Karachi','Clifton Beach & Sea View','Karachi\'s main public beach stretches for kilometers along the Arabian Sea, with camel rides, horse rides, fast food stalls, and stunning sunsets. The beach is the city\'s lung and social hub.','cliftonbeach','nature',['all'],1,2.5,'afternoon',0,'Visit 5-7pm for the famous Karachi sunset; weekday mornings are quieter for a peaceful beach walk.'),
        att('Karachi','Empress Market','A Victorian-era covered market built in 1884 with a clock tower, bustling with vendors selling spices, birds, meat, fabrics, and everything imaginable. It is Karachi\'s most atmospheric traditional market.','empressmarket','shopping',['all'],2,2.0,'morning',0,'Go before 11am for the freshest produce and fewest crowds; the spice hall and dried fruit section are magnificent.'),
        att('Karachi','Mohatta Palace Museum','A stunning 1927 palace built in pink Jodhpur stone, now a museum of Pakistani art, Quaid-e-Azam Fatimah Jinnah\'s residence, and a venue for major art exhibitions. The architecture is exceptional.','mohattapalace','culture',['all'],2,2.0,'morning',300,'Closed Wednesdays; the ground-floor permanent collection of Sindhi crafts is free; temporary exhibitions extra.'),
        att('Karachi','Karachi Fish Harbour & BBQ','The largest fish harbour in Pakistan where fresh catch from the Arabian Sea is auctioned at dawn, then grilled at the adjacent BBQ area. The seafood—pomfret, lobster, crabs—is extraordinary.','karachifish','food',['all'],1,2.5,'evening',0,'Arrive at sunset (6-8pm) for the best grilled fish experience; a full seafood meal costs PKR 800-2,000 per person.'),
        att('Karachi','Quaid-e-Azam Mazar','The magnificent white marble mausoleum of Pakistan\'s founder Muhammad Ali Jinnah, standing in a beautifully maintained park. The elegant simplicity of the design and the eternal flame are moving.','qaidmazarkarachi','spiritual',['all'],1,1.5,'morning',0,'Well lit at night for an alternative view; the changing of the guard ceremony adds pageantry to the visit.'),

        # GWADAR
        att('Gwadar','Hammerhead Cliff (Koh-e-Batil)','A dramatic sea cliff on the Gwadar headland with 360-degree views of the Arabian Sea, Gwadar Bay, and the surrounding Makran coastal mountains. One of the most stunning natural viewpoints in Pakistan.','hammerhead','nature',['all'],1,2.0,'morning',0,'Visit at sunrise (6am) for the best light and fewest tourists; strong winds—hold onto belongings.'),
        att('Gwadar','Gwadar Fish Harbour','The deep-sea fishing harbour of Gwadar is one of Asia\'s busiest, with massive dhows bringing in marlin, tuna, and shark. The harbour market at dawn is raw, authentic, and extraordinary.','gwadarfish','food',['all'],2,2.0,'morning',0,'Arrive before 6am for the fish auction; try the freshly-grilled tuna steak at the harbour-side stalls.'),
        att('Gwadar','Ormara Beach Day Trip','65 km from Gwadar, Ormara has pristine turtle beaches and dramatic sea stacks. A day trip from Gwadar can be arranged by local guesthouses.','ormara','nature',['all'],1,6.0,'morning',0,'Hire a car from Gwadar (PKR 2,500 return); the Makran Coastal Highway drive is itself spectacular.'),
        att('Gwadar','Pishukan Mangroves','A mangrove forest and lagoon system accessible by boat from Gwadar, important for migratory birds and as nursery for fish. Boat tours pass through narrow channels lined with ancient mangrove trees.','pishukanmangroves','nature',['all'],2,3.0,'morning',400,'Boat hire PKR 1,000 for a 2-hour tour; bring binoculars for flamingos and herons.'),

        # ORMARA
        att('Ormara','Sea Turtle Nesting Beach','Ormara is one of Pakistan\'s most important green sea turtle nesting sites. From November to January, turtles come ashore at night to lay eggs. Guided night tours with wildlife officials are unforgettable.','ormalaturtles','nature',['all'],1,3.0,'evening',0,'Contact Ormara Wildlife Department in advance to book turtle-watching nights; strictly no flash photography.'),
        att('Ormara','Ormara Sea Stacks','Dramatic rock stacks rising from the sea near Ormara, carved by Arabian Sea waves into arches, pillars and spires. Boat tours from the harbour circle the stacks for close-up photography.','ormararocks','nature',['all'],1,2.5,'morning',300,'Hire a local fisherman\'s boat (PKR 800); early morning is best for photography with calm seas.'),
        att('Ormara','Makran Coastal Highway Drive','The stretch of Makran Coastal Highway through Ormara is perhaps the most scenic section—golden beaches, ochre cliffs, turquoise sea, and complete solitude.','makrancoastal','adventure',['all'],2,3.0,'morning',0,'Drive west from Ormara at sunrise for the best light; the cliff sections above the sea are breathtaking.'),

        # KUND MALIR
        att('Kund Malir','Kund Malir Beach Walk','Walking the 25 km golden sand beach with rust-coloured limestone cliffs as a backdrop is one of Pakistan\'s most dramatic coastal experiences. The beach is empty, wild, and pristine.','kundmalirsbeach','nature',['all'],1,3.0,'morning',0,'Camp overnight to walk the beach at dawn—the light on the ochre cliffs at sunrise is extraordinary.'),
        att('Kund Malir','Cliff Photography','The towering rust, ochre, and purple cliffs dropping straight into the turquoise sea at Kund Malir are iconic. Golden hour photography from the cliff tops is world-class.','kundmalircliffs','nature',['all'],1,2.0,'afternoon',0,'Best photography light is 4-6pm; the cliff paths require sure footing—do not approach cliff edges after dark.'),
        att('Kund Malir','Hingol National Park','Pakistan\'s largest national park (6,100 km²) begins at Kund Malir, protecting Balochistan\'s coastal desert ecosystem including the rare Hingol mud volcanoes, Hindu Hinglaj Mata Shrine, and the Princess of Hope rock formation.','hingolpark','nature',['all'],2,4.0,'morning',200,'The Princess of Hope rock formation is 30 km inside the park; arrange a park ranger guide from Kund Malir.'),

        # LAHORE
        att('Lahore','Lahore Fort (Shahi Qila)','A UNESCO World Heritage Mughal fort containing 21 remarkable monuments built by Akbar, Jahangir, Shah Jahan, and Aurangzeb. The Sheesh Mahal (Palace of Mirrors) is the highlight—mosaic mirror work of breathtaking intricacy.','lahorefort','culture',['all'],1,3.0,'morning',500,'Arrive at 8am opening time to avoid crowds; hire official guide at gate for PKR 500; Sheesh Mahal requires extra entry.'),
        att('Lahore','Badshahi Mosque','The world\'s 5th largest mosque, built by Aurangzeb in 1673. Its red sandstone exterior, white marble domes, and vast courtyard holding 100,000 worshippers make it one of the grandest religious buildings on earth.','badshahimosque','spiritual',['all'],1,2.0,'morning',0,'Dress modestly; free entry; best visited Friday morning for atmosphere; the view from the minaret (extra fee) is exceptional.'),
        att('Lahore','Gawalmandi Food Street','Lahore\'s most famous food street with a 200-metre promenade of historic havelis converted to restaurants, all serving classic Lahori food—Nihari, Paye, Chargha, Chaat. An essential evening experience.','foodstreetlahore','food',['all'],1,2.0,'evening',0,'Arrive at 8pm when it\'s most vibrant; the entire street is decorated with lights; try Nihari at Waris Nihari.'),
        att('Lahore','Shalimar Gardens','A UNESCO World Heritage 17th-century Mughal garden built by Shah Jahan with three terraces of fountains, marble pavilions, and fruit trees. The water channels and symmetrical design are a masterpiece of Mughal landscape art.','shalamargardens','nature',['all'],2,2.0,'afternoon',200,'Best in spring (March–April) when flowers are in bloom; the upper terrace view at sunset is magnificent.'),
        att('Lahore','Wagah Border Flag Ceremony','The daily flag-lowering ceremony at the Pakistan-India Wagah Border is a spectacular display of military pageantry, national pride, and crowd energy. The BSF and Pakistan Rangers perform in perfect synchronized drama.','wagahborder','culture',['all'],1,2.5,'evening',0,'Arrive 2 hours before sunset to get good seats; the ceremony is free; the crowds and atmosphere are electric.'),
        att('Lahore','Walled City Heritage Walk','A guided walk through the 13 historic gates of Lahore\'s Walled City—exploring Hazuri Bagh, Wazir Khan Mosque (finest Mughal tile work in Pakistan), and the old merchant lanes.','walledcitylahore','culture',['all'],2,3.0,'morning',300,'Book a heritage walk guide at Delhi Gate (PKR 1,000); Wazir Khan Mosque tile work is unmissable.'),

        # TAXILA
        att('Taxila','Taxila Museum','One of Pakistan\'s finest museums with the world\'s best collection of Gandhara Buddhist art—stucco Buddhas, friezes, coins, and jewelry spanning 500 BC to 500 AD. The museum alone justifies the visit.','taxilamuseum','culture',['all'],1,2.5,'morning',200,'Hire the official museum guide (PKR 500)—the historical context transforms the experience; photography allowed without flash.'),
        att('Taxila','Dharmarajika Stupa','A 3rd-century BC stupa built by Emperor Ashoka, one of the oldest Buddhist monuments in South Asia. The complex includes monastery ruins, votive stupas, and a processional path—an atmospheric ancient pilgrimage site.','dharmarajika','culture',['all'],1,2.0,'morning',200,'Visit early morning when the site is quiet and the light on the old brick ruins is beautiful.'),
        att('Taxila','Jaulian Monastery','The best-preserved Buddhist monastery in Pakistan, with rows of decorative stupa pedestals featuring Gandhara Buddha figures, and two intact courtyards on a hilltop overlooking the Taxila Valley.','jaulian','culture',['all'],1,2.0,'afternoon',200,'The hilltop walk (15 minutes) is manageable; the stucco Buddhas here are in remarkable condition.'),
        att('Taxila','Sirkap Ancient City','Excavated ruins of a 2nd-century BC Indo-Greek city with grid-plan streets, temples, wells, and shops laid out in a recognizable urban form—evidence of the sophisticated Hellenistic culture that flourished here.','sirkap','culture',['all'],2,2.0,'morning',200,'The Double-Headed Eagle Stupa and Apsidal Temple at Sirkap are the key monuments; sturdy shoes recommended.'),

        # LARKANA
        att('Larkana','Mohenjo-daro UNESCO Site','The best-preserved city of the Indus Valley Civilization (2600-1900 BC), with brick streets, two-story houses, drains, and the Great Bath. Walking its 5,000-year-old streets is a profound experience.','mohenjodaro','culture',['all'],1,4.0,'morning',500,'Hire the official archaeologist guide at the site gate (PKR 800)—brings the ruins to life; visit Oct–Feb to avoid extreme heat.'),
        att('Larkana','Mohenjo-daro Museum','The excellent on-site museum displays original Indus Valley artifacts including the famous Dancing Girl bronze figurine (replica), the Priest-King steatite sculpture, and exquisite carved seals with undeciphered script.','mohenjodazomuseum','culture',['all'],1,1.5,'morning',0,'Combine with site tour; the Dancing Girl replica and Priest-King statue are the must-see pieces.'),
        att('Larkana','Great Bath of Mohenjo-daro','The most extraordinary structure at Mohenjo-daro—a precisely engineered public bath of bitumen-sealed bricks, 12×7 m, believed to have been a ritual purification pool. One of the world\'s oldest public buildings.','greatbath','culture',['all'],1,1.0,'morning',0,'This is included in the site entry; stand on the viewing platform for the best perspective on the engineering.'),
        att('Larkana','Larkana Bazaar & Sindhi Crafts','Larkana\'s bazaar is famous for hand-woven Sindhi aaee (embroidered cloth), ajrak fabric printing workshops, and traditional Sindhi leather sandals. A living tradition of 4,000 years of Sindhi craftsmanship.','larkana','shopping',['all'],3,2.0,'afternoon',0,'The ajrak printing workshops in the old bazaar welcome visitors; a hand-printed ajrak shawl costs PKR 600–2,000.'),

        # PESHAWAR
        att('Peshawar','Qissa Khwani Bazaar','The legendary "Street of Storytellers" where caravans from Central Asia and India have traded and shared tales for 2,500 years. Its tea houses, fresh kebabs, and chaotic energy are uniquely Pashtun.','qissakhwani','culture',['all'],1,2.5,'afternoon',0,'Best experienced between 3-7pm when the bazaar is at peak energy; the Charsi Tikka is legendary for seekh kebab.'),
        att('Peshawar','Peshawar Museum','Holds Pakistan\'s finest collection of Gandhara Buddhist sculpture alongside Islamic calligraphy, Mughal miniatures, Pashtun tribal weapons, and ethnographic exhibits. One of the best museums in South Asia.','peshawrmuseum','culture',['all'],1,2.0,'morning',200,'Closed Sundays; the Gandhara Gallery alone is worth the trip; hire guide at entrance for PKR 400.'),
        att('Peshawar','Bala Hisar Fort','An imposing fort dominating Peshawar since the Kushan era, later used by the Durrani Empire and British. Now a Frontier Corps HQ but accessible for guided historical tours.','balahisarfort','culture',['all'],2,1.5,'morning',0,'Arrange visit through KPK Tourism (security escort required); the fort walls give panoramic views of old Peshawar.'),
        att('Peshawar','Mahabat Khan Mosque','A 17th-century Mughal mosque in the heart of the old city, famous for its painted interior with floral Mughal frescoes—one of the few painted Mughal mosques remaining in Pakistan.','mahabatkhan','spiritual',['all'],2,1.0,'morning',0,'Non-Muslims welcome outside prayer times; the flower paintings inside the mosque are rare and beautiful.'),
        att('Peshawar','Khyber Pass Drive','The legendary mountain pass connecting Pakistan and Afghanistan—one of history\'s most strategic routes. The 30 km drive from Peshawar passes through dramatic rocky narrows with ancient inscriptions and forts.','khyberpass','adventure',['luxury','standard'],2,4.0,'morning',0,'Requires NOC permit from Khyber Pakhtunkhwa Home Department (arrange 2-3 days in advance); military escort compulsory.'),

        # MULTAN
        att('Multan','Shah Rukn-e-Alam Shrine','A magnificent 14th-century Sufi shrine with one of the finest examples of Tughlaq brick architecture—geometric blue and white tiled exterior and massive wooden doors. One of Pakistan\'s most important spiritual sites.','shahruknealam','spiritual',['all'],1,2.0,'morning',0,'Visit Thursday evening for qawwali music (8-11pm); dress modestly; the interior tile work is among Pakistan\'s best.'),
        att('Multan','Bahauddin Zakariya Shrine','The revered shrine of the great 13th-century Sufi scholar Bahauddin Zakariya, with gold-tipped minarets and a courtyard constantly full of devotees. The largest and most visited shrine in Multan.','bahauddinzakariya','spiritual',['all'],1,1.5,'morning',0,'The devotional atmosphere is most intense at Fajr (dawn) prayer and Thursday nights; free langar available.'),
        att('Multan','Multan Fort (Qasim Bagh)','A partially surviving ancient fort converted to a public park and sports stadium. The remaining towers give views of Multan\'s skyline of shrines and minarets—a remarkable urban panorama.','multanfort','culture',['all'],2,1.5,'afternoon',100,'The towers open to climbing; sunset from the fort walls over the shrine domes is memorable.'),
        att('Multan','Multan Blue Pottery Workshops','Multan is famous for its distinctive blue glazed pottery—a 14th-century craft tradition. Workshops in the pottery quarter let visitors watch artisans hand-painting intricate geometric designs on vases, tiles, and plates.','multanpottery','culture',['all'],1,2.0,'afternoon',0,'Buy directly from workshops (PKR 300–3,000); some workshops offer 1-hour pottery painting sessions for PKR 500.'),
        att('Multan','Hussain Agahi Bazaar','Multan\'s vibrant central bazaar famous for camel-skin lamps (shades painted with Mughal miniature designs), embroidered textiles, and dried fruits from Balochistan. The most colourful market in southern Punjab.','hussainagahi','shopping',['all'],2,2.0,'afternoon',0,'Camel-skin lamps (PKR 500–5,000) are unique souvenirs; the dried fruit sellers at the north end have excellent Balochi apricots.'),

        # NARAN
        att('Naran','Saif-ul-Muluk Lake','Pakistan\'s most famous lake at 3,224 m—an intensely turquoise glacial lake below the 5,291 m Malika Parbat. The mountain reflection in the still water creates one of Asia\'s most photographed scenes.','saifulmluk','nature',['all'],1,3.0,'morning',200,'Jeep up from Naran (PKR 600 per person) or hike 8 km; arrive before 10am before clouds cover Malika Parbat; bring warm clothes.'),
        att('Naran','Babusar Pass','The 4,173 m pass at the head of Kaghan Valley, open July–September, with panoramic views of the Himalayan and Hindu Raj ranges and the Diamer Valley below. One of Pakistan\'s most scenic mountain drives.','babusar','adventure',['all'],2,3.0,'morning',0,'Jeep required (PKR 3,000 from Naran); depart by 7am to beat afternoon cloud cover; snow on the pass even in July.'),
        att('Naran','Lulusar Lake','An emerald-green lake at 3,410 m surrounded by alpine meadows, 50 km above Naran on the Babusar road. The lake reflects the surrounding snow peaks and the meadows are carpeted with wildflowers in July.','lulusar','nature',['all'],2,2.0,'morning',0,'Combine with Babusar Pass trip; the lake is most beautiful 8-10am before wind disturbs the reflection.'),
        att('Naran','Kunhar River Rafting','White-water rafting on the Kunhar River below Naran through grade 3-4 rapids between pine-forested gorges. One of Pakistan\'s best rafting experiences.','kunharrafting','adventure',['luxury','standard','budget'],2,2.5,'morning',2500,'Book through Naran adventure operators; minimum age 12; best flow June–August; all equipment provided.'),

        # GOJAL / ATTABAD
        att('Gojal/Attabad','Attabad Lake Boat Ride','The 20 km boat journey across the vivid turquoise Attabad Lake is one of Pakistan\'s most dramatic travel experiences. The lake covers submerged villages whose rooftops can sometimes be seen underwater.','attabadboat','nature',['all'],1,2.5,'morning',500,'Boats depart from Attabad jetty; the 30-min crossing to Gulmit is most popular; kayaks also available for hire.'),
        att('Gojal/Attabad','Borith Lake','A serene high-altitude lake near Passu with views of the Passu Cathedral peaks (Tupopdan), one of the world\'s most dramatic mountain silhouettes. A 2-hour walk from the Karakoram Highway.','borithlake','nature',['all'],2,3.0,'morning',0,'Walk from Passu village; the Passu Cones reflection in Borith Lake at sunrise is world-class photography.'),
        att('Gojal/Attabad','Passu Cones','The Passu Cathedral peaks (Tupopdan) are among the world\'s most dramatic mountain shapes—vertical rock spires rising 7,284 m directly from the valley floor. Visible from the KKH and best appreciated from the Borith Lake path.','passucones','nature',['all'],1,2.0,'morning',0,'Simply walking the KKH near Passu village gives magnificent views; morning light at 7-9am is best.'),
        att('Gojal/Attabad','Khunjerab Pass','The world\'s highest paved international border crossing at 4,693 m, between Pakistan and China on the Karakoram Highway. The drive from Gojal through Sost to Khunjerab is spectacularly desolate mountain scenery.','khunjerab','adventure',['all'],1,6.0,'morning',0,'Open May–November; passport required at Sost customs; Marco Polo sheep and yaks are often seen near the pass.'),

        # ISLAMABAD
        att('Islamabad','Faisal Mosque','One of the world\'s largest mosques, designed by Turkish architect Vedat Dalokay in 1986, with a striking desert-tent inspired design and 88 m minarets. Set against the Margalla Hills backdrop, it is Pakistan\'s most iconic modern building.','faisalmosque','spiritual',['all'],1,2.0,'morning',0,'Non-Muslims welcome outside prayer times; dress modestly; the adjacent Islamic University campus can be included in the walk.'),
        att('Islamabad','Margalla Hills Hiking','The Margalla Hills National Park behind Islamabad has well-marked trails to peaks like Trail 3, Trail 5, and the Monal restaurant. Dense forest with monkeys, leopards, and over 250 bird species.','margallatrails','nature',['all'],1,3.0,'morning',0,'Trail 3 (3 km) is the most popular; depart before 8am to avoid heat; the Monal restaurant at the summit has spectacular city views.'),
        att('Islamabad','Pakistan Monument','A petal-shaped marble monument representing the four provinces of Pakistan, with a museum of Pakistan\'s history beneath. The view from the monument platform over Islamabad and Rawalpindi is excellent.','pakistanmonument','culture',['all'],2,1.5,'afternoon',150,'Visit at sunset for views of Faisal Mosque illuminated against the Margallas; the underground museum is well-curated.'),
        att('Islamabad','Lok Virsa Museum','Pakistan\'s national folk heritage museum with the finest collection of regional crafts, textiles, musical instruments, and ethnic costumes from all provinces. An essential introduction to Pakistan\'s cultural diversity.','lokvirsa','culture',['all'],2,2.0,'morning',200,'Closed Mondays; the Sindhi embroidery and Balochi carpet galleries are superb; photography allowed.'),

        # UPPER DIR
        att('Upper Dir','Kumrat Valley Trek','The pristine Kumrat Valley has day hiking trails through dense Deodar cedar forests, past waterfalls and alpine meadows, with views of 5,000+ m peaks. Largely undiscovered by tourists, it has an authentic frontier feel.','kumrattrek','nature',['all'],1,4.0,'morning',0,'Hire local guide from Thal village (PKR 800/day); proper boots essential; the Jahaz Banda plateau (3,500 m) is the 2-day target.'),
        att('Upper Dir','Jahaz Banda Alpine Meadow','A vast treeless alpine meadow at 3,500 m surrounded by peaks, carpeted with wildflowers in July–August. Local Gujar nomads graze their yak and cattle herds here in summer.','jahazband','nature',['all'],1,5.0,'morning',0,'A 2-day trek from Kumrat; tented camps available; the night sky here is extraordinary with no light pollution.'),
        att('Upper Dir','Patigai Lake','A crystal-clear mountain lake near Kumrat with a dense cedar forest backdrop. Very peaceful and undiscovered—on weekdays visitors may have the lake entirely to themselves.','patigailake','nature',['all'],2,3.0,'morning',0,'Local jeep hire from Thal (PKR 1,500); trail around the lake takes 45 mins; the water is clear enough to see the bottom.'),

        # SWAT
        att('Swat','Malam Jabba Ski Resort','Pakistan\'s premier ski resort at 2,804 m with 5 ski runs, ski lifts, and spectacular views over the Swat Valley. In summer it becomes an adventure park with hiking, mountain biking, and paragliding.','malamjabba','adventure',['luxury','standard','budget'],1,4.0,'morning',1000,'Ski season January–March; day pass PKR 1,500; equipment rental available; beginner lessons PKR 2,000.'),
        att('Swat','Kalam Valley','The head of Swat Valley at 2,001 m, surrounded by towering peaks and dense forests, with the Swat River rushing through. Kalam is the base for treks to Mahodand Lake and Ushu Forest.','kalamvalley','nature',['all'],1,3.0,'morning',0,'Hire jeep from Mingora to Kalam (2.5 hours, PKR 3,000); the road follows the Swat River through spectacular gorges.'),
        att('Swat','Butkara Stupa (Mingora)','One of the most important Buddhist sites in Swat—a 3rd century BC Ashokan stupa with hundreds of votive stupas, monasteries, and Gandhara sculptures in situ. In its heyday, 10,000 Buddhist monks studied here.','butkara','culture',['all'],2,2.0,'morning',200,'The Archaeological Museum of Swat (Saidu Sharif) complements this site perfectly; visit both in one morning.'),
        att('Swat','Mahodand Lake','A glacier-fed lake at 2,928 m, 40 km above Kalam, surrounded by snowfields and spectacular peaks. The drive up through the Ushu Valley and Forest is through some of Pakistan\'s densest alpine forest.','mahodandlake','nature',['all'],1,5.0,'morning',200,'Jeep from Kalam required (PKR 2,000 return); departure by 7am essential; camping by the lake is memorable.'),

        # KAGHAN
        att('Kaghan','Shogran Plateau','A beautiful high plateau at 2,362 m above the Kaghan Valley, with panoramic views of the Himalayan peaks, pine forests, and alpine meadows. Accessible by jeep or cable car from Siri.','shogran','nature',['all'],1,3.0,'morning',400,'The cable car from Siri to Shogran (15 mins, PKR 600) gives aerial views of the valley; sunrise from Shogran is outstanding.'),
        att('Kaghan','Siri Lake','A scenic lake at 2,500 m on the Shogran plateau, encircled by pine forest and overlooking the Kaghan Valley. Boat rides and trout fishing are available.','sirilake','nature',['all'],2,2.0,'morning',300,'Combine with Shogran visit; trout fishing permits available at the lake hut (PKR 500/hour).'),
        att('Kaghan','Balakot Town & Bazaar','The main commercial town of Kaghan Valley at the entrance of the valley, with a lively bazaar, fresh trout restaurants, and the remains of the historic Balakot battlefield of 1831.','balakot','culture',['budget','backpacker','standard'],3,1.5,'afternoon',0,'The fresh trout restaurants along the river are excellent value (PKR 600 for a full trout meal); best bazaar in the valley.'),

        # NEELUM VALLEY
        att('Neelum Valley','Arang Kel','A fairy-tale mountain village accessible only by a 30-minute cable car ride followed by a 45-minute hike, floating above the Neelum River in a sea of green forest with views of Himalayan snowfields. Nicknamed "Heaven on Earth".','arangkel','nature',['all'],1,4.0,'morning',600,'Cable car at Kel village (PKR 200); the climb to the village takes 40 mins; limited basic guesthouses for overnight stay.'),
        att('Neelum Valley','Ratti Gali Lake','A high-altitude lake at 3,700 m surrounded by wildflower meadows, accessible by jeep and then a 2-hour hike. The deep blue lake against the white snowfields and green meadows is Pakistan\'s most beautiful alpine lake.','rattigali','nature',['all'],1,5.0,'morning',300,'Accessible July–September only; jeep from Dhirkot (PKR 3,000 return); 2-hour hike each way; overnight camping is permitted.'),
        att('Neelum Valley','Sharda Fort & University Ruins','Ruins of a 1,500-year-old Hindu Sharda Peeth university and temple complex on the banks of the Neelum River, once one of the Hindu world\'s most important centres of learning.','shardaruins','culture',['all'],2,2.0,'morning',100,'The ruined university walls and carved doorways are well-preserved; local guides available from Sharda village.'),
        att('Neelum Valley','Neelum River Fishing','The Neelum River is one of Pakistan\'s finest trout fishing rivers. Brown and rainbow trout are plentiful in clear, cold, fast-flowing water. Fishing camps along the river offer full equipment and guide service.','neelumfishing','adventure',['all'],2,3.0,'morning',800,'Fishing permits from AJK Fisheries Department; camp-side cooking of your catch is an unforgettable experience.'),

        # KALASH VALLEYS
        att('Kalash Valleys','Bumburet Valley Walk','Walking Bumburet, the largest Kalash valley, past wooden Kalash houses, grape-vine fences, walnut and mulberry orchards, and ancient shrines, with Kalash women in their distinctive black robes and beaded headdresses.','bumburetvalley','culture',['all'],1,3.0,'morning',300,'Hire local Kalash guide (PKR 800); festival times (May Chilam Joshi, Aug Uchal) are extraordinary; photography requires consent.'),
        att('Kalash Valleys','Kalash Museum Brun','A small but excellent community museum in Brun village documenting Kalash history, religion, festivals, and dress, with English-language displays and local staff who can answer questions.','kalashmuseum','culture',['all'],2,1.5,'morning',300,'Well-organized; the explanations of the Kalash festival calendar and burial rites are fascinating and respectful.'),
        att('Kalash Valleys','Rumbur Valley Trek','A quieter Kalash valley with fewer tourists than Bumburet, connected by a mountain path through walnut forests. The valley has some of the most traditional Kalash villages with ancient carvings and wooden ancestral effigies.','rumburtrek','culture',['all'],2,3.0,'morning',0,'2-hour trek from Bumburet or jeep (PKR 500); the traditional Kalash wooden burial grounds here are unique and sobering.'),
        att('Kalash Valleys','Chilam Joshi Spring Festival','The Kalash spring festival in mid-May welcoming the summer pastures season—3 days of dancing, music, floral crowns, and communal feasting. One of Pakistan\'s most unique cultural events.','chilamjoshi','culture',['all'],1,3.0,'any',0,'Mid-May annually; book accommodation months in advance; the festival is entirely authentic—Kalash community event, not staged for tourists.'),

        # ZIARAT
        att('Ziarat','Ancient Juniper Forest','The world\'s second-largest juniper forest around Ziarat, with trees 2,000–5,000 years old and grotesquely beautiful twisted trunks. Walking through the forest is genuinely primeval.','ziaratjuniper','nature',['all'],1,3.0,'morning',0,'Forest trails start 2 km from Ziarat town; dawn walks in the mist when ibex are often seen grazing are extraordinary.'),
        att('Ziarat','Quaid-e-Azam Residency','The mountain cottage where Pakistan\'s founder Muhammad Ali Jinnah spent his last months in 1948. Preserved exactly as he left it, with personal belongings and photographs, it has a poignant atmosphere.','qaidziarat','culture',['all'],1,1.5,'morning',100,'Closed Mondays; the caretaker provides moving personal stories about Jinnah\'s final days; the garden view is peaceful.'),
        att('Ziarat','Ziarat Valley Wildflowers','In spring (April–June) the Ziarat Valley hillsides burst with wild roses, juniper berry flowers, and alpine wildflowers. Combined with ibex sightings, it makes for exceptional wildlife photography.','ziaratflowers','nature',['all'],2,2.0,'morning',0,'April–June for maximum wildflowers; bring binoculars—Suleiman Markhor (world\'s largest wild goat) inhabits these hills.'),

        # AYUBIA
        att('Ayubia','Pipeline Track Walk','A famous 5 km forest walk along an old water pipeline through dense oak and rhododendron forest in Ayubia National Park, connecting Ayubia to Dunga Gali. Barking deer, yellow-throated martens, and monkeys are common.','pipelinetrack','nature',['all'],1,3.0,'morning',0,'Depart from Ayubia Chairlift station; the trail is clearly marked; bring binoculars for bird watching—270+ species recorded.'),
        att('Ayubia','Ayubia Chair Lift','A 2 km chair lift through dense pine and rhododendron canopy above Ayubia, one of the most scenic chair lifts in Pakistan, with views over the Galiyat hills and Hazara valley.','ayubiacairlift','adventure',['all'],2,1.0,'morning',500,'Closed Tuesdays; best in autumn (October–November) for golden forest colours and clear Himalayan views.'),
        att('Ayubia','Nathiagali Hill Station','A charming British-era hill station with a Victorian Church, the Governor\'s Residency, and a 3-km nature trail through monkeys and mist. The treetop-level walk connects to Mukshpuri summit (2,788 m).','nathiagali','nature',['all'],2,2.5,'morning',0,'The Mukshpuri trek (2 hrs each way) gives a 360° view from Punjab plains to Kashmir; best October–April for clear days.'),

        # DEOSAI
        att('Deosai','Sheosar Lake','A high-altitude (4,142 m) lake in the heart of Deosai Plains, named "blind lake" in Shina language. Brown bears frequently fish in the lake in July–August. The reflection of clouds in the mirror-flat water is ethereal.','sheosarlake','nature',['all'],1,2.0,'morning',0,'Arrive early morning for bear sightings; the high altitude means UV is intense—wear full sun protection.'),
        att('Deosai','Himalayan Brown Bear Safari','Deosai is one of the last refuges of the Himalayan Brown Bear. Guided jeep safaris to bear feeding grounds in July–August, when they forage on marmots and wildflowers, give sightings with 70%+ success rate.','brownearbsafari','nature',['all'],1,4.0,'morning',1000,'Book through Skardu tour operators (PKR 3,500–5,000 per person); patient early-morning observation is key.'),
        att('Deosai','Wildflower Carpet Walk','In July–August the entire Deosai plateau (3,000 km²) becomes carpeted with blue gentians, yellow buttercups, pink phlox, and hundreds of alpine wildflower species—one of the world\'s great wildflower spectacles.','deosaiflowers','nature',['all'],1,3.0,'morning',300,'Simply walking from your camp in any direction works; the wildflower display peaks in late July.'),

        # NALTAR
        att('Naltar','Naltar Lakes','Three adjacent lakes (Naltar, Bashkiri, and Dudipatsar) at 3,578 m, each a different impossible colour—vivid blue, emerald green, and milky white—created by different mineral concentrations. One of Pakistan\'s most extraordinary natural phenomena.','naltarlakes','nature',['all'],1,3.0,'morning',0,'2-hour jeep from Gilgit then 30-min walk; the lakes are best in morning light 8-11am before shadows move in.'),
        att('Naltar','Naltar Ski Resort','Pakistan Army\'s Naltar Ski Resort, open December–March, with 5 ski runs and one of Pakistan\'s few ski lifts. The setting—surrounded by 5,000+ m peaks—is extraordinary.','naltarskireort','adventure',['luxury','standard'],2,4.0,'morning',2000,'Ski season Dec–March; day pass PKR 2,000; equipment rental available; stunning views while skiing.'),
        att('Naltar','Forest Camping','The dense Naltar pine and blue spruce forest provides exceptional wilderness camping opportunities. Campfire evenings with stargazing at 3,000+ m altitude are unforgettable.','naltarcamp','adventure',['budget','backpacker'],2,8.0,'any',0,'Bring your own tent; firewood available from local community for PKR 200; the forest soundscape at night is pristine.'),
    ]

    att_cols = ('city_id','name','description','image_url','category','budget_levels',
                'priority','duration_hours','time_of_day','entry_fee_pkr','tip')
    att_ph = ','.join(['?']*len(att_cols))

    c.executemany(f'INSERT INTO attractions({",".join(att_cols)}) VALUES({att_ph})', attractions_data)

    # ── HOTELS ─────────────────────────────────────────────────────
    def hotel(city_name, name, level, stars, price, address, amenities, desc, tip):
        return (city_map[city_name], name, level, stars, price, address,
                json.dumps(amenities), desc, tip)

    hotels_data = [
        # ── SKARDU ─────────────────────────────────────────────────
        hotel('Skardu', 'Shangrila Resort Skardu', 'luxury', 5, 38000, 'Lower Kachura Lake, Skardu, GB',
              ['Lakeside gardens','Heritage plane-shaped restaurant','Fine dining','Lake-view rooms','Guided excursions'],
              'Pakistan\'s most iconic resort on the shore of emerald Lower Kachura Lake, with Mughal-style gardens and a legendary aircraft-shaped restaurant. Rooms look out over the water to snow-capped Karakoram peaks.',
              'Request a "heritage wing" lake-view room; summer (Jun-Aug) books out 3 months ahead.'),
        hotel('Skardu', 'PTDC Motel Skardu', 'standard', 3, 9500, 'Airport Road, Skardu, GB',
              ['Mountain views','Restaurant','Tour desk','Parking','Wi-Fi in lobby'],
              'Government-run motel with comfortable en-suite rooms set in pleasant gardens within walking distance of Skardu bazaar. A reliable mid-range base for exploring Satpara, Deosai and Shigar.',
              'Ask for the upper-floor rooms facing the Karakoram for sunrise views over the valley.'),
        hotel('Skardu', 'Mashabrum Hotel', 'budget', 2, 2800, 'College Road, Skardu Bazaar, GB',
              ['Hot showers','In-house dining','24-hr generator','Jeep booking desk'],
              'A long-running family guesthouse near Skardu bazaar with clean twin rooms and friendly staff who arrange treks to Deosai and K2 base camp.',
              'Rates are negotiable off-season (Oct-Apr); trout dinner is only PKR 700 and excellent.'),
        hotel('Skardu', 'K2 Backpackers Hostel', 'backpacker', 1, 800, 'Naya Bazaar, Skardu, GB',
              ['Dorm beds','Shared kitchen','Trekker lounge','Gear storage'],
              'A no-frills hostel beloved by international climbers heading to Baltoro Glacier. Dorms, basic twins, and a lively common room with K2 expedition memorabilia.',
              'Perfect place to find trekking partners for Deosai or K2 Base Camp; join the noticeboard for cost-sharing trips.'),

        # ── HUNZA ──────────────────────────────────────────────────
        hotel('Hunza', 'Serena Hunza', 'luxury', 5, 42000, 'Karimabad, Hunza, GB',
              ['Panoramic mountain terrace','Heritage architecture','Spa','Fine dining','Concierge trek services'],
              'Set in Karimabad amidst apricot orchards with commanding views of Rakaposhi and Ultar Sar. Blends Hunzai stone-and-wood architecture with modern luxury.',
              'The deluxe valley-view rooms wake you to sunrise on Rakaposhi; reserve 2-3 months ahead for summer.'),
        hotel('Hunza', 'Hunza Embassy Hotel', 'standard', 3, 8500, 'Karimabad Main Bazaar, Hunza, GB',
              ['Rakaposhi-view balconies','Restaurant','Tour desk','Heating','Hot water'],
              'Comfortable mid-range hotel on the main Karimabad ridge with wooden-balcony rooms looking straight at Rakaposhi. Close to Baltit Fort and the bazaar.',
              'Rooms 201-206 have the best Rakaposhi views — request specifically at booking.'),
        hotel('Hunza', 'Old Hunza Inn', 'budget', 2, 2500, 'Karimabad, Hunza, GB',
              ['Apricot garden','Home-cooked Hunzai food','Terrace','Hot showers'],
              'A cozy family-run guesthouse set in an apricot orchard, famed for authentic Hunzai home cooking (chapshuro, daudo, walnut cake) served on the garden terrace.',
              'Mrs. Bano\'s home cooking is the highlight — order the Hunzai thali dinner in advance.'),
        hotel('Hunza', 'Karimabad Youth Hostel', 'backpacker', 1, 700, 'Below Baltit Fort, Karimabad, GB',
              ['Dorm beds','Shared kitchen','Mountain-view lounge','Laundry'],
              'A simple backpacker favourite just below Baltit Fort with shared dorms and private singles. The rooftop chai sessions at sunset are legendary.',
              'Rooftop views of Rakaposhi beat most luxury hotels — bring a warm layer for evenings year-round.'),

        # ── GILGIT ─────────────────────────────────────────────────
        hotel('Gilgit', 'Serena Gilgit', 'luxury', 5, 32000, 'Jutial, Gilgit, GB',
              ['Landscaped gardens','Fine dining','Business centre','Tour desk','Heated rooms'],
              'The most polished hotel in Gilgit set in large wooded gardens in upscale Jutial suburb, with elegant rooms, fine dining and a capable trekking desk.',
              'The garden-facing rooms on the ground floor open onto rose beds; ideal for longer KKH-prep stays.'),
        hotel('Gilgit', 'Riveria Hotel', 'standard', 3, 7500, 'Konodas, Bank Road, Gilgit, GB',
              ['River views','Restaurant','Airport transfer','Heating'],
              'Riverside mid-range hotel on the Gilgit River with clean modern rooms and a popular restaurant serving Pakistani and Chinese dishes. Walking distance to bazaar.',
              'River-facing rooms are worth the small upcharge; the restaurant\'s Gilgiti chapshuro is first-rate.'),
        hotel('Gilgit', 'Madina Guest House', 'budget', 2, 2200, 'Babar Road, Gilgit, GB',
              ['Garden courtyard','Home cooking','Jeep hire','Trek advice'],
              'A legendary Gilgit guesthouse run by the Madina family, famed among KKH cyclists and trekkers for decades. Basic but spotless rooms around a fruit-tree courtyard.',
              'Yaqoob and his brothers have encyclopedic KKH knowledge — ask for advice over breakfast.'),
        hotel('Gilgit', 'Tourist Cottage Hostel', 'backpacker', 1, 600, 'Jamat Khana Bazaar, Gilgit, GB',
              ['Dorm beds','Communal kitchen','Bike storage','Roof terrace'],
              'A bare-bones hostel popular with long-haul overlanders and cyclists. Dorm beds, shared bathrooms, and a rooftop perfect for plotting the next KKH leg.',
              'Central bazaar location means you can walk to NATCO bus stand and jeep stands for onward travel.'),

        # ── CHITRAL ────────────────────────────────────────────────
        hotel('Chitral', 'Hindukush Heights', 'luxury', 5, 28000, 'Above Chitral Town, KP',
              ['Panoramic terrace','Hindukush views','Fine dining','Library','Organic garden'],
              'Perched on a hillside above Chitral town with unrestricted views of Tirich Mir (7,708 m), this boutique hotel blends local stone-and-wood architecture with refined cuisine from its own organic garden.',
              'Sundowners on the terrace as Tirich Mir turns pink are unmissable; sunset best June-September.'),
        hotel('Chitral', 'PTDC Motel Chitral', 'standard', 3, 7000, 'Shahi Mosque Road, Chitral, KP',
              ['Garden setting','Restaurant','Tour desk','Parking'],
              'A relaxed government motel in pleasant gardens near the Shahi Mosque and polo ground, with spacious en-suite rooms and dependable mid-range service.',
              'Stay here during the Shandur Polo Festival (July) — it\'s 10 min walk to the bazaar and polo ground.'),
        hotel('Chitral', 'Mountain Inn Chitral', 'budget', 2, 2300, 'Attaliq Bazaar, Chitral, KP',
              ['Family rooms','Hot water','Chitrali cuisine','Free parking'],
              'A family-run hotel in the bazaar with simple but clean rooms and excellent Chitrali home cooking (pulao, shoshp, chapati). Walking distance to everything in town.',
              'Ask for the Chitrali yak-meat pulao — a regional specialty rarely found elsewhere.'),
        hotel('Chitral', 'Chitral Backpackers Inn', 'backpacker', 1, 700, 'Polo Ground Road, Chitral, KP',
              ['Dorm beds','Shared kitchen','Kalash tour info','Bike storage'],
              'Budget dorm-style rooms run by a Kalash-heritage family. The common room is a hub for travellers heading to the Kalash valleys or Shandur.',
              'The owner arranges shared jeep rides to Bumburet — much cheaper than private hire if you can team up.'),

        # ── MURREE ─────────────────────────────────────────────────
        hotel('Murree', 'PC Bhurban (Pearl Continental)', 'luxury', 5, 45000, 'Bhurban, near Murree, Punjab',
              ['Golf course','Indoor pool','Spa','Multiple restaurants','Kids club'],
              'Pakistan\'s premier mountain resort at Bhurban with Pakistan\'s only 9-hole mountain golf course, indoor pool, spa, and sweeping pine-valley views. The benchmark for luxury in the Galiyat.',
              'The pine-facing rooms in the Golf Wing have the best views; book the "Summer Escape" package for meals included.'),
        hotel('Murree', 'Shangrila Midway House Murree', 'standard', 4, 12000, 'Mall Road, Murree, Punjab',
              ['Mall Road location','Restaurant','Valley views','Heating','Room service'],
              'A well-run mid-range hotel steps from Mall Road with warm rooms, cosy restaurant and pine-forest views. Excellent base for Mall walks, Patriata chair lift and Pindi Point.',
              'Winter (Dec-Feb) gets regular snowfall — the valley-view rooms are magical under snow.'),
        hotel('Murree', 'Lockwood Hotel', 'budget', 2, 3200, 'Lower Mall, Murree, Punjab',
              ['Central location','Restaurant','Hot water','Parking'],
              'Century-old hotel on Lower Mall with simple, clean rooms and a popular Punjabi-Chinese restaurant. Walking distance to Mall Road cable car and Kashmir Point.',
              'Midweek rates are 40% cheaper than weekend Islamabad-crowd rates; avoid long weekends.'),
        hotel('Murree', 'Youth Hostel Murree (PYHA)', 'backpacker', 1, 900, 'Jhika Gali, Murree, Punjab',
              ['Dorm beds','Shared kitchen','Forest trail access','Common room'],
              'Pine-forest-set Pakistan Youth Hostels Association property with clean dorms and private singles. Near Pindi Point chairlift and the Jhika Gali forest trail.',
              'PYHA card gives 20% discount; bring a warm sleeping bag liner even in summer — nights are chilly.'),

        # ── ATTOCK ─────────────────────────────────────────────────
        hotel('Attock', 'Attock View Resort', 'luxury', 4, 22000, 'GT Road near Attock Bridge, Punjab',
              ['Indus river views','Restaurant','Lawn gardens','Tour desk','Pool'],
              'A modern riverside resort overlooking the confluence of the Indus and Kabul rivers near historic Attock Bridge. Spacious rooms, a swimming pool and riverside lawns.',
              'The river-confluence view from the pool deck is spectacular at sunset — time dinner there.'),
        hotel('Attock', 'Attock Regency Hotel', 'standard', 3, 7500, 'GT Road, Attock City, Punjab',
              ['Restaurant','Conference hall','Parking','Room service'],
              'The main business-grade hotel in Attock city with comfortable modern rooms, a decent restaurant and reliable service. Convenient for Attock Fort visits.',
              'Ask the front desk to arrange a private tour of Attock Fort — army permission is usually granted with a day\'s notice.'),
        hotel('Attock', 'Shalimar Hotel Attock', 'budget', 2, 2400, 'Kamra Road, Attock, Punjab',
              ['AC rooms','Restaurant','Parking','Hot water'],
              'A reliable budget hotel on the main road with clean AC rooms and simple Pakistani cuisine. Good for a one-night stop en route to Peshawar or Islamabad.',
              'Order the Attock-style fried fish (from the Indus) at the in-house restaurant — a regional specialty.'),
        hotel('Attock', 'Indus Traveller Lodge', 'backpacker', 1, 800, 'Old Bazaar, Attock, Punjab',
              ['Shared rooms','Basic bath','Chai corner','Roof terrace'],
              'A modest traveller\'s lodge in the old bazaar, suitable for one-night stops. Rooms are basic but clean and the chai-wala next door is excellent.',
              'Walk five minutes to the Indus at dusk to watch the light change — a highlight of any Attock stay.'),

        # ── TARBELA ────────────────────────────────────────────────
        hotel('Tarbela', 'WAPDA Guest House Tarbela', 'luxury', 4, 18000, 'Tarbela Dam Colony, KP',
              ['Dam views','Manicured gardens','Fine dining','Boat trips','Tennis court'],
              'WAPDA\'s premier guesthouse within Tarbela\'s secure dam colony, offering lakeside rooms, boat trips on the reservoir and beautifully maintained colonial-era gardens.',
              'Booking requires a WAPDA reference letter; tour operators in Islamabad can arrange access 1 week ahead.'),
        hotel('Tarbela', 'Tarbela Lake Resort', 'standard', 3, 8000, 'Ghazi, near Tarbela, KP',
              ['Lake views','Restaurant','Boat hire','Lawn'],
              'A private resort near Ghazi village with lake-facing cottages, a decent restaurant and on-site boat hire for lake excursions.',
              'Cottages 4-6 sit right on the water — ask for them; boat-ride rates are negotiable off-peak.'),
        hotel('Tarbela', 'Ghazi Rest House', 'budget', 2, 2500, 'Ghazi Village, KP',
              ['Simple rooms','Home-cooked meals','Garden','Parking'],
              'A family-run rest house in Ghazi village, walking distance to Tarbela viewpoints. Basic clean rooms and hearty Pashtun home cooking.',
              'The grandmother\'s chapli kebab dinner is a must-order — just tell them you\'re hungry.'),
        hotel('Tarbela', 'Tarbela Traveller Camp', 'backpacker', 1, 600, 'Lakeside, Ghazi, KP',
              ['Tents','Communal kitchen','Campfire','Lake access'],
              'A no-frills lakeside tented camp with simple tents and shared meals. Best for hot-weather lake swims and campfire nights.',
              'Bring your own sleeping bag; camp managers can arrange freshwater fishing gear for PKR 300/day.'),

        # ── SUKKUR ─────────────────────────────────────────────────
        hotel('Sukkur', 'Pearl Continental Sukkur', 'luxury', 5, 28000, 'Workshop Road, Sukkur, Sindh',
              ['Indus views','Pool','Multiple restaurants','Spa','Business centre'],
              'The only 5-star in upper Sindh, overlooking the Indus near Sukkur Barrage with a large pool, several restaurants and the city\'s best Sindhi breakfast buffet.',
              'The riverside Lal Qila restaurant serves excellent Sindhi biryani and palla fish — reserve for Friday evenings.'),
        hotel('Sukkur', 'Inter Pak Inn', 'standard', 3, 7200, 'Military Road, Sukkur, Sindh',
              ['AC rooms','Restaurant','Conference room','Airport transfer'],
              'A dependable business hotel with clean modern rooms and a decent restaurant. Good base for visiting Sukkur Barrage and Sadhu Bela island.',
              'Arrange a tuk-tuk through the reception for Sadhu Bela — they negotiate PKR 600 return including waiting.'),
        hotel('Sukkur', 'Al-Mehran Hotel', 'budget', 2, 2600, 'Shikarpur Road, Sukkur, Sindh',
              ['AC rooms','Sindhi restaurant','Parking','Family rooms'],
              'A local favourite with clean AC rooms and a restaurant serving excellent Sindhi biryani and palla fish curry. Walking distance to Lansdowne Bridge.',
              'Try their palla (river fish) fry in season (July-October) — it\'s one of the best in Sukkur.'),
        hotel('Sukkur', 'Indus Traveller Hostel', 'backpacker', 1, 700, 'Minara Road, Sukkur, Sindh',
              ['Dorm beds','Chai lounge','Bike storage','Roof terrace'],
              'A simple backpacker stop near Minara Road with basic dorms and private singles. Rooftop evening chai with views over the Indus is the highlight.',
              'Walk to Sukkur Barrage at dusk for the best light over the Indus — about 20 mins from the hostel.'),

        # ── KALABAGH ───────────────────────────────────────────────
        hotel('Kalabagh', 'Kalabagh Resort', 'luxury', 4, 20000, 'Kalabagh Hills, Mianwali, Punjab',
              ['Hillside cottages','Indus views','Restaurant','Garden','Boating'],
              'A hillside heritage resort near the Kalabagh Nawab\'s estate with stone cottages overlooking the Indus as it enters the plains. Peaceful, characterful, and rarely busy.',
              'Pre-book with the resort directly — walk-ins are sometimes refused; breakfast on the terrace is a must.'),
        hotel('Kalabagh', 'Mianwali Inn', 'standard', 3, 6500, 'Daud Khel Road, Mianwali, Punjab',
              ['AC rooms','Restaurant','Parking','Tour desk'],
              'A straightforward mid-range hotel in Mianwali with clean AC rooms and a decent Punjabi restaurant. Best base for day trips to Kalabagh hills and Chashma Barrage.',
              'The tour desk can arrange a half-day jeep tour of Kalabagh and Chashma for around PKR 4,500.'),
        hotel('Kalabagh', 'Chashma Rest House', 'budget', 2, 2200, 'Chashma Barrage Road, Mianwali, Punjab',
              ['Barrage views','Simple rooms','Restaurant','Garden'],
              'A WAPDA-affiliated rest house near Chashma Barrage with simple rooms, a restaurant, and lovely evening walks along the canal.',
              'Migratory birds at Chashma Lake (Nov-Feb) are spectacular — bring binoculars and walk at dawn.'),
        hotel('Kalabagh', 'Mianwali Traveller Lodge', 'backpacker', 1, 600, 'Old Bazaar, Mianwali, Punjab',
              ['Basic rooms','Shared bath','Chai corner'],
              'A simple traveller\'s lodge in Mianwali\'s old bazaar suitable for one-night stops. Very basic but clean and friendly.',
              'The nearby Mianwali-style seekh kebab stalls after 7pm are legendary — ask any tuk-tuk driver.'),

        # ── ROHRI ──────────────────────────────────────────────────
        hotel('Rohri', 'Rohri Riverside Resort', 'luxury', 4, 18000, 'Bypass Road, Rohri, Sindh',
              ['Indus views','Restaurant','Pool','Garden','Boat trips'],
              'A modern riverside resort with lake-facing rooms and a pool overlooking the Indus. Convenient for Lansdowne Bridge and Sadhu Bela island excursions.',
              'The pool deck at sunset has the best view of Lansdowne Bridge — perfect for photographers.'),
        hotel('Rohri', 'Rohri Palace Hotel', 'standard', 3, 6800, 'Station Road, Rohri, Sindh',
              ['AC rooms','Sindhi restaurant','Parking','Tour desk'],
              'A reliable mid-range hotel with clean AC rooms and a Sindhi-cuisine restaurant. Walking distance to Rohri station and the river front.',
              'The tour desk arranges boat trips to Sadhu Bela for PKR 1,500 return — cheaper than Sukkur side.'),
        hotel('Rohri', 'Indus Lodge Rohri', 'budget', 2, 2200, 'Main Bazaar, Rohri, Sindh',
              ['Fan/AC rooms','Home-style meals','Parking'],
              'A family-run budget lodge in Rohri bazaar with simple clean rooms and hearty Sindhi home cooking.',
              'Ask for palla fish curry if they have it in season — their grandmother\'s recipe is superb.'),
        hotel('Rohri', 'Rohri Traveller Inn', 'backpacker', 1, 500, 'Station Road, Rohri, Sindh',
              ['Dorm beds','Shared bath','Chai corner'],
              'A very basic traveller\'s inn near Rohri Junction station, handy for early-morning train connections.',
              'Rohri Junction is one of Pakistan\'s busiest junctions — book sleeper tickets 48 hours ahead.'),

        # ── BAHAWALPUR ─────────────────────────────────────────────
        hotel('Bahawalpur', 'Noor Mahal Heritage Suites', 'luxury', 5, 35000, 'Near Noor Mahal Palace, Bahawalpur, Punjab',
              ['Palace views','Heritage rooms','Fine dining','Lawns','Cultural tours'],
              'Luxurious heritage-style suites close to the iconic Noor Mahal Palace, blending Nawabi architecture with modern comfort. The on-site restaurant serves royal Bahawalpuri cuisine.',
              'Book the Noor Mahal evening tour package — includes palace entry and Nawabi dinner at the hotel.'),
        hotel('Bahawalpur', 'Hotel One Bahawalpur', 'standard', 3, 8500, 'Model Town, Bahawalpur, Punjab',
              ['Modern rooms','Restaurant','Gym','Free Wi-Fi','Airport transfer'],
              'A modern PC-brand mid-range hotel in Model Town with bright rooms, a competent restaurant and reliable service. Good base for Derawar Fort expeditions.',
              'Book the Derawar Fort jeep package through the hotel — PKR 12,000 covers vehicle, driver and lunch.'),
        hotel('Bahawalpur', 'Al-Noor Hotel Bahawalpur', 'budget', 2, 2800, 'Circular Road, Bahawalpur, Punjab',
              ['AC rooms','Bahawalpuri cuisine','Parking','Tour desk'],
              'A long-standing budget hotel in the city centre with clean AC rooms and a restaurant famous for its Bahawalpuri sohan halwa and sajji.',
              'Order sajji (whole roasted lamb) in advance (4 hours) — it\'s spectacular and feeds 4 people for PKR 6,000.'),
        hotel('Bahawalpur', 'Cholistan Backpackers Hostel', 'backpacker', 1, 900, 'Railway Road, Bahawalpur, Punjab',
              ['Dorm beds','Shared kitchen','Cholistan tour info','Roof terrace'],
              'A popular backpacker base run by desert-trek enthusiasts who organise budget-friendly group trips to Derawar Fort and Cholistan Jeep Rally.',
              'Join the monthly Derawar overnight camp — PKR 4,500 covers transport, tent, and Cholistani dinner.'),

        # ── UMARKOT ────────────────────────────────────────────────
        hotel('Umarkot', 'Umarkot Desert Resort', 'luxury', 4, 16000, 'Umarkot-Chhor Road, Sindh',
              ['Desert views','Thatched cottages','Pool','Camel safari','Sindhi cuisine'],
              'A boutique desert resort with thatched cottages and a pool set amid the Thar landscape. The restaurant serves excellent traditional Sindhi thali.',
              'The camel safari at sunset (PKR 2,500pp) is magical; the resort also arranges overnight desert camps.'),
        hotel('Umarkot', 'Thar Inn', 'standard', 3, 6500, 'Main Bazaar, Umarkot, Sindh',
              ['AC rooms','Restaurant','Parking','Tour desk'],
              'A clean mid-range hotel in Umarkot town with AC rooms and a restaurant serving Sindhi-Rajasthani cuisine. Handy for visiting Umarkot Fort.',
              'The hotel arranges Hindu-temple tours of Umarkot (Krishna birthplace) with a knowledgeable local guide.'),
        hotel('Umarkot', 'Umarkot Guesthouse', 'budget', 2, 2000, 'Fort Road, Umarkot, Sindh',
              ['Fan/AC rooms','Home cooking','Garden','Parking'],
              'A simple family-run guesthouse near Umarkot Fort with clean rooms and home-cooked Sindhi meals.',
              'The owners are Hindu Sindhi — ask about Holi celebrations in March, they\'re spectacular here.'),
        hotel('Umarkot', 'Thar Traveller Camp', 'backpacker', 1, 700, 'Outskirts of Umarkot, Sindh',
              ['Desert tents','Shared kitchen','Camel rides','Campfire'],
              'A rustic tented camp run by a local Thari family. Desert stargazing and communal meals around the fire make for memorable nights.',
              'Bring a sleeping bag; the Thar nights are surprisingly cold Dec-Feb (can drop to 5°C).'),

        # ── MITHI ──────────────────────────────────────────────────
        hotel('Mithi', 'Mithi Desert Lodge', 'luxury', 4, 15000, 'Mithi-Nagarparkar Road, Tharparkar, Sindh',
              ['Desert views','Cottages','Traditional Sindhi dining','Garden','Cultural evenings'],
              'A boutique lodge with beautifully designed earth-and-wood cottages overlooking the Thar dunes. Cultural evenings of Sindhi folk music are a highlight.',
              'Ask for the sunrise camel ride package — includes dune visit, breakfast on the dunes and local guide.'),
        hotel('Mithi', 'Thar Heritage Hotel', 'standard', 3, 5500, 'Main Bazaar, Mithi, Sindh',
              ['AC rooms','Restaurant','Tour desk','Parking'],
              'A mid-range hotel in Mithi town serving as a reliable base for exploring Tharparkar\'s villages, temples and Nagarparkar Jain temples.',
              'Arrange a Jain-temple day trip (PKR 6,000) — Nagarparkar\'s 900-year-old marble temples are stunning.'),
        hotel('Mithi', 'Mithi Guest House', 'budget', 2, 1800, 'Village Road, Mithi, Sindh',
              ['Fan rooms','Home-cooked meals','Courtyard'],
              'A simple guesthouse run by a local Thari family with clean fan-cooled rooms and wholesome vegetarian Sindhi-Hindu home cooking.',
              'The vegetarian thali (PKR 400) is exceptional — try the Thari-style daal bati.'),
        hotel('Mithi', 'Thar Backpackers Camp', 'backpacker', 1, 500, 'Outskirts of Mithi, Sindh',
              ['Tents','Shared kitchen','Dune walks','Campfire'],
              'A rustic desert camp for backpackers, with simple tents and communal Thari meals. Ideal for those wanting an authentic desert experience.',
              'Watch for peacocks at dawn — Tharparkar has one of Pakistan\'s largest wild peacock populations.'),

        # ── RAHIM YAR KHAN ─────────────────────────────────────────
        hotel('Rahim Yar Khan', 'Pearl Continental Rahim Yar Khan', 'luxury', 5, 25000, 'Airport Road, Rahim Yar Khan, Punjab',
              ['Pool','Spa','Multiple restaurants','Business centre','Gym'],
              'The best hotel in southern Punjab with spacious rooms, an excellent pool and the region\'s finest restaurants. Premier base for visiting Qila Derawar and Cholistan.',
              'The Abbasi Suite has desert views; their Saraiki breakfast buffet is regionally famous.'),
        hotel('Rahim Yar Khan', 'Hotel One Rahim Yar Khan', 'standard', 3, 7500, 'Model Town, Rahim Yar Khan, Punjab',
              ['Modern rooms','Restaurant','Free Wi-Fi','Airport transfer'],
              'Modern mid-range hotel with bright rooms and a capable restaurant. Reliable base for business or desert excursions.',
              'Book the Bhong Mosque half-day trip — the ornate mosque (Aga Khan Award winner) is an hour\'s drive.'),
        hotel('Rahim Yar Khan', 'Shalimar Hotel RYK', 'budget', 2, 2500, 'Railway Road, Rahim Yar Khan, Punjab',
              ['AC rooms','Punjabi cuisine','Parking','Tour desk'],
              'A long-standing budget hotel with clean AC rooms and solid Punjabi-Saraiki cuisine. Convenient for the railway station and bazaar.',
              'Order their sohan halwa to take home — RYK\'s local version rivals Multan\'s.'),
        hotel('Rahim Yar Khan', 'Desert Traveller Lodge', 'backpacker', 1, 800, 'Bypass Road, Rahim Yar Khan, Punjab',
              ['Dorm beds','Shared kitchen','Desert tour info','Roof terrace'],
              'Basic backpacker lodge with dorms and single rooms. Staff help organise shared jeep trips to Cholistan and Derawar.',
              'Cholistan Jeep Rally (February) is a highlight — book 2 months ahead as RYK fills up.'),

        # ── KARACHI ────────────────────────────────────────────────
        hotel('Karachi', 'Mövenpick Hotel Karachi', 'luxury', 5, 42000, 'Club Road, Karachi, Sindh',
              ['Multiple restaurants','Pool','Spa','Gym','Business centre'],
              'Landmark 5-star on Club Road with elegant rooms, a rooftop pool and Karachi\'s best Sunday brunch. Walking distance to Frere Hall and shopping.',
              'Sunday brunch at Pearl serves 150+ dishes and books out — reserve Friday.'),
        hotel('Karachi', 'Regent Plaza Hotel', 'standard', 4, 11000, 'Shahrah-e-Faisal, Karachi, Sindh',
              ['Pool','Restaurant','Gym','Airport transfer','Business centre'],
              'Well-run mid-range hotel on main Shahrah-e-Faisal with reliable business-class rooms and a pleasant pool. 10 min from the airport.',
              'The 24-hour café serves excellent nihari till 3am — a Karachi tradition.'),
        hotel('Karachi', 'Hotel Blue Star', 'budget', 2, 3200, 'Preedy Street, Saddar, Karachi, Sindh',
              ['AC rooms','Restaurant','Central location','Parking'],
              'A cheerful budget hotel in Saddar\'s heart with clean AC rooms and walking-distance access to Empress Market, Frere Hall and heritage streets.',
              'Walk to Burns Road for Karachi\'s best street food at night — 15 mins on foot.'),
        hotel('Karachi', 'Moin Backpackers Hostel', 'backpacker', 1, 1000, 'DHA Phase 2, Karachi, Sindh',
              ['Dorm beds','Kitchen','Rooftop lounge','Surf-trip info'],
              'Karachi\'s best-run backpacker hostel in DHA with clean dorms, a big communal kitchen and staff who help arrange beach and surf trips.',
              'They organise weekend trips to French Beach and Hawkesbay — PKR 2,500 all-inclusive.'),

        # ── GWADAR ─────────────────────────────────────────────────
        hotel('Gwadar', 'Pearl Continental Gwadar', 'luxury', 5, 38000, 'Koh-e-Batil, Gwadar, Balochistan',
              ['Private beach','Pool','Spa','Fine dining','Sea views'],
              'Perched on Koh-e-Batil cliff overlooking the Gwadar hammerhead, this PC offers dramatic ocean views, a private beach and the only real luxury on this coast.',
              'Sea-facing rooms are essential; sunset from the pool deck over the Arabian Sea is unforgettable.'),
        hotel('Gwadar', 'Zaver Pearl-Continental Motel', 'standard', 3, 9000, 'Fish Harbour Road, Gwadar, Balochistan',
              ['Sea views','Restaurant','AC rooms','Airport transfer'],
              'A mid-range sister property with sea-facing rooms and a good seafood restaurant. Best value for those wanting coast views without luxury prices.',
              'Order the fresh local lobster and prawns at dinner — caught that morning from Gwadar harbour.'),
        hotel('Gwadar', 'Gwadar Beach Lodge', 'budget', 2, 3200, 'Marine Drive, Gwadar, Balochistan',
              ['Beach access','Seafood restaurant','AC rooms','Parking'],
              'A simple beach-side lodge with AC rooms and a rooftop restaurant serving freshly caught seafood. Walking distance to Padi Zirr beach.',
              'Walk to Padi Zirr at sunset for the iconic Gwadar hammerhead silhouette shot.'),
        hotel('Gwadar', 'Ormara-Gwadar Traveller Camp', 'backpacker', 1, 800, 'East Bay, Gwadar, Balochistan',
              ['Beach tents','Shared kitchen','Surf gear rental','Campfire'],
              'A rustic beach camp with tents on East Bay. Surf-friendly waves, communal Balochi meals and campfire evenings under the stars.',
              'Register with Balochistan Levies on arrival — the camp owner handles permits; NOC is simple.'),

        # ── ORMARA ─────────────────────────────────────────────────
        hotel('Ormara', 'Ormara Beach Resort', 'luxury', 4, 18000, 'Hammerhead Road, Ormara, Balochistan',
              ['Private beach','Sea-view cottages','Restaurant','Fishing trips','Sunset deck'],
              'The only proper resort on the Ormara coast, with whitewashed cottages on a private beach and a restaurant specialising in fresh grilled fish.',
              'The hammerhead-facing cottages are stunning at sunset; dolphin-watching boat trips available Nov-Mar.'),
        hotel('Ormara', 'Ormara Bay Lodge', 'standard', 3, 6500, 'Main Bazaar, Ormara, Balochistan',
              ['AC rooms','Seafood restaurant','Parking','Tour desk'],
              'A simple mid-range lodge in Ormara village with AC rooms and a restaurant serving the day\'s catch. Good base for exploring the coast.',
              'Staff help arrange dolphin-spotting trips (PKR 4,000/boat) from the fishing harbour.'),
        hotel('Ormara', 'Ormara Fishing Guesthouse', 'budget', 2, 1800, 'Harbour Road, Ormara, Balochistan',
              ['Fan rooms','Home cooking','Harbour views'],
              'A family-run guesthouse next to the fishing harbour with simple rooms and fantastic home-cooked Balochi fish curries.',
              'Walk to the harbour at dawn to watch the fishing boats unload — an unforgettable sight.'),
        hotel('Ormara', 'Ormara Beach Camping', 'backpacker', 1, 600, 'East Beach, Ormara, Balochistan',
              ['Tents','Campfire','Shared meals','Surf access'],
              'Bare-bones beach camping on the long Ormara east beach. BYO sleeping bag; tents, meals and firewood provided.',
              'Expect to be the only campers — the Makran coast is remarkably quiet outside peak months.'),

        # ── KUND MALIR ─────────────────────────────────────────────
        hotel('Kund Malir', 'Hingol Desert Resort', 'luxury', 4, 16000, 'Kund Malir, Balochistan',
              ['Beachfront','Cottages','Restaurant','Safari jeeps','Desert views'],
              'A remote luxury desert camp with stone cottages between the mountains and the Arabian Sea. The restaurant serves fresh grilled fish nightly.',
              'Book the Hingol National Park safari day (PKR 8,000) — includes Princess of Hope and Buzi Pass.'),
        hotel('Kund Malir', 'Kund Malir Beach Hut', 'standard', 3, 6500, 'Beach Road, Kund Malir, Balochistan',
              ['Sea-view rooms','Restaurant','Parking','Tour desk'],
              'A rustic mid-range option with simple beach huts overlooking the Arabian Sea, each with its own verandah and a shared restaurant.',
              'Book via the Makran Coastal Highway tour operators in Karachi — no direct reservations.'),
        hotel('Kund Malir', 'Kund Malir Rest House', 'budget', 2, 2000, 'Coastal Highway, Kund Malir, Balochistan',
              ['Basic rooms','Shared bath','Canteen','Parking'],
              'A basic PWD rest house on the Makran Coastal Highway, suitable for one-night stops. Simple rooms and a canteen serving daal-chawal.',
              'Arrive before sunset; the highway is unlit and remote Balochistan coast travel is discouraged after dark.'),
        hotel('Kund Malir', 'Kund Malir Beach Camping', 'backpacker', 1, 500, 'Kund Malir Beach, Balochistan',
              ['Tents','Campfire','BYO sleeping bag','Sea views'],
              'Wild beach camping on the dramatic Kund Malir shoreline. Local fishermen set up tents and cook fresh catch over an open fire.',
              'Bring all your own water and supplies from Karachi; the nearest town is 100+ km away.'),

        # ── LAHORE ─────────────────────────────────────────────────
        hotel('Lahore', 'Pearl Continental Lahore', 'luxury', 5, 45000, 'Shahrah-e-Quaid-e-Azam, Lahore, Punjab',
              ['Pool','Spa','Multiple restaurants','Shopping arcade','Gym'],
              'The grande-dame of Lahore hotels in landscaped gardens off The Mall, famed for its marble lobby, Sunday brunch and proximity to GPO and Mall Road heritage sites.',
              'Marco Polo\'s Sunday brunch is a Lahore institution; Lahori nihari at Nadia coffee shop is excellent.'),
        hotel('Lahore', 'Avari Hotel Lahore', 'standard', 4, 15000, 'The Mall, Lahore, Punjab',
              ['Pool','Dynasty Chinese restaurant','Gym','Business centre'],
              'A long-standing Mall Road stalwart with comfortable rooms, the famous Dynasty Chinese restaurant and walking distance to GPO, Tollinton Market and Anarkali.',
              'Dynasty is widely regarded as Lahore\'s best Chinese restaurant — book a window table.'),
        hotel('Lahore', 'Hotel One Lahore Downtown', 'budget', 2, 3500, 'Davis Road, Lahore, Punjab',
              ['AC rooms','Restaurant','Free Wi-Fi','Airport transfer'],
              'A smart budget option in PC\'s Hotel One chain with modern rooms, clean bathrooms and a small café. Good base for Anarkali and Mall Road.',
              'Walk or Careem to Food Street Gawalmandi for an authentic Lahori dinner.'),
        hotel('Lahore', 'Regale Internet Inn', 'backpacker', 1, 1000, 'Regal Chowk, The Mall, Lahore, Punjab',
              ['Dorm beds','Rooftop terrace','Tour desk','Laundry'],
              'A legendary backpacker hostel on The Mall, home to generations of overland travellers. The rooftop chai sessions and Malik\'s Walled City tours are famous.',
              'Malik\'s Walled City night walk (PKR 1,500) is a must-do — starts 7pm from the hostel lobby.'),

        # ── TAXILA ─────────────────────────────────────────────────
        hotel('Taxila', 'Taxila Heritage Resort', 'luxury', 4, 20000, 'Near Taxila Museum, Punjab',
              ['Heritage design','Gandhara-art-themed rooms','Garden','Restaurant','Tour desk'],
              'A boutique resort near Taxila Museum with Gandhara-inspired architecture, peaceful gardens and a restaurant focusing on Pothohari cuisine.',
              'Book the licensed-guide package for Bhir, Sirkap and Jaulian — covers all three main archaeological sites.'),
        hotel('Taxila', 'PTDC Motel Taxila', 'standard', 3, 7000, 'Taxila Museum Road, Punjab',
              ['Clean rooms','Garden','Restaurant','Parking'],
              'A reliable government motel next to the Taxila Museum with clean en-suite rooms and a simple restaurant. Ideal launching pad for heritage exploration.',
              'Open the day with Taxila Museum (opens 9am) then walk straight to Sirkap — saves hiring transport.'),
        hotel('Taxila', 'Taxila Comfort Inn', 'budget', 2, 2500, 'GT Road, Taxila, Punjab',
              ['AC rooms','Pakistani restaurant','Parking','Tour desk'],
              'A straightforward budget hotel on GT Road with clean AC rooms and a Pakistani-Chinese restaurant. Good base for day trips from Islamabad.',
              'Share a taxi with museum visitors — PKR 1,500 return covers all three archaeological sites.'),
        hotel('Taxila', 'Taxila Traveller Lodge', 'backpacker', 1, 700, 'Wah Cantt Road, Taxila, Punjab',
              ['Dorm beds','Shared kitchen','Bike hire','Common room'],
              'A budget backpacker lodge popular with students from Islamabad. Bike hire available for exploring the dispersed ruins.',
              'Rent a bike (PKR 400/day) — the archaeological sites are 4-8 km apart, perfect for cycling.'),

        # ── LARKANA ────────────────────────────────────────────────
        hotel('Larkana', 'Sambara Inn Larkana', 'luxury', 4, 18000, 'Station Road, Larkana, Sindh',
              ['Modern rooms','Pool','Restaurant','Gym','Airport transfer'],
              'The smartest hotel in Larkana with a swimming pool, excellent restaurant and the city\'s most reliable service. Premier base for Mohenjo-daro.',
              'Book the full-day Mohenjo-daro package — includes guide, lunch at the site and return transfer.'),
        hotel('Larkana', 'Sachal Hotel', 'standard', 3, 6500, 'VIP Road, Larkana, Sindh',
              ['AC rooms','Sindhi restaurant','Parking','Tour desk'],
              'A mid-range business hotel with clean AC rooms and an excellent restaurant specialising in Sindhi biryani and palla fish.',
              'Their Sindhi biryani dinner is regionally famous — order in advance for best results.'),
        hotel('Larkana', 'Indus Rest House Larkana', 'budget', 2, 2300, 'Bakrani Road, Larkana, Sindh',
              ['Fan/AC rooms','Home cooking','Parking'],
              'A simple but clean family-run rest house popular with archaeologists and students visiting Mohenjo-daro and Indus Valley sites.',
              'Share a van to Mohenjo-daro (45 min) with other guests — reception arranges it for PKR 400pp.'),
        hotel('Larkana', 'Mohenjo-daro Backpackers Lodge', 'backpacker', 1, 700, 'Shikarpur Road, Larkana, Sindh',
              ['Dorm beds','Chai corner','Archaeology tour info'],
              'A basic lodge run by an archaeology enthusiast, with dorms and a common room full of Mohenjo-daro books and maps.',
              'The owner offers guided Mohenjo-daro day trips — he\'s excavated there and gives a master-class tour.'),

        # ── PESHAWAR ───────────────────────────────────────────────
        hotel('Peshawar', 'Pearl Continental Peshawar', 'luxury', 5, 32000, 'Khyber Road, Peshawar, KP',
              ['Pool','Multiple restaurants','Spa','Gym','Business centre'],
              'The top hotel in Peshawar in a large walled garden on Khyber Road, with spacious rooms, a pool and the city\'s best Afghan-Pashtun cuisine.',
              'Chandni Restaurant\'s Peshawari karahi and Afghan-style lamb kebab are city-famous.'),
        hotel('Peshawar', 'Shelton Rezidor', 'standard', 4, 12000, 'University Road, Peshawar, KP',
              ['Modern rooms','Restaurant','Gym','Pool','Airport transfer'],
              'A modern mid-range hotel on University Road with bright rooms, a good restaurant and a small pool. Convenient for university, airport and Qissa Khwani.',
              'Careem to Qissa Khwani for the chai — 10 min away, and a Peshawar must-visit.'),
        hotel('Peshawar', 'Hotel Khyber Ikram', 'budget', 2, 3000, 'Jamrud Road, Peshawar, KP',
              ['AC rooms','Afghan restaurant','Parking','Tour desk'],
              'A reliable budget hotel with clean AC rooms and an Afghan-Peshawari restaurant. Walking distance to Qissa Khwani Bazaar.',
              'Try the hotel\'s kabuli pulao — the restaurant caters to Afghan diaspora and the recipe is authentic.'),
        hotel('Peshawar', 'Greens Hotel Peshawar', 'backpacker', 1, 900, 'Saddar Bazaar, Peshawar, KP',
              ['Dorm beds','Shared kitchen','Chai lounge','Tour info'],
              'A no-frills traveller\'s hotel in Saddar Bazaar with dorms and basic singles. Central location, friendly staff and great chai corner.',
              'Walk to Qissa Khwani for the old storytellers\' chai and namak mandi for Peshawari kebabs.'),

        # ── MULTAN ─────────────────────────────────────────────────
        hotel('Multan', 'Ramada by Wyndham Multan', 'luxury', 5, 28000, 'Abdali Road, Multan, Punjab',
              ['Pool','Spa','Multiple restaurants','Gym','Business centre'],
              'The top international-brand hotel in Multan with spacious rooms, a pool and excellent Punjabi-Saraiki cuisine. Central base for shrines and Old City.',
              'Book a sunset rickshaw Old-City tour through concierge — covers Shah Rukn-e-Alam and Bahauddin Zakariya shrines.'),
        hotel('Multan', 'Avari Xpress Multan', 'standard', 3, 8500, 'Bosan Road, Multan, Punjab',
              ['Modern rooms','Restaurant','Gym','Airport transfer'],
              'A smart mid-range property with clean contemporary rooms and a capable restaurant. Good base for Multan\'s shrines and crafts.',
              'The Saraiki-cuisine Sunday buffet is exceptional — sohan halwa, sajji and local Multani dishes.'),
        hotel('Multan', 'Hotel Sindbad', 'budget', 2, 2600, 'Nishtar Road, Multan, Punjab',
              ['AC rooms','Pakistani restaurant','Parking','Tour desk'],
              'A long-running budget hotel with clean AC rooms and hearty Punjabi-Saraiki cuisine. Walking distance to Multan Fort and shrines.',
              'Walk to Multan Fort at sunset — the light on the blue-tiled Shah Rukn-e-Alam shrine is unmatched.'),
        hotel('Multan', 'Multan Backpackers Hostel', 'backpacker', 1, 900, 'Chowk Shah Abbas, Multan, Punjab',
              ['Dorm beds','Shared kitchen','Rooftop','Heritage walks'],
              'A traveller\'s hostel near the shrines with dorms and a rooftop overlooking the Old City. Run by a heritage-enthusiast who leads free walking tours.',
              'Join the free Friday afternoon heritage walk — covers shrines, bazaars and street food.'),

        # ── NARAN ──────────────────────────────────────────────────
        hotel('Naran', 'Arcadian Blue Pines Resort', 'luxury', 4, 22000, 'Naran Town, KP',
              ['River views','Log cabins','Restaurant','Tour desk','Heating'],
              'A charming log-cabin resort on the Kunhar River with river-view rooms and a restaurant serving fresh trout. Premier mid-to-luxury option in Kaghan-Naran.',
              'Request a river-facing cabin; the sound of the Kunhar at night is the perfect accompaniment.'),
        hotel('Naran', 'PTDC Motel Naran', 'standard', 3, 8000, 'Main Road, Naran, KP',
              ['River views','Restaurant','Parking','Tour desk'],
              'A long-established government motel on the Kunhar riverbank with comfortable rooms and a busy restaurant. Ideal base for Saiful Muluk and Babusar.',
              'Jeeps to Saiful Muluk Lake leave from outside the motel at dawn — PKR 2,500 return per jeep.'),
        hotel('Naran', 'Lalazar Hotel Naran', 'budget', 2, 2800, 'Bazaar Road, Naran, KP',
              ['AC/heated rooms','Trout restaurant','Parking'],
              'A reliable budget hotel in Naran bazaar with clean heated rooms and a popular trout restaurant. Walking distance to jeep stands.',
              'Order the Kunhar trout in garlic butter — their speciality and a regional standout.'),
        hotel('Naran', 'Naran Youth Hostel', 'backpacker', 1, 800, 'Old Bazaar, Naran, KP',
              ['Dorm beds','Shared kitchen','Tour desk','Common room'],
              'A simple hostel popular with Pakistani students and international trekkers. Dorm beds, basic singles, and shared jeep bookings to Saiful Muluk.',
              'Sharing jeep rides (6 per jeep) keeps Saiful Muluk costs to PKR 400pp; the front desk arranges groups.'),

        # ── GOJAL/ATTABAD ──────────────────────────────────────────
        hotel('Gojal/Attabad', 'Luxus Hunza Attabad Lake Resort', 'luxury', 5, 40000, 'Attabad Lake, Gojal, GB',
              ['Lakefront cottages','Private jetty','Fine dining','Spa','Boat rides'],
              'Pakistan\'s most striking lakeside luxury, with timber-framed cottages stepping down to Attabad\'s electric-blue water. Private jetty, spa and outstanding cuisine.',
              'Book the lake-villa category; sunrise from the private jetty over the blue water is unforgettable.'),
        hotel('Gojal/Attabad', 'Attabad Lake View Hotel', 'standard', 3, 9500, 'Hussaini, Gojal, GB',
              ['Lake views','Restaurant','Heating','Boat booking'],
              'Mid-range hotel perched above Attabad Lake with clean, warm rooms and panoramic lake views. Convenient for Hussaini suspension bridge.',
              'Walk to Hussaini Bridge at sunrise — the most photogenic moment, before other tourists arrive.'),
        hotel('Gojal/Attabad', 'Passu Inn', 'budget', 2, 2800, 'Passu Village, Gojal, GB',
              ['Mountain views','Home cooking','Garden','Hot showers'],
              'A friendly family-run inn in Passu with views of the Passu Cones and glacier. Home-cooked Wakhi meals are a highlight.',
              'Order the Wakhi tumoro (shapik) bread fresh from the tandoor; evening walks to the glacier snout are spectacular.'),
        hotel('Gojal/Attabad', 'Sost Backpackers Inn', 'backpacker', 1, 900, 'Sost Town, Gojal, GB',
              ['Dorm beds','Shared kitchen','KKH tour info','Customs-area access'],
              'The northernmost backpacker hotel in Pakistan at Sost, the Khunjerab border town. Basic dorms and singles popular with KKH cyclists and Chinese-border travellers.',
              'Cross-border arrangements are easier from Sost — the owner helps with Khunjerab permits and Chinese visa paperwork.'),

        # ── ISLAMABAD ──────────────────────────────────────────────
        hotel('Islamabad', 'Serena Hotel Islamabad', 'luxury', 5, 48000, 'Khayaban-e-Suharwardy, Islamabad',
              ['Heritage architecture','Pool','Spa','Multiple restaurants','Gardens'],
              'The grande-dame of Islamabad, with Mughal-inspired architecture, lush gardens overlooking Margalla Hills, an acclaimed spa and six restaurants. The best address in the capital.',
              'Book a Margalla-view room; the Taipan Chinese restaurant and Zamana Sunday brunch are city-defining.'),
        hotel('Islamabad', 'Ramada Islamabad', 'standard', 4, 13000, 'Club Road, F-5, Islamabad',
              ['Pool','Gym','Restaurant','Airport transfer','Business centre'],
              'A reliable international-brand hotel in F-5 with contemporary rooms, a pool and easy access to Blue Area offices and Centaurus Mall.',
              'Careem to Daman-e-Koh (15 min) at sunset for the best Islamabad panorama.'),
        hotel('Islamabad', 'Hotel One Super', 'budget', 2, 3500, 'F-10 Markaz, Islamabad',
              ['AC rooms','Restaurant','Free Wi-Fi','Parking'],
              'Smart budget hotel in F-10 Markaz with clean modern rooms and walking distance to cafes, pharmacies and groceries.',
              'The F-10 cafés and food street are a 5 min walk; Saidpur Village by Careem (20 min) for dinner views.'),
        hotel('Islamabad', 'Islamabad Backpackers Hostel', 'backpacker', 1, 1000, 'F-7 Markaz, Islamabad',
              ['Dorm beds','Shared kitchen','Margalla trail info','Rooftop'],
              'The capital\'s best-known backpacker hostel in F-7 with dorms, private singles and a rooftop where travellers plot KKH adventures.',
              'Join the weekly Trail 3 Margalla hike — the hostel organises it free every Saturday at 6am.'),

        # ── UPPER DIR ──────────────────────────────────────────────
        hotel('Upper Dir', 'Kumrat Continental Resort', 'luxury', 4, 18000, 'Kumrat Valley Road, Upper Dir, KP',
              ['Forest cottages','River views','Restaurant','Campfire lounge','Trek desk'],
              'Beautifully sited log cottages in Kumrat Valley\'s cedar forest, with river-sound rooms, a rustic restaurant and organised day-treks to Jahaz Banda.',
              'Request the river-side cottages; Jahaz Banda Meadows day-trek (PKR 3,500 with guide) is a must.'),
        hotel('Upper Dir', 'PTDC Hut Kumrat', 'standard', 3, 6500, 'Thal, Upper Dir, KP',
              ['Forest setting','Shared dining','Heating','Trek info'],
              'Simple government huts in Thal village (gateway to Kumrat) with clean rooms and a communal dining hall. Perfect for trek prep.',
              'Thal to Kumrat core area is 1.5 hr by 4×4 — share rides for PKR 800pp.'),
        hotel('Upper Dir', 'Dir Comfort Inn', 'budget', 2, 2200, 'Dir Khas Bazaar, Upper Dir, KP',
              ['Fan/AC rooms','Pashtun cuisine','Parking'],
              'Family-run budget hotel in Dir town with simple clean rooms and hearty Pashtun home cooking.',
              'The owner\'s wife makes exceptional painda (Dir-style meat stew) — order in advance.'),
        hotel('Upper Dir', 'Kumrat Forest Camping', 'backpacker', 1, 700, 'Kumrat Core Valley, Upper Dir, KP',
              ['Forest tents','Campfire','Shared meals','Trek access'],
              'Tented camping inside Kumrat Valley\'s cedar forest. The nightly campfires and communal Pashtun meals are the highlight.',
              'Bring a warm sleeping bag — nights drop below 10°C even in mid-summer at 2,100 m.'),

        # ── SWAT ───────────────────────────────────────────────────
        hotel('Swat', 'Serena Swat', 'luxury', 5, 32000, 'Saidu Sharif, Swat, KP',
              ['Heritage architecture','Pool','Spa','Garden','Fine dining'],
              'A beautifully restored heritage hotel in Saidu Sharif, once a royal guesthouse of the Wali of Swat. Mountain views, lush gardens and excellent Swati cuisine.',
              'Request a garden-view suite; the Swati buffet dinner features rare local dishes.'),
        hotel('Swat', 'Rock City Resort', 'standard', 4, 10000, 'Malam Jabba Road, Swat, KP',
              ['Mountain views','Restaurant','Conference room','Heating'],
              'A popular mid-range resort on Malam Jabba Road with spacious rooms and a decent restaurant. Ideal for skiing and Kalam trips.',
              'Ski season (Dec-Feb) needs early booking; summer rates can drop 40% on weekdays.'),
        hotel('Swat', 'Hotel Pameer', 'budget', 2, 2700, 'Mingora Main Bazaar, KP',
              ['AC rooms','Swati restaurant','Parking','Tour desk'],
              'A long-established budget hotel in Mingora with clean rooms and Swati cuisine. Walking distance to Butkara Stupa and the museum.',
              'Walk to the Swat Museum early morning — it opens at 9am and it\'s 10 min from the hotel.'),
        hotel('Swat', 'Swat Backpackers Lodge', 'backpacker', 1, 800, 'Mingora Bazaar, KP',
              ['Dorm beds','Shared kitchen','Tour desk','Rooftop'],
              'Budget hostel popular with archaeologists and trekkers. Staff organise shared jeeps to Kalam, Mahodand and Ushu Forest.',
              'Sharing jeep costs to Kalam (PKR 500pp) is the hostel\'s biggest draw — ask at reception.'),

        # ── KAGHAN ─────────────────────────────────────────────────
        hotel('Kaghan', 'Pine Park Shogran', 'luxury', 4, 22000, 'Shogran Plateau, Kaghan, KP',
              ['Forest cottages','Plateau views','Restaurant','Campfire lounge','Jeep rides'],
              'Pine-clad cottages on the Shogran Plateau with panoramic Himalayan views, a rustic restaurant and evening bonfires.',
              'The sunset from the terrace over Kaghan is spectacular; book a plateau-view cottage.'),
        hotel('Kaghan', 'PTDC Motel Kaghan', 'standard', 3, 7000, 'Kaghan Village, KP',
              ['River views','Restaurant','Parking','Tour desk'],
              'A well-established motel in Kaghan village on the Kunhar riverbank with clean rooms and dependable service.',
              'Ask for rooms 101-105 — they face directly onto the Kunhar rapids.'),
        hotel('Kaghan', 'Balakot Comfort Hotel', 'budget', 2, 2500, 'Main Bazaar, Balakot, KP',
              ['AC rooms','Trout restaurant','Parking'],
              'A reliable budget hotel in Balakot with clean rooms and fresh river trout from their own riverside restaurant.',
              'Balakot\'s river-side trout restaurants serve whole trout meals for PKR 600 — superb value.'),
        hotel('Kaghan', 'Kaghan Valley Campsite', 'backpacker', 1, 700, 'Kaghan Village outskirts, KP',
              ['Tents','Shared meals','Campfire','River access'],
              'Rustic riverside camping in Kaghan village with simple tents, communal meals and evening campfires by the Kunhar.',
              'Bring warm clothes — the valley cools to single digits even in July nights.'),

        # ── NEELUM VALLEY ──────────────────────────────────────────
        hotel('Neelum Valley', 'Neelum Valley Resort Keran', 'luxury', 4, 20000, 'Keran, Neelum Valley, AJK',
              ['River-front cottages','Forest views','Restaurant','Trek desk','Trout pond'],
              'A timber-cottage resort on the Neelum riverbank in Keran with forest-lined verandahs, a trout pond and an excellent trout-focused restaurant.',
              'Book the river-edge cottages (101-105) months ahead for summer; AJK permit required.'),
        hotel('Neelum Valley', 'PTDC Motel Sharda', 'standard', 3, 7500, 'Sharda Town, Neelum Valley, AJK',
              ['River views','Restaurant','Parking','Tour desk'],
              'Well-kept government motel in Sharda with clean river-view rooms and a restaurant. Convenient for Sharda ruins and Kel excursions.',
              'AJK permit needed — allow 48 hours at the Pakistan AJK office in Muzaffarabad.'),
        hotel('Neelum Valley', 'Kel Hotel', 'budget', 2, 2500, 'Kel Village, Neelum Valley, AJK',
              ['Simple rooms','Home cooking','River views','Arang Kel access'],
              'A family-run hotel in Kel village, base for the Arang Kel cable car. Clean rooms and homely Kashmiri meals.',
              'Cable car to Arang Kel opens 8am; go at dawn to beat the day-tripper crowds.'),
        hotel('Neelum Valley', 'Arang Kel Camping Lodge', 'backpacker', 1, 800, 'Arang Kel Village, AJK',
              ['Wooden huts','Shared kitchen','Forest walks','Campfire'],
              'Wooden huts in the fairy-tale village of Arang Kel above the Neelum River — accessible only by cable car and a 45-min hike.',
              'Stay at least one night at Arang Kel — the dawn mist and sunset colours are unforgettable.'),

        # ── KALASH VALLEYS ─────────────────────────────────────────
        hotel('Kalash Valleys', 'Kalash Hilton Bumburet', 'luxury', 4, 15000, 'Bumburet Village, Kalash Valleys, KP',
              ['Valley views','Traditional architecture','Restaurant','Kalash tour desk'],
              'Boutique hotel in Bumburet with traditional Kalash-style wooden verandahs, excellent valley views and culturally sensitive tour packages.',
              'Book the Kalash-culture day package with a Kalash guide — far richer than self-exploring.'),
        hotel('Kalash Valleys', 'Kalash Continental', 'standard', 3, 6500, 'Bumburet Valley, Kalash Valleys, KP',
              ['Valley views','Restaurant','Tour desk','Garden'],
              'A reliable mid-range hotel with clean rooms and a restaurant serving Kalashi and Chitrali cuisine. Walking distance to Kalash museum.',
              'Festivals (Chilam Joshi May, Uchal Aug, Chaumos Dec) need 2-3 months\' advance booking.'),
        hotel('Kalash Valleys', 'Bumburet Guesthouse', 'budget', 2, 2200, 'Bumburet Village, KP',
              ['Simple rooms','Kalashi meals','Garden','Cultural info'],
              'A family-run guesthouse in a Kalash village with simple clean rooms and home-cooked Kalashi meals (walnut cakes, mulberry wine).',
              'The family happily explain Kalash traditions over dinner — a highlight.'),
        hotel('Kalash Valleys', 'Rumbur Community Guesthouse', 'backpacker', 1, 800, 'Rumbur Valley, KP',
              ['Basic rooms','Shared bath','Kalashi home meals'],
              'A community-run guesthouse in quieter Rumbur Valley, cheaper and more authentic than Bumburet. Simple shared-bath rooms and Kalashi family meals.',
              'Respect photography customs — always ask before photographing Kalash women or homes.'),

        # ── ZIARAT ─────────────────────────────────────────────────
        hotel('Ziarat', 'Ziarat Serena Heritage Lodge', 'luxury', 4, 20000, 'Main Ziarat Road, Balochistan',
              ['Juniper-forest views','Fireplace lounge','Restaurant','Heritage architecture'],
              'A heritage stone-and-wood lodge near the Quaid-e-Azam Residency with fireplace-warmed rooms and views over the ancient juniper forest.',
              'The fireplace evenings in the lounge are the best part of Ziarat — book a fireplace-room category.'),
        hotel('Ziarat', 'PTDC Motel Ziarat', 'standard', 3, 6500, 'Near Residency, Ziarat, Balochistan',
              ['Forest views','Restaurant','Heating','Parking'],
              'A long-running PTDC motel with clean warm rooms next to the Quaid-e-Azam Residency and walking distance to the juniper forest.',
              'Dawn forest walks starting from the motel (3 km) — keep eyes peeled for Suleiman Markhor.'),
        hotel('Ziarat', 'Juniper Inn', 'budget', 2, 2300, 'Bazaar Road, Ziarat, Balochistan',
              ['Fan/AC rooms','Balochi cuisine','Parking'],
              'A simple budget hotel in Ziarat bazaar with clean rooms and hearty Balochi meals. Walking distance to main sights.',
              'Order sajji (slow-roasted whole lamb) for dinner — 4 hours\' notice needed.'),
        hotel('Ziarat', 'Ziarat Forest Rest House', 'backpacker', 1, 700, 'Juniper Forest, Ziarat, Balochistan',
              ['Basic rooms','Shared kitchen','Forest trails'],
              'A forest department rest house deep in the juniper woods, basic but atmospheric. Perfect for bird-watching and wildlife enthusiasts.',
              'Permit via the Balochistan Forest Department in Quetta — 24 hr advance notice.'),

        # ── AYUBIA ─────────────────────────────────────────────────
        hotel('Ayubia', 'Ayubia Resort Hotel', 'luxury', 4, 22000, 'Ayubia Main Road, Galiyat, KP',
              ['Forest views','Restaurant','Heating','Garden','Pool'],
              'A well-designed resort in Ayubia with forest-facing rooms, a decent restaurant and outdoor pool for warm-weather stays.',
              'Forest-view rooms 201-215 are best; pipeline trail access is 2 min from the lobby.'),
        hotel('Ayubia', 'PTDC Motel Nathiagali', 'standard', 3, 8000, 'Nathiagali, Galiyat, KP',
              ['Hilltop views','Restaurant','Parking','Tour desk'],
              'A hilltop motel in Nathiagali with views to the Kashmir peaks, clean rooms and a restaurant serving Galiyat cuisine.',
              'Mukshpuri Peak hike starts 200 m away — 2 hours up, gives 360° mountain views.'),
        hotel('Ayubia', 'Gaitry Inn', 'budget', 2, 2500, 'Ayubia Bazaar, KP',
              ['Fan rooms','Pakistani cuisine','Forest walks'],
              'A cheap and cheerful budget hotel in Ayubia bazaar with simple clean rooms. Perfect base for the pipeline trail.',
              'Walk the pipeline trail early morning — 5 km of dense forest with great birding.'),
        hotel('Ayubia', 'Ayubia Youth Hostel', 'backpacker', 1, 800, 'Near Chairlift, Ayubia, KP',
              ['Dorm beds','Shared kitchen','Forest access','Common room'],
              'PYHA-affiliated youth hostel near the Ayubia chairlift, with dorms and a common room popular with student hikers.',
              'PYHA card gives 20% discount; bring warm layers — Ayubia is 2,400 m and chilly.'),

        # ── DEOSAI ─────────────────────────────────────────────────
        hotel('Deosai', 'Deosai Sky Camp', 'luxury', 4, 25000, 'Bara Pani, Deosai Plains, GB',
              ['Plateau views','Luxury tents','Fine dining','Bear-safari desk'],
              'Pakistan\'s highest luxury tented camp at 4,000 m on Deosai Plains with plush canvas suites, proper beds and a field kitchen serving surprisingly good meals.',
              'July-August only (snow-bound rest of year); book 3 months ahead through Skardu operators.'),
        hotel('Deosai', 'Deosai Camp Bara Pani', 'standard', 3, 9500, 'Bara Pani, Deosai, GB',
              ['Plateau views','Tents','Communal dining','Campfire'],
              'A mid-range tented camp at Bara Pani with comfortable but simpler canvas tents, hot meals and bonfires under Deosai\'s cold night skies.',
              'Altitude 4,000 m — spend a night in Skardu first to acclimatise and drink lots of water.'),
        hotel('Deosai', 'Sheosar Lake Rest House', 'budget', 2, 3200, 'Near Sheosar Lake, Deosai, GB',
              ['Lake views','Basic rooms','Shared kitchen'],
              'A GB Parks department rest house near Sheosar Lake — simple, atmospheric, and the only non-tent option on the plateau.',
              'Book via GB Parks department in Skardu; bring sleeping bag — rooms are basic.'),
        hotel('Deosai', 'Deosai Traveller Tent Camp', 'backpacker', 1, 1000, 'Kala Pani, Deosai, GB',
              ['Basic tents','Shared meals','Campfire','Bear-watch info'],
              'The cheapest way to overnight on Deosai — shared tents with communal meals and brown-bear watching excursions.',
              'Himalayan Brown Bear sightings best 5-7 am; the camp organises dawn safaris.'),

        # ── NALTAR ─────────────────────────────────────────────────
        hotel('Naltar', 'PAF Naltar Ski Resort', 'luxury', 4, 22000, 'Naltar Valley, GB',
              ['Ski-in/ski-out','Mountain views','Restaurant','Ski rental','Heated rooms'],
              'Pakistan Air Force\'s Naltar Ski Resort — the country\'s best winter destination, with warm chalet rooms, ski rental and 5 runs.',
              'PAF reference required; book Dec-Mar through PAF or Gilgit travel operators.'),
        hotel('Naltar', 'Naltar Continental', 'standard', 3, 7500, 'Naltar Pain Village, GB',
              ['Valley views','Restaurant','Heating','Tour desk'],
              'A mid-range family hotel in Naltar Pain with pine-forest-view rooms and a decent restaurant. Good for summer lake trips.',
              'Naltar Lakes jeep hire (PKR 3,500 return) — the hotel arranges, lakes are 2 hr away.'),
        hotel('Naltar', 'Naltar Forest Lodge', 'budget', 2, 2500, 'Naltar Bala, GB',
              ['Forest views','Basic rooms','Home cooking','Trek info'],
              'A simple forest-set lodge in Naltar Bala with clean rooms and Wakhi home cooking.',
              'Ask for yak-meat curry — a Naltar-Wakhi specialty, needs 4 hr notice.'),
        hotel('Naltar', 'Naltar Forest Camping', 'backpacker', 1, 800, 'Naltar Pine Forest, GB',
              ['Tents','Shared kitchen','Forest walks','Campfire'],
              'Tented camping in Naltar\'s pine and blue-spruce forest with communal campfires and exceptional stargazing.',
              'Bring warm gear — nights drop to freezing even July-August at 3,000 m.'),
    ]

    hotel_cols = ('city_id','name','budget_level','stars','price_per_night_pkr',
                  'address','amenities','description','booking_tip')
    hotel_ph = ','.join(['?'] * len(hotel_cols))
    c.executemany(f'INSERT INTO hotels({",".join(hotel_cols)}) VALUES({hotel_ph})', hotels_data)

    conn.commit()
    conn.close()
    print(f"Database initialized successfully at {DB_PATH}")
    print(f"  Terrain types: 8")
    c2 = get_db().cursor()
    c2.execute('SELECT COUNT(*) FROM cities')
    print(f"  Cities: {c2.fetchone()[0]}")
    c2.execute('SELECT COUNT(*) FROM attractions')
    print(f"  Attractions: {c2.fetchone()[0]}")
    c2.execute('SELECT COUNT(*) FROM hotels')
    print(f"  Hotels: {c2.fetchone()[0]}")

if __name__ == '__main__':
    init_db()
