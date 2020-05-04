import unittest


import json
import os


def setUpModule():
    pass

def tearDownModule():
    pass


class TaskFlowTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from fairways import taskflow
        cls.Chain = taskflow.Chain
        cls.SkipFollowing = taskflow.SkipFollowing
        cls.Handler = taskflow.Handler 
        cls.HandlerThen = taskflow.HandlerThen
        cls.HandlerFail = taskflow.HandlerFail
        import os
        cls.os = os

        # from fairways import log
        from fairways.conf import load
        load(None)

        from fairways.ci import helpers
        # cls.helpers = helpers

        # import logging
        # log = logging.getLogger()
        cls.log = helpers.getLogger()

    @classmethod
    def tearDownClass(cls):
        pass
    
    def test_create_handler(self):
        Handler = self.Handler
        h = Handler(lambda x: x, topic="my_topic")
        self.assertEqual(h.topic, "my_topic")

    def test_create_handler_then(self):
        HandlerThen = self.HandlerThen
        h = HandlerThen(lambda x: x)
        self.assertEqual(h.q_topic, "data")

    def test_create_handler_fail(self):
        HandlerFail = self.HandlerFail
        h = HandlerFail(lambda x: x)
        self.assertEqual(h.q_topic, "failure")

    def test_create_handler_fail_on(self):
        HandlerFail = self.HandlerFail
        h = HandlerFail(lambda x: x, topic="MyException")
        self.assertEqual(h.q_topic, "failure/MyException")

    def test_then(self):
        """
        """
        Chain = self.Chain

        arg = "a"

        chain = Chain(
            ).then(lambda a: a + "b"
            ).then(lambda a: a + "c"
            ).then(lambda a: a + "d"
            )

        result = chain(arg)

        self.assertEqual(result, "abcd")
    
    @unittest.skip("not ready")
    def test_handler_functools_partial(self):
        """Taskflow should resolve partial name when partial traced in flow
        """

    @unittest.skip("not ready")
    def test_all(self):
        """
        """
        Chain = self.Chain

        arg = 2

        chain = Chain().all(
            lambda a: a * 2,
            lambda a: a * 2,
            lambda a: a * 2,
        )

        result = chain(arg)

        self.assertEqual(result, [4, 4, 4])

    @unittest.skip("not ready")
    def test_merge(self):
        """
        """
        Chain = self.Chain

        arg = {
            'a': None,
            'b': None,
            'c': None,
        }

        chain = Chain().merge(
            lambda a: {'a': 'a'},
            lambda a: {'b': 'b', 'c': '<will be overwritten>'},
            lambda a: {'c': 'c'},
        # ).then(
        #     lambda a: json.dumps(a)
        )

        result = chain(arg)

        self.assertEqual(result, {"a": "a", "b": "b", "c": "c"})



    def test_middleware(self):
        """
        """
        Chain = self.Chain

        arg = {}

        trace = []

        def mid_show_name(method, arg, **kwargs):
            """
            Transforms dict to list of pairs
            """
            trace.append(method.__name__)
            return method(arg)

        def step1(arg):
            return arg

        def step2(arg):
            return arg

        def step3(arg):
            return arg

        chain = Chain(
            ).then(step1
            ).then(step2
            ).then(step3
            )

        result = chain(arg, middleware=mid_show_name)

        self.assertEqual(trace, ['step1', 'step2', 'step3'])


    def test_middleware_exact_calls(self):
        """
        Middleware should be called only on methods which actually invoked
        """
        Chain = self.Chain

        arg = {"data": "unchanged"}

        trace = []

        def mid_show_name(method, arg, **kwargs):
            """
            Transforms dict to list of pairs
            """
            result = method(arg)
            trace.append("Passed: %s" % method.__name__)
            return result

        def step1(arg):
            return arg

        def step2(arg):
            1/0 # force exception
            return arg

        def step3(arg):
            return arg

        def catch(arg):
            return arg

        chain = Chain(
            ).then(step1 # should be passed (invoked)
            ).then(step2 # should be ignored (invoked but not finished)
            ).then(step3 # should be ignored (not invoked)
            ).catch(lambda x: None # should be passed (invoked)
            )

        result = chain(arg, middleware=mid_show_name)

        self.assertDictEqual(result, {"data": "unchanged"})
        self.assertEqual(trace, ['Passed: step1', 'Passed: <lambda>'])


    def test_on_if_found(self):
        Chain = self.Chain

        arg = {"data":"should be unchanged", "event": "Old value"}

        chain = Chain().on(
            "event",
            lambda _: "modified!"
        )

        result = chain(arg)

        self.assertEqual(result, {'data': 'should be unchanged', 'event': 'modified!'})
        
    def test_on_if_not_found(self):
        Chain = self.Chain

        arg = {"data":"should be unchanged", "alien-event": 1}

        chain = Chain().on(
            "event",
            lambda e: e+1
        )

        result = chain(arg)

        self.assertEqual(result, {'data': 'should be unchanged', 'alien-event': 1})



    def test_nested_on_if_found(self):
        Chain = self.Chain

        arg = {
            "data":"should be unchanged", 
            "event": "Some value"
        }
        tree = {"nested": arg}

        chain = Chain().on(
            "nested/event",
            lambda _: "modified!"
        )

        result = chain(tree)

        self.assertEqual(result, {'nested': {'data': 'should be unchanged', 'event': 'modified!'}})
        
    def test_nested_on_if_not_found(self):
        Chain = self.Chain

        arg = {
            "data":"should be unchanged",
            "event": None
        }
        tree = {"nested": arg}

        chain = Chain().on(
            "nested/event",
            lambda e: e+1
        )

        result = chain(tree)

        self.assertEqual(result, {'nested': {'event': None, 'data': 'should be unchanged'}})


    def test_catch_no_error(self):
        Chain = self.Chain

        observer = TracerMiddleware()
        arg = []

        def step1(arg):
            return arg + [1]

        def step2(arg):
            return arg + [2]

        def step3(arg):
            return arg + [3]
        
        # def handle_error(error):
        #     error_trace.append("catched")

        def step4(arg):
            return arg + ["always"]

        chain = Chain(
            ).then(step1
            ).then(step2
            ).then(step3
            ).catch(handle_error
            ).then(step4
            )

        result = chain(arg, observer)

        self.assertListEqual(result, [1, 2, 3, 'always'])
        self.assertListEqual(observer.steps, ['step1', 'step2', 'step3', 'step4'])

    def test_catch_on_any_error(self):
        Chain = self.Chain

        observer = TracerMiddleware()
        arg = []

        def step1(arg):
            return arg + [1]

        def step2(arg):
            return arg + [2]

        def step_with_exception(arg):
            1/0
            return arg + [3]
        
        # def handle_error(err_info):
        #     extype, failure = err_info.popitem()
        #     self.log.warning(f">>>>>>>>>>>>>>> Triggered: handle_error: {extype};{failure};{err_info}")
        #     typename_extype = type(extype).__name__
        #     typename_failure = type(failure).__name__
        #     error_trace.append(f"catched, key type: {typename_extype}; value type: {typename_failure}")
        #     data_before_failure = failure.data_before_failure
        #     data_before_failure += [extype]
        #     return data_before_failure

        def step4(arg):
            return arg + ["always"]

        chain = Chain(
            ).then(step1
            ).then(step2
            ).then(step_with_exception
            ).catch(handle_error
            ).then(step4
            )

        result = chain(arg, observer)

        self.assertEqual(result, [1, 2, 'Catch any: ZeroDivisionError', 'always'])
        self.assertEqual(observer.steps, ['step1', 'step2', 'step_with_exception', 'handle_error', 'step4'])


    def test_catch_on_specific_error(self):
        Chain = self.Chain

        observer = TracerMiddleware()
        arg = []

        def step1(arg):
            return arg + [1]

        def step2(arg):
            return arg + [2]

        def step_with_exception_zero_division(arg):
            1/0
            return arg + [3]

        # def handle_error(error):
        #     self.log.warning(f">>>>>>>>>>>>>>> Triggered: handle_error: {error}")
        #     typename_error = type(error).__name__
        #     error_trace.append("catched: %s" % typename_error)
        #     data_before_failure = error.data_before_failure
        #     return data_before_failure

        def step4(arg):
            return arg + ["always"]

        chain = Chain(
            ).then(step1
            ).then(step2
            ).then(step_with_exception_zero_division
            ).catch_on(
                ZeroDivisionError,
                handle_selected_error
            ).then(step4
            )

        result = chain(arg, observer)

        self.assertListEqual(result, [1, 2, 'Catch only: ZeroDivisionError', 'always'])
        # self.assertListEqual(observer.steps, [1, 2, 'ZeroDivisionError', 'always'])

    def test_catch_allow_to_restore_data_before_failure(self):
        Chain = self.Chain

        arg = []

        def step1(arg):
            return arg + [1]

        def step2(arg):
            return arg + [2]

        def step_with_exception_zero_division(arg):
            1/0
            return arg + [3]

        def step4(arg):
            return arg + ["always"]

        chain = Chain(
            ).then(step1
            ).then(step2
            ).then(step_with_exception_zero_division
            ).catch_on(
                ZeroDivisionError,
                lambda e: None
            ).then(step4
            )

        result = chain(arg)

        self.assertListEqual(result, [1, 2, "always"])


    def test_catch_able_to_replace_envelope_after_exception(self):
        Chain = self.Chain

        arg = []

        def step1(arg):
            return arg + [1]

        def step2(arg):
            return arg + [2]

        def step_with_exception_zero_division(arg):
            1/0
            return arg + [3]

        # def handle_selected_error(error):
        #     arg = error.data_before_failure
        #     self.log.warning(f">>>>>>>>>>>>>>> Triggered: handle_error: {error}")
        #     error_trace.append("catched")
        #     return arg + ['recovered']

        def step4(arg):
            return arg + ["always"]

        chain = Chain(
            ).then(step1
            ).then(step2
            ).then(step_with_exception_zero_division
            ).catch_on(
                ZeroDivisionError,
                handle_selected_error
            ).then(step4
            )

        result = chain(arg)

        self.assertEqual(result, [1, 2, 'Catch only: ZeroDivisionError', 'always'])


    def test_catch_on_should_ignore_other_error(self):
        Chain = self.Chain

        observer = TracerMiddleware()
        arg = []

        def step1(arg):
            return arg + [1]

        def step2(arg):
            return arg + [2]

        def step_with_exception_key_error(arg):
            {}["Key"]
            return arg + [4]

        # def handle_selected_error(error):
        #     extype, failure = error.popitem()
        #     self.log.warning(f">>>>>>>>>>>>>>> Triggered: handle_error: {extype}")
        #     print("ERROR========================>: ", str(failure), repr(failure))
        #     error_trace.append("specific catched")

        # def handle_any_error(error):
        #     extype, failure = error.popitem()
        #     self.log.warning(f">>>>>>>>>>>>>>> Triggered: handle_any_error: {extype}")
        #     print("ERROR------------------------>: ", repr(failure))
        #     error_trace.append("catched")

        def step4(arg):
            print("Step 4:", arg)
            return arg + ["always"]

        chain = Chain(
            ).then(step1
            ).then(step2
            ).then(step_with_exception_key_error
            ).catch_on(
                ZeroDivisionError,
                handle_selected_error
            ).catch(handle_error
            ).then(step4
            )

        result = chain(arg, observer)

        self.assertListEqual(result, [1, 2, 'Catch any: KeyError', 'always'], "Normal trace deviation")
        self.assertListEqual(observer.steps, ['step1', 'step2', 'step_with_exception_key_error', 'handle_error', 'step4'], "Failure trace deviation")



    def test_skip_following(self):
        Chain = self.Chain
        SkipFollowing = self.SkipFollowing

        observer = TracerMiddleware()
        # error_trace = []
        arg = []

        def step1(arg):
            return arg + [1]

        def step2(arg):
            return arg + [2]

        def step_with_exception(arg):
            raise SkipFollowing("Jump to bottom!")
            return arg + [0]

        def step3(arg):
            return arg + [3]

        def step4(arg):
            return arg + [4]

        # def handle_skip(error):
        #     self.log.warning(f">>>>>>>>>>>>>>> Catched: handle_error: {error}")
        #     # error_trace.append("catched")

        def step5(arg):
            return arg + ["always"]

        chain = Chain(
            ).then(step1 # Should be passed
            ).then(step2 # Should be passed
            ).then(step_with_exception # Should be invoked
            ).on("some_key", step3 # Should be ignored
            ).then(step4
            ).catch_on(
                SkipFollowing,
                handle_selected_error
            ).then(step5
            )

        result = chain(arg, observer)

        self.assertListEqual(result, [1, 2, 'Catch only: SkipFollowing', 'always'])
        self.assertListEqual(observer.steps, ['step1', 'step2', 'step_with_exception', 'handle_selected_error', 'step5'])


    def test_data_after_catched_exception_should_be_same(self):
        Chain = self.Chain

        arg = {"data": None}

        def step1(arg):
            arg["data"] = "Some"
            return arg

        def step_with_exception(arg):
            1/0
            # Unreachable code:
            arg["Data"] = "Never!"
            return arg 

        chain = Chain(
            ).then(step1 # Should be passed
            ).then(step_with_exception # Should be invoked
            ).catch(
                lambda failure: None
            )

        result = chain(arg)

        self.assertDictEqual(result, {'data': 'Some'})


    def test_data_after_catched_exception_could_be_changed(self):
        Chain = self.Chain

        arg = {"data": None}

        def step1(arg):
            arg["data"] = "Some"
            return arg

        def step_with_exception(arg):
            1/0
            # Unreachable code:
            arg["Data"] = "Never!"
            return arg 

        chain = Chain(
            ).then(step1 # Should be passed
            ).then(step_with_exception # Should be invoked
            ).catch(
                lambda failure: {"data": "Changed!"}
            )

        result = chain(arg)

        self.assertDictEqual(result, {'data': 'Changed!'})

    def test_data_after_catched_exception_should_be_same_for_children(self):
        Chain = self.Chain

        arg = {"data": "Initial"}

        def step1(arg):
            return "Some"

        def step_with_exception(arg):
            1/0
            # Unreachable code:
            arg["Data"] = "Never!"
            return arg 

        chain = Chain(
            ).on("data", step1 # Should be passed
            ).then(step_with_exception # Should be invoked
            ).catch(
                lambda failure: None
            )

        result = chain(arg)

        self.assertDictEqual(result, {'data':'Some'})


    def test_data_after_catched_exception_could_be_changed_for_children(self):
        Chain = self.Chain

        arg = {"data": "Initial"}

        def step1(arg):
            return "Some"

        def step_with_exception(arg):
            1/0
            # Unreachable code:
            arg["Data"] = "Never!"
            return arg 

        chain = Chain(
            ).on("data", step1 # Should be passed
            ).then(step_with_exception # Should be invoked
            ).catch(
                lambda failure: {"data":"Changed!"}
            )

        result = chain(arg)

        self.assertDictEqual(result, {'data': 'Changed!'})


    def test_data_after_catched_exception_should_be_same_for_children_case2(self):
        Chain = self.Chain

        arg = {"data": "Initial"}

        def step1(arg):
            return "Some"

        def step_with_exception(arg):
            1/0
            # Unreachable code:
            return "Never!"
        
        def err_handler(failure):
            topic = failure.topic
            return None

        chain = Chain(
            ).on("data", step1 # Should be passed
            ).on("data", step_with_exception # Should be invoked
            ).catch(err_handler
            )

        result = chain(arg)

        self.assertDictEqual(result, {'data':'Some'})


    def test_data_after_catched_exception_could_be_changed_for_children_case2(self):
        Chain = self.Chain

        arg = {"data": "Initial"}

        def step1(arg):
            return "Some"

        def step_with_exception(arg):
            1/0
            # Unreachable code:
            return "Never!"

        def err_handler(failure):
            # NOTE: we changing only child value here because exception occurs in a child value
            print("SAVED: ", failure.data_before_failure)
            topic = failure.topic
            return "Child value in topic '%s'" % topic

        chain = Chain(
            ).on("data", step1 # Should be passed
            ).on("data", step_with_exception # Should be invoked
            ).catch(err_handler
            )

        result = chain(arg)

        self.assertDictEqual(result, {'data': "Child value in topic 'data'"})

# def handle_error(err_info):
def handle_error(failure):
    "Common generic handler for all tests"
    # extype, failure = err_info.popitem()
    extype = failure.exc_name
    print("\nGENERIC HANDLER =====>", extype, failure)
    typename_extype = type(extype).__name__
    typename_failure = type(failure).__name__
    # error_trace.append(f"catched, key type: {typename_extype}; value type: {typename_failure}")
    data_before_failure = failure.data_before_failure
    # data_before_failure += [extype]
    return data_before_failure + ["Catch any: %s" % extype]

def handle_selected_error(failure):
    print("\nNARROW HANDLER========================>: ", str(failure))
    # error_trace.append("specific catched")
    data_before_failure = failure.data_before_failure
    # data_before_failure += [extype]
    return data_before_failure + ["Catch only: %s" % failure.exc_name]


class TracerMiddleware:
    def __init__(self):
        self.steps = []
    
    def __call__(self, method, ctx, **kwargs):
        method_name = method.__name__
        print("STEP: ", method_name, kwargs)
        self.steps.append(method_name)
        return method(ctx)


if __name__ == '__main__':
    unittest.main(verbosity=2)
