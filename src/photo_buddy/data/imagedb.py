from PIL import ImagePil
import imagehash
from pathlib import Path
import shelve
import glob
from photo_buddy import settings

@dataclass
class Image:
    hash
    name: str
    uri: str

class ImageDb:

    def __init__(self, path):
        self.path = settings.db.path
        self.db = shelve.open(self.path, writeback=False)

    def add_image(self, image_path):
        image_pil = ImagePil.open(image_path)

        Image(
            name=Path(image_path).name(),
            hash=str(imagehash.dhash(image_pil)),
            uri=Path(image_path).as_uri()
        )
        self.db[hash] = self.db.get(hash, []) + [Image]
