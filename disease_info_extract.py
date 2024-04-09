
import os
import spacy
from tqdm import tqdm
import pandas as pd
import json
import os
import nltk
import spacy
import pandas as pd
import re
import numpy as np
from tqdm import tqdm


nltk.download('averaged_perceptron_tagger')

def check_any_in(list, text):
    for word in list:
        if word in text:
            return word
    return False

def get_label(caption_list, max_seq):
    output = np.zeros(max_seq)
    output[:len(caption_list)] = np.array(caption_list)
    return output

def find_report(study_id, report_path):
    path = '../mimic_all.csv'
    df_all = pd.read_csv(path)
    subject_id = df_all[df_all['study_id'] == int(study_id)]['subject_id'].values[0]
    p1 = 'p' + str(subject_id)[:2]
    p2 = 'p'+str(subject_id)
    report_name = 's' + str(int(study_id)) + '.txt'
    with open(os.path.join(report_path, p1, p2, report_name), 'r') as f:
        report = f.read()

    report.replace('\n', '').replace('FINDINGS', '\nFINDINGS').replace('IMPRESSION', '\nIMPRESSION')
    return report

def sub_find_attribute(re_searched, all_prep_words,anchor, dict_attributes, print_test):
    if re_searched is not None:
        text_pre = re_searched.group(1).strip()
        if anchor in text_pre: # todo: inner loop of detecting multiple findings (see the other todo for details)
            re_searched2 = re.search('(.*)' + anchor + '(.*)', text_pre, re.I)
            dict_attributes =  sub_find_attribute(re_searched2, all_prep_words, anchor, dict_attributes, print_test)
            text_pre = re_searched2.group(2).strip()
        if text_pre.split(' ')[-1] in all_prep_words:
            text_pre = ''
        while check_any_in(all_prep_words, text_pre):
            re_searched2 = re.search('(in|of|with) (.*)', text_pre, re.I) # todo. add 'and'
            if re_searched2 is not None:
                text_pre = re_searched2.group(2)
            else:
                break


        if check_any_in(phrases_list, text_pre):
            phrase = check_any_in(phrases_list, text_pre)
            text_list = [phrase]
            rest_list = text_pre.split(phrase)
            for text in rest_list:
                if text != '':
                    text_list += text.strip().split(' ')
        else:
            text_list = text_pre.strip().split(' ')[-5:]


        for word in text_list:
            if word == '':
                continue
            if len(d_loc[d_loc['location'] == word].values) != 0:
                if dict_attributes[anchor]['location'] == None:
                    dict_attributes[anchor]['location'] = [word]
                else:
                    if word not in dict_attributes[anchor]['location']:
                        dict_attributes[anchor]['location'].append(word)
                if print_test:
                    print('location:', word)
            elif len(d_t[d_t['type'] == word].values) != 0:
                if dict_attributes[anchor]['type'] == None:
                    dict_attributes[anchor]['type'] = [word]
                else:
                    if word not in dict_attributes[anchor]['type']:
                        dict_attributes[anchor]['type'].append(word)
                if print_test:
                    print('type:', word)
            elif len(d_lev[d_lev['level'] == word].values) != 0:
                if dict_attributes[anchor]['level'] == None:
                    dict_attributes[anchor]['level'] = [word]
                else:
                    if word not in dict_attributes[anchor]['level']:
                        dict_attributes[anchor]['level'].append(word)
                if print_test:
                    print('level:', word)
            else:
                if print_test:
                    print('pre:', word)
    return dict_attributes

def find_pre_attribute(match_words, prep, text,dict_attributes, print_test):
    re_searched = re.search('(.*) ' + match_words[0], text, re.I)
    dict_attributes = sub_find_attribute(re_searched, prep, match_words[0], dict_attributes, print_test)
    for i in range(len(match_words) - 1):
        if print_test:
            print(' ')
        word1 = match_words[i]
        word2 = match_words[i + 1]
        re_searched = re.search(word1 + '(.*)' + word2, text, re.I)
        # if 'suggest' in re_searched.group(1):
        #     print('suggest:', word1, word2)
        dict_attributes = sub_find_attribute(re_searched, prep,match_words[i+1], dict_attributes, print_test)
    return dict_attributes
def find_post_attribute(match_words, text, dict_attributes, print_test):
    keyword = ['in the', 'at the', 'seen']

    resolved_words = ['has resolved', 'have resolved']
    new_match_words = [] # in case some disease has been resolved
    for i in range(len(match_words)):
        word1 = match_words[i]
        if i +1 < len(match_words):
            word2 = match_words[i+1]
            re_searched = re.search(word1 + '(.*)' + word2, text, re.I)
        else:
            re_searched = re.search(word1 + '(.*)', text, re.I)
        text_post = re_searched.group(1).strip()

        if check_any_in(resolved_words, text_post):
            del dict_attributes[word1]
            continue
        else:
            new_match_words.append(word1)

        if check_any_in(keyword,text_post):
            phrase = check_any_in(phrases_list_post, text_post)
            if phrase:
                dict_attributes[word1]['post_location'] = phrase
                if print_test:
                    print('post_location:', phrase)
            else:
                if print_test:
                    print('post:',text_post)
    return new_match_words, dict_attributes


def create_empty_attributes(match_words):
    dict = {}
    for word in match_words:
        dict[word] = {'entity_name':word, 'location': None, 'type': None, 'level': None, 'post_location':None, 'location2':None, 'type2':None, 'level2':None, 'post_location2':None}
    return dict

def find_attribute(match_words,text, print_test):
    prep = ['and', 'in', 'of', 'with']
    dict_attributes = create_empty_attributes(match_words)
    if len(match_words) == 0:
        return dict_attributes
    match_words, dict_attributes = find_post_attribute(match_words, text, dict_attributes, print_test)
    if len(match_words)> 0:
        dict_attributes = find_pre_attribute(match_words, prep, text,dict_attributes, print_test)#main
    return dict_attributes

def reorder(match_words, indexes, text):
    # make sure the oder in match_words is corresponding to the original text
    index = text.find(match_words[-1])
    i = 0
    while i < len(indexes):
        if index < indexes[i]:
            indexes = indexes[:i] + [index] + indexes[i:]
            match_words = match_words[:i] + [match_words[-1]] + match_words[i:-1]
            break
        else:
            i += 1
    if i == len(indexes):
        indexes.append(index)
    return match_words, indexes

def get_phrases_list(d, title):
    outlist = []
    for i in range(len(d)):
        if len(d.iloc[i][title].split(' '))> 1:
            outlist.append(d.iloc[i][title])
    return outlist

def fix_order(dict_attributes):
    path = './libs/disease_lib.csv'
    d_d = pd.read_csv(path)
    new_dict = {}
    # make sure the order of the attributes is consistent with d_d['official_name']
    official_names = d_d['official_name'].values
    for name in official_names:
        if name in dict_attributes:
            new_dict[name] = dict_attributes[name]

    assert len(new_dict) == len(dict_attributes)
    return new_dict


def process_core(text_core, nlp,print_test, uniform_name= False, fixed_order=False):

    index = 0
    for i in range(len(d_d)):
        names = d_d.iloc[i]['report_name'].split(';')
        for name in names:
            df.loc[index] = [int(d_d.iloc[i]['id']), name]
            # df.at[index,'report_name'] = name
            index += 1

    if print_test:
        doc = nlp(text_core)
        print('ref_entity:', doc.ents)

    #by_match
    yes_id = set()
    match_out = []
    location = []
    mix_out= []
    indexes = []
    for i in range(len(df)):
        name = df.iloc[i]['report_name']
        # if
        if df.iloc[i]['report_name'] in text_core:
            id = df.iloc[i]['id']
            if id not in yes_id:
                yes_id.add(id)
                match_out.append(df.iloc[i]['report_name'])
                match_out, indexes = reorder(match_out, indexes, text_core)
    dict_attributes = find_attribute(match_out, text_core, print_test)
    if uniform_name:
        ori_dict = dict_attributes
        dict_attributes = {}
        for key in ori_dict:
            id = df[df['report_name'] == key]['id'].values[0]
            new_name = d_d[d_d['id'] == id]['official_name'].values[0]
            ori_dict[key]['entity_name'] = new_name
            dict_attributes[new_name] = ori_dict[key]
    if fixed_order:
        dict_attributes = fix_order(dict_attributes)    # 修改 disease name 排列顺序
    if print_test:
        print('match_way: ', ', '.join(match_out))

    if print_test:
        missed = []
        for ent in doc.ents:
            if ent.text not in ' '.join(match_out):
                missed.append(ent.text)
        if missed!= []:
            print('missed:', ', '.join(missed))


        tokened_s = nltk.word_tokenize(text_core)
        pos = nltk.pos_tag(tokened_s)
        chanageset = {'layering', 'right', 'small', 'minimal', 'left', 'of'}
        for i in range(len(pos)):
            p = pos[i]
            if p[0] in chanageset:
                pos[i] = (p[0], 'RB')
        # print(result)
        out = ''
        outpos = []
        skipset = {'VB', 'IN', 'CC', 'VBD', 'VBG', 'VBP', 'VBZ'}
        for j in range(len(tokened_s)):
            if pos[j][1] in skipset or tokened_s[j] == ',' or tokened_s[j] == '.' or tokened_s[j] == '//':
                break
            out += tokened_s[j] + ' '
            outpos.append(pos[j])
        # if out != '':
        print('ref_nltk_way: ', out)
        # if out == 'right ' or out == 'areas ' or out == 'left ' or out == 'small ' or out == 'to ':
        #     print(s)
        #     print(pos)
    return dict_attributes

def check_matches(entities1, entities2):
    # remove the entities that are in the other
    for e1 in entities1:
        for e2 in entities2:
            if df[df['report_name'] ==e1]['id'].values[0] == df[df['report_name'] ==e2]['id'].values[0]:
                entities1.remove(e1)
    return entities1
            # if e1.text == e2.text:
            #     return True

def replace_location_words(attributes):
    for key in attributes:
        if attributes[key]['location'] is not None:
            location = ' '.join(attributes[key]['location'])
            for j in range(len(dc)):
                location = location.replace(dc.iloc[j]['from'], dc.iloc[j]['to'])
            attributes[key]['location'] = location.split(' ')

        if attributes[key]['post_location'] is not None:
            location = attributes[key]['post_location']
            for j in range(len(dc)):
                location = location.replace(dc.iloc[j]['from'], dc.iloc[j]['to'])
            attributes[key]['post_location'] = location
    return attributes

def find_better_attributes(file_attributes, sent_attributes):
    file_score = 0
    sent_score = 0
    for key in file_attributes:
        if file_attributes[key] is not None:
            file_score += 1
    for key in sent_attributes:
        if sent_attributes[key] is not None:
            sent_score += 1
    if file_score > sent_score:
        return file_attributes
    else:
        return sent_attributes

def add_new_instance(one_file_attributes, one_sent_attributes):
    for key in one_sent_attributes:
        if key not in one_file_attributes:
            one_file_attributes[key] = one_sent_attributes[key]
        else:
            sent_key_loc_word = False
            file_key_loc_word = False
            if one_sent_attributes[key]['location'] is not None:
                sent_key_loc_word = check_any_in(['left', 'right', 'bilateral', 'bibasilar'], ' '.join(one_sent_attributes[key]['location']))
            if one_file_attributes[key]['location'] is not None:
                file_key_loc_word = check_any_in(['left', 'right', 'bilateral', 'bibasilar'], ' '.join(one_file_attributes[key]['location']))
            if sent_key_loc_word and file_key_loc_word and sent_key_loc_word != file_key_loc_word:
                one_file_attributes[key]['location2'] = one_sent_attributes[key]['location']
                one_file_attributes[key]['type2'] = one_sent_attributes[key]['type']
                one_file_attributes[key]['level2'] = one_sent_attributes[key]['level']
                one_file_attributes[key]['post_location2'] = one_sent_attributes[key]['post_location'] # todo: now only support two findings of the same disease
            else:
                the_one_to_keep = find_better_attributes(one_file_attributes[key], one_sent_attributes[key])
                one_file_attributes[key] = the_one_to_keep
    return one_file_attributes

def find_general(sentences, nlp, print_test, uniform_name, fixed_order):
    one_file_positives = []
    one_file_negatives = []
    for s in sentences:
        s = s.lower()
        if print_test:
            print(' ')
            print(s)
        text_core = s.replace('     ', ' ').replace('    ', ' ').replace('   ', ' ').replace('  ', ' ')
        text_no = ''

        # definately no
        if 'no longer' in text_core or ('resolved' in text_core and 'not resolved' not in text_core) or ('disappeared' in text_core and 'not disappeared' not in text_core):
            text_no = text_core
            text_core = ''
        elif re.search('(.*) (without|no |clear of|r/o |rule out|less likely)(.*)', text_core, re.I) is not None:
            re_searched = re.search('(.*) (without|no |clear of|r/o |rule out|less likely)(.*)', text_core, re.I)
            text_core = re_searched.group(1)
            text_no = re_searched.group(3) + ' ' + text_no
            if re.search('(.*) (without|no |clear of|r/o |rule out|less likely)(.*)', text_core, re.I) is not None:
                re_searched2 = re.search('(.*) (without|no |clear of|r/o |rule out|less likely)(.*)', text_core, re.I)
                text_core = re_searched2.group(1)
                text_no2 = re_searched2.group(3)
                text_no = text_no2 + ' ' + text_no
                if re.search('(.*) (without|no |clear of|r/o |rule out|less likely)(.*)', text_core, re.I) is not None:
                    re_searched3 = re.search('(.*) (without|no |clear of|r/o |rule out|less likely)(.*)', text_core, re.I)
                    text_core = re_searched3.group(1)
                    text_no3 = re_searched3.group(3)
                    text_no = text_no3 + ' ' + text_no
                    if re.search('(.*) (without|no |clear of|r/o |rule out|less likely)(.*)', text_core, re.I) is not None:
                        re_searched4 = re.search('(.*) (without|no |clear of|r/o |rule out|less likely)(.*)', text_core, re.I)
                        text_core = re_searched4.group(1)
                        text_no4 = re_searched4.group(3)
                        text_no = text_no4 + ' ' + text_no
            if 'change in' in text_no:
                text_core = text_core + ' ' + text_no
                text_no = ''
        if text_no != '':
            no_out = process_core(text_no, nlp, print_test, uniform_name, fixed_order)
            for key in no_out:
                if one_file_negatives == []:
                    one_file_negatives = [key]  # 分别加入 negative 和 positive 列表
                else:
                    one_file_negatives.append(key)
            if print_test:
                print('no out:', no_out)

        one_sent_attributes = process_core(text_core, nlp,print_test, uniform_name, fixed_order)
        one_sent_attributes = replace_location_words(one_sent_attributes)
        if 'heart size is enlarged' in one_sent_attributes:
            one_sent_attributes['cardiomegaly'] = one_sent_attributes['heart size is enlarged']
            one_sent_attributes['cardiomegaly']['entity_name'] = 'cardiomegaly'
            one_sent_attributes.pop('heart size is enlarged')
        if not fixed_order:
            one_file_negatives = check_matches(one_file_negatives, one_sent_attributes)
        else:
            for key in one_file_negatives:
                if key in one_sent_attributes:
                    one_sent_attributes.pop(key)
        if one_file_positives == []:
            one_file_positives = one_sent_attributes
        else:
            one_file_positives = add_new_instance(one_file_positives, one_sent_attributes) # todo: outer loop (see the other todo for details)

        # transfrom structure
    #     out = []
    #     for k in one_file_positives:
    #         out.append(one_file_positives[k])
    # return out
    return one_file_positives, one_file_negatives

def process_postlocation(d_ploc, dc):
    for i in range(len(d_ploc)):
        text = d_ploc.iloc[i]['post_location']
        for j in range(len(dc)):
            new_text = text.replace(dc.iloc[j]['from'], dc.iloc[j]['to'])
            # if d_ploc does not have the new text, add it
            if new_text not in d_ploc['post_location'].values:
                d_ploc.loc[d_ploc.shape[0]] = [new_text, d_ploc.iloc[i]['relate_keyword']]
    return d_ploc


def test_extract_report(study_id, report_path):
    '''
    extract json KeyInfo data from the report
    '''
    initial_library()
    nlp = spacy.load("en_ner_bc5cdr_md")

    path_all = '../mimic_all.csv'
    df_all = pd.read_csv(path_all)
    subject_id = df_all[df_all['study_id']==study_id]['subject_id'].values[0]

    path = report_path
    fold1 = 'p' + str(subject_id)[:2]
    fold2 = 'p' + str(subject_id)
    file_name = 's%s.txt' % str(study_id)
    file_path = os.path.join(path, fold1, fold2, file_name)
    with open(file_path, 'r') as f:
        ori_text = f.read()
    lib = []
    if 'FINDINGS:' in ori_text:
        text = ori_text[ori_text.find('FINDINGS:'):]
    elif 'IMPRESSION:' in ori_text:
        text = ori_text[ori_text.find('IMPRESSION:'):]
    t = text
    t = t.replace('\n', ' ')
    lib = lib + t.split('.')

    print('report:',ori_text)

    out, no_out = find_general(lib, nlp, print_test=False, uniform_name=True, fixed_order=True)

def gen_disease_json(report_path, print_test = False, stop=False, save=True, uniform_name=True, fixed_order=True):
    '''
    this function is used to generate the keyInfo data for each report. The keyInfo data is then used to generate questions.
    '''
    print('Start KeyInfo data extraction')
    initial_library()
    nlp = spacy.load("en_ner_bc5cdr_md") if print_test else None

    p1 = os.listdir(report_path)
    final_diseases = []

    print('start')
    for fold1 in p1:
        print(fold1)
        if fold1[0] != 'p':
            continue
        path2 = os.path.join(report_path,fold1)
        p2 = os.listdir(path2)
        for i in tqdm(range(len(p2))):
            fold2 = p2[i]
            path3 = os.path.join(path2,fold2)
            files = os.listdir(path3)
            for file in files:
                with open(os.path.join(path3, file), 'r') as f:
                    record = {}
                    record['study_id'] = file[1:-4]
                    record['subject_id'] = fold2[1:]
                    t = file[:-4] + '\n'
                    text = f.read()
                    lib = []
                    if 'FINDINGS:' in text:
                        text = text[text.find('FINDINGS:'):]
                    elif 'IMPRESSION:'in text:
                        text = text[text.find('IMPRESSION:'):]
                    t += text
                    t = t.replace('\n', ' ')
                    lib = lib + t.split('.')

                    out, no_out = find_general(lib,nlp,print_test, uniform_name, fixed_order)
                    record['entity'] = out
                    record['no_entity'] = no_out
                    if print_test:
                        print('final out:',out)
                        print('final noout:',no_out)
                    final_diseases.append(record)

                # if stop:
                #     break
            # if stop:
            #     break
        if stop:
            break

    if save:
        disease_path = '../all_diseases.json'
        with open(disease_path,'w') as f:
            json.dump(final_diseases,f, indent=4)

def if_positive_entity(entity, text):
    # determine if the entity is negative
    negative_part = re.search('(.*) (without|no |clear of|r/o |rule out|less likely)(.*)', text, re.I)
    if negative_part:
        negative_part = negative_part.group(3)
        if entity in negative_part:
            return False

    # determine if the entity is positive
    if entity in text.split():
        return True
    else:
        return False

def post_process_record(out, no_out,record):
    record['entity'] = out
    record['no_entity'] = no_out
    return record


def get_exist_disease_id(record):
    id_set = set()
    for key in record['entity']:
        id = df[df['report_name']==key]['id'].values
        id_set.add(id[0])
    return id_set


def convert_list_of_name2offical(list):
    for i in range(len(list)):
        try:
            name = d_d[d_d['report_name'].str.contains(list[i])]['official_name'].values[0]
        except:
            continue
        list[i] = name
    return list


def transform_pos_tag(tag_list, d_pos, max_seq):
    out = []
    for item in tag_list:
        tag = item[1]
        id = d_pos[d_pos['tag'] == tag]['id'].values[0]
        out.append(id)
    for i in range(len(out),max_seq):
        out.append(0)
    return out


def process(list, diseases_list, mode = 'strict'):
    out = []
    for i in range(len(list)):
        if mode == 'strict':
            if list[i] == 1:
                out.append(diseases_list[i].lower())
        else:
            if list[i] == 1 or list[i] == -1:
                out.append(diseases_list[i].lower())
    return out


def contains_number(string):
    return any(char.isdigit() for char in string)

def are_capitals(string):
    for char in string:
        if char.isalpha() and not char.isupper():
            return False
    return True


def initial_library():
    global d_d, d_lev, d_loc, d_t, d_ploc, phrases_list, phrases_list_post, df,dc
    path = './libs/disease_lib.csv'
    d_d = pd.read_csv(path)

    path_lev = './libs/level_lib.csv'
    d_lev = pd.read_csv(path_lev)
    path_loc = './libs/location_lib.csv'
    d_loc = pd.read_csv(path_loc)
    path_t = './libs/type_lib.csv'
    d_t = pd.read_csv(path_t)
    path_ploc = './libs/postlocation_lib.csv'
    d_ploc = pd.read_csv(path_ploc)
    path_change = './libs/position_change.csv'
    dc = pd.read_csv(path_change)

    process_postlocation(d_ploc, dc)


    phrases_list = get_phrases_list(d_lev, 'level')
    phrases_list += get_phrases_list(d_loc, 'location')
    phrases_list_post = get_phrases_list(d_ploc, 'post_location')

    df = pd.DataFrame(columns=['id', 'report_name'])
    df['report_name'] = df['report_name'].astype(object)
    index = 0
    for i in range(len(d_d)):
        names = d_d.iloc[i]['report_name'].split(';')
        for name in names:
            df.loc[index] = [int(d_d.iloc[i]['id']), name]
            # df.at[index,'report_name'] = name
            index += 1

def gen_disease_json(report_path, print_test = False, stop=False, save=True, uniform_name=True, fixed_order=True):
    '''
    this function is used to generate the keyInfo data for each report.
    '''
    initial_library()
    nlp = spacy.load("en_ner_bc5cdr_md") if print_test else None

    p1 = os.listdir(report_path)
    final_diseases = []

    print('start')
    for fold1 in p1:
        print(fold1)
        if fold1[0] != 'p':
            continue
        path2 = os.path.join(report_path,fold1)
        p2 = os.listdir(path2)
        for i in tqdm(range(len(p2))):
            fold2 = p2[i]
            path3 = os.path.join(path2,fold2)
            files = os.listdir(path3)
            for file in files:
                with open(os.path.join(path3, file), 'r') as f:
                    record = {}
                    record['study_id'] = file[1:-4]
                    record['subject_id'] = fold2[1:]
                    t = file[:-4] + '\n'
                    text = f.read()
                    lib = []
                    if 'FINDINGS:' in text:
                        text = text[text.find('FINDINGS:'):]
                    elif 'IMPRESSION:'in text:
                        text = text[text.find('IMPRESSION:'):]
                    t += text
                    t = t.replace('\n', ' ')
                    lib = lib + t.split('.')

                    out, no_out = find_general(lib,nlp,print_test, uniform_name, fixed_order)
                    record['entity'] = out
                    record['no_entity'] = no_out
                    if print_test:
                        print('final out:',out)
                        print('final noout:',no_out)
                    final_diseases.append(record)
        if stop:
            break
        # break

    if save:
        disease_path = '../all_diseases.json'
        with open(disease_path,'w') as f:
            json.dump(final_diseases,f, indent=4)

if __name__ == '__main__':

    gen_disease_json(report_path= 'mimic-cxr-reports/files', print_test=False, stop= False, save=False, uniform_name=True, fixed_order=True) # generate keyInfo data
