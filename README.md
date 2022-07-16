# TODO_NAME

TODO_NAME - collaborate with AI to make art.

- Fig. 1: Select an area for editing, provide a text prompt for guidance

- Fig. 2: Generate options, pick the one you like best

- Fig. 3: Your choice is inserted into the image

- Fig. 4: Repeat

## Background:

- Uses GLID-3-XL for prompt-guided inpainting
- Interface written in PyQt5
- Simple REST client/server design allows editing on any PC, using Google Colab or a server of your choice to handle image processing.

Unimplemented feature ideas: [./TODO.md]

## Setup

Client/server setup, multiple ways to run:
All scripts support multiple command-line options, use the `--help` flag with any of them to view details.

### Client - editing interface

### Run from build:
TODO: Build standalone executables for Win, Mac, Linux, add to release

#### Run directly:
Install deps:
```
pip install (QT deps, etc)
```

Run:
```
python inpainting_client.py
```

Enter server address on prompt.

### Server - image generation
Note: server currently only supports a single client. Multiple client support will likely be added, but won't scale well without significant changes and a very powerful server.

#### Run from Colab notebook:
[TODO: Colab server link]

Follow instructions in the notebook to connect a free ngrok account, start the server, and get the server address. Most functionality will work in Colab's free GPU instances, but CLIP guidance (untested!) requires more GPU memory.

#### Run directly:
Requires a CUDA-capable GPU with around 10GB of RAM.

Setup: follow [GLID-3-XL documentation](./GLID-3-XL-DOC.md) to get models and install dependencies. I recommend using TODO_CONDA_link to manage dependencies.

Install additional deps:
```
pip install (Flask deps, etc)
```
Run:
```
python inpainting_server.py
```

The server link will appear in the output, port can be changed with `TODO_PORT_FLAG`.

#### Run both as a single application:
Follow direct server setup instructions above to install dependencies.

Run `python inpainting_ui.py`

#### Tips:
- Larger edit areas lose details due to scaling, best results are at 256x256 or smaller.
- Non-square edit areas tend to produce worse results than square areas.
- Use sketch mode to provide visual cues to the image generator.

#### Original GLID-3-XL command-line functionality:
All functionality is still available although some features are untested, and some like CPU mode weren't working in the original project either. I've created a [colab notebook](colab link here) you can use to test these. Scripts have been divided up into separate files. Examples below provide minimal valid commands, but all command line options from the original are still present. Setup: follow [GLID-3-XL documentation](./GLID-3-XL-DOC.md) .

- Image generation: `python generate.py --text "Your prompt here"
- Single inpainting operations: `python quickEdit.py --edit "path/to/edited/image" --text "Your prompt here"`
