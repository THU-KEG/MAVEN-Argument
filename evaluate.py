#!/usr/bin/env python

# Scoring program for the AutoML challenge
# Isabelle Guyon and Arthur Pesah, ChaLearn, August 2014-November 2016

# ALL INFORMATION, SOFTWARE, DOCUMENTATION, AND DATA ARE PROVIDED "AS-IS".
# ISABELLE GUYON, CHALEARN, AND/OR OTHER ORGANIZERS OR CODE AUTHORS DISCLAIM
# ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR ANY PARTICULAR PURPOSE, AND THE
# WARRANTY OF NON-INFRINGEMENT OF ANY THIRD PARTY'S INTELLECTUAL PROPERTY RIGHTS.
# IN NO EVENT SHALL ISABELLE GUYON AND/OR OTHER ORGANIZERS BE LIABLE FOR ANY SPECIAL,
# INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF SOFTWARE, DOCUMENTS, MATERIALS,
# PUBLICATIONS, OR INFORMATION MADE AVAILABLE FOR THE CHALLENGE.

# Some libraries and options
import os
from sys import argv
import json
import yaml
import re
import copy
import json
import string
import numpy as np
from collections import Counter, defaultdict
from scipy.optimize import linear_sum_assignment



def get_normalized_answer(input_string) -> str:
    """Lower text and remove punctuation, articles and extra whitespace."""

    def remove_articles(text: str):
        return re.sub(r"\b(a|an|the)\b", " ", text)

    def white_space_fix(text: str):
        return " ".join(text.split())

    def remove_punc(text: str):
        exclude = set(string.punctuation)
        return "".join(ch for ch in text if ch not in exclude)

    def lower(text: str):
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(input_string))))


def get_tokens(input_string):
    return get_normalized_answer(input_string).split()


def compute_exact_match(label_str, pred_str):
    return get_normalized_answer(pred_str) == get_normalized_answer(label_str)


def compute_bow_f1(label_str, pred_str, return_pr=False):
    prediction_tokens = get_tokens(pred_str)
    ground_truth_tokens = get_tokens(label_str)
    common = Counter(prediction_tokens) & Counter(ground_truth_tokens)
    num_same = sum(common.values())
    if num_same == 0:
        if return_pr: return 0, 0, 0 
        else: return 0
    precision = 1.0 * num_same / len(prediction_tokens)
    recall = 1.0 * num_same / len(ground_truth_tokens)
    f1 = (2 * precision * recall) / (precision + recall)
    if return_pr:
        return precision, recall, f1
    else:
        return f1


def get_pred_label_spans(pred_path, test_file, ignore_non_entity=False):
    '''Compute metrics for each role of each trigger mention.
       1. Count all mentions; 
       2. Average the metric across all mentions
    ''' 
    # convert to ``id to label per role type``
    # {
    #     `doc id-event id-trigger id-label role type`: {`event type`: ``label type``, `spans`: [[`text`]]} # each item in spans is an entity
    # }
    maven_data = []
    with open(test_file) as f:
        for line in f.readlines():
            maven_data.append(json.loads(line.strip()))
    label_id2spans = defaultdict(list)
    all_triggers = {} # {id: event_type}
    docid2text = {}
    tid2eid = {}
    for item in maven_data:
        docid2text[item["id"]] = item["text"]
        for event in item["events"]:
            for trigger in event["triggers"]:
                all_triggers[f"{item['id']}-{event['id']}-{trigger['id']}"] = event["type"]
                assert trigger['id'] not in tid2eid
                tid2eid[trigger['id']] = event['id']
                for argument in trigger["arguments"]:
                    id = f"{item['id']}-{event['id']}-{trigger['id']}-{argument['role']}"
                    if id not in label_id2spans: # Maybe multiple arguments have the same role
                        label_id2spans[id] = {
                            "event_type": event["type"],
                            "spans": []
                        }
                    spans = []
                    if "non-entity" in argument["id"] and ignore_non_entity:
                        for mention in argument["mentions"]:
                            spans.append("<NA>")
                        # continue
                    else:
                        for mention in argument["mentions"]:
                            spans.append(item["text"][mention["position"][0]:mention["position"][1]])
                    label_id2spans[id]["spans"].append(spans)
        for mention in item['negative_triggers']:
            tid2eid[mention['id']]="NA"
    # (doc id, event id, trigger id, pred event type, position, pred role type)
    # convert to ``id to prediction per role type``
    # {
    #     `doc id-event id-trigger id-pred role type`: {`event type`: ``pred type``, `spans`: [`text`]}
    # }
    pred_id2spans = {}
    with open(pred_path, "r") as fin:
        lines=fin.readlines()
        for line in lines:
            doc=json.loads(line)
            if doc['id'] not in docid2text:
                continue
            for tid in doc['preds']:
                if tid not in tid2eid:
                    continue
                event_id=tid2eid[tid]
                event_type=doc['preds'][tid]['event_type']
                for role in doc['preds'][tid]:
                    if role=='event_type':
                        continue
                    id = f"{doc['id']}-{event_id}-{tid}-{event_type}.{role}"
                    pred_id2spans[id]={
                        "event_type": event_type,
                        "spans": doc['preds'][tid][role]
                    }
    
    return label_id2spans, pred_id2spans, all_triggers


def find_optimal_match(gold_spans, pred_spans):
    scores = np.zeros([len(gold_spans), len(pred_spans)])
    for gold_index, gold_item in enumerate(gold_spans):
        for pred_index, pred_item in enumerate(pred_spans):
            scores[gold_index, pred_index] = compute_bow_f1(gold_item, pred_item)
    row_ind, col_ind = linear_sum_assignment(-scores)

    return row_ind, [(gold_spans[i], pred_spans[j]) for i, j in zip(row_ind, col_ind)]


def compute_mention_level_F1(label_id2spans, pred_id2spans, all_triggers, schema):
    mention_exact_match = []
    mention_bow = {
        "precision": [],
        "recall": [],
        "f1": []
    }
    # for all triggers
    for trigger in all_triggers:
        event_type = all_triggers[trigger]
        all_roles = schema[event_type]
        for role in all_roles:
            role = f"{event_type}.{role}"
            id = f"{trigger}-{role}"
            if id not in pred_id2spans:
                if id not in label_id2spans: 
                    continue
                else: # false negative roles
                    # gold_spans = [span for spans in label_id2spans[id]["spans"] for span in spans]
                    # mention_exact_match.extend([0]*len(gold_spans))
                    # for key in mention_bow:
                    #     mention_bow[key].extend([0]*len(gold_spans))
                    mention_exact_match.append(0)
                    for key in mention_bow:
                        mention_bow[key].append(0)
            else:
                if id not in label_id2spans: # 1. false positive roles
                    # pred_spans = pred_id2spans[id]["spans"]
                    # mention_exact_match.extend([0]*len(pred_spans))
                    # for key in mention_bow:
                    #     mention_bow[key].extend([0]*len(pred_spans))
                    mention_exact_match.append(0)
                    for key in mention_bow:
                        mention_bow[key].append(0)
                else:
                    if pred_id2spans[id]["event_type"] != label_id2spans[id]["event_type"]:
                        # gold_spans = [span for spans in label_id2spans[id]["spans"] for span in spans]
                        # mention_exact_match.extend([0]*len(gold_spans))
                        # for key in mention_bow:
                        #     mention_bow[key].extend([0]*len(gold_spans))
                        mention_exact_match.append(0)
                        for key in mention_bow:
                            mention_bow[key].append(0)
                    else:
                        gold_spans = [span for spans in label_id2spans[id]["spans"] for span in spans]
                        pred_spans = pred_id2spans[id]["spans"]
                        gold_span_idx, pairs = find_optimal_match(gold_spans, pred_spans)
                        penalty = min(len(gold_spans), len(pred_spans)) / max(len(gold_spans), len(pred_spans))
                        # import pdb; pdb.set_trace()
                        for pair in pairs:
                            em = int(compute_exact_match(pair[0], pair[1]))
                            p, r, f1 = compute_bow_f1(pair[0], pair[1], True)
                            mention_exact_match.append(em * penalty)
                            mention_bow["precision"].append(p * penalty)
                            mention_bow["recall"].append(r * penalty)
                            mention_bow["f1"].append(f1 * penalty)
                        # # penalty
                        # diff = abs(len(gold_spans) - len(pred_spans))
                        # mention_exact_match.extend([0]*diff)
                        # for key in mention_bow:
                        #     mention_bow[key].extend([0]*diff)
    # for false positive trigger predictions
    for id in pred_id2spans:
        event_id = id.split("-")[1]
        if event_id == "NA":
            # pred_spans = pred_id2spans[id]["spans"]
            # mention_exact_match.extend([0]*len(pred_spans))
            # for key in mention_bow:
            #     mention_bow[key].extend([0]*len(pred_spans))
            mention_exact_match.append(0)
            for key in mention_bow:
                mention_bow[key].append(0)
    # average across all mentions
    global_res = {
        "EM": np.mean(mention_exact_match) * 100,
        "Precision": np.mean(mention_bow["precision"]) * 100,
        "Recall": np.mean(mention_bow["recall"]) * 100,
        "F1": np.mean(mention_bow["f1"]) * 100
    }
    # print("Mention Level: Exact Match: {}, Bag-of-Words F1: {}".format(global_em, global_bow))
    return global_res


def merge_entity_score(gold_spans):
    mention_idx_to_entity_idx = {}
    flat_spans = []
    for entity_idx, spans in enumerate(gold_spans):
        for span in spans:
            mention_idx_to_entity_idx[len(flat_spans)] = entity_idx
            flat_spans.append(span)
    return mention_idx_to_entity_idx


def compute_entity_coref_level_F1(label_id2spans, pred_id2spans, all_triggers, schema):
    mention_exact_match = []
    mention_bow = {
        "precision": [],
        "recall": [],
        "f1": []
    }
    # for all triggers
    for trigger in all_triggers:
        event_type = all_triggers[trigger]
        all_roles = schema[event_type]
        for role in all_roles:
            role = f"{event_type}.{role}"
            id = f"{trigger}-{role}"
            if id not in pred_id2spans:
                if id not in label_id2spans: 
                    continue
                else: # false negative roles
                    mention_exact_match.append(0)
                    for key in mention_bow:
                        mention_bow[key].append(0)
            else:
                if id not in label_id2spans: # 1. false positive roles
                    mention_exact_match.append(0)
                    for key in mention_bow:
                        mention_bow[key].append(0)
                else:
                    if pred_id2spans[id]["event_type"] != label_id2spans[id]["event_type"]:
                        mention_exact_match.append(0)
                        for key in mention_bow:
                            mention_bow[key].append(0)
                    else:
                        gold_spans = [span for spans in label_id2spans[id]["spans"] for span in spans]
                        pred_spans = pred_id2spans[id]["spans"]
                        gold_span_idx, pairs = find_optimal_match(gold_spans, pred_spans)
                        mention_idx_to_entity_idx = merge_entity_score(label_id2spans[id]["spans"])
                        max_entity_score = []
                        for i in range(len(label_id2spans[id]["spans"])):
                            max_entity_score.append({
                                "bow_f1": 0.0,
                                "gold_span": None,
                                "pred_span": None
                            })
                        for idx, pair in zip(gold_span_idx, pairs):
                            p, r, f1 = compute_bow_f1(pair[0], pair[1], True)
                            if f1 > max_entity_score[mention_idx_to_entity_idx[idx]]["bow_f1"]:
                                max_entity_score[mention_idx_to_entity_idx[idx]] = {
                                    "bow_f1": f1,
                                    "gold_span": pair[0],
                                    "pred_span": pair[1]
                                }
                        for entity in max_entity_score:
                            if entity["gold_span"] is not None:
                                em = int(compute_exact_match(entity["gold_span"], entity["pred_span"]))
                                p, r, f1 = compute_bow_f1(entity["gold_span"], entity["pred_span"], True)
                            else:
                                em = 0
                                p, r, f1 = 0, 0, 0
                            mention_exact_match.append(em)
                            mention_bow["precision"].append(p)
                            mention_bow["recall"].append(r)
                            mention_bow["f1"].append(f1)

    # for false positive trigger predictions
    for id in pred_id2spans:
        event_id = id.split("-")[1]
        if event_id == "NA":
            mention_exact_match.append(0)
            for key in mention_bow:
                mention_bow[key].append(0)
    # average across all mentions
    global_res = {
        "EM": np.mean(mention_exact_match) * 100,
        "Precision": np.mean(mention_bow["precision"]) * 100,
        "Recall": np.mean(mention_bow["recall"]) * 100,
        "F1": np.mean(mention_bow["f1"]) * 100
    }
    # print("Entity Coref Level: Exact Match: {}, Bag-of-Words F1: {}".format(global_em, global_bow))
    return global_res


def compute_event_entity_coref_level_F1(label_id2spans, pred_id2spans, all_triggers, schema):
    mention_exact_match = []
    mention_bow = {
        "precision": [],
        "recall": [],
        "f1": []
    }
    # for all triggers
    scores_per_event = dict()
    for trigger in all_triggers:
        event_id = "-".join(trigger.split("-")[:-1])
        event_type = all_triggers[trigger]
        all_roles = schema[event_type]
        for role in all_roles:
            role = f"{event_type}.{role}"
            id = f"{trigger}-{role}"
            if id not in pred_id2spans:
                if id not in label_id2spans: 
                    continue
                else: # false negative roles
                    mention_exact_match.append(0)
                    for key in mention_bow:
                        mention_bow[key].append(0)
            else:
                if id not in label_id2spans: # 1. false positive roles
                    mention_exact_match.append(0)
                    for key in mention_bow:
                        mention_bow[key].append(0)
                else:
                    if pred_id2spans[id]["event_type"] != label_id2spans[id]["event_type"]:
                        mention_exact_match.append(0)
                        for key in mention_bow:
                            mention_bow[key].append(0)
                    else:
                        event_role_id = f"{event_id}-{role}"
                        if event_role_id not in scores_per_event:
                            scores_per_event[event_role_id] = []
                        gold_spans = [span for spans in label_id2spans[id]["spans"] for span in spans]
                        pred_spans = pred_id2spans[id]["spans"]
                        gold_span_idx, pairs = find_optimal_match(gold_spans, pred_spans)
                        mention_idx_to_entity_idx = merge_entity_score(label_id2spans[id]["spans"])
                        max_entity_score = []
                        for i in range(len(label_id2spans[id]["spans"])):
                            max_entity_score.append({
                                "bow_f1": 0.0,
                                "gold_span": None,
                                "pred_span": None
                            })
                        for idx, pair in zip(gold_span_idx, pairs):
                            p, r, f1 = compute_bow_f1(pair[0], pair[1], True)
                            if f1 > max_entity_score[mention_idx_to_entity_idx[idx]]["bow_f1"]:
                                max_entity_score[mention_idx_to_entity_idx[idx]] = {
                                    "bow_f1": f1,
                                    "gold_span": pair[0],
                                    "pred_span": pair[1]
                                }
                        entity_scores_per_trigger = []
                        for entity in max_entity_score:
                            if entity["gold_span"] is not None:
                                em = int(compute_exact_match(entity["gold_span"], entity["pred_span"]))
                                p, r, f1 = compute_bow_f1(entity["gold_span"], entity["pred_span"], True)
                            else:
                                em = 0
                                p, r, f1 = 0, 0, 0
                            score = {
                                "em": em,
                                "bow": {
                                    "precision": p,
                                    "recall": r,
                                    "f1": f1
                                }
                            }
                            entity_scores_per_trigger.append(score)
                        scores_per_event[event_role_id].append(entity_scores_per_trigger)

    # merge event-entity predictions
    for event_role in scores_per_event:
        all_entity_scores_for_all_triggers = scores_per_event[event_role]
        max_all_entity_scores_per_event = copy.deepcopy(all_entity_scores_for_all_triggers[0])
        for all_entity_scores_per_trigger in all_entity_scores_for_all_triggers:
            for entity_idx, per_entity_scores_per_trigger in enumerate(all_entity_scores_per_trigger):
                if per_entity_scores_per_trigger["em"] > max_all_entity_scores_per_event[entity_idx]["em"]:
                    max_all_entity_scores_per_event[entity_idx]["em"] = per_entity_scores_per_trigger["em"]
                if per_entity_scores_per_trigger["bow"]["f1"] > max_all_entity_scores_per_event[entity_idx]["bow"]["f1"]:
                    max_all_entity_scores_per_event[entity_idx]["bow"]["precision"] = per_entity_scores_per_trigger["bow"]["precision"]
                    max_all_entity_scores_per_event[entity_idx]["bow"]["recall"] = per_entity_scores_per_trigger["bow"]["recall"]
                    max_all_entity_scores_per_event[entity_idx]["bow"]["f1"] = per_entity_scores_per_trigger["bow"]["f1"]
        for max_per_entity_scores_per_event in max_all_entity_scores_per_event:
            mention_exact_match.append(max_per_entity_scores_per_event["em"])
            for key in mention_bow.keys():
                mention_bow[key].append(max_per_entity_scores_per_event["bow"][key])

    # for false positive trigger predictions
    for id in pred_id2spans:
        event_id = id.split("-")[1]
        if event_id == "NA":
            mention_exact_match.append(0)
            for key in mention_bow:
                mention_bow[key].append(0)
    # average across all mentions
    # global_em = np.mean(mention_exact_match) * 100
    global_res = {
        "EM": np.mean(mention_exact_match) * 100,
        "Precision": np.mean(mention_bow["precision"]) * 100,
        "Recall": np.mean(mention_bow["recall"]) * 100,
        "F1": np.mean(mention_bow["f1"]) * 100
    }
    # print("Event-Entity Coref Leval: Exact Match: {}, Bag-of-Words F1: {}".format(global_em, global_bow))
    return global_res

if __name__ == "__main__":
    input_dir = argv[1]
    output_dir = argv[2]
    submit_dir = os.path.join(input_dir, 'res')
    truth_dir = os.path.join(input_dir, 'ref')
    # Create the output directory, if it does not already exist and open output files
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    score_file = open(os.path.join(output_dir, 'scores.txt'), 'w')
    html_file = open(os.path.join(output_dir, 'scores.html'), 'w')

    # read ground truth
    pred_path = os.path.join(submit_dir,"test_prediction.jsonl")
    test_file = os.path.join(truth_dir,"test.unified.jsonl")
    schema = json.load(open(os.path.join(truth_dir,"label2role.json")))
    label_id2spans, pred_id2spans, all_triggers = get_pred_label_spans(pred_path, test_file, ignore_non_entity=False)
    m_global_res = compute_mention_level_F1(label_id2spans, pred_id2spans, all_triggers, schema)
    ec_global_res = compute_entity_coref_level_F1(label_id2spans, pred_id2spans, all_triggers, schema)
    eec_global_res = compute_event_entity_coref_level_F1(label_id2spans, pred_id2spans, all_triggers, schema)
    metrics = {
        "Mention_Level": m_global_res,
        "Entity_Coref_Level": ec_global_res,
        "Event_Coref_Level": eec_global_res
    }
    def output_score(key, score):
        print(key + ": %0.2f\n" % score)
        html_file.write("======= score (" + key + ")=%0.2f =======\n" % score)
        score_file.write(key + ": %0.2f\n" % score)
    for l in metrics:
        for m in metrics[l]:
            output_score(l+"_"+m, metrics[l][m])

    # Read the execution time and add it to the scores:
    try:
        metadata = yaml.load(open(os.path.join(input_dir, 'res', 'metadata'), 'r'))
        score_file.write("Duration: %0.2f\n" % metadata['elapsedTime'])
    except:
        score_file.write("Duration: 0\n")
        html_file.close()
    score_file.close()
