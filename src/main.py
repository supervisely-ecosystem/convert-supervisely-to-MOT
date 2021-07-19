import os
import supervisely_lib as sly
from supervisely_lib.io.fs import mkdir, get_file_name
from supervisely_lib.geometry.rectangle import Rectangle
from distutils import util
from glob import glob
import cv2

my_app = sly.AppService()

TEAM_ID = int(os.environ['context.teamId'])
WORKSPACE_ID = int(os.environ['context.workspaceId'])
PROJECT_ID = int(os.environ['modal.state.slyProjectId'])
TASK_ID = int(os.environ["TASK_ID"])

RESULT_DIR_NAME = 'Convert Supervisely to MOT'
images_dir_name = 'img1'
ann_dir_name = 'gt'
dir_train = 'train'
image_ext = '.jpg'
# gt_name = 'gt.txt'
seq_name = 'seqinfo.ini'
# frame_rate = 25
conf_tag_name = 'ignore_conf'
working_folder = 'working_folder'
logger = sly.logger

try:
    os.environ['modal.state.shapes']
except KeyError:
    logger.warn('The option to export project is not selected, project will be export with all shapes')
    DOWNLOAD_ALL_SHAPES = True
else:
    DOWNLOAD_ALL_SHAPES = bool(util.strtobool(os.environ['modal.state.shapes']))


@my_app.callback("from_sl_to_MOT")
@sly.timeit
def from_sl_to_MOT(api: sly.Api, task_id, context, state, app_logger):

    project = api.project.get_info_by_id(PROJECT_ID)
    if project is None:
        raise RuntimeError("Project with ID {!r} not found".format(PROJECT_ID))
    if project.type != str(sly.ProjectType.VIDEOS):
        raise TypeError("Project type is {!r}, but have to be {!r}".format(project.type, sly.ProjectType.VIDEOS))

    project_name = project.name
    ARCHIVE_NAME = '{}_{}_{}.tar.gz'.format(TASK_ID, PROJECT_ID, project_name)
    meta_json = api.project.get_meta(PROJECT_ID)
    meta = sly.ProjectMeta.from_json(meta_json)

    dest_dir = os.path.join(my_app.data_dir, working_folder)
    sly.download_video_project(api, PROJECT_ID, dest_dir, log_progress=True)

    RESULT_ARCHIVE = os.path.join(my_app.data_dir, ARCHIVE_NAME)
    RESULT_DIR = os.path.join(my_app.data_dir, RESULT_DIR_NAME)
    datasets_pathes = glob(dest_dir + "/*/")
    for ds_path in datasets_pathes:
        ds_name = ds_path.split('/')[-2]
        anns_pathes = glob(ds_path + "ann" + "/*")
        for ann_path in anns_pathes:
            ann_json = sly.io.json.load_json_file(ann_path)
            ann = sly.VideoAnnotation.from_json(ann_json, meta)
            video_name = sly.io.fs.get_file_name(ann_path)
            video_path = os.path.join(ds_path, "video", video_name)
            video_info = sly.video.get_info(video_path)['streams'][0]

            curr_objs_geometry_types = [obj.obj_class.geometry_type for obj in ann.objects]

            if not DOWNLOAD_ALL_SHAPES and Rectangle not in curr_objs_geometry_types:
                logger.warn('Video {} not contain firuges with shape Rectangle'.format(video_name))
                continue

            result_images = os.path.join(RESULT_DIR, ds_name, dir_train, get_file_name(video_name),
                                         images_dir_name)
            result_anns = os.path.join(RESULT_DIR, ds_name, dir_train, get_file_name(video_name),
                                       ann_dir_name)
            seq_path = os.path.join(RESULT_DIR, ds_name, dir_train, get_file_name(video_name), seq_name)

            # gt_path = os.path.join(result_anns, gt_name)
            progress = sly.Progress('Video being processed', len(anns_pathes), app_logger)
            mkdir(result_images)
            mkdir(result_anns)

            with open(seq_path, 'a') as f:
                f.write('[Sequence]\n')
                f.write('name={}\n'.format(get_file_name(video_name)))
                f.write('imDir={}\n'.format(images_dir_name))
                f.write('frameRate={}\n'.format(round(1 / video_info['framesToTimecodes'][1])))
                f.write('seqLength={}\n'.format(video_info['framesCount']))
                f.write('imWidth={}\n'.format(video_info['width']))
                f.write('imHeight={}\n'.format(video_info['height']))
                f.write('imExt={}\n'.format(image_ext))

            id_to_video_obj = {}
            for idx, curr_video_obj in enumerate(ann.objects):
                id_to_video_obj[curr_video_obj] = idx + 1

            image_pathes = []
            for frame_index, frame in enumerate(ann.frames):
                for figure in frame.figures:
                    if not DOWNLOAD_ALL_SHAPES and figure.video_object.obj_class.geometry_type != Rectangle:
                        continue

                    rectangle_geom =  figure.geometry.to_bbox()
                    left = rectangle_geom.left
                    top = rectangle_geom.top
                    width = rectangle_geom.width
                    height = rectangle_geom.height
                    conf_val = 1
                    for curr_tag in figure.video_object.tags:
                        if conf_tag_name == curr_tag.name and (
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
                image_name = str(frame_index + 1).zfill(6) + image_ext
                image_path = os.path.join(result_images, image_name)
                image_pathes.append(image_path)
                if frame_index == ann.frames_count:
                    break

            vidcap = cv2.VideoCapture(video_path)
            success, image = vidcap.read()
            count = 0
            while success:
                curr_image_path = image_pathes[count]
                cv2.imwrite(curr_image_path, image)
                success, image = vidcap.read()
                count += 1
                if count == len(image_pathes):
                    break

            progress.iter_done_report()

    sly.fs.archive_directory(RESULT_DIR, RESULT_ARCHIVE)
    app_logger.info("Result directory is archived")

    upload_progress = []
    remote_archive_path = "/{}/{}".format(RESULT_DIR_NAME, ARCHIVE_NAME)

    def _print_progress(monitor, upload_progress):
        if len(upload_progress) == 0:
            upload_progress.append(sly.Progress(message="Upload {!r}".format(ARCHIVE_NAME),
                                                total_cnt=monitor.len,
                                                ext_logger=app_logger,
                                                is_size=True))
        upload_progress[0].set_current_value(monitor.bytes_read)

    file_info = api.file.upload(TEAM_ID, RESULT_ARCHIVE, remote_archive_path, lambda m: _print_progress(m, upload_progress))
    app_logger.info("Uploaded to Team-Files: {!r}".format(file_info.full_storage_url))
    api.task.set_output_archive(task_id, file_info.id, ARCHIVE_NAME, file_url=file_info.full_storage_url)

    my_app.stop()


def main():
    sly.logger.info("Script arguments", extra={
        "TEAM_ID": TEAM_ID,
        "WORKSPACE_ID": WORKSPACE_ID,
        "modal.state.slyProjectId": PROJECT_ID
    })
    my_app.run(initial_events=[{"command": "from_sl_to_MOT"}])


if __name__ == '__main__':
    sly.main_wrapper("main", main)
