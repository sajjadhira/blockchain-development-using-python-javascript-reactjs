import time
from backend.blockchain.block import Block, GENESIS_DATA
from backend.config import MINE_RATE, SECONDS
from backend.util.hex_to_binary import hex_to_binary


def test_mine_block():
    """
    mine_block: Create a block and add it to the blockchain.
    """
    last_block = Block.genesis()
    data = 'test-data'
    block = Block.mine_block(last_block, data)

    assert isinstance(block, Block)
    assert block.data == data
    assert block.last_hash == last_block.hash
    assert hex_to_binary(block.hash)[
        0:block.dificulty] == '0' * block.dificulty


def test_genesis():
    """
    genesis: Generate the genesis block.
    """
    genesis = Block.genesis()

    assert isinstance(genesis, Block)
    for key, value in GENESIS_DATA.items():
        assert getattr(Block.genesis(), key) == value


def test_quickly_mined_block():
    """
    mine_block: Create a block and add it to the blockchain.
    """
    last_block = Block.mine_block(Block.genesis(), 'foo')
    mined_block = Block.mine_block(last_block, 'bar')

    assert mined_block.dificulty == last_block.dificulty + 1


def test_slowly_mined_block():
    """
    mine_block: Create a block and add it to the blockchain.
    """
    last_block = Block.mine_block(Block.genesis(), 'foo')

    time.sleep(MINE_RATE / SECONDS)

    mined_block = Block.mine_block(last_block, 'bar')

    assert mined_block.dificulty == last_block.dificulty - 1


# def test_mined_block_difficulty_limits_at_1():
#     """
#     mine_block: Create a block and add it to the blockchain.
#     """
#     last_block = Block(
#         time.time_ns(),
#         'test_last_hash',
#         'test_hash',
#         'test_data',
#         1,
#         0
#     )

#     time.sleep(MINE_RATE / SECONDS)

#     mined_block = Block.mine_block(last_block, 'bar')

#     assert mined_block.dificulty == 1
