import subprocess
import soundfile
import numpy as np
from matplotlib import pyplot as plt
from texts import sound2text


def time2s(time):  # 00:00:00(h:m:s) を秒数に変換する関数
    h_m_s = list(map(int, time.split(":")))
    result = 0
    for i in range(len(h_m_s)):
        result += h_m_s[-i-1]*60**i
    return result


def download_movie(url):  # 動画をダウンロードする関数
    check = subprocess.call(
        ['youtube-dl', '--output', './source/source_video.mp4', f"{url}"])
    return check


def remake_movies(file_path, title):
    files = movie_cut(file_path)
    subprocess.call(["mkdir", f"{file_path}/vtts/"])
    subprocess.call(["mkdir", f"{file_path}/subtitles/"])
    for i in files:
        text = sound2text(f"{file_path}/sounds/{i}.wav")
        if text == "-1":
            subprocess.call(
                ["cp", f"{file_path}/movies/{i}.mp4", f"{file_path}/subtitles/{i}.mp4"])
            continue
        with open(f"{file_path}/vtts/{i}.vtt", mode='w') as f:
            texts = ["WEBVTT", "Language: ja", "", text]
            f.write("\n".join(texts))
        put_subtitle(f"{file_path}/movies/{i}.mp4",
                     f"{file_path}/vtts/{i}",
                     f"{file_path}/subtitles/{i}.mp4")
    connecting_movies(file_path, files, title)
    subprocess.call(["rm","-rf",file_path])


def connecting_movies(file_path, files, title):
    c = "concat:"
    for i in files:
        c += f"{file_path}/subtitles/{i}.mp4|"
    subprocess.call(["ffmpeg","-i",f"{c[:-1]}","-c","copy",f"./movies/{title}.mp4"])


def put_subtitle(movie_path, path, output_path):
    # subprocess.call([["ffmpeg", "-i", f"{movie_path}", "-i", f"{path}.vtt", "-map", "0:v", "-map", "0:a", "-map","1", "-metadata:s:s:0", "language=jpn", "-c:v", "copy", "-c:a", "copy", "-c:s", "srt", f"{path}.mkv"]])
    subprocess.call(["ffmpeg", "-i", f"{path}.vtt", f"{path}.ass"])
    # subprocess.call(["ffmpeg", "-i", movie_path, "-i",f"{path}.ass", "-map", "0", "-map", "1", "-c", "copy", "-c:s", "mov_text", output_path])
    subprocess.call(["ffmpeg", "-i", movie_path, "-vf",
                    f"ass={path}.ass", output_path])
    # subprocess.call(["ffmpeg", "-i", f"{path}.mkv", "-vcodec", "copy", f"{output_path}"])


def split_movie(start, file_path, d, output_path):  # 動画を切り取ります
    check = subprocess.call(
        ["ffmpeg", "-ss", f"{start}", "-i", file_path, "-t", f"{d}", "-c", "copy", f"{output_path}/source.mp4"])
    if check == 0:
        subprocess.call(["ffmpeg", "-i", f"{output_path}/source.mp4", "-ac", "1",
                        "-ar", "44100", "-acodec", "pcm_s16le", f"{output_path}/source.wav"])
    return check


# timestamp = [['00:00', '00:00', 'タイトル'],[]] を持っているファイルを受け取ります
def split_movies(timestamp):
    file_path = "./source/source_video.mp4"
    movie_list = []

    for i in range(len(timestamp)):
        start = time2s(timestamp[i][0])
        end = time2s(timestamp[i][1])
        d = end - start
        name = timestamp[i][2]
        output_path = f"./source/{i}/"

        subprocess.call(['mkdir', f"./source/{i}"])
        if split_movie(start, file_path, d, output_path) == 0:
            movie_list.append(i)

    return movie_list


def movie_cut(file_path):
    # https://nantekottai.com/2020/06/14/video-cut-silence/
    # 無音部分のカットはこちらのコードを参考にさせていただきました。
    # 音声読み込み
    # data, sr = librosa.load(f"{file_path}/source.mp3")
    data, sr = soundfile.read(f"{file_path}/source.wav")
    thres = 0.05
    amp = np.abs(data)
    b = amp > thres
    min_silence_duration = 0.5
    silences = []
    prev = 0
    entered = 0
    for i, v in enumerate(b):
        if prev == 1 and v == 0:  # enter silence
            entered = i
        if prev == 0 and v == 1:  # exit silence
            duration = (i - entered) / sr
            if duration > min_silence_duration:
                silences.append({"from": entered, "to": i, "suffix": "cut"})
                entered = 0
        prev = v
    if entered > 0 and entered < len(b):
        silences.append({"from": entered, "to": len(b), "suffix": "cut"})
    min_keep_duration = 0.4
    cut_blocks = []
    blocks = silences
    while 1:
        if len(blocks) == 0:
            break
        # print(len(blocks))
        if len(blocks) == 1:
            cut_blocks.append(blocks[0])
            break

        block = blocks[0]
        next_blocks = [block]
        for i, b in enumerate(blocks):
            if i == 0:
                continue
            interval = (b["from"] - block["to"]) / sr
            if interval < min_keep_duration:
                block["to"] = b["to"]
                next_blocks.append(b)

        cut_blocks.append(block)
        blocks = list(filter(lambda b: b not in next_blocks, blocks))
        # blocks.pop(0)

    keep_blocks = []
    for i, block in enumerate(cut_blocks):
        if i == 0 and block["from"] > 0:
            keep_blocks.append(
                {"from": 0, "to": block["from"], "suffix": "keep"})
        if i > 0:
            prev = cut_blocks[i - 1]
            keep_blocks.append(
                {"from": prev["to"], "to": block["from"], "suffix": "keep"})
        if i == len(cut_blocks) - 1 and block["to"] < len(data):
            keep_blocks.append(
                {"from": block["to"], "to": len(data), "suffix": "keep"})

    padding_time = 0.2
    files = []
    subprocess.call(["mkdir", f"{file_path}/movies/"])
    subprocess.call(["mkdir", f"{file_path}/sounds/"])
    for i, block in enumerate(keep_blocks):
        # fr = block["from"] / sr
        # to = block["to"] / sr
        fr = max(block["from"] / sr - padding_time, 0)
        to = min(block["to"] / sr + padding_time, len(data) / sr)
        duration = to - fr
        subprocess.call(["ffmpeg", "-ss", f"{fr}", "-i", f"{file_path}/source.mp4",
                        "-t", f"{duration}", "-c", "copy", f"{file_path}/movies/{i}.mp4"])
        subprocess.call(["ffmpeg", "-i", f"{file_path}/movies/{i}.mp4", "-ac", "1",
                        "-ar", "44100", "-acodec", "pcm_s16le", f"{file_path}/sounds/{i}.wav"])
        files.append(i)
    return files


if __name__ == '__main__':
    # print(time2s('1:0:0'))
    # timestamp = [['0:00', '1:20', 'テスト'], ['1:0:02', '1:0:32', '２個目']]
    # split_movies(timestamp)
    # movie_cut("./source/1")
    pass
