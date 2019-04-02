#!/usr/bin/env python
import os
import sys
import tarfile
import time
from datetime import datetime
from pathlib import Path
from shutil import rmtree
from typing import List

import click


@click.command()
@click.option("--chain-id", required=True, type=int)
@click.option(
    "--archive-directory",
    required=True,
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
)
@click.option("--delete", type=bool, default=False)
def main(chain_id: int, archive_directory: str, delete: bool):
    accounts = get_accounts()
    raiden_dir = get_raiden_dir()

    db_directories = get_db_directories(accounts, raiden_dir, chain_id)
    log_directories = logs(accounts, chain_id)
    all_directories = db_directories + log_directories

    if len(all_directories) == 0:
        print('No state to cleanup')
        exit(0)

    tar_file = tarfile.open(tar_name(archive_directory, chain_id), 'w:xz')
    print(f'preparing archive {tar_file.name}')

    for directory in all_directories:
        print(f'compressing directory {directory}')
        if 'logs' in directory:
            logs_archive_path = os.path.join('logs', directory.split('logs/')[1])
            tar_file.add(directory, logs_archive_path)
        elif '.raiden' in directory:
            dbs_archive_path = os.path.join('dbs', directory.split('.raiden/')[1])
            tar_file.add(directory, dbs_archive_path)

    tar_file.close()

    if not delete:
        print('Skipping state delete')
        exit(0)

    print('removing directories')

    for directory in all_directories:
        print(f'deleting directory {directory}')
        rmtree(directory)

    exit(0)


def get_db_directories(accounts, raiden_dir, chain_id: int):
    node_directories = get_db_folders(accounts)
    dir_contents = os.listdir(raiden_dir)
    db_directories = set(node_directories) & set(dir_contents)
    directories = list(os.path.join(raiden_dir, directory) for directory in db_directories)

    directories_for_chain = []
    for directory in directories:
        if f'netid_{chain_id}' in os.listdir(directory):
            directories_for_chain.append(os.path.join(directory, f'netid_{chain_id}'))

    return directories_for_chain


def tar_name(log_directory: str, chain_id: int) -> str:
    label = datetime.utcfromtimestamp(time.time()).strftime('%Y%m%d_%H%M%S')
    name = f"{label}_netid_{chain_id}_raiden_db_logs.tar.xz"
    return os.path.join(log_directory, name)


def logs(accounts: List[str], chain_id: int) -> List[str]:
    parent_directory = os.path.abspath(os.path.join(os.path.join(__file__, os.pardir), os.pardir))
    logs_directory = os.path.join(parent_directory, 'logs')
    chain_directory = os.path.join(logs_directory, f'{chain_id}')
    production = os.path.join(chain_directory, 'production')

    log_directories = os.listdir(production)

    account_directories = set(log_directories) & set(accounts)
    return list(os.path.join(production, directory) for directory in account_directories)


def get_db_folders(accounts: List[str]) -> List[str]:
    node_directories = []
    for account in accounts:
        directory = 'node_' + account.replace('0x', '').lower()[:8]
        node_directories.append(directory)
    return list(node_directories)


def get_raiden_dir():
    home = Path.home()
    raiden_dir = os.path.join(str(home), '.raiden')
    if not os.path.exists(raiden_dir):
        print('raiden directory was not detected')
        sys.exit(1)
    return raiden_dir


def get_accounts() -> List[str]:
    testing_accounts = os.environ['RT_ENV__TESTING_ACCOUNTS']
    if not testing_accounts:
        print('$RT_ENV_TESTING_ACCOUNTS environment variable was undefined')
        sys.exit(1)
    return testing_accounts.split(':')


if __name__ == '__main__':
    main()
