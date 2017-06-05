import os

import boto3

from .user import User


class S3:
    bucket_name = "rewe-bot"
    profile_name = "rewe-bot"
    base_path = "./resources"

    def __init__(self, user: User):
        """
        
        :param user: rewe.User User the file will be saved with
        """
        self.session = boto3.Session(profile_name=self.profile_name)
        self.s3 = self.session.resource("s3")
        self.bucket: self.s3.Bucket = self.s3.Bucket(self.bucket_name)

        self.user = user

    def _get_local_filepath(self, directory: str = None, filename: str = None):
        if not directory:
            directory = self.base_path
        if not filename:
            filename = self.get_s3_name()

        return os.path.join(directory, filename)

    def upload(self, *, directory: str = None, filename: str = None):
        self.bucket.upload_file(self._get_local_filepath(directory, filename), self.get_s3_name())

    def download(self, *, directory: str = None, filename: str = None):
        return self.bucket.download_file(self.get_s3_name(), self._get_local_filepath(directory, filename))

    def get_s3_name(self):
        return "{}.json".format(self.user.id)
