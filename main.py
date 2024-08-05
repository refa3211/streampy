import libtorrent as lt
import time
import sys
import vlc

def stream_magnet(magnet_link):
    # Create a libtorrent session
    ses = lt.session()
    
    # Add magnet link
    params = lt.parse_magnet_uri(magnet_link)
    handle = ses.add_torrent(params)

    print("Downloading metadata...")
    while not handle.has_metadata():
        time.sleep(1)
    print("Got metadata, starting torrent download...")

    # Prioritize first file
    files = handle.get_torrent_info().files()
    largest_file = max(enumerate(files), key=lambda x: x[1].size)
    largest_file_index = largest_file[0]
    handle.file_priority(largest_file_index, 7)

    # Wait for the file to start downloading
    while handle.status().state != lt.torrent_status.seeding:
        s = handle.status()
        print(f'\rProgress: {s.progress:.2%}', end='')
        time.sleep(1)

    print("\nStarting playback...")
    
    # Get the file path
    file_path = handle.status().save_path + '/' + files[largest_file_index].path

    # Create a VLC instance
    instance = vlc.Instance()

    # Create a MediaPlayer with the file
    player = instance.media_player_new()
    media = instance.media_new(file_path)
    player.set_media(media)

    # Play the media
    player.play()

    # Keep the script running
    while True:
        time.sleep(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <magnet_link>")
        sys.exit(1)
    
    magnet_link = sys.argv[1]
    stream_magnet(magnet_link)
