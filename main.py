import click
from click_default_group import DefaultGroup
from pathlib import Path
from tqdm.auto import tqdm
from soundfile import SoundFile

from tts import generate, get_sample_rate, get_f5tts
from content import get_content

f5tts = None

@click.group(cls=DefaultGroup, default='tts', default_if_no_args=False)
def cli():
  """
  Generates spoken audio for a given text file using F5-TTS and MLX.
  
  COMMAND: Optional. Can be used to only call a sub-command. By default, runs the default chain of commands, i.e., "tts".
  """
  pass

@cli.command()
@click.pass_context
@click.argument('inpath', type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option('-o', '--out-path', 'outpath', type=click.Path(file_okay=False, path_type=Path), help="Path to directory in which to save the generated audio. Defaults to the same directory as the text input.")
@click.option('-f', '--format', 'frmt', type=click.Choice(["WAV", "MP3"]), default="MP3", show_default=True, help="Format in which to save the generated audio.")
@click.option('-c', '--chunk-size', type=click.IntRange(100, 2000, clamp=True), default=250, show_default=True, help="Maximum length (characters) in which to split the text. Needs be less than 40 seconds of generated audio.")
@click.option('--overwrite/--no-overwrite', 'overwrite', default=None, help="ATTENTION! If set (to true), overwrites the output without asking. If explicitly set to no-overwrite, the program will exit gracefully.")
@click.option('--debug', '--verbose', '-v', 'debug', default=False, show_default=True, help="Increases the verbosity of the messages printed to stdout.")
def tts(ctx: click.Context, inpath: Path, outpath: Path|None, frmt: str, chunk_size: int, overwrite: bool|None, debug: bool):
  """
  Generates spoken audio for a given text file using F5-TTS and MLX.
  
  INPATH: path to the plain text file containing the to-be-spoken text.
  """
  global f5tts
  
  if inpath is None:
    click.echo("INPATH missing!")
    return None
  
  outpath = ctx.invoke(prepare, inpath=inpath, outpath=outpath, frmt=frmt, overwrite=overwrite)
  if outpath is None: return None
  content = ctx.invoke(clean, inpath=inpath, chunk_size=chunk_size)

  f5tts = get_f5tts()

  ctx.invoke(process_content, outpath=outpath, overwrite=True if overwrite is None else overwrite, debug=debug, content=content)
  
@cli.command('prepare')
@click.option('-i', '--in-path', 'inpath', type=click.Path(exists=True, dir_okay=False, path_type=Path), help="path to the plain text file containing the to-be-spoken text.")
@click.option('-o', '--out-path', 'outpath', type=click.Path(file_okay=False, path_type=Path), help="Path to directory in which to save the generated audio. Defaults to the same directory as the text input.")
@click.option('-f', '--format', 'frmt', type=click.Choice(["WAV", "MP3"]), default="MP3", show_default=True, help="Format in which to save the generated audio.")
@click.option('--overwrite/--no-overwrite', 'overwrite', default=None, help="ATTENTION! If set (to true), overwrites the output without asking. If explicitly set to no-overwrite, the program will exit gracefully.")
def prepare(inpath: Path, outpath: Path, frmt: str, overwrite: bool) -> Path:
  """Prepare parameters. Check if out-path exists, prompt if necessary"""
  if inpath is None:
    click.echo("INPATH missing!")
    return None
  
  outname = inpath.with_suffix(f".{frmt.lower()}")
  if outpath is not None:
    outpath = Path.joinpath(outpath, outname.name)
  else:
    outpath = outname
    
  check_overwrite_or_exit(outpath, overwrite)
  
  return outpath

@cli.command('clean')
@click.argument('inpath', type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option('-c', '--chunk-size', type=click.IntRange(100, 2000, clamp=True), default=250, show_default=True, help="Maximum length (characters) in which to split the text. Needs be less than 40 seconds of generated audio.")
def clean(inpath: Path, chunk_size: int):
  """
  Cleans the content from the given file to improve TTS quality.
  
  INPATH: path to the plain text file containing the to-be-spoken text.
  """
  if inpath is None: return None
  
  content = get_content(inpath, chunk_size)
  with open(inpath.with_suffix(".cleaned.txt"), "w") as file:
    for line in content:
      file.write(line)
      file.write("\n")
  return content

@cli.command('process')
@click.option('--overwrite', default=False, help="ATTENTION! If set (to true), overwrites the output without asking. Else, the program will exit gracefully.")
@click.option('--debug', '--verbose', '-v', 'debug', default=False, show_default=True, help="Increases the verbosity of the messages printed to stdout.")
@click.option('-o', '--out-path', 'outpath', type=click.Path(exists=True, dir_okay=False, path_type=Path), help="path to the plain text file containing the to-be-spoken text.")
@click.argument('content', nargs=-1)
def process_content(overwrite: bool|None, debug: bool, outpath: Path, content: list[str]):
  """Process the content iteratively."""
  global f5tts
  
  if outpath is None or content is None or len(content) <= 0: return None
  
  check_overwrite_or_exit(outpath, overwrite)
  
  if f5tts is None: f5tts = get_f5tts()
  
  with get_outfile(outpath) as outfile:
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
  
def check_overwrite_or_exit(out_path: Path, overwrite: bool|None):
  if out_path.exists() and out_path.stat().st_size > 0 and (
    overwrite == False or (overwrite is None and not click.confirm(
      f"Output ({out_path.absolute()}) exists. Do you want to continue?")
    )):
    click.echo(f"Will NOT overwrite {out_path}. Exiting now.")
    exit(0)
  click.echo(f"Will write to: {out_path}")

if __name__ == "__main__":
  cli()