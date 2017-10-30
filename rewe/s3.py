import os

import boto3
from botocore.exceptions import ClientError

from .logger import Logger


class S3:
    bucket_name = "rewe-bot"
    profile_name = "rewe-bot"
    base_path = "./resources"
    filename = None

    def __init__(self, p_user, log_level: str = "INFO"):
        """

        :param p_user: rewe.User User the file will be saved with
        """
        self.log = Logger("S3", level=log_level)
        self.log.debug("Creating s3 instance for user: {}".format(p_user.id))
        self.log.debug("Creating s3 session with profile {} for user: {}".format(self.profile_name, p_user.id))
        self.session = boto3.Session(profile_name=self.profile_name)
        self.log.debug("Creating s3 resource for user: {}".format(p_user.id))
        self.s3 = self.session.resource("s3")
        self.log.debug("Getting bucket ({}) for user: {}".format(self.bucket_name, p_user.id))
        self.bucket: self.s3.Bucket = self.s3.Bucket(self.bucket_name)

        self.user = p_user

        self.log.debug("Creating resource path {} for user: {}".format(self.base_path, p_user.id))
        os.makedirs(self.base_path, exist_ok=True)
        self.log.debug("Created s3 instance for user: {}".format(p_user.id))

        # if self.exists():
        #     self.download()

    def get_local_filepath(self, directory: str = None, filename: str = None):
        if not directory:
            directory = self.base_path
            self.base_path = directory
        if not filename:
            filename = self.get_s3_name()

        result = os.path.join(directory, filename)
        self.log.debug("{}".format(result))
        return result

    def upload(self, *, directory: str = None, filename: str = None):
        self.log.debug("Upload")
        local = self.get_local_filepath(directory, filename)
        self.log.debug("Local: %s", local)
        remote = self.get_s3_name()
        self.log.debug("Remote: %s", remote)
        self.log.debug("Upload %s to %s", local, remote)
        self.bucket.upload_file(local, remote)

    def download(self, *, directory: str = None, filename: str = None):
        self.log.debug("Download")
        local = self.get_local_filepath(directory, filename)
        self.log.debug("Local: %s", local)
        remote = self.get_s3_name()
        self.log.debug("Remote: %s", local)
        self.log.debug("Download %s to %s", local, remote)
        return self.bucket.download_file(remote, local)

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
        exists = False
        if not name:
            name = self.get_s3_name()

        self.log.debug("Does %s exist?", name)
        try:
            import random
            import string
            self.download(filename="/tmp/{}".format("".join([x for x in random.choices(string.ascii_letters, k=20)])))
            self.log.debug("Downloaded %s for user: %s", name, self.user.id)
            exists = True
        except ClientError as ce:
            exists = not "Not Found" in str(ce)
            self.log.debug("Remote file %s not found in remote for user: %s", name, self.user.id)

        return exists
