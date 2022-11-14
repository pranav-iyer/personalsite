from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.files import File
from django.db.utils import IntegrityError
from pixelart.models import ArtPiece
from typing import Any, Optional
import os
import shutil
import json

class Command(BaseCommand):
    help = 'searches for newly uploaded pixelart folders and adds their contents to the database.'

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        upload_dir = settings.PIXELART_UPLOAD_DIR
        new_art_dirs = []
        for d in os.listdir(upload_dir):
            abs_path = os.path.join(upload_dir, d)
            if os.path.isdir(abs_path):
                new_art_dirs.append(abs_path)
        if not new_art_dirs:
            print("No new art pieces found.")
            return
        art_dirs_str = '\n\t'.join(new_art_dirs)
        print(f"Found {len(new_art_dirs)} new art piece(s):\n\t{art_dirs_str}\n")
        for art_dir in new_art_dirs:
            print(f"Exploring {art_dir}...")
            contents = os.listdir(art_dir)
            if not "info.json" in contents:
                raise RuntimeError(f"Folder {art_dir} does not contain an info.json file.")
            with open(os.path.join(art_dir, 'info.json'), 'r') as f:
                info_dict = json.load(f)
            title = info_dict['title']
            slug = info_dict['slug']
            pixart_fnam = info_dict["pixart_file"]
            thumb_fnam = info_dict['thumb_file']
            thumb_gs_fnam = info_dict['thumb_gs_file']

            if not pixart_fnam in contents:
                raise RuntimeError(f"Folder {art_dir} does not contain a {pixart_fnam} file.")
            if not thumb_fnam in contents:
                raise RuntimeError(f"Folder {art_dir} does not contain a {thumb_fnam} file.")
            if not thumb_gs_fnam in contents:
                raise RuntimeError(f"Folder {art_dir} does not contain a {thumb_gs_fnam} file.")

            success = True
            with open(os.path.join(art_dir, pixart_fnam), "r") as pixart_file, \
                open(os.path.join(art_dir, thumb_gs_fnam), "rb") as empty_thumb_file, \
                open(os.path.join(art_dir, thumb_fnam), "rb") as filled_thumb_file:
                try:
                    ArtPiece.objects.create(
                        title=title, slug=slug,
                        pixart=File(pixart_file, name=pixart_fnam),
                        thumbnail=File(empty_thumb_file, name=thumb_gs_fnam),
                        filled_thumbnail=File(filled_thumb_file, name=thumb_fnam)
                    )
                except IntegrityError:
                    success = False
                    print(f'Could not create new art piece with slug "{slug}", one already exists in the database. Please edit info.json with a new slug and try again.')
            if success:
                print(f"Created new pixel art {title}, removing original directory...")
                shutil.rmtree(art_dir)

        print(f"\nSuccessfuly added {len(new_art_dirs)} new art pieces to database.")