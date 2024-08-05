import libtorrent as lt
import time
import sys
import vlc
import tempfile
import os

def stream_magnet(magnet_link):
    # Create a libtorrent session
    ses = lt.session()
    
    # Create a temporary directory to store the downloaded files
    with tempfile.TemporaryDirectory() as tmpdirname:
        print(f"Created temporary directory: {tmpdirname}")
        
        # Add magnet link
        params = {
            'save_path': tmpdirname,
            'storage_mode': lt.storage_mode_t(2),
        }
        handle = lt.add_magnet_uri(ses, magnet_link, params)

        print("Downloading metadata...")
        while not handle.has_metadata():
            time.sleep(1)
        print("Got metadata, starting torrent download...")

        # Prioritize first file
        torrent_info = handle.get_torrent_info()
        files = torrent_info.files()
        largest_file = max(enumerate(files), key=lambda x: x[1].size)
        largest_file_index = largest_file[0]
        handle.file_priority(largest_file_index, 7)

        # Wait for the file to start downloading
        while handle.status().state != lt.torrent_status.seeding:
            s = handle.status()
            state_str = ['queued', 'checking', 'downloading metadata', 
                         'downloading', 'finished', 'seeding', 'allocating']
            print(f'\r{state_str[s.state]} {s.progress:.2%} complete (down: {s.download_rate / 1000:.1f} kB/s up: {s.upload_rate / 1000:.1f} kB/s peers: {s.num_peers})', end=' ')
            time.sleep(1)

        print("\nStarting playback...")
        
        # Get the file path
        file_path = os.path.join(tmpdirname, files.file_path(largest_file_index))

        # Create a VLC instance
        instance = vlc.Instance()

        # Create a MediaPlayer with the file
        player = instance.media_player_new()
        media = instance.media_new(file_path)
        player.set_media(media)

        # Play the media
        player.play()

        print("Press Ctrl+C to stop playback and exit.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping playback and cleaning up...")
            player.stop()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <magnet_link>")
        sys.exit(1)
    
    magnet_link = sys.argv[1]
    stream_magnet(magnet_link)
