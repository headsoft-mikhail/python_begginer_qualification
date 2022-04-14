import tokens
from vk import VkPhotos
from yandex_disk import YandexDisk
import time
import json
import os

def get_photo_data(vk, albums, filename="photos_data.json", **kwargs):
    photos = {}
    for album in albums:
        photos[album] = vk.get_photos_formatted(album, **kwargs)
    with open(filename, "w") as output_file:
        json.dump(photos, output_file)
        print(f"Photos data saved to '{filename}'")

# upload all albums in photos dict to disk
def backup_photos(disk, photos, max_count=5, clear=False):
    for album_id in photos.keys():
        backup_album(disk, photos, album_id, max_count=max_count, clear=clear)
    print(f"Backup successfully finished")

# upload specified by id album from photos dict to disk
def backup_album(disk, photos, album_id, max_count=5, clear=False):
    # clear directory before photo uploading
    if clear and disk.check_dir(f"photos/{album_id}/"):
        if disk.delete(f"photos/{album_id}/", **{"force_async": "true"}):
            while disk.check_dir(f"photos/{album_id}/"):
                # wait while server deletes directory, then continue
                time.sleep(0.5)

    old_root = disk.root
    root = f"{disk.root}photos/{album_id}/"
    disk.set_root(root)

    # upload photos to disc
    loaded_files = []
    max_count = min(max_count, len(photos[album_id]))
    for photo in photos[album_id]:
        if disk.upload_from_url(photo["file_name"], photo["url"]):
            loaded_files.append(photo["file_name"])
            print(f"{len(loaded_files)} of {max_count} files "
                  f"uploaded to {disk.root} [{'%.1f'%(100*len(loaded_files)/max_count)}% finished]")
        # on album uploading finished
        if len(loaded_files) == max_count:
            print(f"Backup of album '{album_id}' successfully finished")
            disk.set_root(old_root)
            return


if __name__ == "__main__":
    # create objects
    root = "loads/vk/"
    ya_disk = YandexDisk(tokens.YANDEX_TOKEN, root)
    vk = VkPhotos(tokens.VK_TOKEN)

    # # loading file from hard drive
    # source_path = os.path.join(os.getcwd(), "test_upload_from_hard_drive")
    # filename = "test_file.txt"
    # ya_disk.upload_file(filename, os.path.join(source_path, filename))
    #
    # # loading directory from hard drive
    # dir_name = "test_folder"
    # ya_disk.upload_dir(dir_name, os.path.join(source_path, dir_name))


    albums = ["profile", "wall"]
    filename = "photos_data.json"
    # get photo data from VK and save to file "photos_data.json"
    # parameter "count" is how many photos to get from VK
    get_photo_data(vk, albums, filename, **{"owner_id": tokens.MY_VK_ID, "count": 2})

    # get photos data from "photos_data.json" and upload photos to yandex disk
    # "max_count" is maximum count of photos to load to yandex disk
    with open(file=filename, mode="r") as data_file:
        print(f"Photos data file '{filename}' opened")
        backup_photos(ya_disk, json.load(data_file), max_count=2, clear=True)
