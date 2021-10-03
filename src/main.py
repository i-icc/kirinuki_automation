import subprocess
from movies import download_movie,  remake_movies, split_movies
from texts import read_timestamp


def main():
    subprocess.call(['mkdir', './source'])
    # 動画をダウンロードします正しくダウンロードできなければ終了
    if download_movie('https://www.youtube.com/watch?v=nZiPBqfjTec') == 0:
        print('Download successful')
    else:
        print('Download failed')
        return

    timestamp = read_timestamp()
    movie_list = split_movies(timestamp)
    for i in movie_list:
        remake_movies(f"./source/{i}",timestamp[i][2])

    subprocess.call(['rm','-rf','./source'])


if __name__ == '__main__':
    main()
