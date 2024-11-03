# CLI for F5-TTS (using MLX)

## Best UX: [uv](https://github.com/astral-sh/uv)!
[uv](https://github.com/astral-sh/uv) makes interacting with different python environments and tools a breeze.

1. Install [uv](https://github.com/astral-sh/uv)
    1. On macOS and Linux.
          ```bash
          curl -LsSf https://astral.sh/uv/install.sh | sh
          ```
    2. On Windows
          ```bash
          powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
          ```
    3. With pip
          ```bash
          pip install uv
          ```

2. Prepare the Environment
    ```bash
    uv venv -p python3.10
    ```

3. RUN!
    ```bash
    uv run ...
    ```

## Development / Installation

### Without uv
Requires `setuptools` to be present. Then, just execute:
```bash
pip install --editable .
```
Now the tool can be used as `f5tts`.

### With uv (RECOMMENDED!)
```bash
uv venv -p python3.10
uv pip install setuptools
uv pip install --editable .
```

## Usage
```bash
uv run f5tts --help

Usage: f5tts [OPTIONS] INPATH

  Generates spoken audio for a given text file using F5-TTS and MLX.

  INPATH: path to the plain text file containing the to-be-spoken text.

Options:
  -o, --out-path DIRECTORY        Path to directory in which to save the
                                  generated audio. Defaults to the same
                                  directory as the text input.
  -f, --format [WAV|MP3]          Format in which to save the generated audio.
                                  [default: MP3]
  -c, --chunk-size INTEGER RANGE  Maximum length (characters) in which to
                                  split the text. Needs be less than 40
                                  seconds of generated audio.  [default: 250;
                                  100<=x<=2000]
  --overwrite / --no-overwrite    ATTENTION! If set (to true), overwrites the
                                  output without asking. If explicitly set to
                                  no-overwrite, the program will exit
                                  gracefully.
  -v, --debug, --verbose BOOLEAN  Increases the verbosity of the messages
                                  printed to stdout.  [default: False]
  --help                          Show this message and exit.
```

# Depends on
(among others)
1. [F5-TTS](https://github.com/SWivid/F5-TTS)
2. [MLX](https://github.com/ml-explore/mlx)
3. [F5-TTS-MLX](https://github.com/lucasnewman/f5-tts-mlx)
4. [Click](https://github.com/pallets/click)
5. [setuptools](https://github.com/pypa/setuptools)
6. [tqdm](https://github.com/tqdm/tqdm)