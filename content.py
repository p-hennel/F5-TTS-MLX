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

  for sentence in sentence_tokenizer.tokenize(content):
    if sentence is None or len(sentence) <= 0: continue
    if len(sentence) >= max_length:
      for split in sentence.split(" "): queue.append(split)
    else: queue.append(sentence)
    while len(queue) > 1:
      if len(queue[0] + " " + queue[1]) >= max_length:
        yield clean_text(queue.popleft())
      else:
        queue.appendleft(queue.popleft() + " " + queue.popleft())
    if len(queue) > 0:
      yield clean_text(queue.pop())

def _re_mod(match: re.Match, sep: str = " ", lowercase=False) -> str:
  return sep.join([group.lower() if lowercase else group for group in match.groups()])
def _re_lowercase(match: re.Match) -> str:
  return _re_mod(match, lowercase=True)

_re_upper = re.compile(r"([A-Z]+)")
_re_citation = re.compile(r"\(((\w+[\s\-\.\,\;]+)+[\s\,\;]?)+\d{2,4}\w?\)")
_re_special_chars = re.compile(r"[\-\–\—\'\"\’\´\`\<\>\°\#\^\_\#\+\*\=\/\\\(\)\[\]\{\}]")
_re_space_stop = re.compile(r"\s?\.")
_re_multi_space = re.compile(r"\s{2,}")
_re_maxi_pause = re.compile(r"(\,\s){4,}$")
_re_ending = re.compile(r"(\,\s{0,2})+$")
def clean_text(content: str) -> str:
  """Cleans the given text. Removes citations, replaces special characters, ..."""
  content = _re_upper.sub(_re_lowercase, content)
  content = _re_citation.sub("", content)
  content = _re_special_chars.sub(" ", content)
  content = content.replace("&", " and ")
  content = content.replace("\n", ", , ")
  content = _re_space_stop.sub("., ", content)
  content = _re_multi_space.sub(" ", content)
  content = _re_maxi_pause.sub(", ", content)
  content = _re_ending.sub("", content)
  return content