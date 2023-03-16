# VRC Controller

This Python Module is a wrapper for VR Chat's OSC binding and listens to vrchat audio.

In this package, when sound is heard the program records sound for the time specified in constants.py or until there's silence, and then does speech -> text through SpeechRecognition. 
You can use your own dictation models like vosk if you want.

This project was heavily inspired by [AI Joken](https://git.vreml.org/skuld/ssvrcbot/-/tree/main/). I wanted some python bindings so here we are.

*THIS PROJECT IS IN A HEAVILY DEVELOPMENTAL STATE*