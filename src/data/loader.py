import kagglehub
from pathlib import Path
import shutil
import logging
from src.config import DATA_RAW

logger = logging.getLogger(__name__)

DATASETS = {
    'tickets_200k': 'mirzayasirabdullah07/customer-support-tickets-dataset-200k-records',
    'bitext': 'bitext/bitext-gen-ai-chatbot-customer-support-dataset',
}

def download_datasets(force=False):
    paths = {}
    for name, slug in DATASETS.items():
        dest = DATA_RAW / name
        if dest.exists() and not force:
            logger.info(f'{name} already exists at {dest}, skipping download')
            paths[name] = dest
            continue
        logger.info(f'Downloading {name} from Kaggle: {slug}')
        raw_path = kagglehub.dataset_download(slug)
        dest.mkdir(parents=True, exist_ok=True)
        src = Path(raw_path)
        for f in src.rglob('*'):
            if f.is_file():
                target = dest / f.name
                shutil.copy2(f, target)
                logger.info(f'  Copied {f.name} -> {target}')
        paths[name] = dest
        logger.info(f'  {name} ready at {dest}')
    return paths

def list_raw_files():
    for p in DATA_RAW.rglob('*'):
        if p.is_file():
            size_mb = p.stat().st_size / 1_000_000
            print(f'  {p.relative_to(DATA_RAW)}  ({size_mb:.1f} MB)')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    paths = download_datasets()
    print('Downloaded datasets:')
    for name, path in paths.items():
        print(f'  {name}: {path}')
    print('All raw files:')
    list_raw_files()
