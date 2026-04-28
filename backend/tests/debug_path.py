import sys

def test_path():
    print('--- sys.path start ---')
    for p in sys.path[:5]:
        print(p)
    print('--- sys.path end ---')
    import src
    assert hasattr(src, 'app')
