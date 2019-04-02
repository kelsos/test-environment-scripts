#!/usr/bin/env python
import signal
import threading
import time

import click
import tqdm
import yaml

from raiden_api.api import Api
from raiden_api.model.exceptions import HttpErrorException
from raiden_api.model.requests import PaymentRequest


class ServiceExit(Exception):
    pass


class TransferJob(threading.Thread):
    def __init__(
        self,
        port: int,
        receiver: str,
        position: int,
        total: int,
        single: int,
        errors_allowed: int,
        token: str,
        timeout: int,
    ):
        """
        :type port: int The port where the raiden node is listening from.
        :type receiver: str The receiver of the payment.
        :type position: int The position is used in order to show the progress bar.
        :type total: int The total amount the transfer job will send to the receiver.
        :type single: int The amount that will be send on each transfer in every transfer.
        :type errors_allowed: int The number of errors that allowed to occur before the thread
        terminates.
        :type token: str The token for which the transfer will take place.
        """
        threading.Thread.__init__(self)
        self.terminate = threading.Event()
        self.__receiver = receiver
        self.__position = position
        self.__total = total
        self.__single = single
        self.__errors_allowed = errors_allowed
        self.__token = token
        self.__api = Api(port, timeout)

    def transfer(self):

        address_response = self.__api.address()
        sender = address_response.our_address

        pending_amount = self.__total
        print(
            f'{pending_amount} in transfers of {self.__single} from {sender} -> {self.__receiver}'
        )
        time.sleep(1)

        trange = tqdm.trange(
            int(self.__total / self.__single),
            desc=f"[{self.__position}] {sender[2:9].lower()} -> {self.__receiver[2:9].lower()}",
            position=self.__position,
        )

        total_time = 0
        performed_iterations = 0
        errors = 0

        while pending_amount > 0 and not self.terminate.is_set():
            secs = 60 + (10 * errors)
            try:
                start_time = time.time()
                identifier = int(start_time)

                payment_request = PaymentRequest(amount=self.__single, identifier=identifier)

                payment_response = self.__api.payment(
                    self.__receiver, payment_request, self.__token
                )

                duration = time.time() - start_time
                response_identifier = payment_response.identifier

                if response_identifier != identifier:
                    message = (
                        f'Identifier mismatch:' f'expected {identifier} got {response_identifier}'
                    )
                    raise Exception(message)

                pending_amount -= self.__single
                total_time += duration
                performed_iterations += 1
                trange.update()

            except Exception as e:
                print(f'transfer from {sender} failed, waiting for {secs} sec [{errors}] -> {e}')
                time.sleep(secs)
                errors += 1

                if isinstance(e, HttpErrorException):
                    print(f'{e.code} -- {str(e)}')

                if errors > self.__errors_allowed:
                    break

            errors = 0

        throughput = 0
        if performed_iterations > 0:
            throughput = total_time / performed_iterations

        print(
            f'Elapsed for {sender} requests:'
            f' {performed_iterations} {total_time} sec -> {throughput} sec/t'
        )

    def run(self):
        self.transfer()


@click.command()
@click.option('--transfer-amount', type=int, default=5000)
@click.option('--per-transfer', type=int, default=5)
@click.option('--allowed-errors', type=int, default=50)
@click.option('--token', type=str, required=True)
@click.option("--config", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option('--timeout', type=int, default=60)
def main(
    transfer_amount: int, per_transfer: int, allowed_errors: int, token: str, config, timeout: int
):
    configuration_file = open(config, 'r')
    configuration = yaml.load(configuration_file)

    nodes_ = configuration['nodes']
    if not nodes_:
        print('nodes element is missing from configuration')
        exit(1)

    jobs = []

    for position in range(0, len(nodes_)):
        node = nodes_[position]
        port = node['port']
        receiver = node['target']
        job = TransferJob(
            port, receiver, position, transfer_amount, per_transfer, allowed_errors, token, timeout
        )
        jobs.append(job)

    try:
        for j in jobs:
            j.start()

        while True:
            time.sleep(1)
            alive = filter(lambda j: j.is_alive(), jobs)
            if len(list(alive)) == 0:
                break

    except ServiceExit:
        for j in jobs:
            j.terminate.set()
            j.join()

        print('Service terminated')
        exit(0)

    print('Service complete')


def shutdown_handler(_signo, _stackframe):
    raise ServiceExit


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)

    main()
