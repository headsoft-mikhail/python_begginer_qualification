import requests
import os

class YandexDisk:
    def __init__(self, token, root):
        self.token = token
        self.root = ""
        self.set_root(root)

    # sets the base folder for work with disk
    # creates it if it not exists
    def set_root(self, root):
        self.root = ""
        if not self.check_dir(root):
            for depth in range(root.count("/")):
                dir_name = root.split("/")[depth]
                self.create_dir(dir_name)
                self.root += dir_name + "/"
        else:
            self.root = root

    # get headers
    def _get_headers(self):
        return {
            "Content-type": "application/json",
            "Authorization": "OAuth {}".format(self.token)
        }

    # common request
    def _send_request(self, request_type, method, path, **kwargs):
        url = "https://cloud-api.yandex.net/v1/disk/" + method
        headers = self._get_headers()
        params = {"path": self.root + path}
        params.update(kwargs)
        return request_type(url, headers=headers, params=params)

    # gets a link to upload file from hard drive
    def _get_upload_link(self, upload_path, **kwargs):
        response = self._send_request(requests.get, "resources/upload", upload_path, **kwargs)
        return response.json()

    # check if path exists on the disk
    def check_dir(self, path, **kwargs):
        response = self._send_request(requests.get, "resources", path, **kwargs)
        if response.status_code == 200:
            print(f"Path '{self.root + path}' exists")
            return True
        else:
            print(f"Path '{self.root + path}' does not exists")
            return False

    # creates directory
    def create_dir(self, path, **kwargs):
        if not self.check_dir(path):
            response = self._send_request(requests.put, "resources", path, **kwargs)
            if response.status_code == 201:
                print(f"Directory '{self.root + path}' successfully created")
                return True
            else:
                print(f"Error: {response.status_code}")
                return False

    # deletes directory or path
    def delete(self, path, **kwargs):
        response = self._send_request(requests.delete, "resources", path, **kwargs)
        if response.status_code == 202 or response.status_code == 204:
            return True
            print(f"Delete request of {self.root + path} sent")
        else:
            return False
            print(f"Error: {response.status_code}")

    # upload file from URL
    def upload_from_url(self, upload_path, source_url, **kwargs):
        kwargs.update({"url": source_url})
        response = self._send_request(requests.post, "resources/upload", upload_path, **kwargs)
        if response.status_code == 202:
            print(f"File {self.root + upload_path} successfully uploaded")
            return True
        else:
            print(f"Error: {response.status_code}")
            return False

    # upload file from hard drive
    def upload_file(self, upload_path, source_path, overwrite=True):
        if os.path.exists(source_path):
            href = self._get_upload_link(upload_path, **{"overwrite": str(overwrite).lower()}).get("href", "")
            response = requests.put(href, data=open(source_path, "rb"))
            if response.status_code == 201:
                print(f"File {self.root + upload_path} successfully uploaded")
                return True
            else:
                print(f"Error: {response.status_code}")
                return False
        else:
            print(f"Cancelled:{source_path} does not exists")
            return False

    # upload directory, files and all subdirectories
    def upload_dir(self, upload_path, source_path):
        if os.path.exists(source_path):
            self.create_dir(upload_path)
            files = os.listdir(source_path)
            for file in files:
                if os.path.isdir(os.path.join(source_path, file)):
                    if not self.upload_dir(upload_path + "/" + file, source_path + "/" + file):
                        return False
                else:
                    if not self.upload_file(upload_path + "/" + file, os.path.join(source_path, file)):
                        return False
            return True
        else:
            print(f"Cancelled:{source_path} does not exists")
            return False


