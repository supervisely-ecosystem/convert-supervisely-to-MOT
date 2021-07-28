<div align="center" markdown>
<img src="https://i.imgur.com/wDdLM8H.png"/>


# Export to MOT

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-To-Run">How To Run</a> •
  <a href="#How-To-Use">How To Use</a>
</p>

[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervise.ly/apps/supervisely-ecosystem/export-to-mot-format)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/export-to-mot-format)
[![views](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/export-to-mot-format&counter=views&label=views)](https://supervise.ly)
[![used by teams](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/export-to-mot-format&counter=downloads&label=used%20by%20teams)](https://supervise.ly)
[![runs](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/export-to-mot-format&counter=runs&label=runs&123)](https://supervise.ly)

</div>

## Overview

App converts [Supervisely](https://docs.supervise.ly/data-organization/00_ann_format_navi) format project to [MOTChallenge](https://motchallenge.net/) and prepares downloadable `tar` archive. 
In the modal video you have the option to export figures of all shapes or only figures with shape `Rectangle`. If project that you want to convert contains `None` type `tag` with name `ignore_conf` on video figures, result annotation will have `conf` value 0 for given figure. It means that this figure will not be considered for MOTChallenge framework evaluation. More about MOT format and `conf` value you can read [here](https://motchallenge.net/instructions/). All objects on video must have only one figure per frame. Backward compatible with [`Export to MOT`](https://github.com/supervisely-ecosystem/export-to-mot-format) app.

Current version of application supports only `gt` file annotations.

## How To Run 
**Step 1**: Add app to your team from [Ecosystem](https://ecosystem.supervise.ly/apps/export-to-mot-format) if it is not there.

**Step 2**: Open context menu of video project -> `Download via App` -> `Convert Supervisely to MOT format` 

<img src="https://i.imgur.com/nk80QLx.png" width="800px"/>

**Step 3**: Select project export mode.

<img src="https://i.imgur.com/HN3gFAv.png" width="600px"/>

**Note:** For case `Export all geometry shapes` all object shapes(polygons, bitmaps, etc) other than rectangle will be converted to rectangles.

## How to use

After running the application, you will be redirected to the `Tasks` page. Once application processing has finished, your link for downloading will be available. Click on the `file name` to download it.

<img src="https://i.imgur.com/4oE9sxi.png"/>

**Note:** You can also find your converted project in `Team Files`->`Convert Supervisely to MOT`->`<taskId>_<projectId>_<projectName>.tar.gz`

<img src="https://i.imgur.com/3pDolxh.png"/>
