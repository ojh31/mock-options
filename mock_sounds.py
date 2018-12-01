from gtts import gTTS
import random
import sys
import os


def audio_path(fname):
    mpeg_path = os.path.join(os.getcwd(), 'sound-data', fname)
    return mpeg_path


def clear_line():
    sys.stdout.write("\r\033[K")
    sys.stdout.flush()


def text_to_mp3(text, mpeg_name):
    """
    Google text-to-speech
    """
    mpeg_path = audio_path(mpeg_name)
    tts = gTTS(text=text, lang='en')
    tts.save(mpeg_path)


def play_mp3(mpeg_name):
    """
    Play .mp3 file using mpg321
    """
    mpeg_path = audio_path(mpeg_name)
    if os.path.isfile(mpeg_path):
        os.system('mpg321 -q ' + mpeg_path)
    else:
        raise IOError('bad mp3 path: ', mpeg_path)


def shout(text):
    """
    Play sound from text
    """
    mpeg_name = text.replace(' ', '_') + '.mp3'
    text_to_mp3(text, mpeg_name)
    play_mp3(mpeg_name)


def rand_countdown(beats_min=5, beats_max=30, verbose=True):
    """
    Random countdown after key press
    """
    start_dialogue = input("Press Enter when ready")
    beats_to_wait = random.randint(5, 30)
    for i in range(beats_to_wait, 0, -1):
        if verbose:
            sys.stdout.write('\r{:d}'.format(i))
            sys.stdout.flush()
        play_mp3('clock-ticking.mp3')
        clear_line()
    return start_dialogue


def rand_order():
    """
    Random order voiced at random time
    """
    order = random.choice(['mine', 'yours'])
    order_text = 'Okay...' + order + '!'
    rand_countdown()
    shout(order_text)


if __name__ == "__main__":
    rand_order()
