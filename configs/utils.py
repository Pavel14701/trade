import uuid, pickle, hmac, hashlib, base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.backends import default_backend
from typing import Callable, Any, Tuple, Dict
from celery import Celery # type: ignore
from redis import Redis
from configs.provider import ConfigsProvider


class SecurePickle:
    def __init__(self):
        configs = ConfigsProvider().load_api_okx_configs()
        self._secret_key = bytes(configs.secret_key)
        if configs.api_key is not None and configs.secret_key is not None and configs.flag is not None:
            self.salt = f'{configs.api_key}{configs.secret_key}{configs.flag}'.encode()
        else:
            raise ValueError('All secrets must be setted')
        self._key = self.__derive_key_from_password()

    def __sign_data(self, data: bytes, salt: bytes) -> bytes:
        signature = hmac.new(self._secret_key + salt, data, hashlib.sha256).digest()
        return salt + signature + data

    def __verify_data(self, signed_data: bytes) -> bytes:
        salt = signed_data[:16]
        signature = signed_data[16:48]
        data = signed_data[48:]
        expected_signature = hmac.new(self._secret_key + salt, data, hashlib.sha256).digest()
        if signature != expected_signature:
            raise ValueError("Alert, data has been changed")
        return data

    def __derive_key_from_password(self) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(self._secret_key))

    def serialize(self, obj: Any) -> bytes:
        pickled_data = pickle.dumps(obj)
        salt = uuid.uuid4().bytes  # Генерируем уникальную соль для каждого объекта
        signed_data = self.__sign_data(pickled_data, salt)
        fernet = Fernet(self._key)
        encrypted_data = fernet.encrypt(signed_data)
        return encrypted_data

    def deserialize(self, encrypted_data: bytes) -> Any:
        fernet = Fernet(self._key)
        signed_data = fernet.decrypt(encrypted_data)
        pickled_data = self.__verify_data(signed_data)
        obj = pickle.loads(pickled_data)
        return obj

class CeleryUtil:
    def __init__(self):
        self.sp = SecurePickle()
        self.configs = ConfigsProvider().load_cache_settings()
        self.app = self.__create_app()
        self.redis_client = self.__create_redis_client()
        self.__setup_tasks()

    def __create_app(self) -> Celery:
        return Celery('tasks', broker=f'redis://{self.configs.host}:{self.configs.port}/{self.configs.celery_db}')

    def __create_redis_client(self) -> Redis:
        return Redis(host=self.configs.host, port=self.configs.port, db=self.configs.celery_db)

    def __setup_tasks(self):
        @self.app.task(name='tasks.process_task')
        def __process_task(task_id: str, func_pickle: bytes, *args: Tuple[Any], **kwargs: Dict[str, Any]) -> Any:
            if not self.redis_client.exists(f"task:{task_id}"):
                func: Callable = self.sp.deserialize(func_pickle)
                result: Any = func(*args, **kwargs)
                result_pickle = self.sp.serialize(result)
                self.redis_client.set(f"task:{task_id}", result_pickle)
            result_data = self.redis_client.get(f"task:{task_id}")
            if result_data is not None and isinstance(result_data, bytes):
                return self.sp.deserialize(result_data)
            return None
        self.process_task = __process_task

    def run_task(self, func: Callable[..., Any], *args: Tuple[Any], **kwargs: Dict[str, Any]) -> Any:
        task_id = str(uuid.uuid4())
        func_pickle = self.sp.serialize(func)
        return self.process_task.delay(task_id, func_pickle, *args, **kwargs)