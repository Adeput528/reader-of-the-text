# reader-of-the-text
This is a reader of the text that you entered or selected for those who are too lazy to read it themselves.

This is a script written using the library espeak.
coding and testing takes place on kali linux

This is a quick guide to flags.


flag       example             description
-t        -t "text"       Primary flag for directly specifying text

-v        -v en           Select language/voice (ru, en, de, fr...)

-s        -s 200          Speech rate (80-260, default 160)

-p        -p 70           Voice pitch (0-99, default 50)

-o        -o file.wav     Save speech to an audio file
