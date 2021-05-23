import requests

class VkPhotos:
    def __init__(self, token):
        self.token = token

    # common request
    def _send_request(self, request_type, method, **kwargs):
        url = "https://api.vk.com/method/" + method
        params = {"v": "5.130",
                  "access_token": self.token}
        params.update(kwargs)
        return request_type(url, params=params)

    # gets photos from album
    # to get photos from other user set kwargs = {"owner_id": id}
    def get_photos(self, album_id, **kwargs):
        kwargs.update({"album_id": album_id})
        response = self._send_request(requests.get, "photos.get", **kwargs)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            return None

    # gets list of albums
    def get_albums(self, **kwargs):
        response = self._send_request(requests.get, "photos.getAlbums", **kwargs)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            return None

    # gets photo likes count by photo id
    def get_likes_count(self, photo_id, **kwargs):
        kwargs.update({"type": "photo", "item_id": photo_id})
        response = self._send_request(requests.get, "likes.getList", **kwargs)
        if response.status_code == 200:
            return response.json()["response"]["count"]
        else:
            print(f"Error: {response.status_code}")
            return None

    # requests photo information and return as list of dicts
    def get_photos_formatted(self,  album_id, **kwargs):
        kwargs.update({"extended": 1})
        get_photos_result = self.get_photos(album_id, **kwargs)
        if get_photos_result is None:
            return
        # create a dict of user photos with urls as keys
        photo_urls = {}
        for photo in get_photos_result["response"]["items"]:
            # find largest photo size_type from available size_types
            for size_type in ["w", "z", "y", "r", "q", "p", "o", "x", "m", "s"]:
                if size_type in [size_variant["type"] for size_variant in photo["sizes"]]:
                    max_size_type = size_type
                    break
            for size_variant in photo["sizes"]:
                if size_variant["type"] == max_size_type:
                    # add photo with unique urls to dictionary
                    if size_variant["url"] not in photo_urls:
                        photo_urls[size_variant["url"]] = \
                            {"owner_id": photo["owner_id"],
                             "id": [photo["id"]],
                             "likes": photo["likes"]["count"],
                             "size_type": size_variant["type"],
                             "file_name": f"id{photo['owner_id']}_{photo['id']}_{photo['likes']['count']}.jpg"}
                    else:
                        # if photo with same url posted several times save sum of likes
                        if photo["id"] not in photo_urls[size_variant["url"]]["id"]:
                            photo_urls[size_variant["url"]]["likes"] += photo["likes"]["count"]
                            photo_urls[size_variant["url"]]["id"].append(photo["id"])
        # reformat dict to list of dicts
        photos = []
        for url in photo_urls.keys():
            photos.append(dict(**{"url": url}, **photo_urls[url]))
        print(f"Data for {len(photos)} photos (album:{album_id}) received from Vk" )
        return photos
