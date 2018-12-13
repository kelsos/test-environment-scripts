#!/usr/bin/env python
import time

import click
import requests
import signal
import threading
import tqdm
import yaml


class ServiceExit(Exception):
    pass


def payment(port: int, receiver: str, amount: int, identifier: int, token: str, timeout: int):
    url = f'http://localhost:{port}/api/1/payments/{token}/{receiver}'
    return requests.post(
        url,
        headers={'Content-Type': 'application/json', },
        json={'amount': amount, 'identifier': identifier},
        timeout=timeout
    )


class TransferJob(threading.Thread):

    def __init__(
            self,
            port: int,
            sender: str,
            receiver: str,
            position: int,
            total: int,
            single: int,
            errors_allowed: int,
            token: str,
            timeout: int
    ):
        """
        :type port: int The port where the raiden node is listening from.
        :type sender: str The address of the node sending the transfers. Used for logging purposes.
        :type receiver: str The receiver of the payment.
        :type position: int The position is used in order to show the progress bar.
        :type total: int The total amount the transfer job will send to the receiver.
        :type single: int The amount that will be send on each transfer in every transfer.
        :type errors_allowed: int The number of errors that allowed to occur before the thread terminates.
        :type token: str The token for which the transfer will take place.
        """
        threading.Thread.__init__(self)
        self.terminate = threading.Event()
        self.__sender = sender
        self.__port = port
        self.__receiver = receiver
        self.__position = position
        self.__total = total
        self.__single = single
        self.__errors_allowed = errors_allowed
        self.__token = token
        self.__timeout = timeout

    def transfer(self):

        pending_amount = self.__total
        print(f'{pending_amount} in transfers of {self.__single} from {self.__sender} -> {self.__receiver}')
        time.sleep(1)

        trange = tqdm.trange(
            int(self.__total / self.__single),
            desc=f"[{self.__position}] {self.__sender} -> {self.__receiver}",
            position=self.__position
        )

        total_time = 0
        performed_iterations = 0
        errors = 0

        while pending_amount > 0 and not self.terminate.is_set():
            secs = 30 + (10 * errors)
            try:
                start_time = time.time()
                identifier = int(start_time)
                resp = payment(
                    port=self.__port,
                    receiver=self.__receiver,
                    amount=self.__single,
                    identifier=identifier,
                    token=self.__token,
                    timeout=self.__timeout
                )
                duration = time.time() - start_time

                if resp.status_code != 200:
                    print(f'Invalid response error for {secs} sec [{errors}]')
                    raise Exception(resp.json()['errors'])

                response_identifier = resp.json()['identifier']
                if response_identifier != identifier:
                    message = f'Identifier mismatch expected {identifier} got {response_identifier}'
                    print(message)
                    raise Exception(message)

                pending_amount -= self.__single
                total_time += duration
                performed_iterations += 1
                trange.update()

            except Exception as e:
                print(f'transfer from {self.__sender} failed, waiting for {secs} sec [{errors}] -> {e}')
                time.sleep(secs)
                errors += 1

                if errors > self.__errors_allowed:
                    break

            errors = 0

        throughput = 0
        if performed_iterations > 0:
            throughput = total_time / performed_iterations

        print(f'Elapsed for {self.__sender} requests: {performed_iterations} {total_time} sec -> {throughput} sec/t')

    def run(self):
        self.transfer()


@click.command()
@click.option('--transfer-amount', type=int, default=5000)
@click.option('--per-transfer', type=int, default=5)
@click.option('--allowed-errors', type=int, default=50)
@click.option('--token', type=str, required=True)
@click.option("--config", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option('--timeout', type=int, default=60)
def main(transfer_amount: int, per_transfer: int, allowed_errors: int, token: str, config, timeout: int):
    configuration_file = open(config, 'r')
    configuration = yaml.load(configuration_file)

    print(configuration)

    nodes_ = configuration['nodes']
    if not nodes_:
        print('nodes element is missing from configuration')
        exit(1)

    jobs = []
    for position in range(0, len(nodes_)):
        node = nodes_[position]
        sender = node['address']
        port = node['port']
        receiver = node['target']
        job = TransferJob(port, sender, receiver, position, transfer_amount, per_transfer, allowed_errors, token,
                          timeout)
        jobs.append(job)

    trange = tqdm.trange(len(jobs), desc="Running transfers", position=0)
    try:
        for j in jobs:
            j.start()

        while True:
            time.sleep(1)

    except ServiceExit:
        for j in jobs:
            j.terminate.set()
            j.join()

    trange.update()
    print('Starting transfers')


def shutdown_handler(_signo, _stackframe):
    raise SystemExit


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)

    main()
