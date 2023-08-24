Dataset **QuinceSet** can be downloaded in [Supervisely format](https://developer.supervisely.com/api-references/supervisely-annotation-json-format):

 [Download](https://assets.supervisely.com/supervisely-supervisely-assets-public/teams_storage/C/4/zQ/aBf28i9MOwjg65aeMHAS59PXyS5mQRNoa6oo3p3sxXJpgDaHykcLGxEC4qoi7ByoxO7ILJCtLxpycsbmduRDTI6oMoShD7ITzdotBatZ54DJ7sqWhmZHeREHSEL8.tar)

As an alternative, it can be downloaded with *dataset-tools* package:
``` bash
pip install --upgrade dataset-tools
```

... using following python code:
``` python
import dataset_tools as dtools

dtools.download(dataset='QuinceSet', dst_dir='~/dataset-ninja/')
```
Make sure not to overlook the [python code example](https://developer.supervisely.com/getting-started/python-sdk-tutorials/iterate-over-a-local-project) available on the Supervisely Developer Portal. It will give you a clear idea of how to effortlessly work with the downloaded dataset.

The data in original format can be [downloaded here](https://zenodo.org/record/6402251/files/QuinceSet.zip?download=1).