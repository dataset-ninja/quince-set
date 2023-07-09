Dataset **QuinceSet** can be downloaded in Supervisely format:

 [Download](https://assets.supervisely.com/supervisely-supervisely-assets-public/teams_storage/S/U/aJ/2HfieJcimxxvP3MLfrUpTbxoPEuoLM5C1RU2SfpPs5tc9EttkY2RDqme3Bj9tFJ6fMygh2hMbX4hTDDFcC29BwDdEprwxtYiVWm6Hns2Cga6Fbe4pyvCWXKKOZwB.tar)

As an alternative, it can be downloaded with *dataset-tools* package:
``` bash
pip install --upgrade dataset-tools
```

... using following python code:
``` python
import dataset_tools as dtools

dtools.download(dataset='QuinceSet', dst_path='~/dtools/datasets/QuinceSet.tar')
```
The data in original format can be 🔗[downloaded here](https://zenodo.org/record/6402251/files/QuinceSet.zip?download=1)