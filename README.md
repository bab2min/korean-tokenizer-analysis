# 언어 모델 Tokenizer 내에 포함된 한글 토큰 분석

여러 언어 모델의 tokenizer vocab에 한국어가 얼마나, 어떤 형태로 들어 있는지 분석하는 저장소입니다.
vocab 중 한글이 들어간 토큰을 골라 [Kiwi](https://github.com/bab2min/kiwipiepy) 형태소 분석기로 분석하고, 샘플 문서를 실제로 토큰화해 한국어 처리 효율을 비교합니다.

## 비교 요약

### Vocab 구성

tokenizer별 vocab 규모와 한글 vocab 비중입니다. 한글 포함 비율이 낮은 순으로 정렬했습니다.

| 모델 | 방식 | 전체 vocab 수 | 한글 포함 vocab 수 | 한글 포함 비율 | 고유 형태소 수 | 한글 vocab 평균 글자 수 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| [GPT-4 (cl100k_base)](reports/tokenizer_gpt4.md) | Byte-level BPE | 100,261 | 299 | 0.30% | 248 | 1.76 |
| [DeepSeek-V4](reports/tokenizer_deepseek_v4.md) | Byte-level BPE | 129,280 | 1,131 | 0.87% | 731 | 1.93 |
| [Gemma 2 (mmBERT-base)](reports/tokenizer_gemma2.md) | BPE (byte fallback) | 256,000 | 2,295 | 0.90% | 1,755 | 1.42 |
| [GPT-5 (o200k_base)](reports/tokenizer_gpt5.md) | Byte-level BPE | 200,000 | 2,365 | 1.18% | 1,507 | 2.14 |
| [Gemma 4](reports/tokenizer_gemma4.md) | BPE (byte fallback) | 262,144 | 4,561 | 1.74% | 2,957 | 2.05 |
| [Muse Glimmer](reports/tokenizer_muse_glimmer.md) | Byte-level BPE | 202,048 | 5,490 | 2.72% | 3,197 | 2.56 |
| [Qwen3.8](reports/tokenizer_qwen3_8.md) | Byte-level BPE | 248,077 | 6,793 | 2.74% | 3,839 | 2.61 |
| [HyperCLOVA X SEED](reports/tokenizer_hyperclovax_seed.md) | Byte-level BPE | 110,524 | 10,067 | 9.11% | 5,287 | 2.82 |
| [Motif-3](reports/tokenizer_motif3.md) | Byte-level BPE | 220,160 | 51,410 | 23.35% | 19,312 | 3.47 |
| [Kanana-2](reports/tokenizer_kanana2.md) | Byte-level BPE | 128,256 | 31,111 | 24.26% | 11,724 | 3.16 |
| [K-EXAONE](reports/tokenizer_k_exaone_236b.md) | Byte-level BPE | 153,600 | 39,269 | 25.57% | 18,859 | 3.39 |
| [Solar Open2](reports/tokenizer_solar_open2_250b.md) | Byte-level BPE | 196,608 | 56,366 | 28.67% | 21,494 | 3.85 |
| [A.X-K2](reports/tokenizer_ax_k2.md) | Byte-level BPE | 163,840 | 65,265 | 39.83% | 21,617 | 3.42 |
| [Kiwi CoCo LM](reports/tokenizer_kiwi.md) | Byte-level BPE | 64,000 | 26,858 | 41.97% | 19,073 | 2.98 |
| [A.X-Encoder](reports/tokenizer_ax_encoder.md) | WordPiece | 50,000 | 24,084 | 48.17% | 17,501 | 2.63 |
| [KF-DeBERTa](reports/tokenizer_kf_deberta.md) | WordPiece | 130,000 | 104,522 | 80.40% | 80,239 | 3.53 |
| [KoELECTRA](reports/tokenizer_koelectra.md) | WordPiece | 35,000 | 29,021 | 82.92% | 22,175 | 3.06 |
| [KLUE RoBERTa](reports/tokenizer_klue_roberta.md) | WordPiece | 32,000 | 28,445 | 88.89% | 22,239 | 3.12 |

- 한글 포함 vocab: 완성형 한글(가–힣)이 한 글자 이상 들어 있는 일반 vocab (특수 토큰 제외)
- 고유 형태소 수: 한글 포함 vocab을 Kiwi로 분석해 얻은 서로 다른 형태소/품사 쌍의 수

### 샘플 문서 토큰화

[`samples/`](samples)의 한국어 문서(11,275 바이트, 1,031 어절)와 영어 문서(4,503 바이트, 693 단어)를 토큰화한 결과입니다. 한국어 토큰 수가 적은 순으로 정렬했습니다.

| 모델 | 한국어 토큰 수 | 한국어 어절당 토큰 수 | 한국어 토큰당 바이트 수 | 영어 토큰 수 | 영어 단어당 토큰 수 | 영어 토큰당 바이트 수 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A.X-K2 | 1,933 | 1.87 | 5.83 | 873 | 1.26 | 5.16 |
| Motif-3 | 1,940 | 1.88 | 5.81 | 685 | 0.99 | 6.57 |
| K-EXAONE | 2,001 | 1.94 | 5.63 | 748 | 1.08 | 6.02 |
| Kanana-2 | 2,030 | 1.97 | 5.55 | 860 | 1.24 | 5.24 |
| Solar Open2 | 2,041 | 1.98 | 5.52 | 853 | 1.23 | 5.28 |
| KF-DeBERTa | 2,210 | 2.14 | 5.10 | 1,123 | 1.62 | 4.01 |
| Kiwi CoCo LM | 2,367 | 2.30 | 4.76 | 906 | 1.31 | 4.97 |
| KLUE RoBERTa | 2,420 | 2.35 | 4.66 | 1,761 | 2.54 | 2.56 |
| KoELECTRA | 2,463 | 2.39 | 4.58 | 1,722 | 2.48 | 2.61 |
| HyperCLOVA X SEED | 2,485 | 2.41 | 4.54 | 901 | 1.30 | 5.00 |
| Muse Glimmer | 2,554 | 2.48 | 4.41 | 881 | 1.27 | 5.11 |
| Qwen3.8 | 2,565 | 2.49 | 4.40 | 893 | 1.29 | 5.04 |
| A.X-Encoder | 2,572 | 2.49 | 4.38 | 1,313 | 1.89 | 3.43 |
| Gemma 4 | 2,812 | 2.73 | 4.01 | 865 | 1.25 | 5.21 |
| GPT-5 (o200k_base) | 2,978 | 2.89 | 3.79 | 874 | 1.26 | 5.15 |
| DeepSeek-V4 | 3,241 | 3.14 | 3.48 | 858 | 1.24 | 5.25 |
| Gemma 2 (mmBERT-base) | 3,289 | 3.19 | 3.43 | 859 | 1.24 | 5.24 |
| GPT-4 (cl100k_base) | 4,724 | 4.58 | 2.39 | 889 | 1.28 | 5.07 |

- 토큰 수에는 BOS/EOS 등 특수 토큰을 포함하지 않습니다.
- 어절(단어)은 공백 문자로 나눈 단위입니다.

### 한글 vocab 형태

| 모델 | 5글자 이상 | 10글자 이상 | 여러 어절 | 반복 패턴 | 불완전 한글 vocab 수 | 불완전 한글 vocab 비율 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| GPT-4 (cl100k_base) | 0 | 0 | 0 | 0 | 144 | 33.88% |
| DeepSeek-V4 | 0 | 0 | 0 | 0 | 214 | 16.04% |
| Gemma 2 (mmBERT-base) | 1 | 0 | 0 | 0 | 4 | 0.17% |
| GPT-5 (o200k_base) | 7 | 0 | 0 | 0 | 253 | 9.71% |
| Gemma 4 | 20 | 0 | 0 | 0 | 4 | 0.09% |
| Muse Glimmer | 62 | 0 | 0 | 0 | 306 | 5.32% |
| Qwen3.8 | 55 | 0 | 0 | 0 | 254 | 3.60% |
| HyperCLOVA X SEED | 127 | 2 | 0 | 1 | 358 | 3.46% |
| Motif-3 | 2,282 | 5 | 174 | 0 | 408 | 0.79% |
| Kanana-2 | 770 | 1 | 0 | 1 | 395 | 1.26% |
| K-EXAONE | 3,242 | 132 | 4,766 | 0 | 381 | 0.96% |
| Solar Open2 | 7,920 | 262 | 0 | 9 | 423 | 0.75% |
| A.X-K2 | 2,943 | 4 | 0 | 12 | 451 | 0.69% |
| Kiwi CoCo LM | 209 | 0 | 0 | 1 | 367 | 1.35% |
| A.X-Encoder | 88 | 0 | 0 | 0 | 0 | 0.00% |
| KF-DeBERTa | 3,002 | 3 | 0 | 0 | 0 | 0.00% |
| KoELECTRA | 261 | 0 | 0 | 0 | 0 | 0.00% |
| KLUE RoBERTa | 261 | 0 | 0 | 0 | 0 | 0.00% |

- 글자 수는 앞뒤 공백을 빼고 세며, 연속된 미완성 UTF-8 바이트는 한 덩어리를 한 글자로 셉니다.
- **여러 어절**: 가운데에 공백이 들어 있는 한글 vocab
- **반복 패턴**: `조조조조`처럼 같은 단위가 세 번 이상 반복되어서만 이루어진 4글자 이상의 한글 vocab
- **불완전 한글 vocab**: `어\xeb\x96`처럼 한글과 미완성 UTF-8 바이트가 섞였거나, 한글 음절의 앞부분 바이트를 포함한 vocab. 비율의 분모는 한글 포함 vocab 수에 한글 음절 앞부분 바이트만 가진 vocab 수를 더한 값입니다.

### 관심 형태소: 사람, 정부

흔한 명사 `사람`과 `정부`가 얼마나 많은 vocab에 중복해서 들어 있는지 비교한 결과입니다. 각 보고서의 "관심 형태소 vocab" 표에서 가져왔습니다.

| 모델 | `사람` vocab 수 | `사람` 고유 형태 수 | `정부` vocab 수 | `정부` 고유 형태 수 |
| --- | ---: | ---: | ---: | ---: |
| GPT-4 (cl100k_base) | 0 | 0 | 0 | 0 |
| DeepSeek-V4 | 1 | 1 | 0 | 0 |
| Gemma 2 (mmBERT-base) | 1 | 1 | 0 | 0 |
| GPT-5 (o200k_base) | 2 | 2 | 2 | 1 |
| Gemma 4 | 4 | 3 | 1 | 1 |
| Muse Glimmer | 6 | 5 | 5 | 4 |
| Qwen3.8 | 7 | 6 | 5 | 4 |
| HyperCLOVA X SEED | 9 | 8 | 9 | 5 |
| Motif-3 | 30 | 25 | 15 | 9 |
| Kanana-2 | 37 | 26 | 12 | 7 |
| K-EXAONE | 39 | 33 | 13 | 9 |
| Solar Open2 | 21 | 16 | 20 | 13 |
| A.X-K2 | 44 | 35 | 15 | 9 |
| Kiwi CoCo LM | 3 | 2 | 2 | 1 |
| A.X-Encoder | 2 | 1 | 2 | 1 |
| KF-DeBERTa | 4 | 3 | 5 | 4 |
| KoELECTRA | 2 | 1 | 2 | 1 |
| KLUE RoBERTa | 2 | 1 | 2 | 1 |

- **vocab 수**: Kiwi로 분석했을 때 `사람/N`, `정부/N` 형태소가 들어 있는 vocab 수입니다. 연속된 명사는 하나로 합쳐 분석하므로 `정부기관`처럼 복합 명사 안에 들어간 경우는 세지 않습니다.
- **고유 형태 수**: 앞뒤 공백(NBSP 포함)을 제거했을 때 서로 다른 형태의 수입니다. vocab 수와의 차이는 ` 사람`과 `사람`처럼 공백 유무만 다른 중복 vocab 수입니다.

각 tokenizer에 실제로 들어 있는 vocab 전체 목록입니다. `\xa0`로 표시된 것은 vocab에 원래 들어 있는 NBSP입니다. WordPiece 방식인 A.X-Encoder, KF-DeBERTa, KoELECTRA, KLUE RoBERTa에서는 앞에 공백이 붙은 것이 단어 첫머리 토큰, 붙지 않은 것이 `##`로 시작하는 단어 중간 토큰입니다.

#### `사람`

| 모델 | vocab 수 | vocab 목록 |
| --- | ---: | --- |
| GPT-4 (cl100k_base) | 0 | 없음 |
| DeepSeek-V4 | 1 | ` 사람` |
| Gemma 2 (mmBERT-base) | 1 | ` 사람` |
| GPT-5 (o200k_base) | 2 | ` 사람`, ` 사람이` |
| Gemma 4 | 4 | ` 사람`, ` 사람은`, ` 사람이`, `사람` |
| Muse Glimmer | 6 | ` 사람`, ` 사람은`, ` 사람을`, ` 사람의`, ` 사람이`, `사람` |
| Qwen3.8 | 7 | ` 사람`, ` 사람에게`, ` 사람은`, ` 사람을`, ` 사람의`, ` 사람이`, `사람` |
| HyperCLOVA X SEED | 9 | ` 사람`, ` 사람과`, ` 사람도`, ` 사람에게`, ` 사람은`, ` 사람을`, ` 사람의`, ` 사람이`, `사람` |
| Motif-3 | 30 | ` 사람`, ` 사람과`, ` 사람과의`, ` 사람도`, ` 사람마다`, ` 사람만`, ` 사람보다`, ` 사람에`, ` 사람에게`, ` 사람에게는`, ` 사람으로`, ` 사람으로서`, ` 사람은`, ` 사람을`, ` 사람의`, ` 사람이`, ` 사람이나`, ` 사람이다`, ` 사람이라`, ` 사람이라고`, ` 사람이라면`, ` 사람이었다`, ` 사람인`, ` 사람입니다`, ` 사람처럼`, `사람`, `사람은`, `사람을`, `사람의`, `사람이` |
| Kanana-2 | 37 | ` 사람`, ` 사람과`, ` 사람과의`, ` 사람도`, ` 사람마다`, ` 사람만`, ` 사람보다`, ` 사람에`, ` 사람에게`, ` 사람에게는`, ` 사람으로`, ` 사람으로서`, ` 사람은`, ` 사람을`, ` 사람의`, ` 사람이`, ` 사람이나`, ` 사람이다`, ` 사람이라`, ` 사람이라고`, ` 사람이라는`, ` 사람이라면`, ` 사람이었다`, ` 사람인`, ` 사람입니다`, ` 사람처럼`, `\xa0사람`, `\xa0사람은`, `\xa0사람을`, `\xa0사람의`, `\xa0사람이`, `사람`, `사람과`, `사람은`, `사람을`, `사람의`, `사람이` |
| K-EXAONE | 39 | ` 다른 사람`, ` 다른 사람에게`, ` 다른 사람의`, ` 다른 사람이`, ` 두 사람`, ` 두 사람은`, ` 두 사람의`, ` 두 사람이`, ` 모든 사람이`, ` 사람`, ` 사람과`, ` 사람도`, ` 사람마다`, ` 사람에게`, ` 사람으로`, ` 사람은`, ` 사람을`, ` 사람의`, ` 사람이`, ` 사람이다`, ` 사람이라면`, ` 아는 사람`, ` 한 사람`, ` 한 사람이`, `는 사람`, `는 사람에게`, `는 사람은`, `는 사람을`, `는 사람의`, `는 사람이`, `사람`, `사람은`, `사람의`, `사람이`, `하는 사람`, `하는 사람이`, `한 사람`, `한 사람은`, `한 사람이` |
| Solar Open2 | 21 | ` 사람`, ` 사람과`, ` 사람도`, ` 사람마다`, ` 사람에`, ` 사람에게`, ` 사람에게는`, ` 사람으로`, ` 사람으로서`, ` 사람은`, ` 사람을`, ` 사람의`, ` 사람이`, ` 사람이나`, ` 사람이다`, ` 사람이라면`, `사람`, `사람은`, `사람을`, `사람의`, `사람이` |
| A.X-K2 | 44 | ` 사람`, ` 사람과`, ` 사람과의`, ` 사람도`, ` 사람마다`, ` 사람만`, ` 사람만이`, ` 사람보다`, ` 사람에`, ` 사람에게`, ` 사람에게는`, ` 사람에게도`, ` 사람으로`, ` 사람으로서`, ` 사람은`, ` 사람을`, ` 사람의`, ` 사람이`, ` 사람이고`, ` 사람이나`, ` 사람이다`, ` 사람이라`, ` 사람이라고`, ` 사람이라는`, ` 사람이라도`, ` 사람이라면`, ` 사람이야`, ` 사람이었다`, ` 사람인`, ` 사람인데`, ` 사람인지`, ` 사람입니다`, ` 사람처럼`, ` 사람한테`, ` 한사람`, `사람`, `사람과`, `사람도`, `사람마다`, `사람에게`, `사람은`, `사람을`, `사람의`, `사람이` |
| Kiwi CoCo LM | 3 | ` 사람`, ` 한사람`, `사람` |
| A.X-Encoder | 2 | ` 사람`, `사람` |
| KF-DeBERTa | 4 | ` 사람`, ` 사람됨`, ` 사람인`, `사람` |
| KoELECTRA | 2 | ` 사람`, `사람` |
| KLUE RoBERTa | 2 | ` 사람`, `사람` |

#### `정부`

| 모델 | vocab 수 | vocab 목록 |
| --- | ---: | --- |
| GPT-4 (cl100k_base) | 0 | 없음 |
| DeepSeek-V4 | 0 | 없음 |
| Gemma 2 (mmBERT-base) | 0 | 없음 |
| GPT-5 (o200k_base) | 2 | ` 정부`, `정부` |
| Gemma 4 | 1 | ` 정부` |
| Muse Glimmer | 5 | ` 정부`, ` 정부가`, ` 정부는`, ` 정부의`, `정부` |
| Qwen3.8 | 5 | ` 정부`, ` 정부가`, ` 정부는`, ` 정부의`, `정부` |
| HyperCLOVA X SEED | 9 | ` 정부`, ` 정부가`, ` 정부는`, ` 정부와`, ` 정부의`, `정부`, `정부가`, `정부는`, `정부의` |
| Motif-3 | 15 | ` 정부`, ` 정부가`, ` 정부는`, ` 정부도`, ` 정부를`, ` 정부에`, ` 정부에서`, ` 정부와`, ` 정부의`, `정부`, `정부가`, `정부는`, `정부에`, `정부와`, `정부의` |
| Kanana-2 | 12 | ` 정부`, ` 정부가`, ` 정부는`, ` 정부에`, ` 정부에서`, ` 정부와`, ` 정부의`, `\xa0정부`, `정부`, `정부가`, `정부는`, `정부의` |
| K-EXAONE | 13 | ` 정부`, ` 정부가`, ` 정부는`, ` 정부에`, ` 정부에서`, ` 정부에서 발급한`, ` 정부에서 발급한 사진이 부착된`, ` 정부와`, ` 정부의`, `정부`, `정부가`, `정부는`, `정부의` |
| Solar Open2 | 20 | ` 정부`, ` 정부가`, ` 정부나`, ` 정부는`, ` 정부도`, ` 정부로부터`, ` 정부를`, ` 정부에`, ` 정부에서`, ` 정부에서는`, ` 정부와`, ` 정부의`, `(정부`, `정부`, `정부가`, `정부는`, `정부에`, `정부에서`, `정부와`, `정부의` |
| A.X-K2 | 15 | ` 정부`, ` 정부가`, ` 정부는`, ` 정부도`, ` 정부를`, ` 정부에`, ` 정부에서`, ` 정부와`, ` 정부의`, `정부`, `정부가`, `정부는`, `정부에서`, `정부와`, `정부의` |
| Kiwi CoCo LM | 2 | ` 정부`, `정부` |
| A.X-Encoder | 2 | ` 정부`, `정부` |
| KF-DeBERTa | 5 | ` 이정부`, ` 정부`, ` 정분`, `정부`, `정부지` |
| KoELECTRA | 2 | ` 정부`, `정부` |
| KLUE RoBERTa | 2 | ` 정부`, `정부` |

KF-DeBERTa의 `정분`은 Kiwi가 `정부/N`으로 잘못 분석한 경우로, 실제로는 `정부`와 관계없는 단어입니다.

### 스팸성 키워드

웹 크롤링 데이터에 흔한 광고·스팸 키워드(`출장|사이트|마사지|추천|소개팅|만남|콜걸|안마|채팅|업소|성인|카지노|놀이터|오피|대출|다운로드`)가 vocab에 얼마나 들어 있는지 비교한 결과입니다.

| 모델 | 정규식 매치 vocab 수 | 스팸성 vocab 수 | 스팸성 vocab 예시 |
| --- | ---: | ---: | --- |
| K-EXAONE | 128 | 41 | `안마 맛사지 페이만남 대행`, `여대생출장마사지`, `온라인 카지노`, `출장타이마사지` |
| HyperCLOVA X SEED | 63 | 39 | `동콜걸출장마사지`, `동출장맛사지후기`, `동출장만남후기`, `사설놀이터` |
| Muse Glimmer | 42 | 17 | `여대생출장마사지`, `성인출장마사지`, `구출장마사지`, `출장아가씨` |
| GPT-5 (o200k_base) | 15 | 3 | `출장안마`, `출장샵` |
| KF-DeBERTa | 74 | 2 | `콜걸`, `야동` |
| Solar Open2 | 138 | 0 | |
| A.X-K2 | 97 | 0 | |
| Motif-3 | 95 | 0 | |
| Kanana-2 | 54 | 0 | |
| KLUE RoBERTa | 27 | 0 | |
| KoELECTRA | 26 | 0 | |
| Kiwi CoCo LM | 25 | 0 | |
| A.X-Encoder | 20 | 0 | |
| Qwen3.8 | 15 | 0 | |
| Gemma 4 | 3 | 0 | |
| GPT-4 (cl100k_base) | 0 | 0 | |
| Gemma 2 (mmBERT-base) | 0 | 0 | |
| DeepSeek-V4 | 0 | 0 | |

- **정규식 매치 vocab 수**: 위 정규식에 걸리는 vocab 수로, 각 보고서의 "정규식 검색 vocab"과 같은 값입니다. `추천드립니다`, `주택담보대출`, `웹사이트`, `오피스텔`처럼 평범한 단어도 함께 걸리므로 이 값만으로 스팸 오염도를 판단할 수는 없습니다. Solar Open2의 매치 138개 중 67개는 `매출채권담보대출` 같은 금융 용어의 `대출`입니다.
- **스팸성 vocab 수**: `출장마사지`, `콜걸`, `토토사이트`, `먹튀검증`처럼 광고 문구에서만 쓰이는 합성어로 좁혀서 센 값입니다. `마사지`, `카지노`, `놀이터`처럼 단독으로도 쓰이는 단어는 제외했습니다.
- HyperCLOVA X SEED의 `동출장`, `면출장`, `역출장`은 "○○동/면/역 출장마사지" 같은 지역명 결합 광고 문구에서 나온 조각입니다. 이런 스팸 문서가 tokenizer 학습 데이터에 대량으로 섞여 있었다는 뜻입니다.
- Muse Glimmer는 한글 vocab이 5,490개로 적은 편인데도 스팸성 vocab이 17개입니다. 가장 긴 한글 vocab 1위가 `여대생출장마사지`(8글자)이고, 2위와 5위도 `출장타이마사지`, `성인출장마사지`입니다. 한글 vocab이 적은 다국어 tokenizer에서는 GPT-5(3개)를 제외하면 이런 vocab이 거의 없는 것과 대조적입니다.

### 드문 한글 음절 분절

`걁`, `겼`, `긂`, `깄`, `뇄`, `렜`, `뢔`, `뢨`, `붴`, `뻤`, `쌘`, `얬`, `칢`, `텼`, `퉜`, `홥` 16개의 잘 쓰이지 않는 한글 음절을 각각 단독으로 토큰화한 결과입니다.

| 모델 | 한 토큰으로 처리된 음절 수 | UNK로 처리된 음절 수 | 음절당 평균 토큰 수 | 한 토큰으로 처리된 음절 | `퉜`의 분절 결과 |
| --- | ---: | ---: | ---: | --- | --- |
| GPT-4 (cl100k_base) | 0 | - | 2.44 | 없음 | `\xed`, `\x89`, `\x9c` |
| DeepSeek-V4 | 0 | - | 2.38 | 없음 | `\xed`, `\x89`, `\x9c` |
| Gemma 2 (mmBERT-base) | 0 | 0 | 3.75 | 없음 | ` `, `\xed`, `\x89`, `\x9c` |
| GPT-5 (o200k_base) | 1 | - | 2.31 | `겼` | `\xed`, `\x89`, `\x9c` |
| Gemma 4 | 4 | 0 | 2.50 | `겼`, `렜`, `뢨`, `뻤` | `\xed`, `\x89`, `\x9c` |
| Muse Glimmer | 1 | - | 2.19 | `겼` | `\xed`, `\x89`, `\x9c` |
| Qwen3.8 | 1 | - | 2.06 | `겼` | `\xed`, `\x89`, `\x9c` |
| HyperCLOVA X SEED | 1 | 0 | 2.12 | `겼` | `\xed`, `\x89`, `\x9c` |
| Motif-3 | 2 | - | 2.00 | `겼`, `뻤` | `\xed\x89`, `\x9c` |
| Kanana-2 | 2 | - | 2.06 | `겼`, `뻤` | `\xed`, `\x89`, `\x9c` |
| K-EXAONE | 2 | 0 | 2.00 | `겼`, `뻤` | `\xed\x89`, `\x9c` |
| Solar Open2 | 1 | 0 | 2.06 | `겼` | `\xed\x89`, `\x9c` |
| A.X-K2 | 2 | 0 | 2.00 | `겼`, `뻤` | `\xed\x89`, `\x9c` |
| Kiwi CoCo LM | 2 | 0 | 2.06 | `겼`, `뻤` | `\xed`, `\x89`, `\x9c` |
| A.X-Encoder | 16 | 0 | 1.00 | `걁`, `겼`, `긂`, `깄`, `뇄`, `렜`, `뢔`, `뢨`, `붴`, `뻤`, `쌘`, `얬`, `칢`, `텼`, `퉜`, `홥` | ` 퉜` |
| KF-DeBERTa | 6 | 10 | 1.00 | `겼`, `렜`, `뢨`, `뻤`, `텼`, `퉜` | ` 퉜` |
| KoELECTRA | 6 | 10 | 1.00 | `겼`, `깄`, `뻤`, `쌘`, `텼`, `퉜` | ` 퉜` |
| KLUE RoBERTa | 2 | 14 | 1.00 | `겼`, `뻤` | `[UNK]` |

- **UNK로 처리된 음절 수**: `-`는 tokenizer에 UNK 토큰이 정의되어 있지 않다는 뜻입니다. byte-level BPE와 byte fallback BPE는 모든 문자를 바이트로 나타낼 수 있어서 UNK가 나오지 않습니다.
- UNK로 처리된 음절은 토큰이 하나여도 원래 정보가 사라지므로 "한 토큰으로 처리된 음절 수"에 넣지 않았습니다.
- `\xNN`은 한 음절의 UTF-8 바이트 조각입니다. Gemma 2는 음절 앞에 공백 토큰(`▁`)을 항상 붙이므로 토큰이 하나 더 많습니다.

### 형태소 경계 일치도

한국어 샘플 문서를 Kiwi로 형태소 분석한 경계와 각 tokenizer의 토큰 경계가 얼마나 일치하는지 비교한 결과입니다. 어절 사이의 경계를 포함한 **전체 경계**(형태소 경계 2,305개)와 어절 안쪽만 본 **단어 내 경계**(형태소 경계 1,281개) 두 가지로 평가했으며, 단어 내 경계 F1이 높은 순으로 정렬했습니다.

| 모델 | 음절 중간 토큰 경계 수 | 전체 Precision | 전체 Recall | 전체 F1 | 단어 내 Precision | 단어 내 Recall | 단어 내 F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| KLUE RoBERTa | 0 | 87.19% | 91.54% | 89.31% | 78.19% | 84.78% | 81.35% |
| KF-DeBERTa | 0 | 91.49% | 87.72% | 89.57% | 84.65% | 77.91% | 81.14% |
| KoELECTRA | 0 | 85.95% | 91.84% | 88.80% | 76.33% | 85.32% | 80.58% |
| A.X-Encoder | 0 | 83.48% | 93.15% | 88.05% | 72.87% | 87.67% | 79.59% |
| Kiwi CoCo LM | 27 | 84.15% | 84.56% | 84.35% | 71.98% | 72.21% | 72.10% |
| K-EXAONE | 3 | 81.20% | 68.76% | 74.47% | 66.17% | 54.96% | 60.04% |
| Gemma 2 (mmBERT-base) | 6 | 63.89% | 86.90% | 73.64% | 46.53% | 76.42% | 57.84% |
| GPT-5 (o200k_base) | 97 | 65.75% | 83.95% | 73.74% | 47.65% | 71.12% | 57.06% |
| Gemma 4 | 6 | 67.30% | 79.48% | 72.89% | 47.78% | 63.08% | 54.37% |
| DeepSeek-V4 | 206 | 61.21% | 85.16% | 71.23% | 43.15% | 73.30% | 54.32% |
| Qwen3.8 | 34 | 69.76% | 75.88% | 72.69% | 49.12% | 56.60% | 52.59% |
| Muse Glimmer | 50 | 69.52% | 76.01% | 72.62% | 48.89% | 56.83% | 52.56% |
| HyperCLOVA X SEED | 90 | 69.78% | 73.15% | 71.43% | 47.80% | 51.68% | 49.66% |
| Kanana-2 | 9 | 77.00% | 66.68% | 71.47% | 53.16% | 40.05% | 45.68% |
| Motif-3 | 7 | 79.43% | 64.82% | 71.38% | 55.87% | 37.55% | 44.91% |
| Solar Open2 | 16 | 76.18% | 66.33% | 70.92% | 51.74% | 39.42% | 44.75% |
| GPT-4 (cl100k_base) | 1,272 | 45.39% | 92.23% | 60.84% | 30.17% | 86.03% | 44.67% |
| A.X-K2 | 7 | 78.15% | 64.38% | 70.60% | 53.00% | 35.91% | 42.81% |

- **경계**: 각 형태소와 토큰이 시작하는 글자 위치입니다. 토큰 앞에 붙은 공백은 건너뛰고 첫 글자를 시작 위치로 봅니다.
- **전체 경계 / 단어 내 경계**: 전체 경계는 문서 처음과 공백 바로 뒤의 어절 첫 글자를 포함합니다. 어절 첫 글자는 거의 모든 tokenizer가 맞히므로, 단어 내 경계는 이를 빼고 어절 안에서 형태소를 얼마나 잘 나누는지만 봅니다.
- **음절 내부 형태소 경계**: `다퉜`(다투+었), `했`(하+었)처럼 한 음절 안에서 합쳐진 형태소 사이의 경계는 그 음절 위치 +0.5로 나타냅니다. 샘플 문서에는 114개가 있으며, 글자나 바이트 단위로 자르는 tokenizer는 이 경계를 맞힐 수 없으므로 Recall의 상한은 전체 경계에서 약 95.1%, 단어 내 경계에서 약 91.1%입니다.
- **음절 중간 토큰 경계**: 토큰이 음절의 UTF-8 바이트 중간에서 시작하는 경우입니다. 음절 위치에 +1/3, +2/3을 더해 나타내므로 형태소 경계와 일치하지 않습니다.
- **Precision**은 토큰 경계 중 형태소 경계와 일치한 비율, **Recall**은 형태소 경계 중 토큰 경계와 일치한 비율입니다.

## 주요 발견 사항

- **한글 vocab 수와 효율**: 한글 포함 vocab이 3만 개를 넘는 tokenizer(Kanana-2 3.1만, K-EXAONE 3.9만, Motif-3 5.1만, Solar Open2 5.6만, A.X-K2 6.5만)는 샘플 문서에서 모두 어절당 1.87 ~ 1.98토큰으로 거의 같았습니다. 이 구간에서는 한글 vocab을 더 늘려도 토큰 수가 크게 줄지 않았습니다. 반면 GPT-4(cl100k_base)는 한글 vocab이 299개뿐이라 어절당 4.58토큰으로 두 배 이상 많습니다. 한글 포함 vocab이 10만 개로 가장 많은 KF-DeBERTa는 어절당 2.14토큰으로, 한글 vocab 수에 비해 효율 이득이 크지 않았습니다. 전체 vocab이 3만 개대인 KLUE RoBERTa(2.35)와 KoELECTRA(2.39)도 Kiwi CoCo LM과 비슷한 수준입니다. 다만 두 모델은 vocab 대부분을 한국어에 써서 영어는 단어당 약 2.5토큰으로, 다른 모델(1.0 ~ 1.9)보다 크게 불리합니다. 전체 vocab이 64,000개인 Kiwi CoCo LM(어절당 2.30토큰)도 20만 개 안팎의 다국어 tokenizer(Muse Glimmer 2.48, Qwen3.8 2.49, Gemma 4 2.73, GPT-5 2.89, DeepSeek-V4 3.14)보다 한국어를 효율적으로 처리합니다.
- **한국어 vocab의 유사도**: 모델 간 한글 포함 vocab 집합의 Jaccard 유사도를 비교하면 뚜렷한 군집이 보입니다.
  - 한국어 특화 대형 vocab: Motif-3–A.X-K2 0.59, Motif-3–Kanana-2 0.52, Motif-3–Solar Open2 0.49
  - 다국어 모델: Gemma 2–Gemma 4 0.48, GPT-5–DeepSeek-V4 0.45, GPT-5–Gemma 4 0.44
  - Muse Glimmer - Qwen3.8 - HyperCLOVA X SEED: Muse Glimmer & Qwen3.8는 0.64, Qwen3.8 & HyperCLOVA X SEED는 0.61, Muse Glimmer & HyperCLOVA X SEED는 0.47로, KLUE RoBERTa–KoELECTRA(0.82) 다음으로 뚜렷한 군집입니다. 한글 vocab 수도 5,490개, 6,793개, 10,067개로 규모가 비슷합니다.
  - 소형 vocab: Kiwi CoCo LM–A.X-Encoder 0.43
  - 한국어 인코더 모델: KLUE RoBERTa–KoELECTRA 0.82로 전체에서 가장 높습니다. 두 모델은 Kiwi CoCo LM(0.58, 0.54), A.X-Encoder(0.50, 0.51)와도 비교적 가깝습니다.
  - GPT-4는 DeepSeek-V4(0.25)를 제외하면 어느 모델과도 0.12 이하입니다. 두 tokenizer 모두 한글 vocab이 적고(299개, 1,131개) `있습니다`, `합니다`처럼 아주 흔한 형태만 가지고 있어서 겹치는 부분이 상대적으로 큽니다.
  - KF-DeBERTa는 한글 vocab이 워낙 많아 어느 모델과도 0.19 이하입니다(가장 가까운 모델은 Kiwi CoCo LM 0.19, K-EXAONE 0.18).
- **긴 vocab에 드러나는 학습 데이터 성격**: 가장 긴 한글 vocab을 보면 tokenizer 학습 데이터가 어느 분야에 치우쳤는지 짐작할 수 있습니다.
  - Solar Open2: `미상환전환형조건부자본증권등발행현황`, `연결재무제표를작성하는주권상장법인` 등 기업 공시·재무 용어가 많고, 5글자 이상 한글 vocab이 7,920개로 가장 많습니다. 반복 패턴 vocab도 `찬성찬성찬성찬성찬성`, `가결가결가결가결가결`, `보통주보통주보통주보통주`처럼 주주총회 결과 공시에서 나온 것들입니다.
  - Motif-3: `포함하는 것을 특징으로 하는`, `에 도시된 바와 같이` 등 특허 명세서 문체가 vocab으로 들어가 있습니다.
  - K-EXAONE: `정보가 누락되었거나 올바르지 않나요`, `트립어드바이저는 매월 수백만 명의` 등 웹페이지 상투 문구가 많습니다. 공백을 포함한 여러 어절짜리 한글 vocab이 4,766개로 다른 모델(Motif-3 174개, 나머지 0개)보다 월등히 많습니다.
  - A.X-K2 (`십이십이십이…`, `조조조조…`)와 HyperCLOVA X SEED (`소셜그래프소셜그래프…`)에는 같은 글자열이 반복된 vocab이 있습니다. 중복 제거가 덜 된 데이터의 흔적으로 보입니다.
- **조사 결합형 vocab**: 한국어 특화 byte-level BPE는 `사람` 하나에 ` 사람에게는`, ` 사람으로서`처럼 조사·어미가 붙은 vocab을 30 ~ 44개 두고 있습니다(A.X-K2 44개, K-EXAONE 39개, Kanana-2 37개, Motif-3 30개). 같은 형태가 공백 유무만 달리해서 한 번 더 들어간 경우도 많습니다. 반면 Kiwi CoCo LM과 WordPiece 방식 모델들(A.X-Encoder, KF-DeBERTa, KoELECTRA, KLUE RoBERTa)은 `사람`, `정부`를 사실상 명사 단독형으로만 둡니다. 이 차이는 "한글 포함 vocab 대비 고유 형태소 수 비율"에도 드러납니다. 조사 결합형이 많은 A.X-K2, Kanana-2, Motif-3, Solar Open2는 0.33 ~ 0.38로 낮고, 이 모델들은 0.71 ~ 0.78로 높습니다.
- **byte-level BPE의 불완전 한글 vocab**: byte-level BPE tokenizer에는 `어\xeb\x96`처럼 한글 음절 뒤에 다음 음절의 UTF-8 바이트 일부가 붙은 vocab이 있습니다. 이런 vocab은 단독으로는 올바른 문자열로 디코딩되지 않습니다.
  - 한국어 특화 tokenizer는 이런 vocab이 350 ~ 450개로 개수는 비슷합니다. 한글 vocab 자체가 많아서 비율은 0.7 ~ 1.4%에 그칩니다.
  - 한글 vocab이 적은 GPT-4는 한글 관련 vocab의 33.88%, DeepSeek-V4는 16.04%, GPT-5는 9.71%, Muse Glimmer는 5.32%, Qwen3.8은 3.60%가 불완전한 조각입니다. 한글 음절을 온전한 단위로 배우지 못하고 바이트 조각으로 나눠 가진 셈입니다.
  - byte fallback 방식(Gemma 2, Gemma 4)은 바이트 토큰 256개만 따로 두므로 거의 0%이고, WordPiece 방식 모델들은 바이트 단위 vocab이 없어 0%입니다.
- **드문 음절 처리 방식**: 드문 한글 음절을 처리하는 방식은 tokenizer 유형에 따라 셋으로 나뉩니다.
  - byte-level BPE: 대부분의 드문 음절을 2 ~ 3개의 바이트 조각으로 나눕니다. 한국어 특화 tokenizer도 16개 중 `겼`, `뻤` 정도만 한 토큰으로 가지고 있습니다. 정보는 보존되지만 토큰 수가 늘어납니다.
  - byte fallback BPE(Gemma 2, Gemma 4): vocab에 없는 음절을 UTF-8 바이트 3개로 나눕니다. 결과적으로 byte-level BPE보다 토큰 수가 많습니다.
  - WordPiece(A.X-Encoder, KF-DeBERTa, KoELECTRA, KLUE RoBERTa): 음절이 vocab에 있으면 한 토큰, 없으면 UNK입니다. A.X-Encoder는 16개를 모두 가지고 있지만, KF-DeBERTa와 KoELECTRA는 10개, KLUE RoBERTa는 14개를 `[UNK]`로 처리해 원래 글자를 잃어버립니다. 한글 vocab 수는 KF-DeBERTa가 훨씬 많지만, 단독 음절 vocab을 얼마나 확보했는지는 별개입니다.
- **형태소 경계 일치도**: 어절 안쪽의 형태소 경계(단어 내 경계)를 가장 잘 맞히는 것은 WordPiece 방식 인코더들입니다(F1 79 ~ 81%). `사람` + `##들` + `##과`처럼 어간과 조사·접사를 따로 두기 때문입니다. byte-level BPE 중에서는 Kiwi CoCo LM(72.10%)과 K-EXAONE(60.04%)이 가장 높습니다.
  - 어절 사이의 경계까지 포함한 전체 경계로 보면 Kiwi CoCo LM과 GPT-4를 제외한 LLM tokenizer의 F1이 70 ~ 74%로 비슷합니다. 하지만 단어 내 경계만 보면 차이가 크게 벌어집니다. 한국어 토큰 효율이 가장 좋은 A.X-K2, Motif-3, Solar Open2, Kanana-2는 단어 내 F1이 43 ~ 46%로 GPT-4(44.67%)와 비슷한 최하위권이고, A.X-K2(42.81%)는 GPT-4보다도 낮습니다.
  - 이 네 모델은 단어 내 Recall이 36 ~ 40%에 그칩니다. ` 사람에게는`처럼 조사까지 붙여 한 토큰으로 두므로 어절 안의 형태소 경계를 대부분 건너뜁니다. 전체 경계에서 Precision이 76 ~ 79%로 높았던 것은 토큰이 대부분 어절 첫 글자에서 시작하기 때문입니다.
  - 한글 vocab이 적은 다국어 tokenizer(Gemma 2, GPT-5, DeepSeek-V4)는 반대로 단어 내 Recall이 71 ~ 76%로 높고 Precision은 43 ~ 48%로 낮습니다. 형태소 경계가 아닌 곳도 잘게 자르기 때문입니다.
  - GPT-4는 단어 내 Recall이 86.03%로 WordPiece 수준이지만 Precision이 30.17%입니다. 토큰 경계 4,684개 중 1,272개가 음절의 바이트 중간에 있습니다.

## 분석 대상

| 보고서 | 분석 대상 |
| --- | --- |
| [tokenizer_gpt4.md](reports/tokenizer_gpt4.md) | `tiktoken:cl100k_base` |
| [tokenizer_gpt5.md](reports/tokenizer_gpt5.md) | `tiktoken:o200k_base` |
| [tokenizer_deepseek_v4.md](reports/tokenizer_deepseek_v4.md) | [`deepseek-ai/DeepSeek-V4-Pro`](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro) |
| [tokenizer_gemma2.md](reports/tokenizer_gemma2.md) | [`jhu-clsp/mmBERT-base`](https://huggingface.co/jhu-clsp/mmBERT-base) |
| [tokenizer_gemma4.md](reports/tokenizer_gemma4.md) | [`google/gemma-4-31B-it`](https://huggingface.co/google/gemma-4-31B-it) |
| [tokenizer_muse_glimmer.md](reports/tokenizer_muse_glimmer.md) | [`meta-models/Muse-Glimmer-30B`](https://huggingface.co/meta-models/Muse-Glimmer-30B) |
| [tokenizer_qwen3_8.md](reports/tokenizer_qwen3_8.md) | [`Qwen/Qwen3.8-27B`](https://huggingface.co/Qwen/Qwen3.8-27B) |
| [tokenizer_hyperclovax_seed.md](reports/tokenizer_hyperclovax_seed.md) | [`naver-hyperclovax/HyperCLOVAX-SEED-Think-14B`](https://huggingface.co/naver-hyperclovax/HyperCLOVAX-SEED-Think-14B) |
| [tokenizer_motif3.md](reports/tokenizer_motif3.md) | [`Motif-Technologies/Motif-3`](https://huggingface.co/Motif-Technologies/Motif-3) |
| [tokenizer_kanana2.md](reports/tokenizer_kanana2.md) | [`kakaocorp/kanana-2-30b-a3b-instruct`](https://huggingface.co/kakaocorp/kanana-2-30b-a3b-instruct) |
| [tokenizer_k_exaone_236b.md](reports/tokenizer_k_exaone_236b.md) | [`LGAI-EXAONE/K-EXAONE-236B-A23B`](https://huggingface.co/LGAI-EXAONE/K-EXAONE-236B-A23B) |
| [tokenizer_solar_open2_250b.md](reports/tokenizer_solar_open2_250b.md) | [`upstage/Solar-Open2-250B`](https://huggingface.co/upstage/Solar-Open2-250B) |
| [tokenizer_ax_k2.md](reports/tokenizer_ax_k2.md) | [`skt/A.X-K2`](https://huggingface.co/skt/A.X-K2) |
| [tokenizer_koelectra.md](reports/tokenizer_koelectra.md) | [`monologg/koelectra-base-v3-discriminator`](https://huggingface.co/monologg/koelectra-base-v3-discriminator) |
| [tokenizer_klue_roberta.md](reports/tokenizer_klue_roberta.md) | [`klue/roberta-base`](https://huggingface.co/klue/roberta-base) |
| [tokenizer_kiwi.md](reports/tokenizer_kiwi.md) | [`kiwi-farm/kiwi-coco-lm-base`](https://huggingface.co/kiwi-farm/kiwi-coco-lm-base) |
| [tokenizer_ax_encoder.md](reports/tokenizer_ax_encoder.md) | [`skt/A.X-Encoder-base`](https://huggingface.co/skt/A.X-Encoder-base) |
| [tokenizer_kf_deberta.md](reports/tokenizer_kf_deberta.md) | [`kakaobank/kf-deberta-base`](https://huggingface.co/kakaobank/kf-deberta-base) |

## 보고서 내용

각 보고서는 다음 항목으로 구성됩니다.

- **Tokenizer 방식**: 알고리즘(BPE, WordPiece 등), 기본 단위(byte-level, byte fallback), 정규화, 사전 분할 방식
- **전체 통계**: vocab 수, 한글 포함 vocab 수와 비율, 고유 형태소 수, 평균 글자 수
- **샘플 문서 토큰화 통계**: 샘플 문서의 토큰 수, 토큰당 글자/바이트 수, 어절당 토큰 수
- **드문 한글 음절 분절**: 잘 쓰이지 않는 한글 음절을 토큰화한 결과와 한 토큰/UNK로 처리된 음절 수
- **형태소 경계 일치도**: 한국어 샘플 문서에서 토큰 경계가 Kiwi 형태소 경계와 얼마나 일치하는지 (전체 경계와 단어 내 경계 각각의 Precision, Recall, F1)
- **한글 vocab 형태**: 긴 vocab, 여러 어절 vocab, 반복 패턴 vocab, 불완전 한글 vocab의 수와 비율, 가장 긴 한글 vocab Top N, 반복 패턴 한글 vocab Top N
- **형태소 Top N**: 한글 포함 vocab에서 자주 등장하는 형태소를 전체 위치 빈도, 첫 위치 빈도, 두 빈도의 기하평균 순으로 정렬
- **명사 Top N**: 위와 같은 순위를 명사로 한정한 결과
- **관심 형태소 / 정규식 검색**: 지정한 형태소나 정규식에 해당하는 vocab 목록

## 사용법

```bash
pip install -r requirements.txt

# Hugging Face tokenizer
python src/analyze_tokenizer.py skt/A.X-K2 --output reports/tokenizer_ax_k2.md

# tiktoken encoding
python src/analyze_tokenizer.py tiktoken:o200k_base --output reports/tokenizer_gpt5.md
```

`reports/`의 보고서는 다음 옵션으로 생성했습니다.

```bash
python src/analyze_tokenizer.py <tokenizer> --output reports/<name>.md \
    --morphemes 사람 정부 \
    --pattern '출장|사이트|마사지|추천|소개팅|만남|콜걸|안마|채팅|업소|성인|카지노|놀이터|오피|대출|다운로드'
```

| 옵션 | 설명 |
| --- | --- |
| `tokenizer` | Hugging Face 모델 이름 또는 경로, 또는 `tiktoken:<encoding>` (예: `tiktoken:o200k_base`) |
| `--output` | 보고서를 저장할 경로 (생략하면 표준 출력) |
| `--morpheme-top-n` | 형태소 순위표에 표시할 개수 (기본값 20) |
| `--vocab-top-n` | 가장 긴 한글 vocab, 반복 패턴 한글 vocab 표에 표시할 개수 (기본값 20) |
| `--vocab-examples` | vocab 예시를 표시할 순위표 (`all`, `prefix`, `geo`; 기본값 `prefix`) |
| `--morphemes` | vocab 목록을 조회할 형태소 |
| `--pattern` | vocab 목록을 조회할 정규식 |
| `--no-concat-nouns` | 연속된 명사를 하나로 합치지 않음 |
| `--include-s` | 형태소 순위에 기호(`/S`)를 포함 |
| `--rare-syllables` | 분절 결과를 확인할 드문 한글 음절 목록 (기본값 16개 음절) |
| `--ko-sample`, `--en-sample` | 토큰 수를 셀 샘플 문서 파일 (기본값 `samples/ko.txt`, `samples/en.txt`) |

## 디렉토리 구조

```
src/analyze_tokenizer.py   분석 스크립트
samples/                   토큰화 통계에 사용하는 한국어/영어 샘플 문서
reports/                   tokenizer별 분석 보고서
```
