import unittest

def run_tests():
    # Discover all tests in the 'tests' directory
    loader = unittest.TestLoader()
    suite = loader.discover('tests')

    # Run the tests
    runner = unittest.TextTestRunner()
    result = runner.run(suite)

    # Check if all tests passed
    if result.wasSuccessful():
        print("All tests passed!")
        return 0
    else:
        print("Some tests failed.")
        return 1

if __name__ == '__main__':
    exit(run_tests())
