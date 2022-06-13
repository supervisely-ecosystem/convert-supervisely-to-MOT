import os
import supervisely as sly
from supervisely.io.fs import mkdir
from supervisely.app.v1.app_service import AppService

my_app = AppService()
api: sly.Api = my_app.public_api

TEAM_ID = int(os.environ['context.teamId'])
WORKSPACE_ID = int(os.environ['context.workspaceId'])
PROJECT_ID = int(os.environ['modal.state.slyProjectId'])
TASK_ID = int(os.environ["TASK_ID"])

images_dir_name = 'img1'
ann_dir_name = 'gt'
image_ext = '.jpg'
seq_name = 'seqinfo.ini'
conf_tag_name = 'ignore_conf'
logger = sly.logger

project = api.project.get_info_by_id(PROJECT_ID)
project_name = project.name
archive_name = f'{TASK_ID}_{PROJECT_ID}_{project_name}.tar.gz'
result_archive = os.path.join(my_app.data_dir, archive_name)

storage_dir = os.path.join(my_app.data_dir, "mot_exporter")
mot_base_dir = os.path.join(storage_dir, "mot_base_dir")
sly_base_dir = os.path.join(storage_dir, "supervisely")

mkdir(storage_dir, remove_content_if_exists=True)
mkdir(sly_base_dir)
mkdir(mot_base_dir)
