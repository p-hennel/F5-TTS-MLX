import click
from pathlib import Path
from tqdm.auto import tqdm
from soundfile import SoundFile

from tts import generate, get_sample_rate, get_f5tts
from f5_tts_mlx import F5TTS
from content import get_content

@click.command()
@click.argument('inpath', type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option('-o', '--out-path', 'outpath', type=click.Path(file_okay=False, path_type=Path), help="Path to directory in which to save the generated audio. Defaults to the same directory as the text input.")
@click.option('-f', '--format', 'frmt', type=click.Choice(["WAV", "MP3"]), default="MP3", show_default=True, help="Format in which to save the generated audio.")
@click.option('-c', '--chunk-size', type=click.IntRange(100, 2000, clamp=True), default=250, show_default=True, help="Maximum length (characters) in which to split the text. Needs be less than 40 seconds of generated audio.")
@click.option('--overwrite/--no-overwrite', 'overwrite', default=None, help="ATTENTION! If set (to true), overwrites the output without asking. If explicitly set to no-overwrite, the program will exit gracefully.")
@click.option('--debug', '--verbose', '-v', 'debug', default=False, show_default=True, help="Increases the verbosity of the messages printed to stdout.")
def cli(inpath: Path, outpath: Path|None, frmt: str, chunk_size: int, overwrite: bool|None, debug: bool):
  """
  Generates spoken audio for a given text file using F5-TTS and MLX.
  
  INPATH: path to the plain text file containing the to-be-spoken text.
  """
  outpath = prepare(inpath, frmt, overwrite)
  content = get_content(inpath, chunk_size)
  f5tts = get_f5tts()

  with get_outfile(outpath) as outfile:
    process(outfile, f5tts, content, debug)

def process(outfile: SoundFile, f5tts: F5TTS, content: list[str], debug: bool):
  """Process the content iteratively."""
  for chnk in tqdm(content):
    audio = generate(f5tts, text=chnk, debug=debug)
    outfile.write(audio)

def get_outfile(out_path: Path) -> SoundFile:
  """Prepare a SoundFile object to write to."""
  return SoundFile(
    out_path,
    mode='w',
    samplerate=get_sample_rate(),
    channels=1
  )

def prepare(in_path: Path, out_path: Path, frmt: str, overwrite: bool) -> Path:
  """Prepare parameters. Check if out-path exists, prompt if necessary"""
  outname = in_path.with_suffix(f".{frmt.lower()}")
  if out_path is not None:
    out_path = Path.joinpath(out_path, outname.name)
  else:
    out_path = outname
  if out_path.exists() and (
    not overwrite or (overwrite is None and not click.confirm(
      f"Output ({out_path.absolute()}) exists. Do you want to continue?")
    )): exit(0)
  return out_path

if __name__ == '__main__':
  cli()