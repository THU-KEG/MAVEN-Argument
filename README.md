# MAVEN-Argument
Dataset for the paper "MAVEN-ARG: Completing the Puzzle of All-in-One Event Understanding Dataset with Event Argument Annotation". The baseline codes will be updated later.

## Overview
MAVEN-Arg is an advanced event argument extraction dataset, which offers three main advantages:

- A comprehensive schema covering 162 event types and 612 argument roles, all with expert-written definitions and examples.
- A large data scale, containing 98,591 events and 290,613 arguments obtained with laborious human annotation.
- The exhaustive annotation supporting all task variants of EAE, which annotates both entity and non-entity event arguments at the document level. 

## MAVEN-Arg Dataset

### Get the data
The dataset (ver. 1.0) can be obtained from [Tsinghua Cloud](https://cloud.tsinghua.edu.cn/f/7c2ddd979ddc48baa85e/?dl=1) or [Google Drive](https://drive.google.com/file/d/14pIzi18NAVixHoVkVGJ1MWv19bqzSG7A/view?usp=sharing).

Note that the annotations of the test set are kept unpublic to maintain a fair evaluation environment. To get evaluation results on the test set, you need to submit your predictions to CodaLab following our [instructions](https://github.com/THU-KEG/MAVEN-Argument#get-test-results-from-codalab).

### Data Format
Each `.jsonl` file is a subset of `MAVEN-Arg` and each line in the files is a JSON string for a document. For the `train.jsonl` and `valid.jsonl`, the JSON format sample is as below:

```JSON5
{
    "id": "10e205fef03228c5599fd76e06aba973",
    "title": "The Virgin Tour",
    "document": "The Virgin Tour was the debut concert tour by American singer-songwriter Madonna . The tour supported her first two studio albums , `` Madonna '' ( 1983 ) and `` Like a Virgin '' ( 1984 ) . although initially planned for an international audience , the tour was restricted to the united states and canada . Warner Bros. Records decided to send Madonna on tour after `` Like a Virgin '' became a success . After an official announcement on March 15 , 1985 , Madonna and her team began production plans . She wanted the tour to be a reflection of her own self and collaborated with designer Maripol for the costumes . Beastie Boys were signed as the opening act , while record producer Patrick Leonard was the music director . The stage was triangular and included ramps around it , with lighting arrangements hanging about 30 feet above . Four giant screens lined three sides of the stage 's outer perimeter . The set list consisted of songs from `` Madonna '' and `` Like a Virgin '' . Madonna was backed by two dancers as she moved energetically across the stage . The show ended with her in a wedding dress , performing `` Like a Virgin '' and `` Material Girl '' . The tour received a mixed reception from critics , but was a commercial success . As soon as it was announced , tickets were sold everywhere . Macy 's New York department store was flooded with buyers , who bought tour merchandise ranging from shirts and sunglasses to crucifix earrings and fingerless gloves . On its end , the tour was reported to have grossed over $ 5 million ( $ million in dollars ) , with `` Billboard '' Boxscore reporting a gross of $ 3.3 million ( $ million in dollars ) . The tour was recorded and released on VHS and LaserDisc , as `` '' , which received a gold certification by the Recording Industry Association of America ( RIAA ) . With the commencement of the Virgin Tour , a wide-ranging audience\u2014especially young women\u2014thronged to attend , attired in Madonna-inspired clothing . This frenzy regarding Madonna gave rise to a new term called Madonna wannabe\u2014a word that was ultimately officially recognized by the Webster 's Dictionary in May 1991 .",
    "events": [
        {
            "id": "EVENT_1d3c5f5babae4f1e51fd159531a2cda7",
            "type": "Supporting",
            "type_id": 42,
            "mention": [
                {
                    "id": "e82a32824ef335909d01eee543b1c0ef",
                    "trigger_word": "supported",
                    "offset": [
                        92,
                        101
                    ]
                }
            ],
            "argument": {
                "Agent": [
                    {
                        "content": "Virgin Tour",
                        "offset": [
                            4,
                            15
                        ]
                    }
                ],
                "Patient": [
                    {
                        "content": "her first two studio albums",
                        "offset": [
                            102,
                            129
                        ]
                    }
                ],
                "Location": [
                    {
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
    "entities": [
        {
            "id": "ENTITY_14e4c32b17ba928980b81c905d32b2e4",
            "type": "Location",
            "mention": [
                {
                    "id": "183ebc2b63e4715003ca98e53395cc49",
                    "mention": "American",
                    "offset": [
                        46,
                        54
                    ]
                },
                {
                    "id": "af43d31659caebaf31f399d158bbf4f1",
                    "mention": "the united states",
                    "offset": [
                        276,
                        293
                    ]
                }
            ]
        },
    ]
}
```

- For the `test.jsonl`, the format is similar but we hide the ground truth annotations to organize a fair evaluation challenge. To get evaluation results on the test set, you need to submit the prediction results to our [CodaLab competition](https://codalab.lisn.upsaclay.fr/competitions/8691#learn_the_details). 
- To avoid leaking the test set of the MAVEN event detection challenge and the MAVEN-ERE event relation extraction challenge, the candidate event mentions we offered here have more than the golden annotations and no coreference clusters. But we only evaluate your predictions for the golden event mentions.

```JSON5
{
  "id": "f28bce270df5a122c09365002d247e76", // an unique string for each document
  "title": "United States occupation of Nicaragua", // the tiltle of the document
  "tokens": [ // a list for tokenized document content. each item is a tokenized sentence
    ["The", "United", "States", "occupation", "of", "Nicaragua", "from", 
    "1912", "to", "1933", "was", "part", "of", "the", "Banana", "Wars", ",", 
    "when", "the", "US", "military", "intervened", "in", "various", 
    "Latin", "American", "countries", "from", "1898", "to", "1934", "."],
  ],
  "sentences": [ // untokenized sentences of the document. each item is a sentence (string)
      "The United States occupation of Nicaragua from 1912 to 1933 was part of the Banana Wars, when the US military intervened in various Latin American countries from 1898 to 1934.",
  ],
  "event_mentions": [ // a list for event mentions (and distractors), you need to predict the relations between the given mentions
    {
      "id": "a75ba55cadad23555a0ffc9454088687", // an unique string for the event mention
      "trigger_word": "assumed", // a string of the trigger word or phrase
      "sent_id": 3, // the index of the corresponding sentence, starts with 0
      "offset": [1, 2], // the offset of the trigger words in the tokens list
      "type": "Choosing", // the event type
      "type_id": 25, // the numerical id for the event type, consistent with MAVEN
    }
  ],
  "TIMEX": [ // a list for annotated temporal expressions (TIMEX), each item is a dict for a TIMEX
    {
      "id": "TIME_833e41f3304210094101eca59905055e", // an unique string for the TIMEX
      "mention": "1912", // a string of the mention of the TIMEX
      "type": "DATE", // the type of the TIMEX
      "sent_id": 0, // the index of the corresponding sentence, starts with 0
      "offset": [7, 8] // the offset of the trigger words in the tokens list
    }
  ]
}
```

## Get Test Results from CodaLab
To get the test results, you can submit your predictions to our permanent [CodaLab competition](https://codalab.lisn.upsaclay.fr/competitions/8691#learn_the_details).

You need to name your result file as `test_prediction.jsonl` and compress it into a zip format file named `submission.zip` for submission. Each line in the submission file should be a `JSON` string encoding the prediction results for one document. The JSON format is as below:

```JSON5
{
  "id": "f28bce270df5a122c09365002d247e76", // an unique string for each document, mandatory
  "coreference": [ // a list for predicted coreference clusters, each item is a cluster of event mentions having coreference relations with each other
      ["a75ba55cadad23555a0ffc9454088687", "555a0ffc9454a75ba08868755cadad23"] // a list for a predicted cluster, each item is the id of an event mention
  ],
  "temporal_relations": { // a list for predicted temporal relations between event mentions (not events) and TIMEXs
    "BEFORE": [ // a list for predicted temporal relations of BEFORE type
      ["a75ba55cadad23555a0ffc9454088687", "555a0ffc9454a75ba08868755cadad23"] // a temporal relation instance, its items shall be id of event mentions or TIMEXs
    ],
    "OVERLAP": [ // all the following types are similar
      ["a75ba55cadad23555a0ffc9454088687", "TIME_id_1"]
    ],
    "CONTAINS": [
      ["a75ba55cadad23555a0ffc9454088687", "555a0ffc9454a75ba08868755cadad23"]
    ],
    "SIMULTANEOUS": [
      ["a75ba55cadad23555a0ffc9454088687", "555a0ffc9454a75ba08868755cadad23"]
    ],
    "ENDS-ON": [
      ["a75ba55cadad23555a0ffc9454088687", "555a0ffc9454a75ba08868755cadad23"]
    ],
    "BEGINS-ON": [
      ["555a0ffc9454a75ba08868755cadad23", "TIME_id_2"]
    ],
  },
  "causal_relations": { // a list for predicted causal relations between event mentions (not events)
    "CAUSE": [  // a list for causal relations of CAUSE type
      ["a75ba55cadad23555a0ffc9454088687", "555a0ffc9454a75ba08868755cadad23"] // a causal relation instance, its items shall be id of event mentions
    ],
    "PRECONDITION": [ // the PRECONDITION type is similar
      ["a75ba55cadad23555a0ffc9454088687", "555a0ffc9454a75ba08868755cadad23"]
    ],
  },
  "subevent_relations": [ // a list for predicted subevent relations between event mention (not events)
    ["a75ba55cadad23555a0ffc9454088687", "555a0ffc9454a75ba08868755cadad23"] // a subevent relation instance, its items shall be id of event mentions
  ]
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
