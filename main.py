import libtorrent as lt
import time
import sys
import vlc
import tempfile
import os
import threading

def download_progress(handle):
    while (handle.status().state != lt.torrent_status.seeding):
        s = handle.status()
        state_str = ['queued', 'checking', 'downloading metadata', 
                     'downloading', 'finished', 'seeding', 'allocating']
        print(f'\r{state_str[s.state]} {s.progress:.2%} complete (down: {s.download_rate / 1000:.1f} kB/s up: {s.upload_rate / 1000:.1f} kB/s peers: {s.num_peers})', end=' ')
        time.sleep(1)
    print("\nDownload completed!")

def stream_magnet(magnet_link):
    # Create a libtorrent session
    ses = lt.session()
    
    # Create a temporary directory to store the downloaded files
    with tempfile.TemporaryDirectory() as tmpdirname:
        print(f"Created temporary directory: {tmpdirname}")
        
        # Add magnet link
        params = lt.parse_magnet_uri(magnet_link)
        params.save_path = tmpdirname
        handle = ses.add_torrent(params)

        print("Downloading metadata...")
        while not handle.has_metadata():
            time.sleep(1)
        print("Got metadata, starting torrent download...")

        # Prioritize first file
        torrent_info = handle.get_torrent_info()
        files = torrent_info.files()
        largest_file = max(range(files.num_files()), key=lambda i: files.file_size(i))
        handle.file_priority(largest_file, 7)

        # Start the download thread
        download_thread = threading.Thread(target=download_progress, args=(handle,))
        download_thread.start()

        # Wait for some initial data to be downloaded (e.g., 5%)
        while handle.status().progress < 0.05:
            time.sleep(1)

        print("\nStarting playback...")
        
        # Get the file path
        file_path = os.path.join(tmpdirname, files.file_path(largest_file))

        # Create a VLC instance
        instance = vlc.Instance()

        # Create a MediaPlayer with the file
        player = instance.media_player_new()
        media = instance.media_new(file_path)
        player.set_media(media)

        # Play the media
        player.play()

        print("Playback started. Press Ctrl+C to stop playback and exit.")
        try:
            while True:
                time.sleep(1)
                # You might want to add some checks here, e.g., to see if playback has ended
        except KeyboardInterrupt:
            print("\nStopping playback and cleaning up...")
            player.stop()

        # Wait for the download thread to finish
        download_thread.join()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <magnet_link>")
        sys.exit(1)
    
    magnet_link = sys.argv[1]
    stream_magnet(magnet_link)
