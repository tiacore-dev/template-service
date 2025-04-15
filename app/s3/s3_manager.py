from loguru import logger
import aioboto3
from botocore.exceptions import ClientError
from app.config import Settings

settings = Settings()


class AsyncS3Manager:
    endpoint_url = settings.ENDPOINT_URL
    region_name = settings.REGION_NAME
    aws_access_key_id = settings.AWS_ACCESS_KEY_ID
    aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
    bucket_name = settings.BUCKET_NAME
    bucket_folder = "crm"

    def _get_session(self):
        return aioboto3.Session()

    async def download_bytes(self, s3_key: str) -> bytes:
        session = self._get_session()
        async with session.client(
            "s3",
            endpoint_url=self.endpoint_url,
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        ) as s3:
            try:
                response = await s3.get_object(Bucket=self.bucket_name, Key=s3_key)
                file_bytes = await response["Body"].read()
                logger.info(
                    f"📥 Файл загружен с S3: {s3_key}, размер: {len(file_bytes)} байт")
                return file_bytes
            except ClientError as e:
                logger.error(f"❌ Ошибка при загрузке файла: {e}")
                raise
