<div align="center" markdown>

<img src="https://i.imgur.com/EWqvYLb.png"  width="1500px"/>


# Import MOTChallenge


<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#Preparation">Preparation</a> •
  <a href="#How-To-Run">How To Run</a> •
  <a href="#How-To-Use">How To Use</a>
</p>
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/export-to-cityscapes)
[![views](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/convert-supervisely-to-MOT(https://github.com/supervisely-ecosystem/convert-supervisely-to-MOT)&counter=views&label=views)](https://supervise.ly)
[![used by teams](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/convert-supervisely-to-MOT&counter=downloads&label=used%20by%20teams)](https://supervise.ly)
[![runs](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/convert-supervisely-to-MOT&counter=runs&label=runs&123)](https://supervise.ly)

</div>

## Overview

Converts [Supervisely](https://docs.supervise.ly/data-organization/00_ann_format_navi) format project to [MOTChallenge](https://motchallenge.net/) and prepares downloadable `tar` archive. 

Supervisely project must necessarily contain class with name `pedestrian` with shape `Rectangle`. There are no restrictions for classes with other names and shapes. If project to convert contain None type tag with name `ignore_conf` on video figures, result annotation file will have `conf` value 0 for given figure. It means that this figure will not be considered when evaluating in MOTChallenge framework. More about MOT format and `conf` value you can read [here](https://motchallenge.net/instructions/).

The folder structure of the MOT dataset is as follows:

```
{root}/{dataset_name}/{train}/{video_name}/{gt}_{img1}_{seqinfo.ini}
```

The meaning of the individual elements is:

- `root` the root folder of the MOT dataset.
- `dataset_name` name of dataset in converted project.
- `video_name` name of video in current dataset.
- `gt` folder with CSV text-file (gt.txt), containing one object instance per line. Each line contain 10 values. More about MOT format value you can read  [here](https://motchallenge.net/instructions/).
- `img1` folder with images of which the video consists.
- `seqinfo.ini` file with images and video information.



You can download example of MOT datasets [here](https://motchallenge.net/data/MOT15/).

Current version of application supports only `gt` the file annotations.





## How To Run 
**Step 1**: Add app to your team from [Ecosystem](https://ecosystem.supervise.ly/apps) if it is not there.

**Step 2**: Open context menu of video project -> `Download via App` -> `Convert Supervisely to MOT format` 

<img src="https://i.imgur.com/0muByrl.png" width="900px"/>


## How to use
After running the application, you will be redirected to the Tasks page. Once application processing has finished, your link for downloading will be available. Click on the file name to download it.

<img src="https://i.imgur.com/nwOQO67.png"/>

**Note** You can also find your converted project in `Team Files`->`ApplicationsData`->`Convert Supervisely to MOT`->`TaskID`->`projectName.tar`

<img src="https://i.imgur.com/goY1opv.png"/>