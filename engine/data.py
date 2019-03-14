from engine.tokenization import FullTokenizer


def load_vocab_as_list(vocab_file):
    vocab = []
    with open(vocab_file, mode='r', encoding='utf8') as f:
        while (True):
            line = f.readline()
            line = line.strip('\n')
            if not line:
                break
            vocab.append(line)
    return vocab


def convert_by_vocab(vocab, items):
    '''

    :param vocab:
    :param items:
    :return:
    '''
    output = []
    for item in items:
        output.append(vocab[item])
    return output


class InputFeatures(object):
    def __init__(self,
                 unique_id,
                 input_ids,
                 input_mask=None,
                 segment_ids=None):
        self.input_ids = input_ids
        self.input_mask = input_mask
        self.segment_ids = segment_ids
        self.unique_id = unique_id

    def show(self):
        print('input_ids:', self.input_ids)
        print('input_mask:', self.input_mask)
        print('segment_ids:', self.segment_ids)
        print('unique_id:', self.unique_id)


class PreProcessor(object):

    def __init__(self, params):

        self.tokenizer = FullTokenizer(params['vocab_file'])
        self.vocab = load_vocab_as_list(params['vocab_file'])


    def str_to_tokens(self, text):
        '''

        :param text: str
        :return: list[str] tokenized wordpieces
        '''
        return self.tokenizer.tokenize(text)

    def tokens_to_idx(self, tokens):
        '''

        :param tokens: list of tokens
        :return: list of indexes
        '''
        output = []
        for token in tokens:
            output.append(self.vocab.index(token))
        return output

    def create_feature(self, question, context, params):

        unique_id = params['unique_id']
        max_query_length = params['max_query_length']
        max_seq_length = params['max_seq_length']

        question_text = question


        doc_tokens = self.tokenizer._tokenize_to_doc_tokens(context)

        token_to_original_index = []
        original_to_token_index = []
        all_doc_tokens = []

        query_tokens = self.str_to_tokens(question_text)
        if len(query_tokens) > max_query_length:
            query_tokens = query_tokens[0:max_query_length]

        for i, token in enumerate(doc_tokens):
            original_to_token_index.append(i)
            sub_tokens = self.str_to_tokens(token)
            for sub_token in sub_tokens:
                token_to_original_index.append(i)
                all_doc_tokens.append(sub_token)

        input_ids = []
        input_mask = []
        segment_ids = []

        input_ids.append('[CLS]')
        segment_ids.append(0)
        for query in query_tokens:
            input_ids.append(query)
            segment_ids.append(0)
        input_ids.append('[SEP]')
        segment_ids.append(0)

        # context
        for doc in all_doc_tokens:
            input_ids.append(doc)
            segment_ids.append(1)
        input_ids.append('[SEP]')
        segment_ids.append(1)

        if len(input_ids) > max_seq_length:
            input_ids = input_ids[0:max_seq_length]
            input_ids[-1] = ['SEP']
            segment_ids = segment_ids[0:max_seq_length]

        _length = len(input_ids)

        for _ in range(_length):
            input_mask.append(1)

        for _ in range(max_seq_length - _length):
            input_mask.append(0)
            segment_ids.append(0)
            input_ids.append(0)

        for i in range(len(input_ids)):
            if input_ids[i] in self.vocab:
                input_ids[i] = self.vocab.index(input_ids[i])

        # input_ids = self.tokens_to_idx(input_ids)

        feature = InputFeatures(unique_id,
                                input_ids,
                                input_mask=input_mask,
                                segment_ids=segment_ids)

        return feature

    def pred_to_text(self, start, end, feature):

        pred_answer_text = ''
        for i in range(start[0], end[0] + 1):
            vocab_idx = feature.input_ids[i]
            word = self.vocab[vocab_idx]
            if '#' in word:
                pred_answer_text += word.strip('#')
            else:
                pred_answer_text += ' ' + word

        return pred_answer_text