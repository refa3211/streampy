import libtorrent as lt
import time
import sys
import subprocess

def stream_torrent(magnet_link):
    # Configure session
    ses = lt.session({'listen_interfaces': '0.0.0.0:6881'})
    
    # Add torrent
    handle = lt.add_magnet_uri(ses, magnet_link, {'save_path': '.'})
    print("Downloading metadata...")
    
    while not handle.has_metadata():
        time.sleep(1)
    print("Got metadata, starting torrent download...")

    # Prioritize first file
    torrent_info = handle.get_torrent_info()
    handle.set_sequential_download(True)
    largest_file = max(torrent_info.files(), key=lambda f: f.size)
    largest_file_index = largest_file.index
    handle.file_priority(largest_file_index, 7)

    # Wait for the file to start downloading
    while handle.status().state != lt.torrent_status.seeding:
        s = handle.status()
        print(f"\rProgress: {s.progress:.2%}, Down: {s.download_rate / 1000:.1f} kB/s", end='')
        
        # Start streaming when we have some data
        if s.progress > 0.05:
            file_path = largest_file.path
            print(f"\nStarting playback of {file_path}")
            subprocess.Popen(['vlc', file_path])
            break
        
        time.sleep(1)

    print("\nPlayback started. Press Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")
    
    ses.remove_torrent(handle)
    print("Torrent removed. Exiting.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <magnet_link>")
        sys.exit(1)
    
    magnet_link = sys.argv[1]
    stream_torrent(magnet_link)