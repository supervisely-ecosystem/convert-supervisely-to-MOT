import os
import cv2
import globals as g
from glob import glob
import supervisely_lib as sly
from supervisely_lib.io.fs import mkdir, get_file_name
from supervisely_lib.geometry.rectangle import Rectangle


def convert_project(dest_dir, result_dir, app_logger):
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

            if len(ann.figures) > 0:
                result_images = os.path.join(result_dir, ds_name, "train", get_file_name(video_name), g.images_dir_name)
                result_anns = os.path.join(result_dir, ds_name, "train", get_file_name(video_name), g.ann_dir_name)
                seq_path = os.path.join(result_dir, ds_name, "train", get_file_name(video_name), g.seq_name)
                mkdir(result_images)
                mkdir(result_anns)
            if len(ann.figures) == 0:
                result_images = os.path.join(result_dir, ds_name, "test", get_file_name(video_name), g.images_dir_name)
                seq_path = os.path.join(result_dir, ds_name, "test", get_file_name(video_name), g.seq_name)
                mkdir(result_images)

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
