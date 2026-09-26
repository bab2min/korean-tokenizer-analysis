import json
import re
import sys
from contextlib import nullcontext
from html import escape
from collections import defaultdict
from pathlib import Path

from transformers import AutoTokenizer
from tokenizers import decoders
from kiwipiepy import Kiwi

class BbpeBytesDecoder:
    def __init__(self):
        self.u2b_map = self._get_u2b_map()
        self.u2b_map[' '] = 32

    def _get_u2b_map(self):
        bs = (
            list(range(ord("!"), ord("~") + 1)) + list(range(ord("¡"), ord("¬") + 1)) + list(range(ord("®"), ord("ÿ") + 1))
        )
        cs = bs[:]
        n = 0
        for b in range(2 ** 8):
            if b not in bs:
                bs.append(b)
                cs.append(2 ** 8 + n)
                n += 1
        cs = [chr(n) for n in cs]
        return dict(zip(cs, bs))

    def decode(self, unicodes:str, errors:str='backslashreplace') -> str:
        try:
            bs = [self.u2b_map[c] for c in unicodes]
        except KeyError:
            raise ValueError(f"Invalid token: {unicodes}. It contains characters that cannot be mapped to bytes.")

        bs = bytes(bs)
        return bs.decode('utf-8', errors=errors if errors != 'escape' else 'strict')

class VocabDecoder:
    """문장 시작 정리 없이 개별 vocab의 표면형과 미완성 바이트를 복원한다."""
    def __init__(self, decoder):
        self.byte_decoder = BbpeBytesDecoder()
        config = json.loads(decoder.__getstate__()) if decoder is not None else None
        self.steps = list(self._steps(config))

    def _steps(self, config):
        if config is None:
            return
        kind = config['type']
        if kind == 'Sequence':
            for child in config['decoders']:
                yield from self._steps(child)
        elif kind in ('ByteLevel', 'ByteFallback', 'WordPiece', 'Metaspace'):
            yield config, None
        elif kind == 'Strip' and config['content'] == ' ':
            # 문장 시작/끝의 공백 제거는 개별 vocab 분석에는 적용하지 않는다.
            return
        else:
            # Replace의 정규식 등은 재구현하지 않고 원래 Rust 디코더를 사용한다.
            native = decoders.Sequence([])
            native.__setstate__(json.dumps(config).encode('utf-8'))
            yield config, native

    def decode(self, vocab):
        for config, native in self.steps:
            kind = config['type']
            if kind == 'ByteLevel':
                vocab = self.byte_decoder.decode(vocab)
            elif kind == 'ByteFallback':
                # 개별 byte fallback 토큰도 U+FFFD로 손실시키지 않는다.
                if re.fullmatch(r'<0x[0-9a-fA-F]{2}>', vocab):
                    vocab = bytes([int(vocab[3:5], 16)]).decode('utf-8', errors='backslashreplace')
            elif kind == 'WordPiece':
                # 단어 시작 경계를 BBPE/Metaspace와 비교할 수 있도록 공백으로 표시한다.
                prefix = config['prefix']
                if prefix and vocab.startswith(prefix):
                    vocab = vocab[len(prefix):]
                else:
                    vocab = ' ' + vocab
            elif kind == 'Metaspace':
                vocab = vocab.replace(config['replacement'], ' ')
            else:
                vocab = native.decode([vocab])
        return vocab


def markdown_cell(value):
    text = escape(str(value), quote=False)
    for char in ('\\', '`', '*', '_', '[', ']', '|'):
        text = text.replace(char, '\\' + char)
    return text.replace('\r', '&#13;').replace('\n', '<br>')

BYTE_RUN = re.compile(r'(?:\\x[0-9a-fA-F]{2})+')

def char_length(vocab):
    # 연속된 미완성 UTF-8 바이트 표기(\xNN)는 한 덩어리를 한 글자로 계산
    return len(BYTE_RUN.sub('?', vocab))

def average_length(vocabs):
    return sum(map(char_length, vocabs)) / len(vocabs) if vocabs else 0.0

def is_hangul_fragment(run):
    """\\xNN 바이트 배열이 완성형 한글(U+AC00–U+D7A3)의 UTF-8 앞부분인지 판별"""
    data = bytes.fromhex(run.replace('\\x', ''))
    if not 0xEA <= data[0] <= 0xED:
        return False
    if len(data) == 1:
        return True
    return (0xEA, 0xB0) <= (data[0], data[1]) <= (0xED, 0x9E)

def is_incomplete_korean(vocab):
    """한글과 미완성 바이트가 섞였거나, 한글 음절의 앞부분 바이트를 포함한 vocab"""
    runs = BYTE_RUN.findall(vocab)
    if not runs:
        return False
    return bool(re.search(r'[가-힣]', vocab)) or any(map(is_hangul_fragment, runs))

def repeated_unit(vocab):
    """같은 단위가 세 번 이상 반복되어서만 이루어진 vocab이면 (반복 단위, 반복 횟수)를 반환"""
    text = vocab.strip()
    match = re.fullmatch(r'(.+?)\1{2,}', text)
    if not match or char_length(text) < 4:
        return None
    unit = match.group(1)
    return unit, len(text) // len(unit)

def print_korean_vocab_shapes(fout, all_normal_vocabs, korean_vocabs, top_n):
    print('## 한글 vocab 형태\n', file=fout)
    lengths = {vocab: char_length(vocab.strip()) for vocab in korean_vocabs}
    multi_word = [vocab for vocab in korean_vocabs if ' ' in vocab.strip()]
    repeated = [(vocab, unit) for vocab in korean_vocabs if (unit := repeated_unit(vocab))]
    fragments = [vocab for vocab in all_normal_vocabs if vocab not in lengths and is_incomplete_korean(vocab)]
    incomplete = [vocab for vocab in korean_vocabs if is_incomplete_korean(vocab)] + fragments
    korean_related = len(korean_vocabs) + len(fragments)
    print_markdown_table(fout, ('항목', '값'), (
        ('5글자 이상 한글 vocab 수', f'{sum(length >= 5 for length in lengths.values()):,}'),
        ('10글자 이상 한글 vocab 수', f'{sum(length >= 10 for length in lengths.values()):,}'),
        ('여러 어절로 된 한글 vocab 수', f'{len(multi_word):,}'),
        ('반복 패턴 한글 vocab 수', f'{len(repeated):,}'),
        ('불완전 한글 vocab 수', f'{len(incomplete):,}'),
        ('불완전 한글 vocab 비율', f'{len(incomplete) / korean_related:.2%}' if korean_related else '0.00%'),
    ))
    print('글자 수는 앞뒤 공백을 제외하고 계산합니다. '
          '여러 어절로 된 vocab은 앞뒤를 제외한 가운데에 공백이 있는 vocab입니다. '
          '반복 패턴 vocab은 같은 단위가 세 번 이상 반복되어서만 이루어진 4글자 이상의 vocab입니다. '
          '불완전 한글 vocab은 한글과 미완성 UTF-8 바이트가 섞여 있거나 한글 음절의 앞부분 바이트를 포함한 vocab이며, '
          '비율의 분모는 한글 포함 vocab 수에 한글 없이 한글 음절 앞부분 바이트를 포함한 vocab 수를 더한 값입니다. '
          '음절 뒷부분 바이트만 있는 경우는 원래 문자를 알 수 없으므로 세지 않습니다.\n', file=fout)

    print(f'### 가장 긴 한글 vocab Top {top_n}\n', file=fout)
    longest = sorted(korean_vocabs, key=lambda vocab: lengths[vocab], reverse=True)[:top_n]
    print_markdown_table(fout, ('순위', 'vocab', '글자 수'), [
        (rank, (vocab,), lengths[vocab]) for rank, vocab in enumerate(longest, 1)
    ], vocab_column=1)

    print(f'### 반복 패턴 한글 vocab Top {top_n}\n', file=fout)
    if not repeated:
        print('반복 패턴 한글 vocab이 없습니다.\n', file=fout)
        return
    repeated.sort(key=lambda item: lengths[item[0]], reverse=True)
    print_markdown_table(fout, ('순위', 'vocab', '반복 단위', '반복 횟수'), [
        (rank, (vocab,), unit, count) for rank, (vocab, (unit, count)) in enumerate(repeated[:top_n], 1)
    ], vocab_column=1)

def print_markdown_table(fout, headers, rows, vocab_column=None):
    print('| ' + ' | '.join(headers) + ' |', file=fout)
    print('| ' + ' | '.join('---' for _ in headers) + ' |', file=fout)
    for row in rows:
        cells = [
            ', '.join(markdown_code(vocab).replace('|', r'\|') for vocab in sorted(cell))
            if index == vocab_column else markdown_cell(cell)
            for index, cell in enumerate(row)
        ]
        print('| ' + ' | '.join(cells) + ' |', file=fout)
    print(file=fout)

def markdown_code(value):
    text = ''.join(char if char.isprintable() else repr(char)[1:-1] for char in value)
    # 화면 표시용 공백만 NBSP로 바꿈
    text = text.replace(' ', '\u00a0')
    delimiter = '`' * (max((len(run) for run in re.findall(r'`+', text)), default=0) + 1)
    if text.startswith('`') or text.endswith('`'):
        text = ' ' + text + ' '
    return delimiter + text + delimiter

def print_morph_table(fout, ranked_morphs, count_label, show_examples):
    headers = ['순위', '형태소/품사', count_label]
    if show_examples:
        headers.append('vocab 예시')
    rows = []
    for rank, (morph, examples) in enumerate(ranked_morphs, 1):
        row = [rank, morph, f'{len(examples):,}']
        if show_examples:
            row.append(examples)
        rows.append(row)
    print_markdown_table(fout, headers, rows, vocab_column=3 if show_examples else None)

def print_morph_rankings(fout, title, morph_examples, prefix_examples, top_n, example_sections, include_s):
    candidates = {
        morph: examples for morph, examples in morph_examples.items()
        if include_s or not morph.endswith('/S')
    }
    frequent = sorted(candidates.items(), key=lambda item: len(item[1]), reverse=True)[:top_n]
    prefix = sorted(
        ((morph, examples) for morph, examples in prefix_examples.items() if morph in candidates),
        key=lambda item: len(item[1]), reverse=True,
    )[:top_n]
    geo = sorted(
        ((morph, (len(examples) * max(1, len(prefix_examples.get(morph, ())))) ** 0.5)
         for morph, examples in candidates.items()),
        key=lambda item: item[1], reverse=True,
    )[:top_n]

    print(f'## {title} Top {top_n}\n', file=fout)
    print('### 전체 위치 빈도\n', file=fout)
    print_morph_table(fout, frequent, '포함 vocab 수', 'all' in example_sections)
    print('### 첫 위치 빈도\n', file=fout)
    print_morph_table(fout, prefix, '첫 위치 vocab 수', 'prefix' in example_sections)
    print('### 기하평균 점수\n', file=fout)
    show_examples = 'geo' in example_sections
    headers = ['순위', '형태소/품사', '점수', '포함 vocab 수', '첫 위치 vocab 수']
    if show_examples:
        headers.append('vocab 예시')
    rows = []
    for rank, (morph, score) in enumerate(geo, 1):
        row = [rank, morph, f'{score:.2f}', f'{len(candidates[morph]):,}',
               f'{len(prefix_examples.get(morph, ())):,}']
        if show_examples:
            row.append(candidates[morph])
        rows.append(row)
    print_markdown_table(fout, headers, rows, vocab_column=5 if show_examples else None)

def print_requested_morphemes(fout, queries, morph_examples):
    print('## 관심 형태소 vocab\n', file=fout)
    rows = []
    for query in dict.fromkeys(queries):
        matches = sorted(
            morph for morph in morph_examples
            if morph == query or morph.rsplit('/', 1)[0] == query
        )
        if not matches:
            rows.append((query, '일치하는 형태소 없음', '0', ()))
        for morph in matches:
            examples = morph_examples[morph]
            rows.append((query, morph, f'{len(examples):,}', examples))
    print_markdown_table(
        fout, ('조회 형태소', '형태소/품사', '포함 vocab 수', 'vocab 예시'), rows,
        vocab_column=3,
    )

def compile_pattern(value):
    try:
        return re.compile(value)
    except re.error as error:
        raise argparse.ArgumentTypeError(f'잘못된 정규식 {value!r}: {error}') from error

def print_requested_patterns(fout, patterns, all_vocabs):
    print('## 정규식 검색 vocab\n', file=fout)
    rows = []
    for pattern in dict.fromkeys(patterns):
        examples = [vocab for vocab in all_vocabs if pattern.search(vocab)]
        rows.append((pattern.pattern, f'{len(examples):,}', examples))
    print_markdown_table(
        fout, ('정규식', '포함 vocab 수', 'vocab 예시'), rows, vocab_column=2,
    )

def normalize_morphs(tokens, concat_nouns=True):
    morphs = []
    for token in tokens:
        tag = 'V' if token.tag in ('XSV', 'XSA') else token.tag[0]
        if concat_nouns and tag == 'X':
            tag = 'N'
        if concat_nouns and tag == 'N' and morphs and morphs[-1][1] == 'N':
            morphs[-1] = (morphs[-1][0] + token.form, tag)
        else:
            morphs.append((token.form, tag))
    return tuple(form + '/' + tag for form, tag in morphs)

SAMPLE_DIR = Path(__file__).resolve().parent.parent / 'samples'

def read_sample(path):
    with open(path, encoding='utf-8', newline='') as f:
        return f.read()

def print_sample_token_stats(fout, encode, samples):
    print('## 샘플 문서 토큰화 통계\n', file=fout)
    rows = []
    for lang, text in samples.items():
        tokens = len(encode(text))
        n_bytes = len(text.encode('utf-8'))
        n_words = len(text.split())
        rows.append((
            lang, f'{len(text):,}', f'{n_bytes:,}', f'{n_words:,}', f'{tokens:,}',
            f'{len(text) / tokens:.2f}' if tokens else '0.00',
            f'{n_bytes / tokens:.2f}' if tokens else '0.00',
            f'{tokens / n_words:.2f}' if n_words else '0.00',
        ))
    print_markdown_table(fout, (
        '언어', '글자 수', 'UTF-8 바이트 수', '어절 수', '토큰 수',
        '토큰당 평균 글자 수', '토큰당 평균 바이트 수', '어절당 평균 토큰 수',
    ), rows)
    print('토큰 수는 BOS/EOS 등 특수 토큰을 제외하고 계산하며, 글자 수와 바이트 수에는 공백과 줄바꿈 문자를 포함합니다. '
          '어절은 공백 문자로 나눈 단위이며 영어에서는 단어에 해당합니다. '
          '언어마다 글자 하나에 담기는 정보량이 다르므로 토큰당 글자/바이트 수는 같은 언어 안에서 토크나이저끼리 비교할 때 사용하는 것이 적절합니다.\n', file=fout)

def component_steps(component):
    """normalizer/pre_tokenizer 설정을 Sequence를 펼친 단계 목록으로 반환"""
    if component is None:
        return []
    config = json.loads(component.__getstate__())
    def flatten(config):
        if config['type'] == 'Sequence':
            for child in config.get('normalizers') or config.get('pretokenizers') or []:
                yield from flatten(child)
        else:
            yield config
    return list(flatten(config))

def describe_step(config):
    kind = config['type']
    pattern = config.get('pattern', {})
    if kind == 'Replace' and 'String' in pattern:
        return f"Replace({pattern['String']!r}→{config['content']!r})"
    if kind == 'Split':
        if 'Regex' in pattern:
            return 'Split(정규식)'
        return f"Split({pattern.get('String')!r})"
    if kind == 'ByteLevel' and config.get('use_regex'):
        return 'ByteLevel(GPT-2 정규식 분할 포함)'
    if kind == 'Metaspace':
        return f"Metaspace(공백→{config['replacement']!r})"
    if kind == 'BertPreTokenizer':
        return 'BertPreTokenizer(공백·구두점 분할)'
    return kind

def describe_tokenizer(backend):
    model = type(backend.model).__name__
    pre_steps = component_steps(backend.pre_tokenizer)
    if any(step['type'] == 'ByteLevel' for step in pre_steps):
        unit, method = 'UTF-8 바이트 (byte-level)', f'Byte-level {model}'
    elif getattr(backend.model, 'byte_fallback', False):
        unit, method = '유니코드 문자 + 미등록 문자는 UTF-8 바이트로 분해 (byte fallback)', f'{model} (byte fallback)'
    else:
        unit, method = '유니코드 문자 (미등록 문자는 UNK)', model
    return {
        '방식': method,
        '기본 단위': unit,
        '정규화': ' → '.join(map(describe_step, component_steps(backend.normalizer))) or '없음',
        '사전 분할': ' → '.join(map(describe_step, pre_steps)) or '없음',
    }

def load_vocab(source):
    """실제 vocab 수, ID 순서의 일반 vocab 표면형, 텍스트 인코딩 함수, tokenizer 방식 정보를 반환"""
    if source.startswith('tiktoken:'):
        name = source.removeprefix('tiktoken:')
        if not name:
            raise ValueError('Wrong tiktoken model name')
        try:
            import tiktoken
        except ImportError as error:
            raise ImportError('tiktoken is required.') from error
        if name not in tiktoken.list_encoding_names():
            raise ValueError(
                f'Unknown tiktoken encoding: {name}. '
                f'Available list: {", ".join(tiktoken.list_encoding_names())}'
            )
        encoding = tiktoken.get_encoding(name)
        token_bytes = sorted(encoding.token_byte_values(), key=encoding.encode_single_token)
        vocab_count = len(token_bytes) + len(encoding.special_tokens_set)
        return (
            vocab_count, [raw.decode('utf-8', errors='backslashreplace') for raw in token_bytes],
            encoding.encode_ordinary, {
                '방식': 'Byte-level BPE (tiktoken)',
                '기본 단위': 'UTF-8 바이트 (byte-level)',
                '정규화': '없음',
                '사전 분할': 'Split(정규식)',
            },
        )

    tokenizer = AutoTokenizer.from_pretrained(source, trust_remote_code=True)
    backend = getattr(tokenizer, 'backend_tokenizer', None)
    if backend is None:
        raise ValueError('Only tokenizers with FastTokenizer backend is supported.')

    decoder = VocabDecoder(backend.decoder)
    vocab = tokenizer.get_vocab()
    added_tokens = getattr(tokenizer, 'added_tokens_decoder', {})
    normal_vocabs = []
    for token, index in sorted(vocab.items(), key=lambda item: item[1]):
        if index in added_tokens:
            continue
        decoded = decoder.decode(token)
        if decoded:
            normal_vocabs.append(decoded)
    return (
        len(vocab), normal_vocabs, lambda text: tokenizer.encode(text, add_special_tokens=False),
        describe_tokenizer(backend),
    )


def main(args):
    vocab_count, all_normal_vocabs, encode, tokenizer_info = load_vocab(args.tokenizer)
    samples = {
        '한국어': read_sample(args.ko_sample),
        '영어': read_sample(args.en_sample),
    }
    all_korean_vocabs = [vocab for vocab in all_normal_vocabs if re.search(r'[가-힣]', vocab)]

    kiwi = Kiwi(num_workers=4)
    kiwi.add_re_word(r'(\\x[0-9a-fA-F]{2})+', 'W_SERIAL')
    morph_examples = defaultdict(list)
    prefix_morph_examples = defaultdict(list)
    for vocab, tokens in zip(all_korean_vocabs, kiwi.tokenize(all_korean_vocabs)):
        tokens = normalize_morphs(tokens, concat_nouns=args.concat_nouns)
        for morph in dict.fromkeys(tokens):
            morph_examples[morph].append(vocab)
        if tokens:
            prefix_morph_examples[tokens[0]].append(vocab)

    top_n = max(0, args.morpheme_top_n)
    example_sections = set(args.vocab_examples)

    output = open(args.output, 'w', encoding='utf-8') if args.output else nullcontext(sys.stdout)
    with output as fout:
        print('# Tokenizer 한국어 분포 분석\n', file=fout)
        print(f'분석 대상: {markdown_cell(args.tokenizer)}\n', file=fout)
        print_markdown_table(fout, ('항목', '값'), tokenizer_info.items())
        print('## 전체 통계\n', file=fout)
        korean_ratio = len(all_korean_vocabs) / vocab_count if vocab_count else 0.0
        print_markdown_table(fout, ('항목', '값'), (
            ('전체 vocab 수', f'{vocab_count:,}'),
            ('특수 토큰 수', f'{vocab_count - len(all_normal_vocabs):,}'),
            ('일반 vocab 수', f'{len(all_normal_vocabs):,}'),
            ('한글 포함 vocab 수', f'{len(all_korean_vocabs):,}'),
            ('한글 포함 vocab 비율', f'{korean_ratio:.2%}'),
            ('한글 포함 vocab의 고유 형태소 수', f'{len(morph_examples):,}'),
            ('한글 포함 vocab 대비 고유 형태소 수 비율', f'{len(morph_examples) / len(all_korean_vocabs):.2}' if all_korean_vocabs else '0.00'),
            ('전체 vocab 평균 글자 수', f'{average_length(all_normal_vocabs):.2f}'),
            ('한글 포함 vocab 평균 글자 수', f'{average_length(all_korean_vocabs):.2f}'),
        ))
        print('한글 포함 여부는 완성형 한글(가–힣)을 기준으로 합니다. '
              '평균 글자 수에는 공백을 포함하며, 연속된 미완성 UTF-8 바이트 배열은 한 덩어리를 한 글자로 계산합니다.\n', file=fout)

        print_sample_token_stats(fout, encode, samples)
        print_korean_vocab_shapes(fout, all_normal_vocabs, all_korean_vocabs, max(0, args.vocab_top_n))

        print_morph_rankings(
            fout, '전체 형태소', morph_examples, prefix_morph_examples,
            top_n, example_sections, args.include_s,
        )
        noun_examples = {
            morph: examples for morph, examples in morph_examples.items() if morph.endswith('/N')
        }
        print_morph_rankings(
            fout, '명사', noun_examples, prefix_morph_examples,
            top_n, example_sections, args.include_s,
        )
        if args.morphemes:
            print_requested_morphemes(fout, args.morphemes, morph_examples)
        if not morph_examples:
            print('분석할 형태소가 없습니다.\n', file=fout)
        if args.pattern:
            print_requested_patterns(fout, args.pattern, all_normal_vocabs)

if __name__ == '__main__':
    import argparse    
    parser = argparse.ArgumentParser()
    parser.add_argument('tokenizer', help='tokenizer_name_or_path to huggingface or tiktoken:encoding (ex: tiktoken:o200k_base)')
    parser.add_argument('--output')
    parser.add_argument('--vocab-examples', nargs='*', choices=('all', 'prefix', 'geo'), default=['prefix'],)
    parser.add_argument('--morpheme-top-n', type=int, default=20)
    parser.add_argument('--vocab-top-n', type=int, default=20)
    parser.add_argument('--morphemes', nargs='+', action='extend', default=[], metavar='MORPH')
    parser.add_argument('--pattern', nargs='+', action='extend', type=compile_pattern, default=[], metavar='REGEX')
    parser.add_argument('--no-concat-nouns', dest='concat_nouns', action='store_false')
    parser.add_argument('--include-s', action='store_true')
    parser.add_argument('--ko-sample', metavar='FILE', default=SAMPLE_DIR / 'ko.txt')
    parser.add_argument('--en-sample', metavar='FILE', default=SAMPLE_DIR / 'en.txt')
    main(parser.parse_args())
