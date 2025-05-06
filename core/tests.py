import unittest
from django.test.runner import DiscoverRunner


class CustomTextTestRunner(unittest.TextTestRunner):
    def run(self, test):
        result = self._makeResult()
        test(result)
        result.stopTestRun()

        return result

    def _makeResult(self):
        result = super()._makeResult()

        result._last_test_class = None

        def startTest(test):
            test_class = test.__class__
            if test_class != result._last_test_class:
                result._last_test_class = test_class
                module_path = test_class.__module__
                print(f"\n🧪 Running test group: {module_path}")

        result.startTest = startTest

        def silent_add_success(test):
            result.testsRun += 1
            print(f"✅ {test._testMethodName}: Passed")

        result.addSuccess = silent_add_success

        def silent_add_failure(test, err):
            result.testsRun += 1
            error_message = str(err[1])
            print(f"❌ {test._testMethodName}: Failed\nReason: {error_message}")
            result.failures.append((test, err))

        result.addFailure = silent_add_failure

        def silent_add_error(test, err):
            result.testsRun += 1
            error_message = str(err[1])
            print(f"🔥 {test._testMethodName}: Error\nReason: {error_message}")
            result.errors.append((test, err))

        result.addError = silent_add_error

        def stopTestRun():
            print("\nTest Summary:")
            total_tests = result.testsRun
            failed_tests = len(result.failures)
            error_tests = len(result.errors)
            passed_tests = total_tests - failed_tests - error_tests

            print(f"🧪 Tests run: {total_tests}")
            print(f"✅ Passed: {passed_tests}")
            print(f"❌ Failures: {failed_tests}")
            print(f"🔥 Errors: {error_tests}\n")

        result.stopTestRun = stopTestRun

        return result

    def printErrors(self):
        pass


class CustomTestRunner(DiscoverRunner):
    def run_suite(self, suite, **kwargs):
        return CustomTextTestRunner(
            verbosity=self.verbosity, failfast=self.failfast
        ).run(suite)
