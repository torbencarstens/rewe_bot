import os

import boto3
from botocore.exceptions import ClientError

from .user import User


class S3:
    bucket_name = "rewe-bot"
    profile_name = "rewe-bot"
    base_path = "./resources"
    filename = None

    def __init__(self, user: User):
        """
        
        :param user: rewe.User User the file will be saved with
        """
        self.session = boto3.Session(profile_name=self.profile_name)
        self.s3 = self.session.resource("s3")
        self.bucket: self.s3.Bucket = self.s3.Bucket(self.bucket_name)

        self.user = user

    def get_local_filepath(self, directory: str = None, filename: str = None):
        if not directory:
            directory = self.base_path
            self.base_path = directory
        if not filename:
            filename = self.get_s3_name()

        return os.path.join(directory, filename)

    def upload(self, *, directory: str = None, filename: str = None):
        self.bucket.upload_file(self.get_local_filepath(directory, filename), self.get_s3_name())

    def download(self, *, directory: str = None, filename: str = None):
        return self.bucket.download_file(self.get_s3_name(), self.get_local_filepath(directory, filename))

    def get_s3_name(self):
        if self.filename:
            if not self.filename.endswith(".json"):
                self.filename = ".".join([self.filename, "json"])

            return self.filename

        return "{}.json".format(self.user.id)

    def exists(self, name: str = None) -> bool:
        """
        Downloads the file too since that appears to be the only way to check
        :param name: 
        :return: 
        """
        if not name:
            name = self.get_s3_name()
        try:
            self.download()
        except ClientError as ce:
            return "Not Found" in str(ce)

        return True
