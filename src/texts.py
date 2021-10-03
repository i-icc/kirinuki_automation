import speech_recognition as sr
import soundfile

r = sr.Recognizer()

def read_timestamp():
    path = './timestamp.txt'
    timestamp = []
    with open(path) as f:
        r = f.readlines()
    for line in r:
        timestamp.append(line.split())
    return timestamp

def get_time(s):
    result = f"00:00:00.000 --> 00:00:{float(s):>06.03f}"
    return result

def sound2text(path):
    data, s = soundfile.read(path)
    text = get_time(len(data)/s) + "\n"
    with sr.AudioFile(path) as source:
        audio = r.record(source)
    try:
        text += r.recognize_google(audio, language='ja-JP')
    except :
        return "-1"
    return text


if __name__ == '__main__':
    print(read_timestamp())
    print(sound2text("./source/1/sounds/0.wav"))
    print(get_time(2))