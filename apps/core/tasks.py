import logging
import os

from celery import shared_task
from redis_store import redis

from apps.core.models import Dataset


logger = logging.getLogger(__name__)


def _load_dataset_file(file_id):
    from apps.file.models import File

    # get file information
    file = File.objects.get(id=file_id)
    data = {"file_url": file.file, "file_size_bytes": os.stat(file.file)}
    Dataset.objects.create(**data)


@shared_task
def create_dataset(file_id):
    key = "load_import_file_{}".format(file_id)
    lock = redis.get_lock(key, 60 * 30)
    have_lock = lock.acquire(blocking=False)
    if not have_lock:
        return False
    try:
        return_value = _load_dataset_file(file_id)
    except Exception:
        logger.error("Failed to Load File", exc_info=True)
        return_value = False

    lock.release()
    return return_value
