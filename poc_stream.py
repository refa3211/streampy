import libtorrent as lt
import time
import vlc
import sys

# Load torrent
ses = lt.session()
info = lt.torrent_info("path_to_torrent_file.torrent")
h = ses.add_torrent({'ti': info, 'save_path': './'})

print('Starting torrent download...')
while not h.is_seed():
    s = h.status()
    print(f'Download rate: {s.download_rate / 1000:.2f} kB/s, Progress: {s.progress * 100:.2f}%')
    time.sleep(1)

print('Download complete, starting stream...')
video_path = "path_to_downloaded_video_file.mp4"  # Adjust this according to your torrent content

# Play video
Instance = vlc.Instance()
player = Instance.media_player_new()
Media = Instance.media_new(video_path)
Media.get_mrl()
player.set_media(Media)
player.play()

while True:
    time.sleep(1)
    if player.get_state() == vlc.State.Ended:
        break
