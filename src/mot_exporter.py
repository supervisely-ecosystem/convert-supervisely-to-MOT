import os
import cv2
import shutil
import globals as g
from glob import glob
import supervisely_lib as sly
from supervisely_lib.io.fs import mkdir, get_file_name
from supervisely_lib.geometry.rectangle import Rectangle


def sort_mot():
    path_to_meta = os.path.join(g.sly_base_dir, "meta.json")
    path_to_key_id_map = os.path.join(g.sly_base_dir, "key_id_map.json")

    meta_json = sly.json.load_json_file(path_to_meta)
    meta = sly.ProjectMeta.from_json(meta_json)

    temp_dir = os.path.join(g.storage_dir, "temp_dir")
    temp_proj_dir = temp_dir
    # temp_proj_dir = os.path.join(temp_dir, g.project_name)
    temp_train_dir = os.path.join(temp_proj_dir, "train")
    temp_test_dir = os.path.join(temp_proj_dir, "test")
    temp_train_ann_dir = os.path.join(temp_train_dir, "ann")
    temp_test_ann_dir = os.path.join(temp_test_dir, "ann")
    temp_train_vid_dir = os.path.join(temp_train_dir, "video")
    temp_test_vid_dir = os.path.join(temp_test_dir, "video")

    sly.fs.mkdir(temp_dir, remove_content_if_exists=True)
    sly.fs.mkdir(temp_proj_dir)
    sly.fs.mkdir(temp_train_dir)
    sly.fs.mkdir(temp_test_dir)

    sly.fs.mkdir(temp_train_ann_dir)
    sly.fs.mkdir(temp_test_ann_dir)
    sly.fs.mkdir(temp_train_vid_dir)
    sly.fs.mkdir(temp_test_vid_dir)

    datasets = [ds for ds in os.listdir(g.sly_base_dir) if os.path.isdir(os.path.join(g.sly_base_dir, ds))]
    for ds in datasets:
        ds_dir = os.path.join(temp_proj_dir, ds)
        mkdir(ds_dir)


        ann_dir = os.path.join(g.sly_base_dir, ds, "ann")
        ann_paths = [os.path.join(ann_dir, ann_path) for ann_path in os.listdir(ann_dir) if
                     os.path.isfile(os.path.join(ann_dir, ann_path))]

        vid_dir = os.path.join(g.sly_base_dir, ds, "video")
        vid_paths = [os.path.join(vid_dir, vid_path) for vid_path in os.listdir(vid_dir) if
                     os.path.isfile(os.path.join(vid_dir, vid_path))]


        for ann_path, vid_path in zip(sorted(ann_paths), sorted(vid_paths)):
            ann_json = sly.json.load_json_file(ann_path)
            ann = sly.VideoAnnotation.from_json(ann_json, meta)
            if len(ann.figures) > 0:
                shutil.copy(ann_path, os.path.join(temp_train_ann_dir, os.path.basename(os.path.normpath(ann_path))))
                shutil.copy(vid_path, os.path.join(temp_train_vid_dir, os.path.basename(os.path.normpath(vid_path))))
            if len(ann.figures) == 0:
                shutil.copy(ann_path, os.path.join(temp_test_ann_dir, os.path.basename(os.path.normpath(ann_path))))
                shutil.copy(vid_path, os.path.join(temp_test_vid_dir, os.path.basename(os.path.normpath(vid_path))))


    shutil.copy(path_to_meta, os.path.join(temp_proj_dir, "meta.json"))
    shutil.copy(path_to_key_id_map, os.path.join(temp_proj_dir, "key_id_map.json"))

    sly.fs.remove_dir(g.sly_base_dir)
    os.rename(temp_dir, g.sly_base_dir)


def convert_project(dest_dir, result_dir, app_logger):
    sort_mot()
    datasets_paths = glob(dest_dir + "/*/")
    if len(datasets_paths) == 0:
        g.logger.warn('There are no datasets in project')

    meta_json = sly.json.load_json_file(os.path.join(dest_dir, 'meta.json'))
    meta = sly.ProjectMeta.from_json(meta_json)

    for ds_path in datasets_paths:
        ds_name = ds_path.split('/')[-2]
        anns_paths = glob(ds_path + "ann" + "/*")
        progress = sly.Progress('Processing Video', len(anns_paths), app_logger)
        for ann_path in anns_paths:
            ann_json = sly.json.load_json_file(ann_path)
            ann = sly.VideoAnnotation.from_json(ann_json, meta)
            video_name = sly.io.fs.get_file_name(ann_path)
            video_path = os.path.join(ds_path, "video", video_name)
            video_info = sly.video.get_info(video_path)['streams'][0]

            curr_objs_geometry_types = [obj.obj_class.geometry_type for obj in ann.objects]

            if not g.DOWNLOAD_ALL_SHAPES and Rectangle not in curr_objs_geometry_types:
                g.logger.warn('Video {} does not contain figures with shape Rectangle'.format(video_name))
                continue

            result_images = os.path.join(result_dir, ds_name, get_file_name(video_name), g.images_dir_name)
            if ds_name == "train":
                result_anns = os.path.join(result_dir, ds_name, get_file_name(video_name), g.ann_dir_name)
            seq_path = os.path.join(result_dir, ds_name, get_file_name(video_name), g.seq_name)

            mkdir(result_images)
            mkdir(result_anns)

            with open(seq_path, 'a') as f:
                f.write('[Sequence]\n')
                f.write('name={}\n'.format(get_file_name(video_name)))
                f.write('imDir={}\n'.format(g.images_dir_name))
                f.write('frameRate={}\n'.format(round(1 / video_info['framesToTimecodes'][1])))
                f.write('seqLength={}\n'.format(video_info['framesCount']))
                f.write('imWidth={}\n'.format(video_info['width']))
                f.write('imHeight={}\n'.format(video_info['height']))
                f.write('imExt={}\n'.format(g.image_ext))

            id_to_video_obj = {}
            for idx, curr_video_obj in enumerate(ann.objects):
                id_to_video_obj[curr_video_obj] = idx + 1

            for frame_index, frame in enumerate(ann.frames):
                for figure in frame.figures:
                    if not g.DOWNLOAD_ALL_SHAPES and figure.video_object.obj_class.geometry_type != Rectangle:
                        continue

                    rectangle_geom = figure.geometry.to_bbox()
                    left = rectangle_geom.left
                    top = rectangle_geom.top
                    width = rectangle_geom.width
                    height = rectangle_geom.height
                    conf_val = 1
                    for curr_tag in figure.video_object.tags:
                        if g.conf_tag_name == curr_tag.name and (
                                curr_tag.frame_range is None or frame_index in range(curr_tag.frame_range[0],
                                                                                     curr_tag.frame_range[1] + 1)):
                            conf_val = 0
                    curr_gt_data = '{},{},{},{},{},{},{},{},{},{}\n'.format(frame_index + 1,
                                                                            id_to_video_obj[figure.video_object],
                                                                            left, top, width - 1, height - 1,
                                                                            conf_val, -1, -1, -1)
                    filename = 'gt_{}.txt'.format(figure.parent_object.obj_class.name)
                    with open(os.path.join(result_anns, filename), 'a') as f:  # gt_path
                        f.write(curr_gt_data)
                if frame_index == ann.frames_count:
                    break

            vidcap = cv2.VideoCapture(video_path)
            success, image = vidcap.read()
            count = 1
            while success:
                image_name = str(count).zfill(6) + g.image_ext
                image_path = os.path.join(result_images, image_name)
                cv2.imwrite(image_path, image)
                success, image = vidcap.read()
                count += 1

            progress.iter_done_report()
    os.rename(g.mot_base_dir, os.path.join(g.storage_dir, g.project_name))
    sly.fs.remove_dir(g.sly_base_dir)
