<div align="center" markdown>
<img src="https://i.imgur.com/kfASO2Y.png"/>


# Convert Supervisely to MOTChallenge

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-To-Run">How To Run</a> •
  <a href="#How-To-Use">How To Use</a>
</p>


[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/convert-supervisely-to-MOT)
[![views](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/convert-supervisely-to-MOT&counter=views&label=views)](https://supervise.ly)
[![used by teams](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/convert-supervisely-to-MOT&counter=downloads&label=used%20by%20teams)](https://supervise.ly)
[![runs](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/convert-supervisely-to-MOT&counter=runs&label=runs&123)](https://supervise.ly)

</div>

## Overview

App converts [Supervisely](https://app.supervise.ly) format project to [MOTChallenge](https://motchallenge.net/) and prepares downloadable `tar` archive. 

There is an additional option to export figures of all shapes or only figures with shape `Rectangle`. If project to convert contains `None` type `tag` with name `ignore_conf` on video figures, result annotation will have `conf` value 0 for given figure. It means that this figure will not be considered for MOTChallenge framework evaluation. More about MOT format and `conf` value you can read [here](https://motchallenge.net/instructions/).

Folder structure of the MOT dataset is as follows:

```python
{root}/{dataset_name}/{train}/{video_name}/{gt + img1 + seqinfo.ini}   
```

The meaning of the individual elements is:

- `root` root folder of the MOT dataset.
- `dataset_name` name of dataset in converted project.
- `video_name` name of video in current dataset.
- `gt` folder with CSV text-files (format: `gt_{classname}.txt`), containing one object instance per line. Each line contain 10 values. More about MOT format value you can read  [here](https://motchallenge.net/instructions/).
- `img1` folder with images the video consists of.
- `seqinfo.ini` file with images and video information.

You can download example of MOT datasets [here](https://motchallenge.net/data/MOT15/).

Current version of application supports only `gt` file annotations.



## How To Run 
**Step 1**: Add app to your team from [Ecosystem](https://ecosystem.supervise.ly/apps/convert-supervisely-to-MOT) if it is not there.

**Step 2**: Open context menu of video project -> `Download via App` -> `Convert Supervisely to MOT format` 

<img src="https://i.imgur.com/2U1invp.png" width="800px"/>

**Step 3**: Select project export mode.

<img src="https://i.imgur.com/dZIp3g7.png" width="600px"/>

**Note:** For case `Export all geometry shapes` all object shapes(polygons, bitmaps, etc) other than rectangle will be converted to rectangles.

## How to use

After running the application, you will be redirected to the `Tasks` page. Once application processing has finished, your link for downloading will be available. Click on the `file name` to download it.

<img src="https://i.imgur.com/61Ghukb.png"/>

**Note:** You can also find your converted project in `Team Files`->`Convert Supervisely to MOT`->`<taskId>_<projectId>_<projectName>.tar`

<img src="https://i.imgur.com/aKCI2Iq.png"/>
