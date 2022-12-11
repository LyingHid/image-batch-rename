#!/usr/bin/python

import os
import datetime
import PIL.Image
import pillow_heif


pillow_heif.register_heif_opener()


def image_extract_timestamp(path):
  ModifyDate = 0x0132  # DateTime
  DateTimeOriginal = 0x9003  # date/time when original image was taken
  CreateDate = 0x9004  # DateTimeDigitized

  SubSecTime = 0x9290  # fractional seconds for ModifyDate
  SubSecTimeOriginal = 0x9291  # fractional seconds for DateTimeOriginal
  SubSecTimeDigitized = 0x9292  # fractional seconds for CreateDate

  image = PIL.Image.open(path)
  exif = image.getexif()

  timestamp = exif.get(DateTimeOriginal)
  timestamp = timestamp or exif.get(CreateDate)
  timestamp = timestamp or exif.get(ModifyDate)

  return timestamp


def timestamp_to_filename(timestamp):
  pydatetime = datetime.datetime.strptime(timestamp, '%Y:%m:%d %H:%M:%S')
  filename = pydatetime.strftime('%Y-%m-%d %H.%M.%S')
  return filename


def enum_all_images(folder_path):
  images = []

  for path in os.listdir(folder_path):
    full_path = os.path.join(folder_path, path)
    if os.path.isdir(full_path):
      recursive_images = enum_all_images(full_path)
      images.extend(recursive_images)
    if os.path.isfile(full_path):
      if path.endswith('.jpg') or path.endswith('.heic'):
        images.append((full_path, folder_path, path))

  return images


def map_image_name(images):
  renamed_images = []

  for full_path, folder_path, path in images:
    name, ext = path.rsplit('.', maxsplit=1)
    timestamp = image_extract_timestamp(full_path)
    new_name = timestamp_to_filename(timestamp)
    new_path = '{}.{}'.format(new_name, ext)

    renamed_images.append((full_path, folder_path, path, new_path))

  return renamed_images


def check_name_conflict(renamed_images):
  book = {}
  has_confilct = False

  for full_path, folder_path, path, new_path in renamed_images:
    if new_path not in book:
      book[new_path] = []
    book[new_path].append(full_path)

  for new_path, old_pathes in book.items():
    if len(old_pathes) > 1:
      has_confilct = True
      print('conflict', new_path, old_pathes)

  return has_confilct


def batch_rename(renamed_images, dry_run=True):
  for full_path, folder_path, path, new_path in renamed_images:
    new_full_path = os.path.join(folder_path, new_path)
    print('rename{}: {} -> {}'.format(' (dry_run)' if dry_run else '', full_path, new_full_path))
    if not dry_run:
      os.rename(full_path, new_full_path)


def drive(folder_path, dry_run=True):
  images = enum_all_images(folder_path)
  renamed_images = map_image_name(images)
  has_confilct = check_name_conflict(renamed_images)
  if has_confilct: return
  batch_rename(renamed_images, dry_run)


if __name__ == '__main__':
  if False:
    timestamp = image_extract_timestamp('/sdcard/DCIM/Tidy/2022-10-22 15.07.56.heic')
    print(timestamp)  # 2022:10:22 15:07:56

  if False:
    pydatetime = timestamp_to_filename('2022:10:22 15:07:56')
    print(pydatetime)  # 2022-10-22 15.07.56

  if False:
    images = enum_all_images('/sdcard/Pictures')
    print(images)
    images = map_image_name(images)
    print(images)


  # drive('/sdcard/Download/S Share/Camera/', dry_run=False)
