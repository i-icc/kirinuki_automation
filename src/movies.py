import subprocess
import soundfile


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


def split_movie(start, file_path, d, output_path):  # 動画を切り取ります
    check = subprocess.call(
        ["ffmpeg", "-ss", f"{start}", "-i", file_path, "-t", f"{d}", "-c", "copy", f"{output_path}/source.mp4"])
    if check == 0:
        #subprocess.call(["ffmpeg", "-i", f"{output_path}/source.mp4", "-f","mp3", "-ab", "192000", "-vn", f"{output_path}/source.mp3"])
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
        if split_movie(start, file_path, d, output_path):
            movie_list.append(i)

    return movie_list


def movie_cut(file_path):
    # 音声読み込み
    # data, sr = librosa.load(f"{file_path}/source.mp3")
    data, sr = soundfile.read(f"{file_path}/source.wav")
    


if __name__ == '__main__':
    print(time2s('1:0:0'))
    timestamp = [['0:00', '1:20', 'テスト'], ['1:0:02', '1:0:32', '２個目']]
    # split_movies(timestamp)
    movie_cut("./source/1")
