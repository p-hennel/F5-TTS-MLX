import re
from typing import Generator
import nltk
from collections import deque
from pathlib import Path

def get_content(input: Path, chunk_size: int, listify=True):
  """Get the content from the given path and chunk it."""
  with open(input) as file:
      content = file.read()
  content = chunk(content, chunk_size)
  if listify: content = list(content)
  return content

def chunk(content: str, max_length: int) -> Generator[str, None, None] | list[str]:
  """Chunk a given text in sentences while also cleaning each chunk."""
  nltk.download('punkt')
  sentence_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
  queue = deque()
  
  content = pre_chunk_clean(content)
  
  yield content
  if True: return

  for sentence in sentence_tokenizer.tokenize(content):
    if sentence is None or len(sentence) <= 0: continue
    if len(sentence) >= max_length:
      for split in sentence.split(" "): queue.append(split)
    else: queue.append(sentence)
    while len(queue) > 1:
      if len(queue[0] + " " + queue[1]) >= max_length:
        yield per_chunk_clean(queue.popleft())
      else:
        queue.appendleft(queue.popleft() + " " + queue.popleft())
    if len(queue) > 0:
      yield per_chunk_clean(queue.pop())

_re_double_newline = re.compile(r"(?:(?<!\n)\n *\n(?!\n))", re.MULTILINE)
_re_multi_newline = re.compile(r"(?:\n\s?){3,}", re.MULTILINE)
_re_upper = re.compile(r"(?:(?:[A-Z\'\:\.\-])+\s){2,}|(?:(?<=\n)[A-Z]+(?=\n))|(?:[A-Z][a-z]+)", re.MULTILINE)
_re_tripple_dot = re.compile(r"(\s*\.\s*){3,}", re.MULTILINE)
_re_prepare_citation = re.compile(r"(?:\set\n\s*al\.?\n(?P<year>\d{4}))", re.MULTILINE)
_re_citation = re.compile(r"\s?\(((\w+[\?\s\-\.\,\;\&]+)+[\s\,\;]?)+\d{2,4}\w?\)", re.MULTILINE)
_re_special_chars = re.compile(r"(?:(?<!al)[\-\–\—\'\"\’\´\`\<\>\°\#\^\_\#\+\*\=\/\\\(\)\[\]\{\}])", re.MULTILINE)
_re_et_al = re.compile(r"\set\.?\s?al\.?\s?(?P<pos>\'?s?)((\s?\()?\s?(?P<year>\d{2,4})(\s?\))?)?", re.MULTILINE)
_re_fix_et_als = re.compile(r"\set\sal\ss\s", re.MULTILINE)
_re_eg = re.compile(r",e\.?\s?g\.?,", re.MULTILINE)
_re_ie = re.compile(r",i\.?\s?e\.?,", re.MULTILINE)
_re_digit_space_colon = re.compile(r"(?P<digit>\d+)\s+\:", re.MULTILINE)
_re_space_line = re.compile(r"(?:^ +)|(?: +$)|(?:(?<=\. ) +)|(?:(?<=\w) +(?=\.))", re.MULTILINE)
_re_space_stop = re.compile(r"\s?\.", re.MULTILINE)
_re_multi_space = re.compile(r"\s{2,}", re.MULTILINE)
_re_maxi_pause = re.compile(r"(\,\s){4,}$", re.MULTILINE)
_re_ending = re.compile(r"\s+$")
_re_heading_pause = re.compile(r"\n(?:(\w+ ?))+(?=\n)")

def pre_chunk_clean(content: str) -> str:
  """
  Cleans the given text. Should be applied before chunking.
  Removes citations, replaces special characters, ...
  """
  content = _re_double_newline.sub("\n", content)
  content = _re_multi_newline.sub("\n\n", content)
  content = _re_tripple_dot.sub("", content)
  content = _re_upper.sub(_re_lowercase, content)
  content = _re_citation.sub("", content)
  content = _re_et_al.sub(" et al\\g<pos> \\g<year>", content)
  content = _re_ie.sub(", that is, ", content)
  content = _re_eg.sub(", for instance, ", content)
  content = _re_special_chars.sub(" ", content)
  content = _re_space_line.sub("", content)
  content = _re_digit_space_colon.sub("\\g<digit>:", content)
  content = content.replace("&", " and ")
  content = _re_multi_space.sub(" ", content)
  content = _re_ending.sub("", content)
  content = _re_heading_pause.
  return content

def _re_group_mod(match: re.Match, sep: str = " ", lowercase=False) -> str:
  return sep.join([group.lower() if lowercase else group for group in match.groups()])
def _re_group_lowercase(match: re.Match) -> str:
  return _re_group_mod(match, lowercase=True)

def _re_lowercase(match: re.Match) -> str:
  return match.group(0).lower()

def per_chunk_clean(content: str) -> str:
  """
  Cleans the given (single chunk) text.
  Removes citations, replaces special characters, ...
  """
  return content