import pytest

from backend.blockchain.blockchain import BlockChain
from backend.blockchain.block import GENESIS_DATA
from backend.wallet.wallet import Wallet
from backend.wallet.transaction import Transaction


def test_blockchain_instance():
    blockchain = BlockChain()
    assert blockchain.chain[0].hash == GENESIS_DATA['hash']


def test_add_block():
    blockchain = BlockChain()
    data = 'test-data'
    blockchain.add_block(data)

    assert blockchain.chain[-1].data == data


@pytest.fixture
def blockchain_three_blocks():
    blockchain = BlockChain()
    for i in range(3):
        blockchain.add_block(
            [Transaction(Wallet(), Wallet().address, i).to_json()])
    return blockchain


def test_is_valid_chain(blockchain_three_blocks):
    BlockChain.is_valid_chain(blockchain_three_blocks.chain)


def test_is_valid_chain_bad_genesis(blockchain_three_blocks):
    blockchain_three_blocks.chain[0].hash = 'evil_hash'

    with pytest.raises(Exception, match='genesis block must be valid'):
        BlockChain.is_valid_chain(blockchain_three_blocks.chain)


def test_replace_chain(blockchain_three_blocks):
    blockchain = BlockChain()
    blockchain.replace_chain(blockchain_three_blocks.chain)

    assert blockchain.chain == blockchain_three_blocks.chain


def test_replace_chain_not_longer(blockchain_three_blocks):
    blockchain = BlockChain()

    with pytest.raises(Exception, match='The incoming chain must be longer'):
        blockchain_three_blocks.replace_chain(blockchain.chain)


def test_replace_chain_bad_chain(blockchain_three_blocks):
    blockchain = BlockChain()
    blockchain_three_blocks.chain[1].hash = 'evil_hash'

    with pytest.raises(Exception, match='The incoming chain is invalid'):
        blockchain.replace_chain(blockchain_three_blocks.chain)


def test_valid_transaction_chain(blockchain_three_blocks):
    BlockChain.is_valid_transaction_chain(blockchain_three_blocks.chain)


def test_is_valid_transaction_chain_duplicate_transactions(blockchain_three_blocks):
    transaction = Transaction(Wallet(), Wallet().address, 1).to_json()
    blockchain_three_blocks.add_block([transaction, transaction])

    with pytest.raises(Exception, match='is not unique'):
        BlockChain.is_valid_transaction_chain(blockchain_three_blocks.chain)


def test_is_valid_transaction_chain_multiple_rewards(blockchain_three_blocks):
    reward_1 = Transaction.reward_transaction(Wallet()).to_json()
    reward_2 = Transaction.reward_transaction(Wallet()).to_json()
    blockchain_three_blocks.add_block([reward_1, reward_2])

    with pytest.raises(Exception, match='one mining reward per block'):
        BlockChain.is_valid_transaction_chain(blockchain_three_blocks.chain)


def test_is_valid_transaction_chain_bad_transaction(blockchain_three_blocks):
    bad_transaction = Transaction(Wallet(), Wallet().address, 1)
    bad_transaction.input['signature'] = Wallet().sign(bad_transaction.output)

    blockchain_three_blocks.add_block([bad_transaction.to_json()])

    with pytest.raises(Exception):
        BlockChain.is_valid_transaction_chain(blockchain_three_blocks.chain)


def test_is_valid_transaction_chain_bad_historic_balance(blockchain_three_blocks):
    wallet = Wallet()
    bad_transaction = Transaction(wallet, Wallet().address, 1)
    bad_transaction.output[wallet.address] = 9000
    bad_transaction.input['amount'] = 9001
    bad_transaction.input['signature'] = wallet.sign(bad_transaction.output)

    blockchain_three_blocks.add_block([bad_transaction.to_json()])

    with pytest.raises(Exception, match='has an invalid input amount'):
        BlockChain.is_valid_transaction_chain(blockchain_three_blocks.chain)
