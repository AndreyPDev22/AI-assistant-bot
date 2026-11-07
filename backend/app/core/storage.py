import logging
from typing import Annotated
from uuid import UUID, uuid4

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import Depends, HTTPException, Request
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE

from app.core.config import Settings

logger = logging.getLogger(__name__)


class S3PhotoStorage:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._client = None

    @property
    def client(self):
        if not self.settings.s3_bucket:
            raise HTTPException(HTTP_503_SERVICE_UNAVAILABLE, "Хранилище фото пока не настроено")
        if self._client is None:
            self._client = boto3.client(
                "s3",
                endpoint_url=self.settings.s3_endpoint_url,
                region_name=self.settings.s3_region,
                aws_access_key_id=(
                    self.settings.s3_access_key_id.get_secret_value()
                    if self.settings.s3_access_key_id
                    else None
                ),
                aws_secret_access_key=(
                    self.settings.s3_secret_access_key.get_secret_value()
                    if self.settings.s3_secret_access_key
                    else None
                ),
                config=Config(
                    signature_version="s3v4",
                    connect_timeout=5,
                    read_timeout=10,
                    retries={"max_attempts": 2, "mode": "standard"},
                    s3={"addressing_style": self.settings.s3_addressing_style},
                ),
            )
        return self._client

    def upload_photo(self, contents: bytes, user_id: UUID) -> str:
        key = f"users/{user_id}/photos/{uuid4()}.jpg"
        try:
            self.client.put_object(
                Bucket=self.settings.s3_bucket,
                Key=key,
                Body=contents,
                ContentType="image/jpeg",
                CacheControl="private, no-store",
            )
        except (BotoCoreError, ClientError) as exc:
            raise HTTPException(HTTP_503_SERVICE_UNAVAILABLE, "Не удалось сохранить фото") from exc
        return key

    def photo_url(self, key: str) -> str:
        try:
            return self.client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self.settings.s3_bucket,
                    "Key": key,
                    "ResponseContentType": "image/jpeg",
                    "ResponseCacheControl": "private, no-store",
                },
                ExpiresIn=self.settings.s3_presigned_url_expire_seconds,
            )
        except (BotoCoreError, ClientError) as exc:
            raise HTTPException(
                HTTP_503_SERVICE_UNAVAILABLE, "Не удалось получить ссылку на фото"
            ) from exc

    def read_photo(self, key: str) -> bytes:
        try:
            result = self.client.get_object(Bucket=self.settings.s3_bucket, Key=key)
            with result["Body"] as body:
                return body.read()
        except (BotoCoreError, ClientError) as exc:
            raise HTTPException(HTTP_503_SERVICE_UNAVAILABLE, "Не удалось прочитать фото") from exc

    def delete_photo(self, key: str) -> None:
        try:
            self.client.delete_object(Bucket=self.settings.s3_bucket, Key=key)
        except (BotoCoreError, ClientError, HTTPException) as exc:
            logger.error("Photo cleanup failed: %s", type(exc).__name__)

    def close(self) -> None:
        if self._client is not None:
            self._client.close()


def get_photo_storage(request: Request) -> S3PhotoStorage:
    return request.app.state.photo_storage


PhotoStorage = Annotated[S3PhotoStorage, Depends(get_photo_storage)]
