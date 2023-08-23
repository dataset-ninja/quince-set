import os
from urllib.parse import unquote, urlparse

import numpy as np
import supervisely as sly
from dotenv import load_dotenv
from supervisely.io.fs import (
    file_exists,
    get_file_ext,
    get_file_name,
    get_file_name_with_ext,
    get_file_size,
)
from tqdm import tqdm

import src.settings as s
from dataset_tools.convert import unpack_if_archive

# https://zenodo.org/record/6402251#.Yk_2vn9Bzmg


def download_dataset(teamfiles_dir: str) -> str:
    """Use it for large datasets to convert them on the instance"""
    api = sly.Api.from_env()
    team_id = sly.env.team_id()
    storage_dir = sly.app.get_data_dir()

    if isinstance(s.DOWNLOAD_ORIGINAL_URL, str):
        parsed_url = urlparse(s.DOWNLOAD_ORIGINAL_URL)
        file_name_with_ext = os.path.basename(parsed_url.path)
        file_name_with_ext = unquote(file_name_with_ext)

        sly.logger.info(f"Start unpacking archive '{file_name_with_ext}'...")
        local_path = os.path.join(storage_dir, file_name_with_ext)
        teamfiles_path = os.path.join(teamfiles_dir, file_name_with_ext)
        fsize = get_file_size(local_path)
        with tqdm(desc=f"Downloading '{file_name_with_ext}' to buffer..", total=fsize) as pbar:
            api.file.download(team_id, teamfiles_path, local_path, progress_cb=pbar)
        dataset_path = unpack_if_archive(local_path)

    if isinstance(s.DOWNLOAD_ORIGINAL_URL, dict):
        for file_name_with_ext, url in s.DOWNLOAD_ORIGINAL_URL.items():
            local_path = os.path.join(storage_dir, file_name_with_ext)
            teamfiles_path = os.path.join(teamfiles_dir, file_name_with_ext)

            if not os.path.exists(get_file_name(local_path)):
                fsize = get_file_size(local_path)
                with tqdm(
                    desc=f"Downloading '{file_name_with_ext}' to buffer {local_path}...",
                    total=fsize,
                    unit="B",
                    unit_scale=True,
                ) as pbar:
                    api.file.download(team_id, teamfiles_path, local_path, progress_cb=pbar)

                sly.logger.info(f"Start unpacking archive '{file_name_with_ext}'...")
                unpack_if_archive(local_path)
            else:
                sly.logger.info(
                    f"Archive '{file_name_with_ext}' was already unpacked to '{os.path.join(storage_dir, get_file_name(file_name_with_ext))}'. Skipping..."
                )

        dataset_path = storage_dir
    return dataset_path


def convert_and_upload_supervisely_project(
    api: sly.Api, workspace_id: int, project_name: str
) -> sly.ProjectInfo:
    # project_name = "QuinceSet"
    dataset_path = "APP_DATA/QuinceSet/QuinceSet"
    batch_size = 30
    ds_name = "ds"
    images_ext = ".jpg"
    bboxes_ext = ".txt"

    def create_ann(image_path):
        labels = []

        image_np = sly.imaging.image.read(image_path)[:, :, 0]
        img_height = image_np.shape[0]
        img_wight = image_np.shape[1]
        ann_path = os.path.join(dataset_path, get_file_name(image_path) + bboxes_ext)

        tags_data = date_to_values[get_file_name(image_path).split("_")[0]]

        air = sly.Tag(tag_air, value=tags_data[0])
        humidity = sly.Tag(tag_humidity, value=tags_data[1])
        soil = sly.Tag(tag_soil, value=tags_data[2])
        moisture = sly.Tag(tag_moisture, value=tags_data[3])
        ppfd = sly.Tag(tag_ppfd, value=tags_data[4])

        with open(ann_path) as f:
            content = f.read().split("\n")

        for curr_data in content:
            if len(curr_data) != 0:
                ann_data = list(map(float, curr_data.rstrip().split(" ")))
                curr_obj_class = idx_to_obj_class[int(ann_data[0])]
                left = int((ann_data[1] - ann_data[3] / 2) * img_wight)
                right = int((ann_data[1] + ann_data[3] / 2) * img_wight)
                top = int((ann_data[2] - ann_data[4] / 2) * img_height)
                bottom = int((ann_data[2] + ann_data[4] / 2) * img_height)
                rectangle = sly.Rectangle(top=top, left=left, bottom=bottom, right=right)
                label = sly.Label(rectangle, curr_obj_class)
                labels.append(label)

        return sly.Annotation(
            img_size=(img_height, img_wight),
            labels=labels,
            img_tags=[air, humidity, soil, moisture, ppfd],
        )

    idx_to_obj_class = {
        0: sly.ObjClass("ripe", sly.Rectangle),
        1: sly.ObjClass("unripe", sly.Rectangle),
    }

    tag_air = sly.TagMeta(
        "air temperature, °C",
        sly.TagValueType.ONEOF_STRING,
        possible_values=["24.9", "23.6", "24.2", "21.3", "22"],
    )
    tag_humidity = sly.TagMeta(
        "humidity, %",
        sly.TagValueType.ONEOF_STRING,
        possible_values=["35.9", "45.9", "57.3", "56.5", "43.5"],
    )
    tag_soil = sly.TagMeta(
        "soil temperature, °C",
        sly.TagValueType.ONEOF_STRING,
        possible_values=["24.0", "22.9", "21.5", "19.3", "20.2"],
    )
    tag_moisture = sly.TagMeta(
        "soil moisture content, %",
        sly.TagValueType.ONEOF_STRING,
        possible_values=["19.0", "16.8", "21.6", "28.9", "19.7"],
    )
    tag_ppfd = sly.TagMeta(
        "PPFD, µmol/m2/s",
        sly.TagValueType.ONEOF_STRING,
        possible_values=["1748.6", "1380.8", "958.2", "906.4", "1205.6"],
    )

    date_to_values = {
        "20210614": ("24.9", "35.9", "24.0", "19.0", "1748.6"),
        "20210615": ("23.6", "45.9", "22.9", "16.8", "1380.8"),
        "20210816": ("24.2", "57.3", "21.5", "21.6", "958.2"),
        "20210820": ("21.3", "56.5", "19.3", "28.9", "906.4"),
        "20210823": ("22", "43.5", "20.2", "19.7", "1205.6"),
    }

    project = api.project.create(workspace_id, project_name, change_name_if_conflict=True)
    meta = sly.ProjectMeta(
        obj_classes=list(idx_to_obj_class.values()),
        tag_metas=[tag_air, tag_humidity, tag_soil, tag_moisture, tag_ppfd],
    )
    api.project.update_meta(project.id, meta.to_json())

    images_names = [item for item in os.listdir(dataset_path) if get_file_ext(item) == images_ext]

    dataset = api.dataset.create(project.id, ds_name, change_name_if_conflict=True)

    progress = sly.Progress("Create dataset {}".format(ds_name), len(images_names))

    for images_names_batch in sly.batched(images_names, batch_size=batch_size):
        img_pathes_batch = [
            os.path.join(dataset_path, image_name) for image_name in images_names_batch
        ]

        img_infos = api.image.upload_paths(dataset.id, images_names_batch, img_pathes_batch)
        img_ids = [im_info.id for im_info in img_infos]

        anns = [create_ann(image_path) for image_path in img_pathes_batch]
        api.annotation.upload_anns(img_ids, anns)

        progress.iters_done_report(len(images_names_batch))
    return project
