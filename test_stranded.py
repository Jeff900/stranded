from stranded import Game

def test_gameclass():
    game = Game('test.db')
    # Check if the database is initializes empty, but contains a schema.
    assert game.check_database() is False
