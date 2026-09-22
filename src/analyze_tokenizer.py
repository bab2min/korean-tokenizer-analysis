import json
import re
import sys
from contextlib import nullcontext
from html import escape
from collections import defaultdict

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

def average_length(vocabs):
    # 연속된 미완성 UTF-8 바이트 표기(\xNN)는 한 덩어리를 한 글자로 계산
    lengths = (len(re.sub(r'(?:\\x[0-9a-fA-F]{2})+', '?', vocab)) for vocab in vocabs)
    return sum(lengths) / len(vocabs) if vocabs else 0.0

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

def load_vocab(source):
    """실제 vocab 수와 ID 순서의 일반 vocab 표면형을 반환"""
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
        return vocab_count, [raw.decode('utf-8', errors='backslashreplace') for raw in token_bytes]

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
    return len(vocab), normal_vocabs


def main(args):
    vocab_count, all_normal_vocabs = load_vocab(args.tokenizer)
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
    parser.add_argument('--morphemes', nargs='+', action='extend', default=[], metavar='MORPH')
    parser.add_argument('--pattern', nargs='+', action='extend', type=compile_pattern, default=[], metavar='REGEX')
    parser.add_argument('--no-concat-nouns', dest='concat_nouns', action='store_false')
    parser.add_argument('--include-s', action='store_true')
    main(parser.parse_args())
