import os
import globals as g
import mot_exporter
import supervisely as sly


@g.my_app.callback("from_sly_to_mot")
@sly.timeit
def from_sly_to_mot(api: sly.Api, task_id, context, state, app_logger):
    sly.download_video_project(api, g.PROJECT_ID, g.sly_base_dir, log_progress=True)
    mot_exporter.convert_project(g.sly_base_dir, g.mot_base_dir, app_logger)

    result_dir = os.path.join(g.storage_dir, g.project_name)
    os.rename(g.mot_base_dir, result_dir)
    sly.fs.remove_dir(g.sly_base_dir)

    sly.fs.archive_directory(result_dir, g.result_archive)
    app_logger.info("Result directory is archived")
    remote_archive_path = "/Export to MOT/{}".format(g.archive_name)

    upload_progress = []
    def _print_progress(monitor, upload_progress):
        if len(upload_progress) == 0:
            upload_progress.append(sly.Progress(message="Upload {!r}".format(g.archive_name),
                                                total_cnt=monitor.len,
                                                ext_logger=app_logger,
                                                is_size=True))
        upload_progress[0].set_current_value(monitor.bytes_read)

    file_info = api.file.upload(g.TEAM_ID, g.result_archive, remote_archive_path, lambda m: _print_progress(m, upload_progress))
    app_logger.info("Uploaded to Team-Files: {!r}".format(file_info.storage_path))
    api.task.set_output_archive(task_id, file_info.id, g.archive_name, file_url=file_info.storage_path)

    g.my_app.stop()


def main():
    sly.logger.info("Script arguments", extra={
        "TEAM_ID": g.TEAM_ID,
        "WORKSPACE_ID": g.WORKSPACE_ID,
        "modal.state.slyProjectId": g.PROJECT_ID
    })
    g.my_app.run(initial_events=[{"command": "from_sly_to_mot"}])


if __name__ == '__main__':
    sly.main_wrapper("main", main)
