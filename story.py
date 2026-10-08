"""
story.py - ALL the text of the game lives here.

This file contains only DATA (no game logic). That makes it easy to read,
to correct and to explain:

    CHARACTERS  -> who appears in the game (name, role, colours for drawing)
    SCENES      -> every scene: what people say, the question, and the choices
    ENDINGS     -> the 9 endings
    TRACKS      -> which ending belongs to which track (A, B, C)

A line of dialogue is a tuple:  (speaker, text)
    speaker = None        -> the narrator is talking
    speaker = "mayeul"    -> a key from the CHARACTERS dictionary
    {name} in a text is replaced by the player's name.

A choice is a dictionary:
    "label"    -> the text on the button
    "kind"     -> "track" (choice 1), "safe" or "bold"
    "chaos"    -> how many Chaos points it adds (Bold choices 2, 3 and 4 = 1)
    "note"     -> what Mayeul secretly writes in his notebook about you
    "reaction" -> the lines we show after the player clicks
    "next"     -> the id of the next scene (not needed for the final choice)
"""

# The scene where the game starts.
FIRST_SCENE = "prologue"


# ---------------------------------------------------------------------------
# CHARACTERS
# The "look" values are only used to draw the characters on screen.
# ---------------------------------------------------------------------------
CHARACTERS = {
    "you": {
        "name": "You", "role": "Recent graduate, one clean shirt",
        "color": "#7fd1ff",
        "look": {"skin": "#f1c7a3", "hair": "#4b2e1f", "hair_style": "messy",
                 "eyes": "dots", "brows": "worried", "mouth": "worried",
                 "outfit": None, "collar": "collar", "accessory": None},
    },
    "mayeul": {
        "name": "Mayeul", "role": "Receptionist. Sees everything.",
        "color": "#b9a2ff",
        "look": {"skin": "#d9a27a", "hair": "#1f1611", "hair_style": "short",
                 "eyes": "half", "brows": "raised_one", "mouth": "flat",
                 "outfit": "#3a3f58", "collar": "collar", "accessory": "glasses"},
    },
    "brieuc": {
        "name": "Brieuc", "role": "HR Manager. Always smiling.",
        "color": "#ffd166",
        "look": {"skin": "#f3c9a8", "hair": "#9a9a9a", "hair_style": "bald",
                 "eyes": "dots", "brows": "normal", "mouth": "big_smile",
                 "outfit": "#4a6fa5", "collar": "tie", "accessory": "notebook"},
    },
    "doe": {
        "name": "Mrs. Doe", "role": "CEO. Your old English teacher.",
        "color": "#ff6b6b",
        "look": {"skin": "#efd2bd", "hair": "#c9c9c9", "hair_style": "bun",
                 "eyes": "dots", "brows": "stern", "mouth": "frown",
                 "outfit": "#7a1f2b", "collar": "shirt", "accessory": "glasses"},
    },
    "mum": {
        "name": "Mum", "role": "On the phone. Always.",
        "color": "#ff9ecd",
        "look": {"skin": "#f0c09a", "hair": "#a0522d", "hair_style": "long",
                 "eyes": "dots", "brows": "normal", "mouth": "smile",
                 "outfit": "#5fa86b", "collar": None, "accessory": "phone"},
    },
    "man": {
        "name": "Man in a Suit", "role": "Lanyard. Name card turned around.",
        "color": "#9ad1a0",
        "look": {"skin": "#c68d64", "hair": "#141414", "hair_style": "short",
                 "eyes": "dots", "brows": "normal", "mouth": "smile",
                 "outfit": "#22252b", "collar": "tie", "accessory": "lanyard"},
    },
    "cyclist": {
        "name": "Cyclist", "role": "Very angry. Very lycra.",
        "color": "#c3f584",
        "look": {"skin": "#e9b48a", "hair": "#3b2a1a", "hair_style": "short",
                 "eyes": "wide", "brows": "stern", "mouth": "open",
                 "outfit": "#2bb673", "collar": None, "accessory": "helmet"},
    },
    "grandma": {
        "name": "Grandma", "role": "Perfectly healthy. Very confused.",
        "color": "#e0e0e0",
        "look": {"skin": "#f1d3c0", "hair": "#f2f2f2", "hair_style": "bun",
                 "eyes": "wide", "brows": "normal", "mouth": "flat",
                 "outfit": "#1b1b1f", "collar": None, "accessory": "glasses"},
    },
}

# What your shirt looks like (it can change during the game!).
SHIRTS = {
    "white":  "White shirt with a coffee stain shaped like Italy",
    "orange": "Bright orange Synergix polo from 2009",
    "pink":   "Pink 'WORLD'S BEST DAD' T-shirt",
}


# ---------------------------------------------------------------------------
# SCENES
# "number" = the choice number shown in the HUD (0 = prologue, no choice)
# "place"  = the background to draw
# "cast"   = the characters standing on screen
# ---------------------------------------------------------------------------
SCENES = {

    # ----------------------------------------------------------- PROLOGUE --
    "prologue": {
        "number": 0, "track": None,
        "place": "station", "location": "Train station", "time": "09:31",
        "cast": ["you"],
        "lines": [
            (None, "Today is the most important day of your life: your first real job interview."),
            (None, "Your alarm did not agree. It didn't ring. Your phone died in the night, quietly, like your dreams."),
            (None, "You ran to the station. The 8:47 train arrived at 9:31. The driver apologised for 'a person on the tracks'. It was a pigeon."),
            (None, "Then a stranger with a huge latte walked straight into you. Now there is a big brown stain on your only white shirt."),
            ("you", "It looks like... a map of Italy. I can even see Sicily."),
            (None, "The stranger said 'Sorry, mate' and disappeared. Forever. Like your chances."),
        ],
        "question": None,
        "choices": [],
        "next": "start",
    },

    # ----------------------------------------------- SCENE 0 (CHOICE 1) --
    "start": {
        "number": 1, "track": None,
        "place": "reception", "location": "Synergix Solutions - Reception", "time": "10:25",
        "cast": ["you", "mayeul"],
        "lines": [
            (None, "10:25. You finally arrive at Synergix Solutions. Your interview was at 10:00."),
            (None, "A sign on the wall says: WELCOME TO THE SYNERGIX FAMILY! Under it, someone has written in pencil: 'help'."),
            (None, "The receptionist, Mayeul, looks at you. Then at the stain. Then at the clock. Then back at the stain."),
            ("mayeul", "You're the 10 o'clock interview?"),
            ("mayeul", "{name}. Yes, you're on my list. Next to the word 'late'."),
            ("mayeul", "It's 10:25. Here at Synergix, that's not late. That's a lifestyle choice."),
        ],
        "question": "Mayeul is waiting. So is your future. What do you do?",
        "choices": [
            {
                "label": "Lie about why you're late.",
                "kind": "track", "track": "A", "chaos": 0, "next": "A1",
                "note": "10:25. Late. Italy-shaped stain. Starts with a lie. Classic.",
                "reaction": [
                    ("you", "Yes! I'm so sorry. I had a... family emergency."),
                    ("mayeul", "A family emergency. Of course you did."),
                    (None, "He slowly opens a notebook. On the cover: 'EXCUSES - VOLUME 7'."),
                ],
            },
            {
                "label": "Tell the truth.",
                "kind": "track", "track": "B", "chaos": 0, "next": "B1",
                "note": "10:25. Late. Tells the truth. Suspicious. Nobody does that.",
                "reaction": [
                    ("you", "Yes. My alarm didn't ring, my train was late, and a stranger turned my shirt into Italy."),
                    ("mayeul", "..."),
                    ("mayeul", "Nobody has told me the truth since 2019. Please. Continue."),
                ],
            },
            {
                "label": "Run away.",
                "kind": "track", "track": "C", "chaos": 0, "next": "C1",
                "note": "10:25. Late. Said 'water the plants'. Ran. The door is still moving.",
                "reaction": [
                    ("you", "No! I'm... here to water the plants."),
                    ("mayeul", "We don't have plants. They all died. Nobody here has the energy to keep anything alive."),
                    (None, "But you are already gone. The door is still moving."),
                ],
            },
        ],
    },

    # ===================================================== TRACK A: THE LIE ==
    "A1": {
        "number": 2, "track": "A",
        "place": "reception", "location": "Synergix Solutions - Reception", "time": "10:26",
        "cast": ["you", "mayeul"],
        "lines": [
            (None, "Mayeul puts down his coffee. He holds his pen like a detective in a bad TV series."),
            ("mayeul", "A family emergency. How terrible. Truly. I'm crying on the inside."),
            ("mayeul", "Who exactly?"),
        ],
        "question": "Who is your 'emergency'?",
        "choices": [
            {
                "label": "\"My grandmother. She's in hospital.\"",
                "kind": "safe", "chaos": 0, "next": "A2",
                "note": "Grandmother in hospital. Lie level: beginner.",
                "reaction": [
                    ("you", "My grandmother. She's in hospital."),
                    (None, "Mayeul writes 'grandmother'. Then 'hospital'. Then a very small question mark."),
                    ("mayeul", "Poor woman. I'll tell Brieuc. He loves a sad story. It's the only thing that makes him feel alive."),
                ],
            },
            {
                "label": "\"My goldfish, Mr. Bubbles. It was complicated.\"",
                "kind": "bold", "chaos": 1, "next": "A2",
                "note": "Goldfish. Mr. Bubbles. Underlined twice. Then a third time, for me.",
                "reaction": [
                    ("you", "My goldfish. Mr. Bubbles. It was... complicated."),
                    (None, "Mayeul writes 'goldfish'. He underlines it twice."),
                    ("mayeul", "Is Mr. Bubbles... still with us?"),
                    ("you", "He's stable. Floating, but stable."),
                    ("mayeul", "Floating is rarely a good sign."),
                ],
            },
        ],
    },

    "A2": {
        "number": 3, "track": "A",
        "place": "reception", "location": "Synergix Solutions - Reception", "time": "10:29",
        "cast": ["you", "brieuc", "mayeul"],
        "lines": [
            (None, "A man walks in. Big smile. Small notebook. The smile never moves. The pen never stops."),
            ("brieuc", "Hello, hello! I'm Brieuc, Head of Human Resources and Happiness! Just Brieuc. No 'Mister'. We're a family here."),
            ("brieuc", "Mayeul told me everything, {name}. You poor thing. At Synergix we're a family, so your pain is our pain."),
            ("brieuc", "So tell me... how is the patient doing?"),
            (None, "He is already writing. You haven't said anything yet."),
        ],
        "question": "How much do you say about 'the patient'?",
        "choices": [
            {
                "label": "Stay vague: \"I'd rather not talk about it.\"",
                "kind": "safe", "chaos": 0, "next": "A3",
                "note": "'I'd rather not talk about it.' Smart. Silence can't be fact-checked.",
                "reaction": [
                    ("you", "I'd rather not talk about it."),
                    ("brieuc", "Of course! Of course. We respect your privacy."),
                    (None, "He writes for one whole minute. You can read the words 'trauma' and 'potential'."),
                    ("mayeul", "Don't worry. Your silence is now in your file."),
                ],
            },
            {
                "label": "Invent everything: the hospital, the nurse, a Latin disease.",
                "kind": "bold", "chaos": 1, "next": "A3",
                "note": "Invented a nurse called Brenda. And a horse. Room 404 does not exist.",
                "reaction": [
                    ("you", "The patient is at St. Margaret's Hospital, room 404. The nurse is called Brenda. It's a very rare disease: Dramaticus Latinus Infinitum."),
                    ("you", "Only three cases in Europe. One of them was a horse."),
                    ("brieuc", "Brenda. Room 404. Dramaticus... how do you spell Infinitum?"),
                    ("brieuc", "This is going in the company newsletter!"),
                    ("mayeul", "Room 404. Patient not found."),
                ],
            },
        ],
    },

    "A3": {
        "number": 4, "track": "A",
        "place": "office", "location": "Interview room", "time": "10:35",
        "cast": ["you", "brieuc"],
        "lines": [
            (None, "The interview room has one window, one plastic plant and one poster: a mountain with the word TEAMWORK. The mountain is alone."),
            ("brieuc", "Right! Let's start. Don't be nervous. Nobody has ever cried in this room. This week."),
            ("brieuc", "Tell me about a difficult situation you handled."),
        ],
        "question": "Which difficult situation do you talk about?",
        "choices": [
            {
                "label": "Tell a story from your internship.",
                "kind": "safe", "chaos": 0, "next": "A4",
                "note": "Printer + paperclip. Brieuc was impressed. Brieuc is impressed by staplers.",
                "reaction": [
                    ("you", "During my internship, the printer broke one hour before a big meeting. I fixed it with a paperclip and a lot of prayer."),
                    ("brieuc", "Resourceful! I'm writing 'paperclip'. It's a powerful word."),
                    (None, "He draws a little paperclip. Then he colours it in. Carefully."),
                ],
            },
            {
                "label": "Use this morning as your example.",
                "kind": "bold", "chaos": 1, "next": "A4",
                "note": "Used today's lie as a job skill. Disgusting. Brilliant.",
                "reaction": [
                    ("you", "This morning. No alarm, a late train, a coffee attack and a family tragedy. And I'm still here."),
                    ("you", "It taught me crisis management."),
                    (None, "Brieuc wipes a tear from his eye."),
                    ("brieuc", "In the middle of a tragedy... you came here. For us. That's the Synergix spirit: suffer, but on time."),
                    ("brieuc", "Well. Almost on time."),
                ],
            },
        ],
    },

    "A4": {
        "number": 5, "track": "A", "final": True,
        "place": "office", "location": "Interview room", "time": "10:48",
        "cast": ["you", "brieuc", "mayeul"],
        "lines": [
            (None, "Brieuc closes his notebook. It's the first time today. It feels dangerous."),
            ("brieuc", "I've seen enough. We'd like to offer you the job!"),
            ("brieuc", "Any questions?"),
            ("mayeul", "(from the door) Think carefully. This is the only time anyone here will ask for your opinion."),
        ],
        "question": "FINAL DECISION. Any questions?",
        "choices": [
            {
                "label": "\"No, thank you. I accept.\"",
                "kind": "safe", "chaos": 0,
                "note": "Accepted without a single question. A natural Synergix employee.",
                "reaction": [
                    ("you", "No, thank you. I accept."),
                    ("brieuc", "Wonderful! Welcome to the family. There's no way out! Ha ha. That's a joke. Mostly."),
                ],
            },
            {
                "label": "Ask for a higher salary and a company car.",
                "kind": "bold", "chaos": 0,
                "note": "Asked for a company car. We don't even have company chairs.",
                "reaction": [
                    ("you", "Yes, actually. I'd like a higher salary. And a company car."),
                    (None, "Silence. Even the air conditioning stops."),
                    ("brieuc", "...Interesting."),
                    (None, "He opens the notebook again. He writes for a very, very long time."),
                ],
            },
        ],
    },

    # =================================================== TRACK B: THE TRUTH ==
    "B1": {
        "number": 2, "track": "B",
        "place": "reception", "location": "Synergix Solutions - Reception", "time": "10:26",
        "cast": ["you", "mayeul"],
        "lines": [
            ("mayeul", "Honesty. How rare. Nobody tells the truth here. It's against company culture."),
            (None, "He opens a drawer marked LOST PROPERTY. He takes out something orange. Very orange."),
            ("mayeul", "We have a spare shirt, if you want. Nobody has worn it since 2009. Nobody was brave enough."),
        ],
        "question": "Italy or orange?",
        "choices": [
            {
                "label": "Keep your stained shirt.",
                "kind": "safe", "chaos": 0, "next": "B2",
                "note": "Kept the stain. Respect. (Do not tell anyone I wrote this.)",
                "reaction": [
                    ("you", "No, thank you. I'll keep my shirt. Italy stays."),
                    ("mayeul", "Respect."),
                    (None, "He almost smiles. Almost. It's the closest thing to a hug you will ever get in this building."),
                ],
            },
            {
                "label": "Accept the spare shirt.",
                "kind": "bold", "chaos": 1, "next": "B2", "shirt": "orange",
                "note": "Wore the 2009 polo. Brave. Or colour-blind.",
                "reaction": [
                    ("you", "Yes, please. Anything is better than Italy."),
                    (None, "It's a bright orange Synergix polo from 2009. The logo is the size of a pizza. It smells like a team-building weekend."),
                    ("mayeul", "It suits you. Like a traffic cone suits a motorway."),
                ],
            },
        ],
    },

    "B2": {
        "number": 3, "track": "B",
        "place": "office", "location": "Interview room", "time": "10:31",
        "cast": ["you", "brieuc"],
        "lines": [
            (None, "Brieuc takes you to the interview room. Big smile. Small notebook. He never stops smiling, and he never stops writing."),
            ("brieuc", "Hello, {name}! I'm Brieuc, Head of Human Resources and Happiness. Mayeul says you're honest! We love honest people. They're so easy to write about."),
            ("brieuc", "Let's start with a classic. Tell me about a time you failed."),
        ],
        "question": "Which failure do you share?",
        "choices": [
            {
                "label": "The burnt birthday cake.",
                "kind": "safe", "chaos": 0, "next": "B3",
                "note": "Burnt cake. Fire brigade. Sweet, but not a real failure.",
                "reaction": [
                    ("you", "I once made a birthday cake for my best friend. I put the oven on 250 degrees and fell asleep."),
                    ("you", "The fire brigade came. They sang Happy Birthday. It was a nice party, actually."),
                    ("brieuc", "Ha! Fire is just energy that needs management. I'm writing 'leadership'."),
                ],
            },
            {
                "label": "The \"Reply All\" love letter.",
                "kind": "bold", "chaos": 1, "next": "B3",
                "note": "'Reply All' love letter. 4,000 readers. I want a copy.",
                "reaction": [
                    ("you", "In my second year, I wrote a love letter to a girl in my class. Then I clicked 'Reply All'."),
                    ("you", "It went to the whole university. Four thousand people. The Dean replied: 'Very touching. Please stop.'"),
                    ("brieuc", "Wow. Did she answer?"),
                    ("you", "She changed universities."),
                    (None, "Brieuc writes: 'Communication skills: unforgettable.'"),
                ],
            },
        ],
    },

    "B3": {
        "number": 4, "track": "B",
        "place": "office", "location": "Interview room", "time": "10:40",
        "cast": ["you", "brieuc"],
        "lines": [
            ("brieuc", "Next question. My favourite one! Why do you want this job?"),
            (None, "He holds his pen above the page. He looks like a cat watching a bird."),
        ],
        "question": "Why do you want this job?",
        "choices": [
            {
                "label": "\"I like your company's projects and values.\"",
                "kind": "safe", "chaos": 0, "next": "B4",
                "note": "Likes our 'values'. Nobody knows our values. Not even the poster.",
                "reaction": [
                    ("you", "I like your company's projects and values."),
                    ("brieuc", "Wonderful! Which values?"),
                    ("you", "...All of them."),
                    ("brieuc", "Perfect answer. Nobody here knows them either."),
                ],
            },
            {
                "label": "\"Because I need money. My rent is 800 euros.\"",
                "kind": "bold", "chaos": 1, "next": "B4",
                "note": "Rent: 800 euros. Fridge: one lemon. Most honest answer since 2009.",
                "reaction": [
                    ("you", "Because I need money. My rent is 800 euros, and my fridge contains one lemon."),
                    (None, "Brieuc stops smiling for half a second. Then he smiles even harder, which is somehow worse."),
                    ("brieuc", "That's the most honest answer we've had since 2009!"),
                    ("mayeul", "(from the corridor) Since the orange polo."),
                ],
            },
        ],
    },

    "B4": {
        "number": 5, "track": "B", "final": True,
        "place": "office", "location": "Interview room", "time": "10:50",
        "cast": ["you", "doe", "brieuc"],
        "lines": [
            (None, "Suddenly, the door opens. The temperature drops by five degrees. Brieuc stands up very fast."),
            (None, "It's Mrs. Doe, the CEO. You know her. She was your English teacher at school."),
            (None, "On your Year 9 report, she wrote: 'Will never amount to anything. Also, please stop writing \"gonna\".'"),
            ("doe", "Well, well, well. {name}. Look who's here. Late, I imagine."),
            ("brieuc", "Mrs. Doe! Do you... know our candidate?"),
        ],
        "question": "FINAL DECISION. Your old teacher is staring at you.",
        "choices": [
            {
                "label": "\"Good morning, Mrs. Doe. It's nice to see you again.\"",
                "kind": "safe", "chaos": 0,
                "note": "Polite to Mrs. Doe. She hates that.",
                "reaction": [
                    ("you", "Good morning, Mrs. Doe. It's nice to see you again."),
                    ("doe", "Full sentence. Correct grammar. A polite lie. You've grown."),
                    (None, "She doesn't look happy. She looks like someone who just lost a bet."),
                ],
            },
            {
                "label": "\"Oh no. Not you.\"",
                "kind": "bold", "chaos": 0,
                "note": "Said 'Oh no. Not you.' to the CEO. I almost dropped my coffee.",
                "reaction": [
                    ("you", "Oh no. Not you."),
                    ("doe", "Oh yes. Me."),
                    (None, "Brieuc writes 'Oh no. Not you.' and underlines it three times."),
                    ("mayeul", "(from the corridor) This is better than Netflix."),
                ],
            },
        ],
    },

    # ================================================ TRACK C: RUN AWAY ==
    "C1": {
        "number": 2, "track": "C",
        "place": "street", "location": "The street outside", "time": "10:27",
        "cast": ["you", "cyclist"],
        "lines": [
            (None, "You run. The automatic door is too slow. You hit it with your face. Then it opens, slowly, as if it wanted to watch."),
            (None, "Outside, you run straight into the bike lane. A cyclist brakes one centimetre from your knees."),
            ("cyclist", "HEY! WATCH WHERE YOU'RE GOING!"),
            ("you", "I DON'T KNOW WHERE I'M GOING! THAT'S THE WHOLE PROBLEM!"),
        ],
        "question": "Your heart is playing a drum solo. Now what?",
        "choices": [
            {
                "label": "Stop at a small park and sit on a bench.",
                "kind": "safe", "chaos": 0, "next": "C2",
                "note": "Sat on a bench. A pigeon judged them. I agree with the pigeon.",
                "reaction": [
                    (None, "You walk into a small park and fall onto a bench."),
                    (None, "A pigeon lands next to you. It looks at the stain. Even the pigeon is judging you."),
                    ("you", "Wait... were you on the train tracks this morning?"),
                    (None, "The pigeon does not answer. It's a professional."),
                ],
            },
            {
                "label": "Keep running. Buy a random shirt and change in the street.",
                "kind": "bold", "chaos": 1, "next": "C2", "shirt": "pink",
                "note": "Bought a 'WORLD'S BEST DAD' shirt. Changed in the street. Not a dad.",
                "reaction": [
                    (None, "You run into the first shop you see and grab the first shirt you see. You change right there, in the street."),
                    (None, "It's pink. On the front, in big letters: WORLD'S BEST DAD."),
                    (None, "An old lady watches the whole thing. She gives you a thumbs up."),
                    ("you", "I'm not a dad."),
                    (None, "She doesn't care. Then your legs stop working, so you sit on a bench in a small park."),
                ],
            },
        ],
    },

    "C2": {
        "number": 3, "track": "C",
        "place": "park", "location": "A small park", "time": "10:33",
        "cast": ["you", "mum"],
        "lines": [
            (None, "Your phone rings. The screen says: MUM. Of course. Mothers can feel failure from 200 kilometres away."),
            ("mum", "{name}, sweetie! So? How was the interview? Did they love you?"),
            ("mum", "Your cousin Kevin got a job at a bank, you know. He has a parking space. With his name on it."),
        ],
        "question": "What do you tell Mum?",
        "choices": [
            {
                "label": "\"I ran away.\"",
                "kind": "safe", "chaos": 0, "next": "C3",
                "note": "Told Mum the truth. Mum is now disappointed in three new ways.",
                "reaction": [
                    ("you", "I ran away."),
                    ("mum", "..."),
                    ("mum", "Like your piano exam. And your driving test. And your own birthday party in 2011."),
                    ("mum", "Okay. Well. Eat something, at least. You sound thin."),
                ],
            },
            {
                "label": "\"It went great, they love me!\"",
                "kind": "bold", "chaos": 1, "next": "C3",
                "note": "Lied to Mum. 47 WhatsApp messages. Uncle Pete sent a banana.",
                "reaction": [
                    ("you", "It went great! They love me!"),
                    ("mum", "I KNEW IT! I'm telling everyone!"),
                    (None, "Your phone vibrates 47 times. The family WhatsApp group is on fire."),
                    (None, "Aunt Linda: 'CONGRATULATIONS!!!' Uncle Pete sends a GIF of a dancing banana. Grandma: 'what is synergix. is it a cult'."),
                    (None, "Kevin from the bank reacts with a thumbs up. Just one. Cold."),
                ],
            },
        ],
    },

    "C3": {
        "number": 4, "track": "C",
        "place": "park", "location": "A small park", "time": "10:41",
        "cast": ["you", "man"],
        "lines": [
            (None, "A man in a very nice suit sits down at the other end of the bench. He wears a lanyard, but the name card is turned around."),
            (None, "He is holding a coffee. You move your shirt away from it. Just in case."),
            ("man", "Rough morning?"),
        ],
        "question": "A stranger wants to talk. Do you open up?",
        "choices": [
            {
                "label": "\"Just resting, thanks.\"",
                "kind": "safe", "chaos": 0, "next": "C4",
                "note": "'Just resting.' On a Tuesday. In an interview outfit. Sure.",
                "reaction": [
                    ("you", "Just resting, thanks."),
                    ("man", "Of course. Resting. On a Tuesday morning. In an interview outfit."),
                    (None, "He smiles like someone who already knows the end of the film."),
                ],
            },
            {
                "label": "Tell him about your whole day, including the stain.",
                "kind": "bold", "chaos": 1, "next": "C4",
                "note": "Told a stranger everything. Including Sicily. Report received.",
                "reaction": [
                    ("you", "Rough? My alarm didn't ring, my train was late because of a pigeon, a stranger attacked me with a latte, and look: my shirt is Italy. That's Sicily. Then I ran away from my interview."),
                    ("man", "Fascinating. And how did the coffee taste?"),
                    ("you", "I don't know. I didn't drink it. I wore it."),
                    (None, "He types something on his phone. Very fast. Like someone writing a report."),
                ],
            },
        ],
    },

    "C4": {
        "number": 5, "track": "C", "final": True,
        "place": "park", "location": "A small park", "time": "10:47",
        "cast": ["you", "man"],
        "lines": [
            ("man", "Listen. We're hiring. There's an interview in five minutes, in the building next door."),
            (None, "He points at a tall grey building. It has dark windows. You can't see the name of the company."),
            ("man", "Interested? No pressure. Well. A little pressure."),
        ],
        "question": "FINAL DECISION. Second chance, or second disaster?",
        "choices": [
            {
                "label": "Refuse politely and wish him good luck.",
                "kind": "safe", "chaos": 0,
                "note": "Refused the second interview. Subject declined. Noted. Very noted.",
                "reaction": [
                    ("you", "No, thanks. I think one interview disaster is enough for one day. Good luck, though!"),
                    ("man", "Shame. Good luck to you too."),
                    (None, "He walks away. Into his phone, you think you hear him say: 'Subject declined.' But you're probably just tired."),
                ],
            },
            {
                "label": "Accept immediately.",
                "kind": "bold", "chaos": 0,
                "note": "Followed a stranger into a grey building. No questions. Excellent.",
                "reaction": [
                    ("you", "Yes. Let's go. Right now. Before my brain can stop me."),
                    ("man", "Excellent. Follow me."),
                    (None, "He doesn't look surprised. Not even a little bit."),
                ],
            },
        ],
    },
}


# ---------------------------------------------------------------------------
# ENDINGS  (number -> ending)
# "type" is "calm", "medium" or "wild"
# ---------------------------------------------------------------------------
ENDINGS = {
    # --------------------------------------------------------- TRACK A --
    1: {
        "title": "Hired by Pity", "type": "calm", "track": "A",
        "place": "office", "location": "Synergix Solutions - Your new desk", "time": "MONDAY",
        "cast": ["you", "brieuc", "mayeul"],
        "lines": [
            (None, "You start on Monday."),
            (None, "On Monday, there is a cake on your desk. The card says: 'Stay strong. We are your family now.'"),
            (None, "On Tuesday, another cake. On Wednesday, a lasagna. On Thursday, a woman you have never met hugs you in the lift and cries."),
            ("brieuc", "How is the patient? Any news? Should we start a fundraiser?"),
            (None, "Everybody thinks someone you love is dying. Nobody asks for details. They just bring sugar."),
            (None, "After one month, you have gained 3 kilos and lost your dignity."),
            ("mayeul", "I never bring cake. I just watch. I know."),
        ],
    },
    2: {
        "title": "Hired by Accident", "type": "medium", "track": "A",
        "place": "office", "location": "Synergix Solutions - Data Department", "time": "FRIDAY",
        "cast": ["you", "brieuc", "mayeul"],
        "lines": [
            (None, "Brieuc takes so many notes that his files get confused. Your file is mixed up with another candidate's: Dr. Priya Raman, PhD, ten years of experience."),
            (None, "The next morning, you receive a contract. Job title: Senior Data Scientist. Salary: big. Very big. PhD big."),
            ("you", "Sorry... what does a Senior Data Scientist do?"),
            ("brieuc", "Nobody knows! That's why we pay so much."),
            (None, "Every Friday, you make a chart. Everyone claps. Nobody reads it."),
            ("mayeul", "Nice chart. Is it upside down?"),
            (None, "It is. You get a bonus for it. Somewhere, Dr. Priya Raman receives a rejection email: 'We were looking for more crisis management.'"),
        ],
    },
    3: {
        "title": "The Funeral of a Perfectly Healthy Grandma", "type": "wild", "track": "A",
        "place": "funeral", "location": "St. Margaret's Church", "time": "SATURDAY",
        "cast": ["you", "grandma", "brieuc", "mayeul"],
        "lines": [
            (None, "On Monday, HR sends a huge bunch of flowers to your 'poor sick grandmother'. To her real address."),
            (None, "On Tuesday, a card signed by 200 employees. On Wednesday, a fruit basket. On Thursday, Brieuc calls."),
            ("brieuc", "We're so sorry for your loss. When is the funeral? The whole family wants to come. The Synergix family, I mean."),
            (None, "You have no choice. You organise a funeral. For a woman who is perfectly healthy and does aqua-gym three times a week."),
            (None, "Your grandmother comes. She wears black. She sits in the first row, eating a sandwich, very confused."),
            ("grandma", "Who died?"),
            ("you", "You did, Grandma. Please act natural."),
            ("grandma", "In that case, I wanted better flowers."),
            ("mayeul", "My condolences. To your career."),
        ],
    },

    # --------------------------------------------------------- TRACK B --
    4: {
        "title": "The Boss Is Your Old Teacher", "type": "calm", "track": "B",
        "place": "office", "location": "Synergix Solutions - Meeting room B", "time": "FRIDAY",
        "cast": ["you", "doe", "brieuc"],
        "lines": [
            (None, "You get the job."),
            ("doe", "I knew you would end up here."),
            (None, "Nobody knows if this is a compliment. Probably not."),
            (None, "Every Friday, she gives you homework: a 500-word essay called 'Why This Meeting Could Have Been an Email'."),
            (None, "When you arrive two minutes late, you get detention. Detention is in meeting room B. With Brieuc. He takes notes."),
            ("doe", "And stop saying 'gonna'. You're an adult now. Allegedly."),
        ],
    },
    5: {
        "title": "The Job You Didn't Apply For", "type": "medium", "track": "B",
        "place": "office", "location": "Synergix Solutions - The basement", "time": "MONDAY",
        "cast": ["you", "doe", "mayeul"],
        "lines": [
            ("doe", "We don't have a job for you. But we do have a job that nobody else wants."),
            (None, "Your new title: Assistant to the Assistant of the Assistant."),
            (None, "Fourteen people refused it before you. One of them was a robot vacuum cleaner. It left the building by itself."),
            (None, "Your main task: bring coffee to the people whose job is to bring coffee."),
            ("mayeul", "Congratulations. You're at the bottom of the food chain. Under the printer."),
            ("you", "Is there any chance of a promotion?"),
            ("doe", "There's a chance of rain."),
        ],
    },
    6: {
        "title": "The Viral Intern", "type": "wild", "track": "B",
        "place": "office", "location": "Synergix Solutions - You live here now", "time": "23:59",
        "cast": ["you", "doe", "mayeul"],
        "lines": [
            (None, "Mrs. Doe looks at you for a long, long time. Like a bad essay she can't stop reading."),
            ("doe", "You have no filter. You never had one. In Year 9, you told the headmaster his tie looked like a sad lasagna."),
            ("doe", "We need someone with no filter. You're running our social media. Starting now."),
            (None, "Your first post: 'We are not a family. We are a company. Please stop asking.'"),
            (None, "One hour later: ten million views. Two hours later: journalists in the car park, a TV crew, and a man selling T-shirts with your post on them."),
            (None, "You can't leave the building. You live in the office now. You sleep under your desk."),
            ("mayeul", "I brought you a blanket. It's orange. Don't ask where it's from."),
        ],
    },

    # --------------------------------------------------------- TRACK C --
    7: {
        "title": "Unemployed but Happy", "type": "calm", "track": "C",
        "place": "park", "location": "The same bench, three months later", "time": "12:30",
        "cast": ["you"],
        "lines": [
            (None, "You never go back to Synergix. You never find out what was in the building next door."),
            (None, "When people ask, you say you are 'looking'. And you are looking. Mostly at sandwiches."),
            (None, "After three months, you know the best sandwich spot in the city: a tiny place behind the station. Chicken and pesto. 4.50 euros. Life-changing."),
            (None, "Your mum tells the family you are 'a freelancer'. Kevin from the bank sends a thumbs up. Cold."),
            ("you", "No alarm. No train. No coffee stains. I'm unemployed... but I'm happy."),
            (None, "The pigeon visits you every day. It's the closest thing you have to a colleague."),
        ],
    },
    8: {
        "title": "The Rival Company", "type": "medium", "track": "C",
        "place": "rivalex", "location": "Rivalex Corporation", "time": "10:52",
        "cast": ["you", "man"],
        "lines": [
            (None, "The building next door belongs to Rivalex: the eternal enemy of Synergix Solutions."),
            (None, "Their slogan is on a huge poster: 'WE ARE NOT A FAMILY. WE ARE A TEAM.' Under it, in pencil: 'also help'."),
            ("man", "You ran away from Synergix? Then you're one of us. You're hired. No questions."),
            ("you", "None? Not even 'tell me about a time you failed'?"),
            ("man", "No need. I can see your shirt."),
            ("man", "Your first mission: steal the Synergix coffee machine. It's the only good one in the city. They've had it since 2009."),
            (None, "At midnight, you go back to Synergix, dressed in black. The reception is dark and silent. Except for one small light."),
            ("mayeul", "Good evening. I had a feeling you would come back."),
        ],
    },
    9: {
        "title": "It Was a Test", "type": "wild", "track": "C", "secret": True,
        "place": "street_window", "location": "The building next door", "time": "10:53",
        "cast": ["you", "man"],
        "lines": [
            (None, "You follow the man to the grey building. At the door, he stops and turns his lanyard around."),
            (None, "It says: SYNERGIX SOLUTIONS - Head of Special Recruitment."),
            (None, "In a window on the second floor, someone is waving at you. Slowly. Without smiling. It's Mayeul."),
            ("mayeul", "Congratulations, {name}. The alarm, the train, the coffee... even your mum's call. That was all us."),
            ("you", "My MUM?!"),
            ("mayeul", "She was very professional. We paid her in cake."),
            ("man", "Stage 1: Chaos Resistance. You passed. Most people just go home and cry."),
            ("mayeul", "Stage 2 starts tomorrow at 7 a.m. Don't set an alarm. We'll take care of it."),
        ],
    },
}


# ---------------------------------------------------------------------------
# TRACKS: the name of each track and which ending matches each ending type.
# ---------------------------------------------------------------------------
TRACKS = {
    "A": {"name": "The Lie",   "endings": {"calm": 1, "medium": 2, "wild": 3}},
    "B": {"name": "The Truth", "endings": {"calm": 4, "medium": 5, "wild": 6}},
    "C": {"name": "Run Away",  "endings": {"calm": 7, "medium": 8, "wild": 9}},
}


# Mayeul's final verdict at the bottom of his notebook (key = Chaos score).
NOTEBOOK_VERDICTS = {
    0: "Chaos 0/3. Safe, polite, forgettable. Like beige paint.",
    1: "Chaos 1/3. Mostly harmless. Slightly dangerous on Tuesdays.",
    2: "Chaos 2/3. A walking HR incident. I'm starting to like you.",
    3: "Chaos 3/3. Pure chaos. Synergix needs people like you. That is not a compliment.",
}


# TROPHIES (achievements). The conditions are checked in engine.py.
ACHIEVEMENTS = {
    "first_day":        ("First Day",          "Finish the story once."),
    "beige_paint":      ("Beige Paint",        "Choose SAFE every single time."),
    "agent_of_chaos":   ("Agent of Chaos",     "Reach 3/3 Chaos."),
    "frozen":           ("Frozen",             "Let the timer run out. Mayeul chose for you."),
    "fashion_victim":   ("Fashion Victim",     "Change your shirt."),
    "rip_mr_bubbles":   ("R.I.P. Mr. Bubbles", "Blame your goldfish."),
    "reply_all":        ("Reply All",          "Tell HR about your love letter."),
    "liar_liar":        ("Liar, Liar",         "Lie to your mum."),
    "chaos_resistance": ("Chaos Resistance",   "Find the secret ending."),
    "tourist":          ("Tourist",            "Finish all three tracks: Lie, Truth and Run away."),
    "wild_child":       ("Wild Child",         "Find the three Wild endings."),
    "completionist":    ("Completionist",      "Find all 9 endings."),
}

# Mayeul chooses a name for you if you don't give one.
DEFAULT_NAME = "Candidate 47"


# Random sarcastic lines for the main menu.
MENU_QUOTES = [
    "\"Press a button. Any button. I'll judge you either way.\"  - Mayeul",
    "\"Your future is waiting. It's also 25 minutes late.\"  - Mayeul",
    "\"Synergix Solutions: we are a family. A very tired family.\"",
    "\"Every choice matters. Mostly to me. I'm writing them down.\"  - Mayeul",
    "\"Is that coffee or is that Italy?\"  - Mayeul",
]
