import argparse
import sys
from startup.utils import *

# argument parsing:
parser = buildArgParser(includeGenParams=False, includeEditParams=False)
parser.add_argument('--port', type = int, default = 5555, required = False,
                    help='Port used when running in server mode.')
args = parser.parse_args()

import gc
import os

from PIL import Image
import torch
from torchvision.transforms import functional as TF
import numpy as np

from startup.load_models import loadModels
from startup.create_sample_function import createSampleFunction
from startup.generate_samples import generateSamples
from startup.utils import *
from startup.ml_utils import *


device = getDevice()
print('Using device:', device)


model_params, model, diffusion, ldm, bert, clip_model, clip_preprocess, normalize = loadModels(device,
        model_path=args.model_path,
        bert_path=args.bert_path,
        kl_path=args.kl_path,
        steps = args.steps,
        clip_guidance = args.clip_guidance,
        cpu = args.cpu,
        ddpm = args.ddpm,
        ddim = args.ddim)
from colabFiles.server import startServer
app = startServer(device, model_params, model, diffusion, ldm, bert, clip_model, clip_preprocess, normalize)
app.run(port=args.port, host= '0.0.0.0')
