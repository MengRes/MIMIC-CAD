# MIMIC-CAD

MIMIC-CAD (Comprehensive Annotation of Diseases) is a dataset based on the MIMIC-CXR dataset. MIMIC-CAD provides lung disease details extracted from radiology reports in the MIMIC-CXR dataset. The previous disease labels only marked the existence of the disease and did not provide more disease information, such as the disease severity, disease uncertainty, disease location, etc., which are all important disease information in clinical diagnosis. Traditional disease classifications do not apply to clinical practice. Our goal is to make full use of the information in medical reports to build a dataset of comprehensive annotation of diseases. 


## Data Description

MIMIC-CAD v1.0 contains a file record of all disease comprehensive annotations. For a patient taking a CXR image one time, the annotation structure is as follows:

```
{
	"study_id": "58729526",
	"subject_id": "18936629",
	"dicom_id": "58c1653b-5d091bf0-ce12c7b3-7f6c738d-cd6f4e1b",
	"view": "postero-anterior",
	"entity": {
		"pneumothorax": {
			"id": 0,
			"entity_name": "pneumothorax",
			"report_name": "pneumothorax",
			"location": null,
			"type": null,
			"level": null,
			"infer": [],
			"derived_from": [],
			"probability": "no ",
			"probability_score": -3
		},
		"lung opacity": {
			"id": 1,
			"entity_name": "lung opacity",
			"report_name": "opacity",
			"location": null,
			"type": null,
			"level": null,
			"infer": [],
			"derived_from": [],
			"probability": "positive",
			"probability_score": 3
		},
		"consolidation": {
			"id": 2,
			"entity_name": "consolidation",
			"report_name": "consolidation",
			"location": null,
			"type": null,
			"level": null,
			"post_location": null,
			"location2": null,
			"type2": null,
			"level2": null,
			"post_location2": null,
			"infer": [],
			"derived_from": [],
			"probability": "positive",
			"probability_score": 3
		},
		"pleural effusion": {
			"id": 3,
			"entity_name": "pleural effusion",
			"report_name": "pleural effusion",
			"location": [
				"left"
			],
			"type": null,
			"level": [
				"small"
			],
			"post_location": null,
			"location2": null,
			"type2": null,
			"level2": null,
			"post_location2": null,
			"infer": [],
			"derived_from": [],
			"probability": "positive",
			"probability_score": 3
		},
		"pleural thickening": {
			"id": 4,
			"entity_name": "pleural thickening",
			"report_name": "pleural thickening",
			"location": [
				"left"
			],
			"type": null,
			"level": null,
			"post_location": null,
			"location2": null,
			"type2": null,
			"level2": null,
			"post_location2": null,
			"infer": [],
			"derived_from": [],
			"probability": "positive",
			"probability_score": 3
		}
	}
},
```



+   `study_id`: An integer unique for an individual study (i.e. an individual radiology report with one or more.
+   `subject_id`: An integer unique for an individual patient.
+   `dicom_id`: An identifier for the `DICOM` file. The stem of each `JPG` image filename is equal to the `dicom_id.``
+   ``view`: The orientation in which the chest radiograph was taken ("AP", "PA", "LATERAL", etc).
+   `entity`: The comprehensive annotation of diseases we extracted from the radiologist report.

The `entity` dictionary includes disease annotations, each kind of disease name is the key and the annotation is the value. 

+   `entity_name`: disease name 
+   `report_name`: disease name extracted from radiologist report
+   `location`: disease location extracted from radiologist report
+   `level`: words extracted from radiologist report report to describe disease severity
+   `probability`: words extracted from radiologists to describe disease uncertainty

The disease information extraction code can be found in the "disease_info_extract.py" file. The diseases' probability info extraction module hasn't been uploaded. The libs folder contains disease and other dictionaries, you can adjust the dictionary yourself. The dictionary may not be comprehensive enough to cover all kinds of scenarios.
To extract the disease info from the reports, you can give the report_path to the function get_disease_json.
The Jupyter Notebook records how to extract info from the .json file. It gives an example to extract disease name, severity, and other info.
