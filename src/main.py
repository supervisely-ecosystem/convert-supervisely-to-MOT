import os
import supervisely_lib as sly
from supervisely_lib.io.fs import mkdir, get_file_name
from supervisely_lib.video_annotation.key_id_map import KeyIdMap
from supervisely_lib.geometry.rectangle import Rectangle
from distutils import util

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
frame_rate = 25
conf_tag_name = 'ignore_conf'
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

    RESULT_ARCHIVE = os.path.join(my_app.data_dir, ARCHIVE_NAME)
    RESULT_DIR = os.path.join(my_app.data_dir, RESULT_DIR_NAME)
    key_id_map = KeyIdMap()
    for dataset in api.dataset.get_list(PROJECT_ID):
        videos = api.video.get_list(dataset.id)
        for batch in sly.batched(videos, batch_size=10):
            for video_info in batch:

                ann_info = api.video.annotation.download(video_info.id)
                ann = sly.VideoAnnotation.from_json(ann_info, meta, key_id_map)
                curr_objs_geometry_types = [obj.obj_class.geometry_type for obj in ann.objects]

                if not DOWNLOAD_ALL_SHAPES and Rectangle not in curr_objs_geometry_types:
                    logger.warn('Video {} not contain firuges with shape Rectangle'.format(video_info.name))
                    continue

                result_images = os.path.join(RESULT_DIR, dataset.name, dir_train, get_file_name(video_info.name),
                                             images_dir_name)
                result_anns = os.path.join(RESULT_DIR, dataset.name, dir_train, get_file_name(video_info.name),
                                           ann_dir_name)
                seq_path = os.path.join(RESULT_DIR, dataset.name, dir_train, get_file_name(video_info.name), seq_name)

                # gt_path = os.path.join(result_anns, gt_name)
                progress = sly.Progress('Video being processed', len(batch), app_logger)
                mkdir(result_images)
                mkdir(result_anns)

                with open(seq_path, 'a') as f:
                    f.write('[Sequence]\n')
                    f.write('name={}\n'.format(get_file_name(video_info.name)))
                    f.write('imDir={}\n'.format(images_dir_name))
                    f.write('frameRate={}\n'.format(frame_rate))
                    f.write('seqLength={}\n'.format(video_info.frames_count))
                    f.write('imWidth={}\n'.format(video_info.frame_width))
                    f.write('imHeight={}\n'.format(video_info.frame_height))
                    f.write('imExt={}\n'.format(image_ext))

                id_to_video_obj = {}
                for idx, curr_video_obj in enumerate(ann.objects):
                    id_to_video_obj[curr_video_obj] = idx + 1
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
                    if frame_index > ann.frames_count:
                        break
                    api.video.frame.download_path(video_info.id, frame_index, image_path)
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
