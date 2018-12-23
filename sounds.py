from gtts import gTTS
import random
import sys
import os


def audio_path(fname):
    audio_cache_dir = os.path.join(os.getcwd(), 'sound-cache')
    if not os.path.isdir(audio_cache_dir):
        os.mkdir(audio_cache_dir)
    mpeg_path = os.path.join(audio_cache_dir, fname)
    return mpeg_path


def clear_line():
    sys.stdout.write("\r\033[K")
    sys.stdout.flush()


def text_to_mp3(text, mpeg_name):
    """
    Google text-to-speech
    """
    mpeg_path = audio_path(mpeg_name)
    text = (text.replace('@', 'at')
                .replace('/', ', ')
                .replace('\n', ' '))
    tts = gTTS(text=text, lang='en')
    tts.save(mpeg_path)


def play_mp3(mpeg_name, cached=True):
    """
    Play .mp3 file using mpg321
    """
    if cached:
        mpeg_path = audio_path(mpeg_name)
    else:
        mpeg_path = mpeg_name
    if os.path.isfile(mpeg_path):
        os.system('mpg321 -q ' + mpeg_path)
    else:
        raise IOError('bad mp3 path: ', mpeg_path)


def shout(text):
    """
    Play sound from text
    """
    mpeg_name = (text.replace(' ', '_')
                     .replace('/', '_')
                     .replace('\n', '') + '.mp3')
    text_to_mp3(text, mpeg_name)
    play_mp3(mpeg_name)


def rand_countdown(beats_min=5, beats_max=30, verbose=True):
    """
    Random countdown after key press
    """
    beats_to_wait = random.randint(5, 20)
    for i in range(beats_to_wait, 0, -1):
        if verbose:
            sys.stdout.write('\r{:d}'.format(i))
            sys.stdout.flush()
        play_mp3('clock-ticking.mp3', cached=False)
        clear_line()


def rand_order():
    """
    Random order voiced at random time
    """
    order = random.choice(['mine', 'yours'])
    order_text = 'Okay...' + order + '!'
    rand_countdown()
    shout(order_text)


if __name__ == "__main__":
    start_dialogue = input("Press Enter when ready")
    rand_order()
