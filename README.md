# MAVEN-Argument
Dataset for the paper "MAVEN-ARG: Completing the Puzzle of All-in-One Event Understanding Dataset with Event Argument Annotation". The baseline codes will be updated later.

## Overview
MAVEN-Arg is an advanced event argument extraction dataset, which offers three main advantages:

- A comprehensive schema covering 162 event types and 612 argument roles, all with expert-written definitions and examples.
- A large data scale, containing 98,591 events and 290,613 arguments obtained with laborious human annotation.
- The exhaustive annotation supporting all task variants of EAE, which annotates both entity and non-entity event arguments at the document level. 

## MAVEN-Arg Dataset

### Get the data
The dataset (ver. 1.0) can be obtained from [Tsinghua Cloud](https://cloud.tsinghua.edu.cn/f/7c2ddd979ddc48baa85e/?dl=1) or [Google Drive](https://drive.google.com/file/d/1EwQOboosygwrQxzmop320b5eYgATG9kk/view?usp=sharing).

Note that the annotations of the test set are kept unpublic to maintain a fair evaluation environment. To get evaluation results on the test set, you need to submit your predictions to CodaLab following our [instructions](https://github.com/THU-KEG/MAVEN-Argument#get-test-results-from-codalab).

### Data Format
Each `.jsonl` file is a subset of `MAVEN-Arg` and each line in the files is a JSON string for a document. For the `train.jsonl` and `valid.jsonl`, the JSON format sample is as below:

```JSON5
{
    "id": "10e205fef03228c5599fd76e06aba973", // an unique string for each document
    "title": "The Virgin Tour", // the title of the document
    "document": "The Virgin Tour was the debut concert tour by American singer-songwriter Madonna ...", // a string, the content of the document
    "events": [ // a list for annotated events, each item is a dict for an event
        {
            "id": "EVENT_1d3c5f5babae4f1e51fd159531a2cda7", // a unique string id for the event
            "type": "Supporting", // the event type
            "type_id": 42, // the numerical id for the event type, consistent with MAVEN
            "mention": [ // a list for the coreferential event triggers of the event, each item is a dict
                {
                    "id": "e82a32824ef335909d01eee543b1c0ef", // an unique string for the event trigger
                    "trigger_word": "supported", // a string of the trigger word or phrase
                    "offset": [ 92, 101 ] // the char offset of the trigger words in the document string
                }
            ],
            "argument": { // the annotated event arguments of the event, a dict
                "Agent": [ // every key is an argument role corresponding to the event type. Its value is a list for all the event arguments of the argument role
                    { // for non-entity arguments, a dict consisting of its content and char offsets in the document string
                        "content": "Virgin Tour", 
                        "offset": [ 4, 15 ]
                    }
                ],
                "Patient": [
                    {
                        "content": "her first two studio albums",
                        "offset": [ 102, 129 ]
                    }
                ],
                "Location": [
                    { // for entity arguments, a dict only contains its entity id
                        "entity_id": "ENTITY_c540c651ba640ff340a3f066301fb57e" 
                    },
                    {
                        "entity_id": "ENTITY_14e4c32b17ba928980b81c905d32b2e4"
                    }
                ],
                "Content": []
            }
        }
    ]
    "entities": [ // a list of the annotated entities of the document, each item is a dict for an entity
        {
            "id": "ENTITY_14e4c32b17ba928980b81c905d32b2e4", // the unique id string for every entity
            "type": "Location", // the entity type
            "mention": [ // a list of all the coreferential entity mentions, each item is a dict for a mention 
                {
                    "id": "183ebc2b63e4715003ca98e53395cc49", // the unique id string for every entity mention
                    "mention": "American", // its content
                    "offset": [ 46, 54 ] // the char offset of the entity mention in the document string 
                },
                {
                    "id": "af43d31659caebaf31f399d158bbf4f1",
                    "mention": "the united states",
                    "offset": [ 276, 293 ]
                }
            ]
        },
    ]
    "negative_triggers": [ // a list for negative instances, each item is a dict for a negative event trigger. used for conducting pipeline evaluation (evaluating event argument extraction considering the errors of event detection).
        {
            "id": "d48f41c5b3a3729dfdcf23e6dfa7734c",
            "trigger_word": "consisted",
            "offset": [
                922,
                931
            ]
        },
        {
            "id": "1fa31015582b2a068aead5928445aeed",
            "trigger_word": "ranging",
            "offset": [
                1399,
                1406
            ]
        }
    ]
}
```

- For the `test.jsonl`, the format is similar but we hide the ground truth annotations to organize a fair evaluation challenge. To get evaluation results on the test set, you need to submit the prediction results to our [CodaLab competition](https://codalab.lisn.upsaclay.fr/competitions/17225). 
- To avoid leaking the test set of the MAVEN-ERE event relation extraction challenge, the candidate event mentions we offered here have no coreference clusters.
```JSON5
{
    "id": "e3e04de8ce0fba75eb678ef5af6c015d", // an unique string for each document
    "title": "Lufthansa Flight 615", // the title of the document
    "document": "The hijacking of Lufthansa Flight 615 was an act of terrorism committed ...", // a string, the content of the document
    "event_mentions": [ // a list for event mentions/triggers, you need to predict the arguments for the given triggers
        {
            "id": "6bb914d51ee13d35b3136286c8759911", // an unique string for the event trigger
            "trigger_word": "massacre", // a string of the trigger word or phrase
            "type": "Killing", // the event type 
            "type_id": 20, // the numerical id for the event type, consistent with MAVEN
            "offset": [ 206, 214 ] // the char offset of the trigger words in the document string
        },
        {
            "id": "d41814e7e00a17bddd4666ea444a4524",
            "trigger_word": "defend",
            "type": "Defending",
            "type_id": 43,
            "offset": [ 1835, 1841 ]
        }
    ],
    "entities": [ // a list of the annotated entities of the document, each item is a dict for an entity
        {
            "id": "ENTITY_b48a2f49a11da300b2801c66d7e2599c", // the unique id string for every entity
            "type": "Product", // the entity type
            "mention": [ // a list of all the coreferential entity mentions, each item is a dict for a mention 
                {
                    "id": "ff02f2ecb4d26c755123f69fae61c3d2", // the unique id string for every entity mention
                    "mention": "Lufthansa Flight 615", // its content
                    "offset": [ 17, 37 ] // the char offset of the entity mention in the document string 
                }
            ]
        },
        {
            "id": "ENTITY_d8b7df846d7898edecceb37eb0e27d3c",
            "type": "Other",
            "mention": [
                {
                    "id": "ac9c0a2ff3988414a7af5271da64055d",
                    "mention": "eleven",
                    "offset": [ 1274, 1280 ]
                }
            ]
        }
    ]
    "negative_triggers": [ // a list for negative instances, each item is a dict for a negative event trigger. used for conducting pipeline evaluation (evaluating event argument extraction considering the errors of event detection).
        {
            "id": "7e01f352a6a80b709fe4ab9b9396e460",
            "trigger_word": "act",
            "offset": [
                45,
                48
            ]
        },
        {
            "id": "185fd3c2b02c39ec0c678abf35607d61",
            "trigger_word": "acts",
            "offset": [
                2619,
                2623
            ]
        }
    ]
}
```

## Get Test Results from CodaLab
To get the test results, you can submit your predictions to our permanent [CodaLab competition](https://codalab.lisn.upsaclay.fr/competitions/17225).

You need to name your result file as `test_prediction.jsonl` and compress it into a zip format file named `submission.zip` for submission. Each line in the submission file should be a `JSON` string encoding the prediction results for one document. The JSON format is as below:

```JSON5
{
    "id": "097b52eff5925669079ad5c227b95425", // an unique string for each document
    "preds": {  // a dict of the submitted predictions, every key is an id for an event mention
        "c0834cd8f9e43caae8aa1865713cad9c": { // id of the event mention (or possibly negative trigger if you are using predicted event triggers)
            "event_type": "Catastrophe",  // its event type, you can use our provided event type (the gold trigger evaluation setup) or use your own predicted event type (the pipeline evaluation setup)
            "Location": [ //the other keys are argument roles, its value is the predicted arguments of the role
                "Hemel Hempstead" //the content string of the predicted arguments 
            ]
        },
        "a5c4a56d93d4bcd7bfbef9607f97d3a7": {
            "event_type": "Destroying",
            "Location": [
                "Hemel Hempstead",
                "tank 912"
            ],
            "Agent": [
                "further explosions"
            ],
            "Patient": [
                "20 large storage tanks"
            ]
        },
    }
}
```

For the detailed implementations of our evaluations, please refer to the [evaluation script](evaluate.py).

## Citation
```bibtex
@article{wang2023mavenarg,
  title={MAVEN-Arg: Completing the Puzzle of All-in-One Event Understanding Dataset with Event Argument Annotation},
  author={Wang, Xiaozhi and Peng, Hao and Guan, Yong and Zeng, Kaisheng and Chen, Jianhui and Hou, Lei and Han, Xu and Lin, Yankai and Liu, Zhiyuan and Xie, Ruobing and Zhou, Jie and Li, Juanzi},
  journal={arXiv preprint arXiv:2311.09105},
  year={2023}
}
```
