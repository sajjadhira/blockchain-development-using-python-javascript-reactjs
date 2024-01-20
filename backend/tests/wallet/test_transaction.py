
from more_itertools import first
import pytest
from backend.wallet.transaction import Transaction
from backend.wallet.wallet import Wallet


def test_transaction():
    wallet = Wallet()
    recipient = 'recipient'
    amount = 50
    transaction = Transaction(wallet, recipient, amount)

    assert transaction.output['recipient'] == amount
    assert transaction.output[wallet.address] == wallet.balance - amount

    assert 'timestamp' in transaction.input

    assert transaction.input['amount'] == wallet.balance
    assert transaction.input['address'] == wallet.address
    assert transaction.input['public_key'] == wallet.public_key
    assert Wallet.verify(
        transaction.input['public_key'],
        transaction.output,
        transaction.input['signature']
    )


def test_transaction_exceeds_balance():
    with pytest.raises(Exception, match='Amount exceeds balance'):
        Transaction(Wallet(), 'recipient', 9001)


def test_transaction_update_exceeds_balance():
    wallet = Wallet()
    transaction = Transaction(wallet, 'recipient', 50)

    with pytest.raises(Exception, match='Amount exceeds balance'):
        transaction.update(wallet, 'new_recipient', 9001)


def test_transaction_update():
    sender_wallet = Wallet()
    first_recipient = 'first_recipient'
    first_amount = 50
    transaction = Transaction(sender_wallet, first_recipient, first_amount)

    next_recipient = 'next_recipient'
    next_amount = 75
    transaction.update(sender_wallet, next_recipient, next_amount)

    assert transaction.output[next_recipient] == next_amount
    assert transaction.output[sender_wallet.address] == \
        sender_wallet.balance - first_amount - next_amount
    assert transaction.output[sender_wallet.address] == 875

    assert Wallet.verify(
        transaction.input['public_key'],
        transaction.output,
        transaction.input['signature']
    )

    to_first_again_amount = 25
    transaction.update(sender_wallet, first_recipient, to_first_again_amount)
    assert transaction.output[first_recipient] == \
        first_amount + to_first_again_amount

    assert Wallet.verify(
        transaction.input['public_key'],
        transaction.output,
        transaction.input['signature']
    )
